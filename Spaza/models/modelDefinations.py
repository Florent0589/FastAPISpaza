from pydantic import BaseModel
from typing import Optional, Union


class Products(BaseModel):
    name: str
    price: float
    currency: str
    quantity = int
    description = str


class CustomerCart(BaseModel):
    customer_id = int
    product_id = int
    quantity = int


class CustomerCartCheckout(BaseModel):
    customer_id = int


class SaveOrder(BaseModel):
    customer_id: int
    order_date: int
    order_amount: int
    billing_address: int
    status: int
