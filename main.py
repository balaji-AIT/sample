import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

# Load environment variables from .env file
load_dotenv()

# Read DATABASE_URL from Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create Database Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create Session
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Declare Base
Base = declarative_base()

# FastAPI App
app = FastAPI()

# Dependency to Get DB Session
async def get_db():
    async with SessionLocal() as session:
        yield session

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Create Tables on Startup
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    print('hello')
    return {"message": "FastAPI + PostgreSQL"}

@app.post("/users/")
async def create_user(name: str, db: AsyncSession = Depends(get_db)):
    new_user = User(name=name)
    db.add(new_user)
    await db.commit()
    return {"id": new_user.id, "name": new_user.name}

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name}
