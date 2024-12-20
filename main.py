import requests
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Article, UserInteraction, User
#from ml.recommender import collaborative_filtering

app = FastAPI()

NEWS_API_KEY = "pub_624603223c8e181a61bcd17adc1b2a82cdaa8"
NEWS_API_URL = "https://newsdata.io/api/1/latest"

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/search/")
def search_news(session: Session = Depends(get_session)):
    response = requests.get(NEWS_API_URL, params={"category": "technology", "country": "br", "apiKey": NEWS_API_KEY})
    data = response.json()
    print(data)
    print("data r")
    print(data["results"])
    if "results" not in data:
        raise HTTPException(status_code=400, detail="Erro ao buscar notícias")

    articles = []
    for article in data["results"]:
        new_article = Article(
            article_id=article["article_id"],
            title=article["title"],
            description=article["description"],
            link=article["link"],
            image_url=article["image_url"]
        )
        session.add(new_article)
        articles.append(new_article)
    session.commit()
    
    return articles

@app.get("/articles/")
def get_articles(session: Session = Depends(get_session)):
    statement = select(Article)
    results = session.exec(statement)
    return results.all()

@app.post("/articles/{article_id}/like/")
def like_article(article_id: int, user_id: int, liked: bool, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    interaction = UserInteraction(user_id=user_id, article_id=article_id, liked=liked)
    session.add(interaction)

    if liked:
        article.liked_by_users += 1
    session.commit()
    return {"message": "Interação registrada"}

#@app.get("/recommendations/")
#def get_recommendations(user_id: int, session: Session = Depends(get_session)):
#    interactions = session.query(UserInteraction).all()
#    articles = {article.id: article for article in session.query(Article).all()}
#    recommendations = collaborative_filtering(interactions, articles, user_id)
#    return recommendations