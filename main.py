import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated
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


class CartBase(BaseModel):
    date: str
    status_id: int
    user_id: int
    product_price_id: int


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

    if tupla is None:
        raise HTTPException(status_code=404, detail='User not Found')
    rs.close
    return {"user_id": tupla[0], "user_name": tupla[1]}


@app.get("/products", status_code=status.HTTP_200_OK)
async def getProducts(db: db_dependency):
    tupla = ()
    sql = (f'select a.id,a.name,a.description,a.image,b.price '
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
                         "description": p[2], "image": p[3], "price": p[4]})
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


@app.post("/products/price", status_code=status.HTTP_201_CREATED)
async def createCart(cart: CartBase, db: db_dependency):
    print("Probando")

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
