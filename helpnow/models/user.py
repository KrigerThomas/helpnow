from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from helpnow.ext.db import db

if TYPE_CHECKING:
    from .role_user import RoleUser
    from .location import Address


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id:         Mapped[int]                = mapped_column(db.Integer, primary_key=True)
    name:       Mapped[str]                = mapped_column(db.String(100), nullable=False, index=True)
    email:      Mapped[str]                = mapped_column(db.String(100), unique=True, nullable=False, index=True)
    password:   Mapped[Optional[str]]      = mapped_column(db.String(255))
    phone:      Mapped[Optional[str]]      = mapped_column(db.String(20))
    cpf:        Mapped[Optional[str]]      = mapped_column(db.String(14), unique=True, index=True)
    photo:      Mapped[Optional[str]]      = mapped_column(db.String(500))
    is_active:  Mapped[bool]               = mapped_column(db.Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime]           = mapped_column(db.DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime(timezone=True), onupdate=func.now())

    role_associations: Mapped[List["RoleUser"]] = relationship(
        "RoleUser", back_populates="user", cascade="all, delete-orphan"
    )
    addresses: Mapped[List["Address"]] = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, senha: str) -> None:
        self.password = generate_password_hash(senha)

    def check_password(self, senha: str) -> bool:
        return bool(self.password and check_password_hash(self.password, senha))

    @property
    def papel(self) -> str:
        ativos = [a for a in self.role_associations if a.finished_at is None]
        for a in ativos:
            if a.role and a.role.name.lower() == "prestador":
                return "prestador"
        return "cliente"

    @property
    def endereco_principal(self):
        return self.addresses[0] if self.addresses else None

    def __repr__(self) -> str:
        return f"<User {self.email}>"
