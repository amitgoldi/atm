from copy import deepcopy
from decimal import Decimal

from fastapi import HTTPException

from atm.server.models.atm import AtmContent, AtmResult, Bills, Coins

TYPES_ORDERED_HIGH_TO_LOW = sorted([bill for bill in Bills] + [coin for coin in Coins], key=lambda x: Decimal(x),
                                   reverse=True)
MONEY_TYPE_TO_VALUE = {
    money_type: Decimal(money_type) for money_type in TYPES_ORDERED_HIGH_TO_LOW
}


class WithdrawService:
    async def withdraw(self, to_withdraw: Decimal) -> AtmResult:
        # self.assert_proper_amount(to_withdraw)
        content = await AtmContent.find_one()
        money_orig = deepcopy(content.money)
        # We expect ATM to have content on startup
        if not content:
            raise Exception("ATM is not initiated")

        result = AtmResult()
        left_to_withdraw = to_withdraw
        # Go over money types from highest to lowest value and attempt to withdraw each type
        for money_type, value in MONEY_TYPE_TO_VALUE.items():
            # Get as much for this money type as we can withdraw
            quantity = int(min(left_to_withdraw // value, content.money.get(money_type.name, 0)))
            if quantity:
                # Withdraw from ATM and add to results
                content.money[money_type.name] -= quantity
                if money_type in Bills:
                    result.bills[money_type] = quantity
                else:
                    result.coins[money_type] = quantity
                # Update amount left to withdraw
                left_to_withdraw -= quantity * value
            # Verify no more than 50 coins
            if sum(quantity for quantity in result.coins.values()) > 50:
                raise HTTPException(status_code=422, detail="Up to 50 coins may be returned")
            if left_to_withdraw == 0:
                break

        if left_to_withdraw:
            raise HTTPException(status_code=409,
                                detail=f"Unable to withdraw {left_to_withdraw}. Max amount to withdraw: {money_orig}")

        await content.save()
        return result
