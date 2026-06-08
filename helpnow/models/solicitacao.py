from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey
from helpnow.ext.db import db

if TYPE_CHECKING:
    from .user import User
    from .servico import Servico

STATUS_PENDENTE  = "Pendente"
STATUS_ACEITO    = "Aceito"
STATUS_RECUSADO  = "Recusado"
STATUS_CONCLUIDO = "Concluído"


class Solicitacao(db.Model):
    __tablename__ = "solicitacoes"
    __table_args__ = {'extend_existing': True}

    id:             Mapped[int]           = mapped_column(db.Integer, primary_key=True)
    status:         Mapped[str]           = mapped_column(db.String(20), default=STATUS_PENDENTE, nullable=False, index=True)
    mensagem:       Mapped[Optional[str]] = mapped_column(db.Text)
    endereco_texto: Mapped[Optional[str]] = mapped_column(db.String(200))
    nota:           Mapped[Optional[int]] = mapped_column(db.Integer)   # avaliação 1–5
    created_at:     Mapped[datetime]      = mapped_column(db.DateTime(timezone=True), server_default=func.now())
    updated_at:     Mapped[Optional[datetime]] = mapped_column(db.DateTime(timezone=True), onupdate=func.now())

    cliente_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    servico_id: Mapped[int] = mapped_column(ForeignKey("servicos.id"), nullable=False, index=True)

    cliente: Mapped["User"]    = relationship("User",    foreign_keys=[cliente_id])
    servico: Mapped["Servico"] = relationship("Servico", foreign_keys=[servico_id])

    @property
    def prestador(self):
        return self.servico.prestador if self.servico else None

    def __repr__(self) -> str:
        return f"<Solicitacao #{self.id} status={self.status}>"
