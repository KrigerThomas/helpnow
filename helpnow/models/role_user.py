from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, UniqueConstraint
from helpnow.ext.db import db

if TYPE_CHECKING:
    from .role import Role
    from .user import User


class RoleUser(db.Model):
    __tablename__ = "roles_has_users"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        {'extend_existing': True}
    )

    id:          Mapped[int]                = mapped_column(db.Integer, primary_key=True)
    role_id:     Mapped[int]                = mapped_column(db.ForeignKey("roles.id"), nullable=False, index=True)
    user_id:     Mapped[int]                = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    created_at:  Mapped[datetime]           = mapped_column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(db.DateTime(timezone=True))

    role: Mapped["Role"] = relationship("Role", back_populates="role_associations")
    user: Mapped["User"] = relationship("User", back_populates="role_associations")

    def __repr__(self) -> str:
        return f"<RoleUser user_id={self.user_id} role_id={self.role_id}>"
