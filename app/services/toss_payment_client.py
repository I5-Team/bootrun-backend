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

    def _get_auth_header(self) -> str:
        """Basic 인증 헤더 생성"""
        # Secret Key 뒤에 콜론(:) 추가 후 Base64 인코딩
        auth_string = f"{self.secret_key}:"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {encoded}"

    async def confirm_payment(
        self,
        payment_key: str,
        order_id: str,
        amount: int
    ) -> dict:
        """
        토스 페이먼츠 결제 승인 API 호출

        Args:
            payment_key: 토스에서 발급한 결제 키
            order_id: 주문 ID
            amount: 결제 금액

        Returns:
            토스 API 응답 (승인 성공 시 결제 정보)

        Raises:
            httpx.HTTPStatusError: API 호출 실패 시
        """
        url = f"{self.api_url}/payments/confirm"

        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }

        body = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=body,
                headers=headers,
                timeout=10.0  # 토스 정책에 맞춰 10초로 설정
            )

            # 에러 발생 시 예외 발생
            if response.status_code != 200:
                error_data = response.json()
                raise TossPaymentError(
                    code=error_data.get("code", "UNKNOWN_ERROR"),
                    message=error_data.get("message", "결제 승인 실패"),
                    status_code=response.status_code
                )

            return response.json()

    async def cancel_payment(
        self,
        payment_key: str,
        cancel_reason: str,
        cancel_amount: Optional[int] = None
    ) -> dict:
        """
        토스 페이먼츠 결제 취소 (환불) API 호출

        Args:
            payment_key: 토스에서 발급한 결제 키
            cancel_reason: 취소 사유
            cancel_amount: 부분 취소 금액 (None이면 전액 취소)

        Returns:
            토스 API 응답 (취소 성공 시 결제 정보)

        Raises:
            TossPaymentError: API 호출 실패 시
        """
        url = f"{self.api_url}/payments/{payment_key}/cancel"

        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }

        body = {"cancelReason": cancel_reason}
        if cancel_amount is not None:
            body["cancelAmount"] = cancel_amount

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=body,
                headers=headers,
                timeout=10.0
            )

            if response.status_code != 200:
                error_data = response.json()
                raise TossPaymentError(
                    code=error_data.get("code", "UNKNOWN_ERROR"),
                    message=error_data.get("message", "결제 취소 실패"),
                    status_code=response.status_code
                )

            return response.json()


class TossPaymentError(Exception):
    """토스 페이먼츠 API 에러"""

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{code}] {message}")