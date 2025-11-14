"""
데이터베이스의 모든 테이블을 삭제하는 스크립트
중앙 DB 초기화 시 사용
"""
import asyncio
from app.core.database import async_engine
from sqlalchemy import text

async def drop_all_tables():
    """모든 테이블을 삭제합니다 (alembic_version 포함)"""
    print("🗑️  모든 테이블 삭제 중...")

    try:
        async with async_engine.begin() as conn:
            # PostgreSQL 스키마 완전 초기화
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

        print("✅ 모든 테이블이 삭제되었습니다.")
        print("📝 이제 'alembic upgrade head'를 실행하세요.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        raise
    finally:
        await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(drop_all_tables())
