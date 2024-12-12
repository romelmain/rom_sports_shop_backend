import datetime
from sqlalchemy import Boolean, Column, Integer, Float, String, DateTime, ForeignKey, select
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    # Table--------------------------------------------
    __tablename__ = "user"
    # Columns------------------------------------------
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    # Relationship-------------------------------------
    cart = relationship('Cart', back_populates='user')


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer)


class Products(Base):
    # Table--------------------------------------------
    __tablename__ = "products"
    # Columns------------------------------------------
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    image = Column(String(200))
    # Relationship--------------------------------------
    productPrice = relationship('ProductPrice', back_populates='products')


class ProductPrice(Base):
    # Table--------------------------------------------
    __tablename__ = "product_price"
    # Columns------------------------------------------
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float)
    status = Column(String(200))
    # ForeignKeys--------------------------------------
    id_product = Column(Integer, ForeignKey('products.id'))
    # Relationship-------------------------------------
    products = relationship('Products', back_populates='productPrice')
    productCart = relationship('ProductCart', back_populates='productPrice')


class StatusCart(Base):
    # Table--------------------------------------------
    __tablename__ = "status_cart"
    # Columns------------------------------------------
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(45))
    # Relationship-------------------------------------
    cart = relationship('Cart', back_populates='statusCart')


class Cart(Base):
    # Table--------------------------------------------
    __tablename__ = "cart"
    # Columns------------------------------------------
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime)
    id_user = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='cart')
    # ForeignKeys--------------------------------------
    id_status = Column(Integer, ForeignKey('status_cart.id'))
    # Relationship-------------------------------------
    statusCart = relationship('StatusCart', back_populates='cart')
    productCart = relationship('ProductCart', back_populates='cart')


class ProductCart(Base):
    # Table--------------------------------------------
    __tablename__ = "product_cart"
    # Columns------------------------------------------
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    # ForeignKeys--------------------------------------
    id_cart = Column(Integer, ForeignKey('cart.id'))
    id_product_price = Column(Integer, ForeignKey('product_price.id'))
    # Relationship-------------------------------------
    cart = relationship('Cart', back_populates='productCart')
    productPrice = relationship('ProductPrice', back_populates='productCart')
