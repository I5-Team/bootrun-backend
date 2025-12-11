"""
테스트 계정 생성 스크립트

이메일 인증 없이 테스트 계정을 바로 생성합니다.

실행 방법:
    python scripts/create_test_account.py
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole, Gender, SocialProvider


async def create_test_account():
    """테스트 계정 생성"""

    # 테스트 계정 정보
    TEST_EMAIL = "test@bootrun.com"
    TEST_PASSWORD = "Test1234!@"
    TEST_NICKNAME = "테스트학생"

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
            # 기존 테스트 계정 확인
            result = await session.execute(
                select(User).where(User.email == TEST_EMAIL)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                if existing_user.is_active:
                    print(f"[INFO] 테스트 계정이 이미 존재합니다: {TEST_EMAIL}")
                    print(f"       계정을 삭제하고 다시 생성하려면 먼저 기존 계정을 삭제하세요.")
                    return
                else:
                    # 비활성화된 계정이면 삭제
                    await session.delete(existing_user)
                    await session.commit()
                    print(f"[INFO] 비활성화된 기존 테스트 계정을 삭제했습니다.")

            # 닉네임 중복 확인
            result = await session.execute(
                select(User).where(User.nickname == TEST_NICKNAME)
            )
            existing_nickname = result.scalar_one_or_none()

            if existing_nickname:
                print(f"[ERROR] 닉네임 '{TEST_NICKNAME}'이(가) 이미 사용 중입니다.")
                print(f"        스크립트의 TEST_NICKNAME을 수정하세요.")
                return

            # 비밀번호 해싱
            hashed_password = hash_password(TEST_PASSWORD)

            # 테스트 계정 생성
            test_user = User(
                email=TEST_EMAIL,
                password_hash=hashed_password,
                nickname=TEST_NICKNAME,
                gender=Gender.MALE,
                birth_date=date(2000, 1, 1),
                role=UserRole.STUDENT,
                is_active=True,
                is_email_verified=True,  # 이메일 인증 건너뛰기
                social_provider=SocialProvider.EMAIL,
            )

            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            print("=" * 60)
            print("[SUCCESS] 테스트 계정이 성공적으로 생성되었습니다!")
            print("=" * 60)
            print(f"이메일: {test_user.email}")
            print(f"비밀번호: {TEST_PASSWORD}")
            print(f"닉네임: {test_user.nickname}")
            print(f"역할: {test_user.role.value}")
            print("=" * 60)
            print("[INFO] 이 계정은 테스트/개발 목적으로만 사용하세요.")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"[ERROR] 테스트 계정 생성 중 오류 발생: {e}")
            raise
        finally:
            await engine.dispose()


async def main():
    """메인 함수"""
    print("\n테스트 계정 생성 스크립트 시작...\n")
    await create_test_account()
    print("\n스크립트 실행 완료\n")


if __name__ == "__main__":
    asyncio.run(main())
