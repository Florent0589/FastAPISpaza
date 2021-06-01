import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.params import Body
from Spaza.models import model
from Spaza.models import modelDefinations as Md
from mongoengine import connect

app = FastAPI(title="Spaza Rest API", description="Spaza integration API documentation", version="v1.0")
connect('spaza', host="localhost", port=27017)
users_cart = {}


@app.get("/v1/api/")
def home():
    return {"message": "welcome to Spaza fastAPI"}


@app.get('/v1/api/getProducts')
def get_products():
    products = model.Products.objects().to_json()
    return products


@app.post('/v1/api/login')
def get_login():
    return {"username": "Ayanda", "first_name": "Ayanda"}


@app.post('/v1/api/addItemsToCart')
def add_items_to_cart(cart_req: Md.CustomerCart):
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
def check_out_cart(check_out_req: Md.CustomerCartCheckout):
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
