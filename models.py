from sqlmodel import SQLModel, Field
from typing import Optional

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    content: Optional[str]
    url: str
    liked_by_users: int = 0  # Contador de likes

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str

class UserInteraction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    article_id: int
    liked: bool  # True para "gostou", False para "não gostou"
