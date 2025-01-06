from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User


router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)

@app.post("/users")
def post_user(email: str, session: Session = Depends(get_session)):
    new_user = User(
        email=email
    )

    session.add(new_user)
    session.commit()

@app.get("/users/{id}")
def get_user(id: int, session: Session = Depends(get_session)):
     #Consulta usuário pelo ID
    statement = select(User).where(User.id == id)
    result = session.exec(statement).first()  # Retorna o primeiro resultado
    return result

@app.post("/login")
def login(email: str, session: Session = Depends(get_session)):
     #Consulta usuário pelo ID
    statement = select(User).where(User.email == email)
    result = session.exec(statement).first()  # Retorna o primeiro resultado
    return result