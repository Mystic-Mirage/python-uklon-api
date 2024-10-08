from pydantic import BaseModel


class PaymentMethod(BaseModel):
    id: str
    description: str
    payment_type: str


class PaymentMethodCard(PaymentMethod):
    card_type: str


class DefaultPaymentMethod(BaseModel):
    id: str
    payment_type: str
    description: str


class PaymentMethods(BaseModel):
    payment_methods: list[PaymentMethod | PaymentMethodCard]
    default_payment_method: DefaultPaymentMethod
