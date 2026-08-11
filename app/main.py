import logging
from contextlib import asynccontextmanager
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import text

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


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