from mongoengine import Document, StringField, IntField, FloatField
from pydantic import BaseModel
from typing import Optional, Union


class Products(Document):
    name = StringField()
    price = FloatField()
    currency = StringField()
    quantity = IntField()
    description = StringField()


class CustomerCart(Document):
    customer_id = IntField()
    product_id = IntField()
    quantity = IntField()


class SaveOrder(Document):
    customer_id = IntField()
    order_date = StringField()
    order_amount = FloatField
    billing_address = StringField()
    status: StringField()
