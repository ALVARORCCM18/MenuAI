from sqlalchemy import Column, Integer, String, Float, Text, Computed
from sqlalchemy.dialects.postgresql import ARRAY
from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    margin = Column(Float, Computed("price - cost"), nullable=False)
    stock_level = Column(Integer, nullable=False, default=0)
    category = Column(String(80), nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=[])
