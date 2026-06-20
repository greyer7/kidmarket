from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ListingStatus(str, Enum):
    active = "active"
    sold = "sold"
    archived = "archived"


class ListingCondition(str, Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[ListingStatus] = mapped_column(
        SAEnum(ListingStatus, name="listing_status"),
        default=ListingStatus.active,
        nullable=False,
    )
    condition: Mapped[ListingCondition] = mapped_column(
        SAEnum(ListingCondition, name="listing_condition"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    image_urls: Mapped[str | None] = mapped_column(Text, nullable=True)
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    seller: Mapped["User"] = relationship(
        "User", back_populates="listings", lazy="selectin"
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="listing", lazy="selectin"
    )