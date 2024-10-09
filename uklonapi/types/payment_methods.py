from pydantic import BaseModel


class PaymentMethodBase(BaseModel):
    id: str
    payment_type: str


class PaymentMethod(PaymentMethodBase):
    description: str


class PaymentMethodCard(PaymentMethod):
    card_type: str


class DefaultPaymentMethod(PaymentMethod):
    pass


class PaymentMethods(BaseModel):
    payment_methods: list[PaymentMethod | PaymentMethodCard]
    default_payment_method: DefaultPaymentMethod
