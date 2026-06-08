from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Index
from helpnow.ext.db import db

if TYPE_CHECKING:
    from .user import User


class City(db.Model):
    __tablename__ = "cities"
    __table_args__ = (
        Index("idx_city_name_state", "name", "state"),
        {'extend_existing': True}
    )

    id:      Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:    Mapped[str]           = mapped_column(String(100), nullable=False)
    state:   Mapped[Optional[str]] = mapped_column(String(2))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    region:  Mapped[Optional[str]] = mapped_column(String(50))

    addresses: Mapped[List["Address"]] = relationship("Address", back_populates="city")

    def __repr__(self) -> str:
        return f"<City {self.name} - {self.state}>"


class Address(db.Model):
    __tablename__ = "address"
    __table_args__ = {'extend_existing': True}

    id:       Mapped[int]           = mapped_column(Integer, primary_key=True)
    road:     Mapped[Optional[str]] = mapped_column(String(100))
    # String em vez de Integer: aceita "S/N", "123-A", "Ap. 5", etc.
    number:   Mapped[Optional[str]] = mapped_column(String(15))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    zipcode:  Mapped[Optional[str]] = mapped_column(String(15))

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="addresses")
    city: Mapped[Optional["City"]] = relationship("City", back_populates="addresses")

    def __repr__(self) -> str:
        return f"<Address {self.road}, {self.number} - {self.district}>"
