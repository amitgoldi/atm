from _decimal import Decimal

from pydantic import BaseModel, Field

from atm.server.models.atm import AtmResponse


class WithdrawRequest(BaseModel):
    amount: Decimal = Field(gt=0, le=2000, decimal_places=2)


class WithdrawResponse(AtmResponse):
    pass
