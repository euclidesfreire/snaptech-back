from newsdataapi import NewsDataApiClient
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session
from models import Article
import requests
import time

#class Article(BaseModel):
#    article_token: Optional[str]
#    title: str
#    description: Optional[str]
#    link: Optional[str]
#    image_url: Optional[str]

NEWS_API_KEY = "pub_624603223c8e181a61bcd17adc1b2a82cdaa8"
NEWS_API_URL = "https://newsdata.io/api/1/latest"

def get_articles_api(q = "", country = "br", category = "technology", session=Session):

    # You can paginate till last page by providing "page" parameter
    page=None
    
    articles = []

    while True:

        response = requests.get(NEWS_API_URL, params={"category": "technology", "country": "br", "page": page, "apiKey": NEWS_API_KEY})
        data = response.json()

        print(data)

        if "results" not in data:
            break
            #raise HTTPException(status_code=400, detail="Erro ao buscar notícias")

        for article in data["results"]:
            new_article = Article(
                article_token=article["article_id"],
                title=article["title"],
                description=article["description"],
                link=article["link"],
                image_url=article["image_url"]
            )
            
            session.add(new_article)
            articles.append(new_article)

        page = data.get('nextPage',None)

        print(page)

        session.commit()

        if not page:
            break
    
    return articles