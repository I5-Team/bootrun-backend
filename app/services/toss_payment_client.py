import base64
import httpx
from typing import Optional
from app.core.config import settings


class TossPaymentClient:
    """토스 페이먼츠 API 클라이언트"""

    def __init__(self):
        self.api_url = settings.toss_api_url
        self.secret_key = settings.toss_secret_key
        self.client_key = settings.toss_client_key

    def _get_auth_header(self):
        """Basic 인증 헤더"""
        auth_str = f"{self.secret_key}:"
        encoded = base64.b64encode(auth_str.encode()).decode()
        return f"Basic {encoded}"

    async def confirm_payment(self, payment_key: str, order_id: str, amount: int):
        """결제 승인"""
        url = f"{self.api_url}/payments/confirm"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        body = {"paymentKey": payment_key, "orderId": order_id, "amount": amount}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=body, headers=headers, timeout=10.0)

            if resp.status_code != 200:
                err = resp.json()
                raise TossPaymentError(
                    err.get("code", "UNKNOWN_ERROR"),
                    err.get("message", "결제 승인 실패"),
                    resp.status_code
                )
            return resp.json()

    async def cancel_payment(self, payment_key: str, cancel_reason: str, cancel_amount=None):
        """결제 취소/환불"""
        url = f"{self.api_url}/payments/{payment_key}/cancel"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }

        body = {"cancelReason": cancel_reason}
        if cancel_amount:
            body["cancelAmount"] = cancel_amount

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=body, headers=headers, timeout=10.0)

            if resp.status_code != 200:
                err = resp.json()
                raise TossPaymentError(
                    err.get("code", "UNKNOWN_ERROR"),
                    err.get("message", "결제 취소 실패"),
                    resp.status_code
                )
            return resp.json()


class TossPaymentError(Exception):
    """토스 페이먼츠 API 에러"""

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{code}] {message}")