from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import motor.motor_asyncio
from typing import List
import os
from dotenv import load_dotenv
from models.products import ProductCollection, Product, ProductUpdate
from bson import ObjectId
from pymongo import ReturnDocument

app = FastAPI()


# Load environment variables from .env file
load_dotenv()
# MongoDB configuration
MONGO_DB = "ecomm"
MONGO_COLLECTION_PRODUCTS = "products"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# MongoDB connection setup
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
database = client[MONGO_DB]
products_collection = database[MONGO_COLLECTION_PRODUCTS]

@app.post("/products/", response_model=Product)
async def createProduct(product: Product = Body(...)):
    result = await products_collection.insert_one(product.model_dump(by_alias=True, exclude=["id"]))
    created_product = await products_collection.find_one(
        {"_id": result.inserted_id}
    )
    return created_product

@app.get("/products/{id}", response_model=Product)
async def getProduct(id: str):
    product = await products_collection.find_one({"_id": ObjectId(id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{id}", response_model=Product)
async def updateProduct(id: str, product_update: ProductUpdate = Body(...)):
    product_update = {
        k: v for k, v in product_update.model_dump(by_alias=True).items() if v is not None
    }
    result = await products_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": product_update},
            return_document=ReturnDocument.AFTER
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

@app.get("/products/")
async def list_products():
    return ProductCollection(products=await products_collection.find().to_list(1000))
