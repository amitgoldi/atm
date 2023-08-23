from fastapi import APIRouter
from fastapi.params import Depends

from atm.server.models.atm import AtmContent, AtmResponse, AtmResult, Bills, Coins
from atm.server.models.refill import RefillRequest, RefillResponse
from atm.server.models.withdraw import WithdrawRequest
from atm.server.services.refill import RefillService
from atm.server.services.withdraw import WithdrawService

atm_router = APIRouter()


@atm_router.post("/withdrawal", description="Withdraw from ATM")
async def withdraw(request: WithdrawRequest,
                   withdraw_service: WithdrawService = Depends(WithdrawService)) -> AtmResponse:
    result = await withdraw_service.withdraw(request.amount)
    return AtmResponse(result=result)


def _to_atm_response(atm_content: AtmContent):
    bills = {}
    coins = {}
    for money_type_name, amount in atm_content.money.items():
        if money_type := Bills.by_name(money_type_name):
            bills[money_type] = amount
        elif money_type := Coins.by_name(money_type_name):
            coins[money_type] = amount
        else:
            raise Exception(f"Unexpected money type : {money_type_name}")
    return RefillResponse(result=AtmResult(bills=bills, coins=coins))


@atm_router.post("/refill", description="Refill ATM")
async def refill(request: RefillRequest, refill_service: RefillService = Depends(RefillService)) -> AtmResponse:
    new_content = await refill_service.refill(request.money)
    return _to_atm_response(new_content)
