import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, List, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text

import json
import pandas as pd

app = FastAPI()

origins = [
    "https://localhost:5173",
    "http://localhost:5173",
    "https://localhost:3000",
]

# obligatory CORS handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


class PostBase(BaseModel):
    title: str
    content: str
    user_id: int


class UserBase(BaseModel):
    username: str
    password: str


class ProductBase(BaseModel):
    id: int
    name: str
    description: str
    image: str


class ProductDto():
    id: int
    name: str
    description: str
    image: str


class ProductPriceDto():
    product_id: int
    price: float
    product: ProductDto


class ProductPriceBase(BaseModel):
    product_id: int
    price: float
    product: ProductBase


class CartBase(BaseModel):
    date: str
    status_id: int
    user_id: int
    product_price_id: int


class CartDto():
    """Cart Dto"""
    id: int
    date: str
    status_id: int
    user_id: int
    list_product_price: List[ProductPriceDto] = []


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()


@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    return post


@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()


@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post was not found')
    db.delete(db_post)
    db.commit()


def validateCart(user_id: int, db: db_dependency):
    id_cart = 0
    tupla = ()
    sql = f"SELECT id FROM cart where id_status = 1 and id_user = {user_id}"
    print(sql)
    try:
        rs = db.execute(text(sql))
        print(rs)
        tupla = rs.first()
        id_cart = tupla[0]
    except TypeError:
        print("No Cart")
    return id_cart


@app.post("/users/login", status_code=status.HTTP_200_OK)
async def login(user: UserBase, db: db_dependency):
    tupla = ()
    print(user.username+""+user.password)
    sql = f"select id,username from user where username = '{
        user.username}' and password = '{user.password}'"
    print(sql)
    rs = db.execute(text(sql))
    print(rs)
    tupla = rs.first()
    print(tupla)
    id_cart = validateCart(tupla[0], db)
    if tupla is None:
        raise HTTPException(status_code=404, detail='User not Found')
    rs.close
    return {"user_id": tupla[0], "user_name": tupla[1], "id_cart": id_cart}


@app.get("/products", status_code=status.HTTP_200_OK)
async def getProducts(db: db_dependency):
    tupla = ()
    sql = (f'select a.id,a.name,a.description,a.image,b.price, b.id as id_product_price '
           'from products a '
           'inner join product_price b on (a.id = b.id_product) '
           'where b.status = 1')
    print(sql)
    rs = db.execute(text(sql))
    print(type(rs))
    tupla = rs.all()

    # Normal --------------------------------------------------
    print("-------------------------")
    products = []
    for p in tupla:
        products.append({"id": p[0], "name": p[1],
                         "description": p[2], "image": p[3], "price": p[4], "id_product_price": p[5]})
        print(p)
        print("-------------------------")
    print("**************************")
    print(products)
    # ----------------------------------------------------------

    # con Pandas -----------------------------------------------
    # se debe instalar pandas: pip install pandas
    # df = pd.DataFrame(tupla, columns=['id', 'name', 'description', 'image'])
    # json_data = df.to_json(orient='records')
    # products = json.loads(json_data)
    # ----------------------------------------------------------

    if tupla is None:
        raise HTTPException(status_code=404, detail='Products not Found')
    rs.close()
    return products


@app.get("/products/{product_id}", status_code=status.HTTP_200_OK)
async def getProductsById(product_id: int, db: db_dependency):
    tupla = ()
    sql = ("select a.id,a.name,a.description,a.image,b.price, b.id as id_product_price "
           "from products a "
           "inner join product_price b on (a.id = b.id_product) "
           f"where b.status = 1 and a.id = {product_id}")
    print(product_id)
    print(sql)
    rs = db.execute(text(sql))
    print(type(rs))
    tupla = rs.all()

    product = {}
    products = []
    for p in tupla:
        products.append({"id": p[0], "name": p[1],
                         "description": p[2], "image": p[3], "price": p[4], "id_product_price": p[5]})
        print(p)
    print(products)

    if len(products) > 0:
        product = products[0]

    if tupla is None or len(products) == 0:
        raise HTTPException(status_code=404, detail='Products not Found')
    rs.close()
    return product


@app.post("/cart", status_code=status.HTTP_201_CREATED)
async def createCart(cart: CartBase, db: db_dependency):
    try:
        newCart = models.Cart()
        newCart.id_status = cart.status_id
        newCart.id_user = cart.user_id
        newCart.date = cart.date

        db.add(newCart)
        db.flush()
        print(newCart.id)

        newProductCart = models.ProductCart()
        newProductCart.id_cart = newCart.id
        newProductCart.id_product_price = cart.product_price_id
        db.add(newProductCart)

        db.commit()
    except:
        db.rollback()

    print(newCart.id)
    return {"id_cart": newCart.id}


@app.get("/cart/{cart_id}", status_code=status.HTTP_200_OK)
async def getCartById(cart_id: int, db: db_dependency):
    try:
        tupla = ()
        sql = ("select a.id, a.date, c.price, d.id as id_product, d.name, d.description, d.image "
               "from cart a "
               "inner join product_cart b on (a.id = b.id_cart) "
               "inner join product_price c on (b.id_product_price = c.id) "
               "inner join products d on (c.id_product = d.id) "
               "inner join status_cart e on (a.id_status = e.id) "
               f"where a.id_status = 1 and a.id = {cart_id}")

        print(sql)
        rs = db.execute(text(sql))
        print(type(rs))
        print(rs)

        tupla = rs.all()

        newCart = CartDto()
        newCart.id = tupla[0][0]
        newCart.date = tupla[0][1]

        listProductPrice = []
        for p in tupla:
            newPproduct = ProductDto()
            newPproduct.id = p[3]
            newPproduct.image = p[6]
            newPproduct.name = p[4]
            newPproduct.description = p[5]
            newProductPrice = ProductPriceDto()
            newProductPrice.product = newPproduct
            newProductPrice.price = p[2]
            listProductPrice.append(newProductPrice)
            newCart.list_product_price = listProductPrice
    except:
        if tupla is None or len(tupla) == 0:
            raise HTTPException(status_code=404, detail='Cart not Found')
    rs.close()
    return newCart
