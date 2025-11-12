"""
초기 관리자 계정 생성 스크립트

이 스크립트는 데이터베이스에 초기 관리자 계정을 생성합니다.
서버 최초 실행 시 자동으로 실행되며, 관리자가 이미 존재하면 건너뜁니다.

실행 방법:
    python scripts/seed_admin.py
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import date

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole, Gender, SocialProvider


async def create_initial_admin():
    """초기 관리자 계정 생성"""

    # 데이터베이스 엔진 생성
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # 기존 관리자 계정 확인
            result = await session.execute(
                select(User).where(User.role == UserRole.ADMIN)
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print(f"[OK] 관리자 계정이 이미 존재합니다: {existing_admin.email}")
                return

            # 초기 관리자 정보 검증
            if not settings.initial_admin_email or not settings.initial_admin_password:
                print("[ERROR] 환경변수에 초기 관리자 정보가 설정되지 않았습니다.")
                print("        INITIAL_ADMIN_EMAIL과 INITIAL_ADMIN_PASSWORD를 .env 파일에 설정하세요.")
                return

            # 비밀번호 해싱
            hashed_password = hash_password(settings.initial_admin_password)

            # 관리자 계정 생성
            admin_user = User(
                email=settings.initial_admin_email,
                password_hash=hashed_password,
                nickname=settings.initial_admin_nickname,
                gender=Gender.OTHER,
                birth_date=date(2000, 1, 1),  # 기본 생년월일
                role=UserRole.ADMIN,
                is_active=True,
                is_email_verified=True,  # 관리자는 자동으로 이메일 인증 완료
                social_provider=SocialProvider.EMAIL,
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            print("=" * 60)
            print("[SUCCESS] 초기 관리자 계정이 성공적으로 생성되었습니다!")
            print("=" * 60)
            print(f"이메일: {admin_user.email}")
            print(f"닉네임: {admin_user.nickname}")
            print(f"비밀번호: (환경변수에 설정된 비밀번호 사용)")
            print("=" * 60)
            print("[WARNING] 보안 경고:")
            print("         1. 첫 로그인 후 반드시 비밀번호를 변경하세요!")
            print("         2. .env 파일은 절대 Git에 커밋하지 마세요!")
            print("         3. 운영 환경에서는 강력한 비밀번호를 사용하세요!")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"[ERROR] 관리자 계정 생성 중 오류 발생: {e}")
            raise
        finally:
            await engine.dispose()


async def main():
    """메인 함수"""
    print("\n초기 관리자 계정 생성 스크립트 시작...\n")
    await create_initial_admin()
    print("\n스크립트 실행 완료\n")


if __name__ == "__main__":
    asyncio.run(main())
