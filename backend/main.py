from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from models import User, Category, Transaction, TransactionRead, TransactionBase, CategoryBase, UserBase, Budget, BudgetRead, BudgetBase

from database import create_db_and_tables, engine, get_session
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI()

# Add CORS middleware for AJAX requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    create_initial_categories()
    create_default_user()

def create_initial_categories():
    """Create initial categories if they don't exist"""
    with Session(engine) as session:
        existing = session.exec(select(Category)).first()
        if not existing:
            categories = [
                Category(name="Salaire", type="Revenu"),
                Category(name="Freelance", type="Revenu"),
                Category(name="Alimentation", type="Dépense"),
                Category(name="Transport", type="Dépense"),
                Category(name="Loisirs", type="Dépense"),
                Category(name="Logement", type="Dépense"),
            ]
            for category in categories:
                session.add(category)
            session.commit()

def create_default_user():
    """Create default admin user if doesn't exist"""
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.email == "admin@budget.com")).first()
        if not existing_user:
            hashed_password = get_password_hash("admin123")
            admin_user = User(email="admin@budget.com", hashed_password=hashed_password)
            session.add(admin_user)
            session.commit()
            print("✅ Default admin user created: admin@budget.com / admin123")

@app.get("/")
def read_root():
    return FileResponse('static/login.html')

@app.get("/summary")
def get_summary(session = Depends(get_session), current_user = Depends(get_current_user)):    # Correction : On joint la table Transaction et Category pour filtrer par type
    statement = select(Transaction).join(Category)
    transactions = session.exec(statement).all()
    
    total_income = sum(t.amount for t in transactions if t.category.type == "Revenu")
    total_expense = sum(t.amount for t in transactions if t.category.type == "Dépense")

    return {"total_income": total_income, "total_expense": total_expense}

