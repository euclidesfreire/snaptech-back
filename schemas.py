from typing import Optional
from sqlmodel import SQLModel

# Schemas para Artigos
class ArticleBase(SQLModel):
    title: str
    description: Optional[str]
    content: Optional[str]
    url: str

class ArticleCreate(ArticleBase):
    pass  # Herda tudo de ArticleBase, usado para criar artigos

class ArticleResponse(ArticleBase):
    id: int
    liked_by_users: int  # Inclui apenas campos relevantes para resposta

    class Config:
        orm_mode = True  # Permite usar objetos ORM diretamente

# Schemas para Usuários
class UserBase(SQLModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str  # Adiciona senha apenas para criação

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# Schemas para Interações
class InteractionBase(SQLModel):
    user_id: int
    article_id: int
    liked: bool

class InteractionCreate(InteractionBase):
    pass  # Usado para criar interações

class InteractionResponse(InteractionBase):
    id: int

    class Config:
        orm_mode = True
