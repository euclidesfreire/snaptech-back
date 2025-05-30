from sqlmodel import SQLModel, Field
from typing import Optional

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: Optional[str]
    title: str
    description: Optional[str]
    #content: Optional[str]
    #keywords: Optional[str]
    #category: Optional[str]
    #pubDate: Optional[str]
    #duplicate: Optional[bool]
    #source_id: Optional[str]
    #source_name: Optional[str]
    #source_priority: Optional[int]
    #country: Optional[str]
    #creator: Optional[str]
    link: Optional[str]
    #language: Optional[str]
    image_url: Optional[str]
    like_by_users: int = 0  
    dislike_by_users: int = 0  
    
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

class UserInteraction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    article_id: int
    like: bool = Field(default=False)
    dislike: bool = Field(default=False)

