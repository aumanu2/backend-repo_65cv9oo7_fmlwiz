import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import MenuItem, Order, OrderItem

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "DineZen API is running"}

# Public schemas endpoint to help tooling (read-only)
@app.get("/schema")
def get_schema():
    return {
        "collections": ["menuitem", "order"],
        "models": {
            "MenuItem": MenuItem.model_json_schema(),
            "Order": Order.model_json_schema()
        }
    }

# Seed some default menu items if collection empty (optional helper)
@app.post("/seed")
def seed_menu():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    if db["menuitem"].count_documents({}) > 0:
        return {"seeded": False}
    defaults = [
        {"name":"Coconut Curry Ramen Bowl","description":"Fragrant coconut broth, ramen, veggies","price":350,"category":"Chef's Specials","image_url":"","is_featured":True},
        {"name":"Classic Cheeseburger","description":"Juicy patty with cheddar","price":240,"category":"Burgers"},
        {"name":"Penne Arrabbiata","description":"Spicy tomato sauce","price":260,"category":"Pasta"},
        {"name":"Chocolate Brownie","description":"Gooey chocolate delight","price":120,"category":"Desserts"},
        {"name":"Ini Salad","description":"Fresh greens mix","price":180,"category":"Salads"},
        {"name":"Drinks Mix","description":"Assorted beverages","price":90,"category":"Drinks"},
    ]
    for m in defaults:
        create_document("menuitem", m)
    return {"seeded": True}

# Menu endpoints
@app.get("/menu", response_model=List[MenuItem])
def list_menu():
    docs = get_documents("menuitem")
    # bson to plain
    for d in docs:
        d.pop("_id", None)
    return docs

# Order endpoints
class CreateOrderRequest(BaseModel):
    table_id: str
    items: List[OrderItem]
    special_instructions: Optional[str] = None

@app.post("/orders")
def place_order(req: CreateOrderRequest):
    data = {
        "table_id": req.table_id,
        "items": [i.model_dump() for i in req.items],
        "special_instructions": req.special_instructions,
        "status": "Order Placed",
        "estimated_time_min": 5,
    }
    oid = create_document("order", data)
    return {"order_id": oid, "status": data["status"], "eta": data["estimated_time_min"]}

@app.get("/orders")
def get_orders(table_id: Optional[str] = None):
    filt = {"table_id": table_id} if table_id else {}
    orders = get_documents("order", filt, limit=50)
    for o in orders:
        o["id"] = str(o.pop("_id", ""))
    return orders

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        doc = db["order"].find_one({"_id": ObjectId(order_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Order not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order id")

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available" if db is None else "✅ Connected & Working",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "collections": []
    }
    if db:
        try:
            response["collections"] = db.list_collection_names()[:10]
        except Exception as e:
            response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