@app.get("/stats/")
def get_stats(month: int, year: int, session = Depends(get_session), current_user = Depends(get_current_user)):
    date_prefix = f"{year}-{month:02d}"
    
    # ❌ ERREUR : select(Transaction).where(Transaction.user_id == current_user.id)
    # ✅ CORRECT : Ajouter le filtre .like(f"{date_prefix}%")
    statement = select(Transaction).where(
        Transaction.user_id == current_user.id,
        Transaction.date.like(f"{date_prefix}%") 
    )
    try:
        # 1. Base de la requête : filtrer par utilisateur
        statement = select(Transaction).where(Transaction.user_id == current_user.id)
        
        # 2. AJOUT : Si on a reçu un mois et une année, on filtre la SQL
        if month and year:
            # On cherche les dates qui commencent par "YYYY-MM"
            prefix = f"{year}-{month:02d}"
            statement = statement.where(Transaction.date.like(f"{prefix}%"))

        # 3. On exécute la requête (filtrée ou non)
        transactions = session.exec(statement).all()
        
        # --- Le reste de ton code de calcul ne change PAS ---
        categories = {c.id: c for c in session.exec(select(Category)).all()}
        expenses_by_category = {}
        total_income = 0
        total_expense = 0
        
        for t in transactions:
            cat = categories.get(t.category_id)
            if not cat: continue
            amount = abs(t.amount)
            if cat.type == "Dépense":
                expenses_by_category[cat.name] = expenses_by_category.get(cat.name, 0) + amount
                total_expense += amount
            else:
                total_income += amount
                
        return {
            "expenses_by_category": expenses_by_category,
            "total_income": total_income,
            "total_expense": total_expense
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/")
def get_history(session = Depends(get_session), current_user = Depends(get_current_user)):
    try:
        statement = select(Transaction).where(Transaction.user_id == current_user.id)
        transactions = session.exec(statement).all()
        
        history_map = {}
        for t in transactions:
            # On s'assure que la date est une chaîne de caractères
            date_str = str(t.date) 
            # On extrait le "YYYY-MM" (les 7 premiers caractères)
            # Exemple: "2024-03-30" -> "2024-03"
            month_key = date_str[:7]
            
            if month_key not in history_map:
                history_map[month_key] = {"income": 0, "expense": 0}
                
            if t.amount > 0:
                history_map[month_key]["income"] += t.amount
            else:
                history_map[month_key]["expense"] += abs(t.amount)
                
        # On prépare la liste pour le frontend
        result = []
        for month, vals in history_map.items():
            result.append({
                "month_label": month,
                "income": round(vals["income"], 2),
                "expense": round(vals["expense"], 2)
            })
            
        # Tri du plus récent au plus ancien
        return sorted(result, key=lambda x: x["month_label"], reverse=True)
        
    except Exception as e:
        print(f"❌ Erreur critique dans /history/: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)):
    """Login endpoint - returns JWT token"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_users_me(current_user: UserBase = Depends(get_current_user)):
    """Get current user info"""
    return {"id": current_user.id, "email": current_user.email}

@app.get("/categories/", response_model=List[Category])
def get_categories(session = Depends(get_session), current_user = Depends(get_current_user)):
    return session.exec(select(Category)).all()

@app.post("/categories/")
def create_category(data: dict, session = Depends(get_session)): # Remplacement par dict
    category = Category(**data)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@app.get("/transactions/")
def get_transactions(
    month: int = None, 
    year: int = None, 
    limit: int = 1000,
    session = Depends(get_session), 
    current_user = Depends(get_current_user)
):
    statement = select(Transaction).where(Transaction.user_id == current_user.id)
    
    # 🎯 LE FILTRE MANQUANT EST ICI :
    if month and year:
        prefix = f"{year}-{month:02d}"
        statement = statement.where(Transaction.date.like(f"{prefix}%"))
    
    # On trie par date pour voir les plus récentes en haut
    statement = statement.order_by(Transaction.date.desc()).limit(limit)
    
    return session.exec(statement).all()

@app.post("/transactions/", response_model=TransactionRead)
def create_transaction(
    transaction_in: TransactionBase, 
    session = Depends(get_session), 
    current_user = Depends(get_current_user)
):
    try:
        # 1. On transforme le schéma reçu en dictionnaire
        data = transaction_in.model_dump()
        
        # 2. On crée l'objet de table
        db_transaction = Transaction(**data)
        
        # 3. LA CORRECTION : On lie la transaction à l'utilisateur connecté
        # On utilise current_user.id qui vient du token JWT
        db_transaction.user_id = current_user.id 

        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
        return db_transaction
        
    except Exception as e:
        session.rollback()
        print(f"❌ ERREUR SQL: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    # 1. Supprimer une transaction
@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, session = Depends(get_session), current_user = Depends(get_current_user)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    session.delete(transaction)
    session.commit()
    return {"detail": "Supprimée"}

# 2. Éditer une transaction
@app.put("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, transaction_update: TransactionBase, session = Depends(get_session), current_user = Depends(get_current_user)):
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction or db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    # Mise à jour des champs
    for key, value in transaction_update.model_dump().items():
        setattr(db_transaction, key, value)
    
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

# 3. Calculer les plafonds par catégorie
@app.get("/budget-status/")
@app.get("/budget-status/")
def get_budget_status(
    month: int, 
    year: int, 
    session = Depends(get_session), 
    current_user = Depends(get_current_user)
):
    print(f"🔍 Requête budget pour : {month}/{year}")
    categories = session.exec(select(Category).where(Category.type == "Dépense")).all()
    
    results = []
    # Format du préfixe de date pour le filtrage SQL (ex: "2026-03")
    date_prefix = f"{year}-{month:02d}"

    for cat in categories:
        # 1. Calculer les dépenses réelles UNIQUEMENT pour ce mois et cet utilisateur
        trans_stmt = select(Transaction).where(
            Transaction.user_id == current_user.id, 
            Transaction.category_id == cat.id,
            Transaction.date.like(f"{date_prefix}%") # Filtrage par mois ici !
        )
        transactions = session.exec(trans_stmt).all()
        spent = sum(abs(t.amount) for t in transactions)
        
        # 2. Chercher la limite spécifique à ce MOIS et cette ANNÉE en base
        budg_stmt = select(Budget).where(
            Budget.user_id == current_user.id, 
            Budget.category_id == cat.id,
            Budget.month == month,
            Budget.year == year
        )
        budget_record = session.exec(budg_stmt).first()
        
        # Si aucun budget n'est défini pour ce mois précis, on met 0.0 (ou 200.0 selon ta préférence)
        limit = budget_record.monthly_limit if budget_record else 0.0
        
        results.append({
            "category_id": cat.id,
            "category": cat.name,
            "spent": round(spent, 2),
            "limit": limit,
            "percent": min((spent / limit) * 100, 100) if limit > 0 else 0
        })
        
    return results

@app.post("/budgets/", response_model=BudgetRead)
def set_budget(budget_in: BudgetBase, session = Depends(get_session), current_user = Depends(get_current_user)):
    # Vérifier si un budget existe déjà pour ce mois/catégorie
    statement = select(Budget).where(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_in.category_id,
        Budget.month == budget_in.month,
        Budget.year == budget_in.year
    )
    existing_budget = session.exec(statement).first()
    
    if existing_budget:
        existing_budget.monthly_limit = budget_in.monthly_limit
        db_budget = existing_budget
    else:
        db_budget = Budget.model_validate(budget_in)
        db_budget.user_id = current_user.id
        
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget

@app.post("/update-budget/")
def update_budget(
    category_id: int, 
    limit: float, 
    session = Depends(get_session), 
    current_user = Depends(get_current_user)
):

    statement = select(Budget).where(
        Budget.user_id == current_user.id, 
        Budget.category_id == category_id
    )
    db_budget = session.exec(statement).first()

    if db_budget:
        db_budget.monthly_limit = limit
    else:
        db_budget = Budget(
            category_id=category_id, 
            monthly_limit=limit, 
            user_id=current_user.id,
            month=datetime.now().month,
            year=datetime.now().year
        )
    
    session.add(db_budget)
    session.commit()
    return {"status": "success", "limit": limit}

# Supprimer une catégorie
@app.post("/categories/", response_model=Category)
def create_category(category: Category, session = Depends(get_session), current_user = Depends(get_current_user)):
    # On peut même imaginer lier les catégories à l'utilisateur si on veut, 
    # mais ici on va les créer pour tout le monde pour simplifier
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

# Supprimer une catégorie
@app.delete("/categories/{category_id}")
def delete_category(category_id: int, session = Depends(get_session), current_user = Depends(get_current_user)):
    statement = select(Category).where(Category.id == category_id)
    category = session.exec(statement).first()
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    # Attention: Supprimer une catégorie peut impacter les transactions liées
    session.delete(category)
    session.commit()
    return {"status": "success"}

# Définir le budget spécifique à un mois
@app.post("/set-monthly-budget/")
def set_monthly_budget(cat_id: int, limit: float, month: int, year: int, session = Depends(get_session), current_user = Depends(get_current_user)):
    statement = select(Budget).where(
        Budget.category_id == cat_id, 
        Budget.month == month, 
        Budget.year == year,
        Budget.user_id == current_user.id
    )
    budget = session.exec(statement).first()
    if budget:
        budget.monthly_limit = limit
    else:
        budget = Budget(category_id=cat_id, monthly_limit=limit, month=month, year=year, user_id=current_user.id)
    session.add(budget)
    session.commit()
    return {"status": "ok"}

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")