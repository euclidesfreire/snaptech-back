from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Article, UserInteraction

router = APIRouter(
    prefix="/articles",
    responses={404: {"description": "Not found"}}
)

NEWS_API_KEY = "pub_624603223c8e181a61bcd17adc1b2a82cdaa8"
NEWS_API_URL = "https://newsdata.io/api/1/latest"

@app.get("/fetch/latest")
def fetch_latest(session: Session = Depends(get_session)):
    response = requests.get(NEWS_API_URL, params={"category": "technology", "country": "br", "apiKey": NEWS_API_KEY})
    data = response.json()

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

@app.get("/")
def get_articles(session: Session = Depends(get_session)):
    statement = select(Article)
    results = session.exec(statement)
    return results.all()

@app.get("/{id}", response_model=Article)
def get_article(id: int, session: Session = Depends(get_session)):
    article = session.get(Article, id)
        
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    return article

@app.post("/{article_id}/like")
def like_article(article_id: int, user_id: int, liked: bool, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    statement = select(UserInteraction).where(
    UserInteraction.user_id == user_id,
    UserInteraction.article_id == article_id
    )

    interaction = session.exec(UserInteraction).first()

    if not interaction:

    interaction = UserInteraction(user_id=user_id, article_id=article_id, liked=liked)
    session.add(interaction)

    if liked:
        article.like_by_users += 1
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
    