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
    # Redis 캐시(주석 처리됨)
    # =====================================================
    # redis_host: str = "localhost"
    # redis_port: int = 6379
    # redis_db: int = 0
    # redis_password: str = "your_redis_password"
    # redis_timeout: int = 5
    #
    # @property
    # def redis_url(self) -> str:
    #     """Redis 연결 URL 구성"""
    #     return (
    #         f"redis://:{self.redis_password}@{self.redis_host}:"
    #         f"{self.redis_port}/{self.redis_db}"
    #     )

    # =====================================================
    # JWT 인증 설정
    # =====================================================
    jwt_secret_key: str = "your_super_secret_jwt_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    class Config:
        """Pydantic 설정"""
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스 생성
settings = Settings()