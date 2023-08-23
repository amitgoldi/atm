from pydantic import StrictInt

from atm.server.models.atm import AtmContent, Bills, Coins, MoneyType


class RefillService:
    async def refill(self, to_refill: dict[MoneyType, int]) -> AtmContent:
        content = await AtmContent.find_one()
        # We expect ATM to have content on startup
        if not content:
            raise Exception("ATM is not initiated")

        for money_type, quantity in to_refill.items():
            content.money[money_type.name] = content.money.get(money_type.name, 0) + quantity

        await content.save()
        return content

    @staticmethod
    async def prefill():
        content = await AtmContent.find_one()
        if not content:
            await AtmContent(money={
                Bills.B200.name: 1,
                Bills.B100.name: 2,
                Bills.B20.name: 5,
                Coins.C10.name: 10,
                Coins.C1.name: 10,
                Coins.C5.name: 10,
                Coins.C01.name: 1,
                Coins.C001.name: 10
            }).create()
