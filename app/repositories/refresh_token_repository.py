"""Repositório de refresh tokens (persistência do jti para revogação)."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: uuid.UUID, jti: uuid.UUID, expires_at: datetime) -> RefreshToken:
        record = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_jti(self, jti: uuid.UUID) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        return self.db.scalar(stmt)

    def revoke(self, jti: uuid.UUID) -> None:
        record = self.get_by_jti(jti)
        if record is not None:
            record.revoked = True
            self.db.commit()
