import requests
import random
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from pydantic import BaseModel
from models import Article, UserInteraction, User
from ml.recommender import cold_start_filtering, cluster_filtering, collaborative_filtering
from articles import get_articles_api
import time

app = FastAPI()

NEWS_API_KEY = "pub_624603223c8e181a61bcd17adc1b2a82cdaa8"
NEWS_API_URL = "https://newsdata.io/api/1/latest"

class UserInteractionStart(BaseModel):
    id: int
    user_id: int
    article_id: int
    like: bool
    dislike: bool

class EmailRequest(BaseModel):
    email: str

@app.get("/fetch/latest")
def fetch_latest(session: Session = Depends(get_session)):
    get_articles_api(session=session)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/users/")
def create_user(data: EmailRequest, session: Session = Depends(get_session)):

    success = post_user(data.email, session)

    return {'success': True}

def post_user(email: str, session: Session):
    new_user = User(
        email=email
    )

    session.add(new_user)
    session.commit()

@app.get("/users/{id}/")
def get_user(id: int, session: Session = Depends(get_session)):
     #Consulta usuário pelo ID
    statement = select(User).where(User.id == id)
    result = session.exec(statement).first()  # Retorna o primeiro resultado
    return result

@app.get("/users/check-email")
def get_user(email: str, session: Session = Depends(get_session)):
    #Consulta usuário pelo ID
    statement = select(User).where(User.email == email)
    result = session.exec(statement).first()  # Retorna o primeiro resultado

    data = { 'exists': True }

    if not result:
        data = { 'exists': False }

    return data

@app.get("/users/")
def get_user_all(session: Session = Depends(get_session)):
    statement = select(User)
    results = session.exec(statement)
    return results.all()

@app.get("/articles/")
def get_articles(session: Session = Depends(get_session)):
    statement = select(Article)
    results = session.exec(statement)
    return results.all()

@app.get("/articles/{id}", response_model=Article)
def get_article(id: int, session: Session = Depends(get_session)):
    article = session.get(Article, id)
        
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    return article

@app.post("/articles/{article_id}/like/")
def create_like_article(article_id: int, user_id: int, like: bool, session: Session = Depends(get_session)):
    return like_article(article_id, user_id, like, session)


def like_article(article_id: int, user_id: int, like: bool, session: Session):
    article = session.get(Article, article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    interaction = UserInteraction(user_id=user_id, article_id=article_id, like=like, dislike=False)
    session.add(interaction)

    if like:
        article.like_by_users += 1
    else:
        article.like_by_users -= 1

    session.commit()

    return {"message": "Interação registrada"}

@app.post("/articles/{article_id}/dislike/")
def create_dislike_article(article_id: int, user_id: int, dislike: bool, session: Session = Depends(get_session)):
    return dislike_article(article_id, user_id, dislike, session)

def dislike_article(article_id: int, user_id: int, dislike: bool, session: Session):
    article = session.get(Article, article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    interaction = UserInteraction(user_id=user_id, article_id=article_id, dislike=dislike, like=False)
    session.add(interaction)

    if dislike:
        article.dislike_by_users += 1
    else:
        article.dislike_by_users -= 1

    session.commit()

    return {"message": "Interação registrada"}

@app.get("/interactions/users/{user_id}")
def get_users_interactions(user_id: int, session: Session = Depends(get_session)):
    statement = select(UserInteraction).where(UserInteraction.user_id == user_id)
    
    interactions = session.exec(statement).all()
    
    return interactions

@app.get("/interactions/articles/{article_id}")
def get_articles_interactions(article_id: int, session: Session = Depends(get_session)):
    statement = select(UserInteraction).where(UserInteraction.article_id == article_id)
    
    interactions = session.exec(statement).all()
    
    return interactions

@app.get("/recommendations/cold_start")
def get_cold_start(session: Session = Depends(get_session)):
    interactions = session.query(UserInteraction).all()
    articles = {article.id: article for article in session.query(Article).all()}
    recommendations = cold_start_filtering(interactions, articles)

    return recommendations

@app.get("/recommendations/")
def get_recommendations(email: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == email)
    result = session.exec(statement).first()
    user_id = result.id

    interactions = session.query(UserInteraction).all()
    articles = {article.id: article for article in session.query(Article).all()}
    recommendations = collaborative_filtering(interactions, articles, user_id)

    return recommendations

@app.get("/start/")
def get_start(session: Session = Depends(get_session)):

    for i in range(0,150): 
        email=f"usuario{i}@dominio.com"
        post_user(email, session)

    
    interactions = {}

    users = get_user_all(session)
    articles = get_articles(session)

    for i in range(1,550):

        user_id_random = 0
        article_id_random = 0

        while True:

            user_id_random = random.choice([j.id for j in users])
            article_id_random = random.choice([k.id for k in articles])

            if (user_id_random, article_id_random) not in interactions:
                break

        liked=(like := random.choice([True, False]))
        disliked=not liked

        user_interaction = UserInteractionStart (
            id=i,
            user_id=user_id_random,
            article_id=article_id_random,
            like=liked,
            dislike=disliked
        )
    

        if like:
            like_article(article_id_random, user_id_random, liked, session)
        else:
            dislike_article(article_id_random, user_id_random, disliked, session)
        
        interactions[(user_id_random, article_id_random)] = user_interaction

    