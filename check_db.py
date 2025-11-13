from app.core.config import settings

print("=" * 60)
print("현재 데이터베이스 연결 설정")
print("=" * 60)
print(f"DB Host: {settings.database_host}")
print(f"DB Port: {settings.database_port}")
print(f"DB Name: {settings.database_name}")
print(f"DB User: {settings.database_user}")
print(f"Full URL: {settings.database_url}")
print("=" * 60)
