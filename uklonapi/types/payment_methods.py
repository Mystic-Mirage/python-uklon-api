from pydantic import BaseModel


class PaymentMethod(BaseModel):
    id: str
    description: str
    payment_type: str
    card_type: str = None


class PaymentMethods(BaseModel):
    payment_methods: list[PaymentMethod]
