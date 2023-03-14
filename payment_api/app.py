import json
from decimal import Decimal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Payment(BaseModel):
    order_id: str | None = None
    acc_number: int | None = None
    is_payed: bool = False
    payed_sum: Decimal | None = None


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/payment/{order_id}/")
async def accept_payment(order_id, request: Request):
    data = json.loads(await request.json())
    card_number = int(data["account_number"])
    price = Decimal(data["price"])
    is_payed = check_payment(card_number)
    payment = Payment(
        order_id=order_id, acc_number=card_number, is_payed=is_payed, payed_sum=price
    )
    print(payment)
    return {"payment": payment}


def check_payment(acc_number: int) -> bool:
    if acc_number % 2 == 0:
        return True
    return False
