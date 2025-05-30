from sqlmodel import Session
from models import Article, UserInteraction
import random
from pydantic import BaseModel
from models import Article, UserInteraction, User
from ml.recommender import cold_start, collaborative_filtering
from articles import get_articles_api
import time

class UserInteractionStart(BaseModel):
    id: int
    user_id: int
    article_id: int
    like: bool
    dislike: bool

def load_data(users=User, articles=Article, session=Session):

    for i in range(0,150): 
        email=f"usuario{i}@dominio.com"
        post_user(email, session)

    users = get_user_all(session)
    articles = get_articles(session)
    
    interactions = {}

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
