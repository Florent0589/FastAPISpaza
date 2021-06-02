import json
import time

import uvicorn
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_403_FORBIDDEN

from Spaza.models import model
from Spaza.models import modelDefinations as Md
from mongoengine import connect
from passlib.context import CryptContext
from datetime import datetime, timedelta

import jwt
from jwt import PyJWTError
from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm, OAuth2

connect('spaza', host="localhost", port=27017)
users_cart = {}
User = model.Users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Spaza Rest API", description="Spaza integration API documentation", version="v1.0")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    try:
        valid_user = User.objects.get(username=username).to_json()
        user = json.loads(valid_user)
        return user
    except User.DoesNotExist:
        return {}


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if len(user) == 0:
        return False
    if not verify_password(password, user['password']):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = Md.TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if len(user) == 0:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.status:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def route_login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def testhome(token: str = Depends(oauth2_scheme)):
    return {"message": "test"}


@app.get("/v1/api/")
async def home():
    return {"message": "welcome to Spaza fastAPI"}


@app.get('/v1/api/getProducts')
async def get_products():
    products = model.Products.objects().to_json()
    return products


@app.post('/v1/api/login')
async def get_login():
    return {"username": "Ayanda", "first_name": "Ayanda"}


@app.post('/v1/api/addItemsToCart')
async def add_items_to_cart(cart_req: Md.CustomerCart):
    product_id = cart_req.product_id
    customer_id = cart_req.customer_id
    quantity = cart_req.quantity

    if product_id is not None:
        product = model.Products.objects.get(product_id)
        if product:
            total_invoice = product.price * quantity
            product_cart = {product_id: {"name": product.name, "quantity": quantity,
                                         "unit_price": product.price,
                                         "total_price": total_invoice}}
            if customer_id in users_cart:
                users_cart[customer_id].update(product_cart)
            else:
                users_cart.update({customer_id: {product_cart}})

    return users_cart[customer_id]


@app.post('/v1/api/CheckOutCart')
async def check_out_cart(check_out_req: Md.CustomerCartCheckout):
    customer_id = check_out_cart.customer_id
    if customer_id in users_cart:
        cart = users_cart[customer_id]
        total_invoice = 0
        for cart_info in cart:
            continue
        new_order = model.SaveOrder(customer_id=customer_id,
                                    order_date=time.now(),
                                    order_amount=total_invoice,
                                    billing_address="",
                                    status="Paid")
        new_order.save()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
