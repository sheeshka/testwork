from decimal import Decimal

import httpx

from app.core.config import settings
from app.schemas.bank import AcquiringCheckResponse, AcquiringStartResponse


class BankClientError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BankClient:
    def __init__(self):
        self._base_url = settings.BANK_API_URL
        self._timeout = settings.BANK_API_TIMEOUT

    async def acquiring_start(self, order_id: str, amount: Decimal) -> AcquiringStartResponse:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/acquiring_start",
                    json={"order_id": order_id, "amount": str(amount)},
                )
                response.raise_for_status()
                data = response.json()
                return AcquiringStartResponse(**data)
            except httpx.TimeoutException:
                raise BankClientError("Банк не ответил: таймаут")
            except httpx.HTTPStatusError as e:
                raise BankClientError(f"Ошибка банка: {e.response.text}")
            except httpx.RequestError:
                raise BankClientError("Банк недоступен")

    async def acquiring_check(self, bank_payment_id: str) -> AcquiringCheckResponse:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/acquiring_check",
                    json={"payment_id": bank_payment_id},
                )
                response.raise_for_status()
                data = response.json()
                return AcquiringCheckResponse(**data)
            except httpx.TimeoutException:
                raise BankClientError("Банк не ответил: таймаут")
            except httpx.HTTPStatusError as e:
                raise BankClientError(f"Ошибка банка: {e.response.text}")
            except httpx.RequestError:
                raise BankClientError("Банк недоступен")
