from sqlalchemy import (
    Column,
    Date,
    ForeignKeyConstraint,
    Integer,
    String,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship
from .database import Base


class HouseListing(Base):
    __tablename__ = "house_listings"

    address = Column(String, primary_key=True)
    city = Column(String, primary_key=True)
    state = Column(String, primary_key=True)
    zip = Column(Integer, primary_key=True)
    beds = Column(Integer)
    baths = Column(Float)
    sqft = Column(Integer)

    price_listings = relationship("PriceListing", back_populates="house_listing")


class PriceListing(Base):
    __tablename__ = "price_listings"

    transaction_id = Column(Integer, primary_key=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(Integer)
    price = Column(Integer)
    date = Column(Date)

    house_listing = relationship("HouseListing", back_populates="price_listings")

    __table_args__ = (
        ForeignKeyConstraint(
            ["address", "city", "state", "zip"],
            [
                "house_listings.address",
                "house_listings.city",
                "house_listings.state",
                "house_listings.zip",
            ],
        ),
    )
