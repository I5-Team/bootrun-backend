from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경 변수로부터 가져온 애플리케이션 설정"""

    # =====================================================
    # 애플리케이션 설정
    # =====================================================
    env: str = "development"
    app_title: str = "BootRun AI Chatbot"
    app_version: str = "1.0.0"
    debug: bool = True
    app_port: int = 8000
    app_host: str = "127.0.0.1"
    workers_count: int = 5

    # =====================================================
    # 데이터베이스 설정 (PostgreSQL)
    # =====================================================
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "bootrun_db"
    database_user: str = "bootrun_user"
    database_password: str = "your_secure_postgres_password"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10

    @property
    def database_url(self) -> str:
        """PostgreSQL 연결 URL 구성"""
        return (
            f"postgresql+psycopg2://{self.database_user}:"
            f"{self.database_password}@{self.database_host}:"
            f"{self.database_port}/{self.database_name}"
        )

    # =====================================================
    # Redis 캐시
    # =====================================================
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = "your_redis_password"
    redis_timeout: int = 5

    @property
    def redis_url(self) -> str:
        """Redis 연결 URL 구성"""
        return (
            f"redis://:{self.redis_password}@{self.redis_host}:"
            f"{self.redis_port}/{self.redis_db}"
        )

    # =====================================================
    # JWT 인증 설정
    # =====================================================
    jwt_secret_key: str = "your_super_secret_jwt_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # =====================================================
    # OpenAI / LangChain 챗봇 설정
    # =====================================================
    openai_api_key: str = "sk-your_openai_api_key_here"
    openai_model_name: str = "gpt-3.5-turbo"
    chatbot_temperature: float = 0.7
    chatbot_max_tokens: int = 1000
    chatbot_memory_buffer_size: int = 5

    # =====================================================
    # AWS S3 설정 (동영상 저장)
    # =====================================================
    aws_access_key_id: str = "your_aws_access_key_id"
    aws_secret_access_key: str = "your_aws_secret_access_key"
    aws_region: str = "ap-northeast-2"
    s3_bucket_name: str = "bootrun-videos"
    s3_videos_folder: str = "videos"
    s3_images_folder: str = "images"

    # =====================================================
    # CORS 설정
    # =====================================================
    cors_origins: str = "https://yourdomain.com,https://www.yourdomain.com"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    cors_allow_headers: str = "Content-Type,Authorization"

    # =====================================================
    # 로깅 설정
    # =====================================================
    log_level: str = "INFO"
    log_file_path: str = "logs/app.log"
    log_max_size: int = 100
    log_retention_days: int = 30

    # =====================================================
    # SMTP 이메일 설정 (인증 이메일)
    # =====================================================
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_smtp_user: str = "your_email@gmail.com"
    email_smtp_password: str = "your_email_password"
    email_from_address: str = "noreply@bootrun.com"
    email_from_name: str = "BootRun"

    # =====================================================
    # 결제 시스템 (Toss Payments)
    # =====================================================
    toss_client_key: str = "your_toss_client_key"
    toss_secret_key: str = "your_toss_secret_key"
    toss_api_url: str = "https://api.tosspayments.com/v1"

    # =====================================================
    # 파일 업로드 설정
    # =====================================================
    max_upload_size_mb: int = 100
    allowed_image_extensions: str = "jpg,jpeg,png,gif,webp"
    allowed_video_extensions: str = "mp4,avi,mov,mkv,webm"
    allowed_document_extensions: str = "pdf,doc,docx,xls,xlsx,ppt,pptx"

    # =====================================================
    # 시간대 및 국제화
    # =====================================================
    timezone: str = "Asia/Seoul"
    default_language: str = "ko"

    class Config:
        """Pydantic 설정"""
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스 생성
settings = Settings()