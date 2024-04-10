from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class Products(str, Enum):
    product = "rambutan"
    price = "500"
    unit = "kg"



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.get("/products/{model_name}")
async def get_model(model_name: Products):
    if model_name is Products.product:
        return {"product": model_name, "price": "500", "unit":"kg"}