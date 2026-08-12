import logging
from contextlib import asynccontextmanager
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import text
from fastapi.responses import HTMLResponse

from app.database import engine, get_session, create_db_and_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    stock: int


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)


class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserCreate(SQLModel):
    name: str
    email: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def portfolio():
    html_content = """
    <html>
    <head>
        <title>Mildred Kuria - Backend Development Portfolio</title>

        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }

            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }

            .student-info {
                background: #e8f4fd;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }

            .student-info strong {
                color: #2c3e50;
            }

            .admission {
                font-size: 1.2em;
                color: #2980b9;
                font-weight: bold;
            }

            .assignment {
                margin: 12px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #3498db;
                transition: all 0.3s ease;
            }

            .assignment:hover {
                background: #e8f4fd;
                transform: translateX(5px);
            }

            .assignment a {
                color: #0366d6;
                text-decoration: none;
                font-weight: 500;
                display: flex;
                align-items: center;
            }

            .assignment a:hover {
                text-decoration: underline;
            }

            .badge {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 0.8em;
                margin-right: 10px;
                white-space: nowrap;
            }

            .lesson-topic {
                color: #7f8c8d;
                font-size: 0.9em;
                margin-left: 10px;
            }

            .footer {
                margin-top: 30px;
                text-align: center;
                color: #95a5a6;
                font-size: 0.9em;
                border-top: 1px solid #ecf0f1;
                padding-top: 20px;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>Backend Development Portfolio 📚</h1>

            <div class="student-info">
                <p>
                    <strong>Student Name:</strong>
                    Mildred Kuria
                </p>

                <p>
                    <strong>Admission Number:</strong>
                    <span class="admission">
                        C027-01-0857/2024
                    </span>
                </p>

                <p>
                    <strong>Email:</strong>
                    mildred.kuria24@students.dkut.ac.ke 📧
                </p>
            </div>


            <h2>Backend Assignments 📝</h2>

            <p style="color: #7f8c8d; margin-bottom: 20px;">
                Click on any assignment to view the complete code on GitHub.
            </p>


            <!-- LESSON 1 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/gighub-api"
                   target="_blank">

                    <span class="badge">Lesson 1</span>

                    <span>HTTP & Your First API</span>

                    <span class="lesson-topic">
                        — FastAPI + Uvicorn, HTTP Methods, Status Codes
                    </span>

                </a>
            </div>


            <!-- LESSON 2 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/bookstore-api"
                   target="_blank">

                    <span class="badge">Lesson 2</span>

                    <span>Docker - Packaging Your API</span>

                    <span class="lesson-topic">
                        — Containers, Dockerfiles, Docker Compose
                    </span>

                </a>
            </div>


            <!-- LESSON 3 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/gighub-api"
                   target="_blank">

                    <span class="badge">Lesson 3</span>

                    <span>Routing, Parameters & Request Bodies</span>

                    <span class="lesson-topic">
                        — Path Parameters, Query Parameters, Pydantic Validation
                    </span>

                </a>
            </div>


            <!-- LESSON 4 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/library-api"
                   target="_blank">

                    <span class="badge">Lesson 4</span>

                    <span>PostgreSQL & SQLModel – Your First Database</span>

                    <span class="lesson-topic">
                        — ORM, Database Migrations, SQLModel
                    </span>

                </a>
            </div>


            <!-- LESSON 5 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/bookstore-api"
                   target="_blank">

                    <span class="badge">Lesson 5</span>

                    <span>CRUD Operations</span>

                    <span class="lesson-topic">
                        — Create, Read, Update, Delete with Error Handling
                    </span>

                </a>
            </div>


            <!-- LESSON 6 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/healthtrack-api"
                   target="_blank">

                    <span class="badge">Lesson 6</span>

                    <span>Error Handling & Validation</span>

                    <span class="lesson-topic">
                        — HTTPException, Custom Validators, Global Handlers
                    </span>

                </a>
            </div>


            <!-- LESSON 7 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/healthtrack-api"
                   target="_blank">

                    <span class="badge">Lesson 7</span>

                    <span>User Authentication – JWT & Password Hashing</span>

                    <span class="lesson-topic">
                        — JWT Tokens, bcrypt, Login/Register Endpoints
                    </span>

                </a>
            </div>

<!-- LESSON 8 -->

<div class="assignment">
<a href="https://github.com/zanzikuria-create/clinicguard-api"
                   target="_blank">
    <span class="badge">Lesson 8</span>

    <span>Authorization & Rate Limiting</span>

    <span class="lesson-topic">
        — RBAC, Dependency Injection, Rate Limiting
    </span>

            
                </a>
            </div>


            <!-- LESSON 9 -->

            <div class="assignment">
                <a href="https://github.com/zanzikuria-create/fastapi-file-upload-external-api"
                   target="_blank">

                    <span class="badge">Lesson 9</span>

                    <span>File Uploads & External APIs</span>

                    <span class="lesson-topic">
                        — File Validation, httpx, Environment Variables
                    </span>

                </a>
            </div>
<!-- LESSON 10 -->

<div class="assignment">
    <span class="badge">Lesson 10</span>

    <span>Testing & Deployment (Cloud)</span>

    <span class="lesson-topic">
        — Pytest, CI/CD, Render Deployment
    </span>


           
            </div>


            <div class="footer">
                Backend Development Portfolio — Mildred Kuria
            </div>

        </div>

    </body>
    </html>
    """

    return html_content


@app.get("/health")
async def health_check(session: Session = Depends(get_session)):
    try:
        session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "error"}


@app.post("/products", status_code=201)
def create_product(product: Product, session: Session = Depends(get_session)):
    logger.info(f"Creating product: {product.name}")
    session.add(product)
    session.commit()
    session.refresh(product)
    logger.info(f"Product created with id={product.id}")
    return product


@app.get("/products/{product_id}")
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")

    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }


@app.get("/weather/{city}")
async def get_weather(city: str):
    logger.info(f"Fetching weather for city: {city}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": "demo_key", "units": "metric"},
                timeout=5.0,
            )
    except httpx.TimeoutException:
        logger.error(f"Weather service timed out for city: {city}")
        raise HTTPException(status_code=503, detail="Weather service timed out")

    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "conditions": data["weather"][0]["description"],
    }


@app.post("/users", status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating user with email: {user.email}")
    existing = session.exec(select(User).where(User.email == user.email)).first()
    if existing:
        logger.warning(f"Duplicate email attempted: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(name=user.name, email=user.email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    logger.info(f"User created with id={db_user.id}")
    return db_user


@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}")
def update_user(
    user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
