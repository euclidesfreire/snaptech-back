from sqlmodel import SQLModel, Field
from typing import Optional

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: Optional[str]
    title: str
    description: Optional[str]
    content: Optional[str]
    link: Optional[str]
    image_url: Optional[str]
    liked_by_users: int = 0  
    disliked_by_users: int = 0  
    
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

class UserInteraction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    article_id: int
    liked: bool = Field(default=False)
    dislike: bool = Field(default=False)

