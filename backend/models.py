from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel

# --- CATEGORY ---
class CategoryBase(SQLModel):
    name: str 
    type: str  # "Revenu" or "Dépense"

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# --- USER ---
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

# --- TRANSACTION ---
class TransactionBase(SQLModel):
    description: str
    amount: float
    date: datetime = Field(default_factory=datetime.utcnow)
    category_id: int = Field(foreign_key="category.id")

# models.py

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # AJOUTE CETTE LIGNE :
    user_id: int = Field(foreign_key="user.id")


class TransactionRead(TransactionBase):
    id: int

class BudgetBase(SQLModel):
    category_id: int = Field(foreign_key="category.id")
    monthly_limit: float = Field(default=0.0)
    month: int
    year: int

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

class BudgetRead(BudgetBase): 
    id: int