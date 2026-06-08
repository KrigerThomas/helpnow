from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey
from helpnow.ext.db import db

if TYPE_CHECKING:
    from .user import User

class Servico(db.Model):
    __tablename__ = "servicos"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(120), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(db.Text)
    categoria: Mapped[str] = mapped_column(db.String(60), nullable=False, index=True)
    preco: Mapped[Optional[float]] = mapped_column(db.Float)
    localidade: Mapped[Optional[str]] = mapped_column(db.String(100))
    ativo: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), server_default=func.now())

    prestador_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    prestador: Mapped["User"] = relationship("User", foreign_keys=[prestador_id])

    def __repr__(self) -> str:
        return f"<Servico {self.titulo}>"
