from pydantic import BaseModel

from . import Unset


class PaymentMethod(BaseModel):
    id: str
    payment_type: str
    description: str = Unset
    card_type: str = Unset

    def for_fare(self):
        return {
            "id": self.id,
            "type": self.payment_type,
        }


class PaymentMethods(BaseModel):
    payment_methods: list[PaymentMethod]
    default_payment_method: PaymentMethod
