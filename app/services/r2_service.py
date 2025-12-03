"""
Cloudflare R2 Storage Service
R2는 S3 호환 API를 사용하므로 boto3 라이브러리로 연동 가능
"""
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from io import BytesIO
from loguru import logger
from app.core.config import settings


class R2Service:
    """Cloudflare R2 스토리지 서비스"""

    def __init__(self):
        """R2 클라이언트 초기화"""
        if not settings.r2_account_id or not settings.r2_access_key_id:
            logger.warning("R2 credentials not configured")
            self.client = None
            return

        # R2 엔드포인트 URL 생성
        endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"

        # boto3 S3 클라이언트 생성 (R2는 S3 호환)
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto"  # R2는 자동으로 리전 선택
        )
        self.bucket_name = settings.r2_bucket_name
        logger.info(f"R2 client initialized for bucket: {self.bucket_name}")

    def upload_file(
        self,
        file_data: BinaryIO,
        file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        R2에 파일 업로드

        Args:
            file_data: 업로드할 파일 데이터
            file_path: R2 버킷 내 파일 경로 (예: "images/profile.jpg")
            content_type: 파일의 Content-Type (예: "image/jpeg")
            metadata: 추가 메타데이터

        Returns:
            업로드된 파일의 URL
        """
        if not self.client:
            raise Exception("R2 client not initialized")

        try:
            # 업로드 파라미터 설정
            upload_params = {
                "Bucket": self.bucket_name,
                "Key": file_path,
                "Body": file_data,
            }

            if content_type:
                upload_params["ContentType"] = content_type

            if metadata:
                upload_params["Metadata"] = metadata

            # 파일 업로드
            self.client.put_object(**upload_params)

            # 공개 URL 생성
            if settings.r2_public_url:
                file_url = f"{settings.r2_public_url}/{file_path}"
            else:
                file_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{file_path}"

            logger.info(f"File uploaded to R2: {file_path}")
            return file_url

        except ClientError as e:
            logger.error(f"R2 upload error: {e}")
            raise Exception(f"Failed to upload file to R2: {str(e)}")

    def download_file(self, file_path: str) -> BytesIO:
        """
        R2에서 파일 다운로드

        Args:
            file_path: R2 버킷 내 파일 경로

        Returns:
            파일 데이터 (BytesIO)
        """
        if not self.client:
            raise Exception("R2 client not initialized")

        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )

            file_data = BytesIO(response["Body"].read())
            logger.info(f"File downloaded from R2: {file_path}")
            return file_data

        except ClientError as e:
            logger.error(f"R2 download error: {e}")
            raise Exception(f"Failed to download file from R2: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """
        R2에서 파일 삭제

        Args:
            file_path: R2 버킷 내 파일 경로

        Returns:
            삭제 성공 여부
        """
        if not self.client:
            raise Exception("R2 client not initialized")

        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"File deleted from R2: {file_path}")
            return True

        except ClientError as e:
            logger.error(f"R2 delete error: {e}")
            raise Exception(f"Failed to delete file from R2: {str(e)}")

    def file_exists(self, file_path: str) -> bool:
        """
        R2에 파일이 존재하는지 확인

        Args:
            file_path: R2 버킷 내 파일 경로

        Returns:
            파일 존재 여부
        """
        if not self.client:
            return False

        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except ClientError:
            return False

    def get_file_url(self, file_path: str) -> str:
        """
        파일의 공개 URL 가져오기

        Args:
            file_path: R2 버킷 내 파일 경로

        Returns:
            파일 URL
        """
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{file_path}"
        else:
            return f"https://{settings.r2_account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{file_path}"

    def generate_presigned_url(
        self,
        file_path: str,
        expiration: int = 3600,
        http_method: str = "GET"
    ) -> str:
        """
        Presigned URL 생성 (임시 접근 URL)

        Args:
            file_path: R2 버킷 내 파일 경로
            expiration: URL 만료 시간 (초, 기본 1시간)
            http_method: HTTP 메서드 (GET, PUT 등)

        Returns:
            Presigned URL
        """
        if not self.client:
            raise Exception("R2 client not initialized")

        try:
            if http_method == "GET":
                url = self.client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": file_path
                    },
                    ExpiresIn=expiration
                )
            elif http_method == "PUT":
                url = self.client.generate_presigned_url(
                    "put_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": file_path
                    },
                    ExpiresIn=expiration
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {http_method}")

            logger.info(f"Generated presigned URL for: {file_path}")
            return url

        except ClientError as e:
            logger.error(f"R2 presigned URL error: {e}")
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def list_files(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        R2 버킷 내 파일 목록 조회

        Args:
            prefix: 파일 경로 접두사 (폴더 필터링)
            max_keys: 최대 조회 개수

        Returns:
            파일 목록
        """
        if not self.client:
            raise Exception("R2 client not initialized")

        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            files = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    files.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "url": self.get_file_url(obj["Key"])
                    })

            logger.info(f"Listed {len(files)} files from R2 with prefix: {prefix}")
            return files

        except ClientError as e:
            logger.error(f"R2 list error: {e}")
            raise Exception(f"Failed to list files from R2: {str(e)}")


# 전역 R2 서비스 인스턴스
r2_service = R2Service()
