from pydantic import BaseModel


class PaymentMethod(BaseModel):
    id: str
    payment_type: str
    description: str = None
    card_type: str = None

    def as_dict(self):
        return self.model_dump(include={"id", "payment_type"})


class PaymentMethods(BaseModel):
    payment_methods: list[PaymentMethod]
    default_payment_method: PaymentMethod
