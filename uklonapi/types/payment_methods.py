from pydantic import BaseModel

from . import Unset


class PaymentMethod(BaseModel):
    id: str
    payment_type: str
    description: str = Unset
    card_type: str = Unset

    def as_dict(self):
        return self.model_dump(include={"id", "payment_type"})


class PaymentMethods(BaseModel):
    payment_methods: list[PaymentMethod]
    default_payment_method: PaymentMethod
