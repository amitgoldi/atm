import json

import pytest
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from atm.server.app import build_app, init
from atm.server.models.atm import AtmContent

# https://anyio.readthedocs.io/en/stable/testing.html

pytestmark = pytest.mark.anyio


@pytest.fixture()
async def mongo_mock_client():
    yield AsyncMongoMockClient()


@pytest.fixture()
def app():
    yield build_app()


@pytest.fixture()
async def test_client(mongo_mock_client, app):
    """Test client pytest fixture.
    https://github.com/tiangolo/fastapi/issues/2003
    """
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
        await init(mongo_client=mongo_mock_client)
        yield client


@pytest.fixture()
def anyio_backend():
    return 'asyncio'


@pytest.mark.parametrize("refill_request, expected_response", [
    # Empty refill
    ({"money": {}},
     {"result": {'bills': {'200': 1, '100': 2, '20': 5},
                 'coins': {'10': 10, '1': 10, '5': 10, '0.1': 1, '0.01': 10}}}
     ),
    # Refill ok
    ({"money": {
        "0.1": 5, "5": 20, "20": 15, "100": 30
    }}, {
         "result": {'bills': {'200': 1, '100': 32, '20': 20},
                    'coins': {'10': 10, '1': 10, '5': 30, '0.1': 6, '0.01': 10}}}
    )
])
async def test_refill_ok(test_client, refill_request, expected_response):
    # When calling refill
    response = await test_client.post("/atm/refill", data=json.dumps(refill_request))
    # Then response is ok
    assert response.status_code == 200
    # And amount has been updated
    assert response.json() == expected_response


@pytest.mark.parametrize("refill_request", [
    {"money": {
        "C01": 5
    }},
    {},
    {"money": {
        "5": "10"
    }},
    {"money": {
        "5": 10.5
    }},
    {"money": {
        "5": -10
    }},
    {"mony": {
        "5": 20
    }}

])
async def test_refill_422(test_client, refill_request):
    # When calling refill with incorrect input
    response = await test_client.post("/atm/refill", data=json.dumps(refill_request))
    # Then response 422 is returned
    assert response.status_code == 422


@pytest.mark.parametrize("withdraw_request, expected_response, expected_atm_content", [
    ({"amount": 0.01},
     {"result": {"bills": {}, "coins": {"0.01": 1}}},
     {"B200": 1, "B100": 2, "B20": 5, "C10": 10, "C1": 10, "C5": 10, "C01": 1, "C001": 9}
     ),
    ({"amount": 300},
     {"result": {"bills": {"100": 1, "200": 1}, "coins": {}}},
     {"B200": 0, "B100": 1, "B20": 5, "C10": 10, "C1": 10, "C5": 10, "C01": 1, "C001": 10},
     ),
    ({"amount": 660.2},
     {"result": {"bills": {"100": 2, "200": 1, "20": 5}, "coins": {"10": 10, "1": 10, "5": 10, "0.1": 1, "0.01": 10}}},
     {"B200": 0, "B100": 0, "B20": 0, "C10": 0, "C1": 0, "C5": 0, "C01": 0, "C001": 0},
     ),
])
async def test_withdraw_ok(test_client, withdraw_request, expected_response, expected_atm_content):
    # When calling withdraw
    response = await test_client.post("/atm/withdrawal", data=json.dumps(withdraw_request))
    # Then response is ok
    assert response.status_code == 200
    assert response.json() == expected_response
    # And amount has been updated
    new_content = await AtmContent.find_one()
    assert new_content.money == expected_atm_content


@pytest.mark.parametrize("withdraw_request, status_code", [
    ({"amount": 1660.21}, 409),
    ({"amount": 0}, 422),
    ({"money": 100}, 422),
    ({}, 422),
    ({"amount": 100.001}, 422),
    ({"amount": -100}, 422),
    ({"amount": 2001}, 422),
    ({"amount": 2000.1}, 422),

])
async def test_withdraw_error(test_client, withdraw_request, status_code):
    # When calling withdraw with bad request
    response = await test_client.post("/atm/withdrawal", data=json.dumps(withdraw_request))
    # Then response code
    assert response.status_code == status_code


@pytest.mark.parametrize("withdraw_request, status_code", [
    ({"amount": 1000}, 422),
])
async def test_withdraw_over_50_coins(test_client, withdraw_request, status_code):
    # Given many coins in the ATM
    await test_client.post("/atm/refill", data=json.dumps({"money": {
        "0.1": 50, "5": 1000
    }}))
    # When calling withdraw that will need more than 50 coins
    response = await test_client.post("/atm/withdrawal", data=json.dumps(withdraw_request))
    # Then response 422 is returned
    assert response.status_code == status_code
