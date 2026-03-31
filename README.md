# 💰 Budget Manager

A full-stack financial tracking application designed for precision and ease of use. This project features a robust **FastAPI** backend and a dynamic **Vanilla JS** frontend, all containerized with **Docker**.

## Features
* **Transaction Management**: Add, categorize, and track your expenses and income.
* **Monthly History**: Automated month-to-month financial summaries.
* **Interactive Analytics**: Visual breakdowns of spending habits using **Chart.js**.
* **Budget Goals**: Set monthly limits per category with real-time progress bars.
* **Secure Authentication**: JWT-based protected routes and user management.

## Tech Stack
* **Backend**: Python, FastAPI, SQLAlchemy (SQLite).
* **Frontend**: HTML5, CSS3, JavaScript (ES6+), Chart.js.
* **DevOps**: Docker, Docker Compose, Nginx (Reverse Proxy).
* **CI/CD**: GitHub Actions for automated testing and deployment.
* **Security**: Let's Encrypt SSL/TLS, JWT Authentication.

## Installation & Deployment
1. **Clone the repository**:
```bash
git clone [https://github.com/johnlepython/budget.git](https://github.com/johnlepython/budget.git)
cd budget
```
   
## Launch with Docker:
```bash
docker-compose up --build
```

## Access the App:
Navigate to https://budget.jsdconsult.cloud (or http://localhost:8000 for local dev).
Public test user: demo@test.com / demo1234

## Testing
The project uses Pytest with HTTPX for asynchronous API testing:

```bash
pytest backend/tests/
```

