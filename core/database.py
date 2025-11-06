"""
데이터베이스 연결 및 세션 관리

SQLAlchemy를 사용한 PostgreSQL 연결과 Redis 연결을 관리합니다.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
from redis import Redis
import logging

from core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

# =====================================================
# SQLAlchemy 엔진 생성 (PostgreSQL)
# =====================================================

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,  # SQL 쿼리 로깅 (개발 시 True)
    poolclass=QueuePool,  # 연결 풀 사용
    pool_size=settings.database_pool_size,  # 기본 연결 풀 크기
    max_overflow=settings.database_max_overflow,  # 추가 연결 허용 수
    pool_pre_ping=True,  # 연결 전 ping으로 유효성 검사
    pool_recycle=3600,  # 1시간마다 연결 재사용 (메모리 누수 방지)
)


# SQLAlchemy 이벤트: 연결 시 타임존 설정
@event.listens_for(engine, 'connect')
def set_timezone(dbapi_conn, connection_record):
    """
    PostgreSQL 연결 시 타임존을 Asia/Seoul로 설정
    """
    cursor = dbapi_conn.cursor()
    cursor.execute(f"SET TIME ZONE '{settings.timezone}'")
    cursor.close()


# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(
    autocommit=False,  # 자동 커밋 비활성화 (명시적 커밋 필요)
    autoflush=False,  # 자동 플러시 비활성화
    bind=engine  # 위에서 생성한 엔진과 연결
)

# 모델 Base 클래스 생성
# 모든 SQLAlchemy 모델은 이 Base를 상속받아야 함
Base = declarative_base()


# =====================================================
# Redis 클라이언트 생성
# =====================================================

def get_redis_client() -> Redis:
    """
    Redis 클라이언트 인스턴스 반환
    
    캐싱, 세션 저장, 통계 데이터 저장 등에 사용합니다.
    
    Returns:
        Redis: Redis 클라이언트 인스턴스
    
    Raises:
        redis.ConnectionError: Redis 연결 실패 시
    """
    try:
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            socket_timeout=settings.redis_timeout,
            decode_responses=True,  # 자동으로 bytes를 str로 변환
            socket_connect_timeout=settings.redis_timeout,
            health_check_interval=30,  # 30초마다 연결 상태 확인
        )
        
        # Redis 연결 테스트
        redis_client.ping()
        logger.info('Redis 연결 성공')
        
        return redis_client
        
    except redis.ConnectionError as e:
        logger.error(f'Redis 연결 실패: {e}')
        raise


# Redis 클라이언트 전역 인스턴스
try:
    redis_client = get_redis_client()
except Exception as e:
    logger.warning(f'Redis 초기화 실패, 캐싱 기능 비활성화: {e}')
    redis_client = None


# =====================================================
# 데이터베이스 세션 의존성
# =====================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의존성으로 사용할 데이터베이스 세션 생성기
    
    요청마다 새로운 세션을 생성하고, 요청 종료 시 자동으로 닫습니다.
    트랜잭션 관리를 위해 명시적으로 commit()을 호출해야 합니다.
    
    Yields:
        Session: SQLAlchemy 데이터베이스 세션
    
    사용 예시:
        @router.get('/users')
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# 데이터베이스 초기화
# =====================================================

def init_db() -> None:
    """
    데이터베이스 테이블 생성
    
    Base를 상속받은 모든 모델의 테이블을 생성합니다.
    주의: 프로덕션에서는 Alembic 마이그레이션을 사용해야 합니다.
    
    사용 예시:
        # main.py
        from core.database import init_db
        
        @app.on_event('startup')
        async def startup():
            init_db()
    """
    try:
        # 모든 모델을 import해야 Base.metadata에 등록됨
        # 여기서는 주석으로 표시하고, 실제로는 main.py에서 import
        # from models import user, course, enrollment, payment, ...
        
        Base.metadata.create_all(bind=engine)
        logger.info('데이터베이스 테이블 생성 완료')
        
    except Exception as e:
        logger.error(f'데이터베이스 초기화 실패: {e}')
        raise


def drop_db() -> None:
    """
    모든 데이터베이스 테이블 삭제
    
    주의: 개발 환경에서만 사용하세요!
    모든 데이터가 삭제됩니다.
    """
    if settings.env == 'production':
        raise RuntimeError(
            '프로덕션 환경에서는 테이블 삭제가 금지되어 있습니다'
        )
    
    Base.metadata.drop_all(bind=engine)
    logger.warning('모든 데이터베이스 테이블 삭제 완료')


# =====================================================
# 데이터베이스 연결 상태 확인
# =====================================================

def check_db_connection() -> bool:
    """
    데이터베이스 연결 상태 확인
    
    헬스체크 엔드포인트에서 사용할수 있습니다.
    
    Returns:
        bool: 연결 성공 시 True, 실패 시 False
    
    사용 예시:
        @router.get('/health')
        def health_check():
            db_ok = check_db_connection()
            return {'database': 'ok' if db_ok else 'error'}
    """
    try:
        db = SessionLocal()
        # 간단한 쿼리로 연결 테스트
        db.execute('SELECT 1')
        db.close()
        return True
        
    except Exception as e:
        logger.error(f'데이터베이스 연결 확인 실패: {e}')
        return False


def check_redis_connection() -> bool:
    """
    Redis 연결 상태 확인
    
    Returns:
        bool: 연결 성공 시 True, 실패 시 False
    """
    if redis_client is None:
        return False
    
    try:
        redis_client.ping()
        return True
        
    except Exception as e:
        logger.error(f'Redis 연결 확인 실패: {e}')
        return False


# =====================================================
# 트랜잭션 헬퍼
# =====================================================

class DatabaseTransaction:
    """
    컨텍스트 매니저를 사용한 트랜잭션 관리
    
    with 문으로 트랜잭션을 관리하여 자동 커밋/롤백을 수행합니다.
    
    사용 예시:
        with DatabaseTransaction() as db:
            user = User(email='test@test.com')
            db.add(user)
            # with 블록을 벗어나면 자동으로 commit
            # 에러 발생 시 자동으로 rollback
    """
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __enter__(self) -> Session:
        """컨텍스트 진입 시 세션 반환"""
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        컨텍스트 종료 시 커밋 또는 롤백
        
        Args:
            exc_type: 예외 타입
            exc_val: 예외 값
            exc_tb: 예외 traceback
        """
        if exc_type is not None:
            # 예외 발생 시 롤백
            self.db.rollback()
            logger.error(
                f'트랜잭션 롤백: {exc_type.__name__}: {exc_val}'
            )
        else:
            # 정상 종료 시 커밋
            self.db.commit()
        
        self.db.close()