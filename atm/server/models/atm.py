from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field, PositiveInt


class Coins(str, Enum):
    C001 = "0.01"
    C01 = "0.1"
    C1 = "1"
    C5 = "5"
    C10 = "10"

    @classmethod
    def by_name(cls, s: str) -> Optional["Coins"]:
        try:
            return Coins[s]
        except KeyError:
            return None


class Bills(str, Enum):
    B20 = "20"
    B100 = "100"
    B200 = "200"

    @classmethod
    def by_name(cls, s: str) -> Optional["Bills"]:
        try:
            return Bills[s]
        except KeyError:
            return None


MoneyType = Bills | Coins


class StrictPositiveInt(PositiveInt):
    strict = True


class AtmResult(BaseModel):
    bills: dict[Bills, int] = Field(default_factory=dict)
    coins: dict[Coins, int] = Field(default_factory=dict)


class AtmResponse(BaseModel):
    result: AtmResult


# Mongo models
class AtmContent(Document):
    """Represents content of ATM"""

    money: dict[str, int]
    """NOTE - this maps MoneyType enum names to quantity. 
    We need to do it like this since mongo does not allow keys such as 0.01"""

    class Settings:
        name = "content"
        # Optimistic locking
        use_revision = True
