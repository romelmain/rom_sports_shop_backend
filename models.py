from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    image = Column(String(200))
    ProductPrice = relationship('ProductPrice', back_populates='products')


class ProductPrice(Base):
    __tablename__ = "product_price"

    id = Column(Integer, primary_key=True, index=True)
    id_product = Column(String(100))
    price = Column(Integer, ForeignKey('products.id'))
    status = Column(String(200))
    product = relationship('Product', back_populates='product_price')
