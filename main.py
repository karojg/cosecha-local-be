from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from helpers import read_csv_as_dict

app = FastAPI()


class Product(BaseModel):
    id: int
    semana: int
    product: str
    type: str
    size: str
    unit: str
    price: int


@app.get("/")
def read_root():
    return {"Hello": "World"}


# get product by id
@app.get("/products/{product_id}")
def get_product_by_id(product_id: int) -> Optional[Product]:
    data = read_csv_as_dict()
    for item in data:
        if item.get("id") == product_id:
            return Product(**item)
    raise HTTPException(status_code=404, detail="Product not found")


# get all products
@app.get("/products/")
def get_all_products() -> List[Product]:
    return read_csv_as_dict()
