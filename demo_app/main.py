from fastapi import FastAPI

from .schemas import OrderResponse


app = FastAPI(title="FastDoctor Demo API")


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    return {
        "id": order_id,
        "customer_name": "Anand",
    }