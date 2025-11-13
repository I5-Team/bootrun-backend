# fix_alembic.py
from sqlalchemy import create_engine, text
from app.core.config import settings  # 본인의 config 경로에 맞게 수정

# sync_database_url 사용
DATABASE_URL = settings.sync_database_url

print(f"연결 중...")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 현재 버전 확인
    result = conn.execute(text("SELECT * FROM alembic_version"))
    current = result.fetchone()
    print(f"현재 버전: {current}")
    
    # 이전 버전으로 변경
    conn.execute(text("UPDATE alembic_version SET version_num = 'ace990837f3d'"))
    conn.commit()
    
    # 확인
    result = conn.execute(text("SELECT * FROM alembic_version"))
    updated = result.fetchone()
    print(f"변경된 버전: {updated}")

print("완료!")