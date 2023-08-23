from pydantic import BaseModel

from atm.server.models.atm import AtmResponse, MoneyType, StrictPositiveInt


class RefillRequest(BaseModel):
    money: dict[MoneyType, StrictPositiveInt]


class RefillResponse(AtmResponse):
    pass
