"""
Repositório de usuário.

Único lugar do sistema que monta queries SQLAlchemy para a tabela
`users`. Services chamam este repositório; nunca fazem `session.query`
diretamente.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == str(email).strip().lower())
        return self.db.scalar(stmt)

    def create(self, data: UserCreate) -> User:
        user = User(
            full_name=data.full_name,
            email=str(data.email).strip().lower(),
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password_hash(self, user: User, hashed_password: str) -> None:
        user.hashed_password = hashed_password
        self.db.add(user)
        self.db.commit()
