"""
관리자 계정 관리 CLI 스크립트

관리자 계정의 생성, 조회, 비밀번호 변경, 삭제 기능을 제공합니다.

실행 방법:
    # 관리자 목록 조회
    python scripts/manage_admin.py list

    # 새 관리자 생성
    python scripts/manage_admin.py create --email admin@example.com --nickname "관리자" --password "SecurePass123!"

    # 관리자 비밀번호 변경
    python scripts/manage_admin.py change-password --email admin@example.com --password "NewSecurePass123!"

    # 관리자 권한 제거 (일반 사용자로 변경)
    python scripts/manage_admin.py revoke --email admin@example.com

    # 일반 사용자를 관리자로 승격
    python scripts/manage_admin.py promote --email user@example.com
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import date
from getpass import getpass

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole, Gender, SocialProvider


class AdminManager:
    """관리자 계정 관리 클래스"""

    def __init__(self):
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """데이터베이스 연결 초기화"""
        self.engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def cleanup(self):
        """리소스 정리"""
        if self.engine:
            await self.engine.dispose()

    async def list_admins(self):
        """모든 관리자 계정 목록 조회"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.role == UserRole.ADMIN)
            )
            admins = result.scalars().all()

            if not admins:
                print("\n[ERROR] 등록된 관리자 계정이 없습니다.\n")
                return

            print("\n" + "=" * 80)
            print("관리자 계정 목록")
            print("=" * 80)
            for idx, admin in enumerate(admins, 1):
                print(f"\n[{idx}]")
                print(f"  ID: {admin.id}")
                print(f"  이메일: {admin.email}")
                print(f"  닉네임: {admin.nickname}")
                print(f"  활성화: {'예' if admin.is_active else '아니오'}")
                print(f"  이메일 인증: {'완료' if admin.is_email_verified else '미완료'}")
                print(f"  가입일: {admin.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  마지막 로그인: {admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else '없음'}")
            print("\n" + "=" * 80 + "\n")

    async def create_admin(self, email: str, nickname: str, password: str = None):
        """새 관리자 계정 생성"""
        async with self.async_session() as session:
            try:
                # 중복 이메일 확인
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"\n[ERROR] 이미 존재하는 이메일입니다: {email}\n")
                    return

                # 비밀번호 입력 (인자로 받지 않은 경우)
                if not password:
                    password = getpass("비밀번호 입력: ")
                    password_confirm = getpass("비밀번호 확인: ")

                    if password != password_confirm:
                        print("\n[ERROR] 비밀번호가 일치하지 않습니다.\n")
                        return

                # 비밀번호 해싱
                hashed_password = hash_password(password)

                # 관리자 계정 생성
                new_admin = User(
                    email=email,
                    password_hash=hashed_password,
                    nickname=nickname,
                    gender=Gender.OTHER,
                    birth_date=date(2000, 1, 1),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_email_verified=True,
                    social_provider=SocialProvider.EMAIL,
                )

                session.add(new_admin)
                await session.commit()
                await session.refresh(new_admin)

                print("\n" + "=" * 60)
                print("[SUCCESS] 관리자 계정이 성공적으로 생성되었습니다!")
                print("=" * 60)
                print(f"이메일: {new_admin.email}")
                print(f"닉네임: {new_admin.nickname}")
                print(f"사용자 ID: {new_admin.id}")
                print("=" * 60 + "\n")

            except Exception as e:
                await session.rollback()
                print(f"\n[ERROR] 관리자 생성 중 오류 발생: {e}\n")

    async def change_password(self, email: str, password: str = None):
        """관리자 비밀번호 변경"""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()

                if not user:
                    print(f"\n[ERROR] 사용자를 찾을 수 없습니다: {email}\n")
                    return

                if user.role != UserRole.ADMIN:
                    print(f"\n[ERROR] 해당 사용자는 관리자가 아닙니다: {email}\n")
                    return

                # 비밀번호 입력
                if not password:
                    password = getpass("새 비밀번호 입력: ")
                    password_confirm = getpass("새 비밀번호 확인: ")

                    if password != password_confirm:
                        print("\n[ERROR] 비밀번호가 일치하지 않습니다.\n")
                        return

                # 비밀번호 변경
                user.password_hash = hash_password(password)
                await session.commit()

                print("\n[SUCCESS] 비밀번호가 성공적으로 변경되었습니다.\n")

            except Exception as e:
                await session.rollback()
                print(f"\n[ERROR] 비밀번호 변경 중 오류 발생: {e}\n")

    async def revoke_admin(self, email: str):
        """관리자 권한 제거 (일반 사용자로 변경)"""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()

                if not user:
                    print(f"\n[ERROR] 사용자를 찾을 수 없습니다: {email}\n")
                    return

                if user.role != UserRole.ADMIN:
                    print(f"\n[ERROR] 해당 사용자는 관리자가 아닙니다: {email}\n")
                    return

                # 관리자가 1명만 남은 경우 경고
                admin_count_result = await session.execute(
                    select(User).where(User.role == UserRole.ADMIN)
                )
                admin_count = len(admin_count_result.scalars().all())

                if admin_count <= 1:
                    print("\n[WARNING] 경고: 마지막 관리자 계정입니다!")
                    confirm = input("정말로 권한을 제거하시겠습니까? (yes/no): ")
                    if confirm.lower() != 'yes':
                        print("\n[CANCELLED] 취소되었습니다.\n")
                        return

                # 일반 사용자로 변경
                user.role = UserRole.STUDENT
                await session.commit()

                print(f"\n[SUCCESS] {email}의 관리자 권한이 제거되었습니다.\n")

            except Exception as e:
                await session.rollback()
                print(f"\n[ERROR] 권한 제거 중 오류 발생: {e}\n")

    async def promote_to_admin(self, email: str):
        """일반 사용자를 관리자로 승격"""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()

                if not user:
                    print(f"\n[ERROR] 사용자를 찾을 수 없습니다: {email}\n")
                    return

                if user.role == UserRole.ADMIN:
                    print(f"\n[ERROR] 이미 관리자입니다: {email}\n")
                    return

                # 관리자로 승격
                user.role = UserRole.ADMIN
                user.is_email_verified = True  # 관리자는 이메일 인증 자동 완료
                await session.commit()

                print(f"\n[SUCCESS] {email}이(가) 관리자로 승격되었습니다.\n")

            except Exception as e:
                await session.rollback()
                print(f"\n[ERROR] 승격 중 오류 발생: {e}\n")


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="BootRun 관리자 계정 관리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/manage_admin.py list
  python scripts/manage_admin.py create --email admin@example.com --nickname "관리자"
  python scripts/manage_admin.py change-password --email admin@example.com
  python scripts/manage_admin.py revoke --email admin@example.com
  python scripts/manage_admin.py promote --email user@example.com
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')

    # list 명령어
    subparsers.add_parser('list', help='관리자 목록 조회')

    # create 명령어
    create_parser = subparsers.add_parser('create', help='새 관리자 생성')
    create_parser.add_argument('--email', required=True, help='이메일 주소')
    create_parser.add_argument('--nickname', required=True, help='닉네임')
    create_parser.add_argument('--password', help='비밀번호 (미입력 시 프롬프트에서 입력)')

    # change-password 명령어
    password_parser = subparsers.add_parser('change-password', help='관리자 비밀번호 변경')
    password_parser.add_argument('--email', required=True, help='이메일 주소')
    password_parser.add_argument('--password', help='새 비밀번호 (미입력 시 프롬프트에서 입력)')

    # revoke 명령어
    revoke_parser = subparsers.add_parser('revoke', help='관리자 권한 제거')
    revoke_parser.add_argument('--email', required=True, help='이메일 주소')

    # promote 명령어
    promote_parser = subparsers.add_parser('promote', help='일반 사용자를 관리자로 승격')
    promote_parser.add_argument('--email', required=True, help='이메일 주소')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # AdminManager 초기화
    manager = AdminManager()
    await manager.initialize()

    try:
        if args.command == 'list':
            await manager.list_admins()
        elif args.command == 'create':
            await manager.create_admin(
                email=args.email,
                nickname=args.nickname,
                password=args.password
            )
        elif args.command == 'change-password':
            await manager.change_password(
                email=args.email,
                password=args.password
            )
        elif args.command == 'revoke':
            await manager.revoke_admin(email=args.email)
        elif args.command == 'promote':
            await manager.promote_to_admin(email=args.email)
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
