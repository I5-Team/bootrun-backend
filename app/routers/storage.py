from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
from datetime import datetime
from urllib.parse import quote
import uuid
import os
from loguru import logger

from app.services.r2_service import r2_service
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/storage", tags=["스토리지"])


def get_file_extension(filename: str) -> str:
    """파일 확장자 추출"""
    return os.path.splitext(filename)[1].lower()


def generate_unique_filename(original_filename: str, user_id: Optional[int] = None) -> str:
    """고유한 파일명 생성"""
    ext = get_file_extension(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]

    if user_id:
        return f"user_{user_id}/{timestamp}_{unique_id}{ext}"
    else:
        return f"uploads/{timestamp}_{unique_id}{ext}"


@router.post("/upload", summary="파일 업로드")
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = "uploads",
    current_user: User = Depends(get_current_active_user)
):
    """
    파일을 R2에 업로드합니다.

    - **file**: 업로드할 파일
    - **folder**: 저장할 폴더 (기본값: uploads)
    """
    try:
        # 파일 읽기
        file_content = await file.read()

        # 고유한 파일명 생성
        file_path = f"{folder}/{generate_unique_filename(file.filename, current_user.id)}"

        # R2에 업로드
        file_url = r2_service.upload_file(
            file_data=file_content,
            file_path=file_path,
            content_type=file.content_type,
            metadata={
                "original_filename": quote(file.filename or "", safe=''),  # URL 인코딩으로 한글 처리
                "uploaded_by": str(current_user.id),
                "upload_date": datetime.now().isoformat()
            }
        )

        logger.info(f"File uploaded by user {current_user.id}: {file_path}")

        return {
            "success": True,
            "message": "파일이 성공적으로 업로드되었습니다",
            "data": {
                "file_path": file_path,
                "file_url": file_url,
                "original_filename": file.filename,
                "content_type": file.content_type
            }
        }

    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")


@router.post("/upload/image", summary="이미지 업로드")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    이미지 파일을 R2에 업로드합니다.

    - 허용 확장자: jpg, jpeg, png, gif, webp
    """
    # 이미지 확장자 검증
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    ext = get_file_extension(file.filename)

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않은 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
        )

    try:
        file_content = await file.read()
        file_path = f"images/{generate_unique_filename(file.filename, current_user.id)}"

        file_url = r2_service.upload_file(
            file_data=file_content,
            file_path=file_path,
            content_type=file.content_type,
            metadata={
                "type": "image",
                "original_filename": quote(file.filename, safe=''),  # URL 인코딩으로 한글 처리
                "uploaded_by": str(current_user.id)
            }
        )

        return {
            "success": True,
            "message": "이미지가 성공적으로 업로드되었습니다",
            "data": {
                "file_path": file_path,
                "file_url": file_url,
                "original_filename": file.filename
            }
        }

    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail=f"이미지 업로드 실패: {str(e)}")


@router.post("/upload/video", summary="동영상 업로드")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    동영상 파일을 R2에 업로드합니다.

    - 허용 확장자: mp4, avi, mov, mkv, webm
    """
    # 동영상 확장자 검증
    allowed_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    ext = get_file_extension(file.filename)

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않은 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
        )

    try:
        file_content = await file.read()
        file_path = f"videos/{generate_unique_filename(file.filename, current_user.id)}"

        file_url = r2_service.upload_file(
            file_data=file_content,
            file_path=file_path,
            content_type=file.content_type,
            metadata={
                "type": "video",
                "original_filename": quote(file.filename or "", safe=''),  # URL 인코딩으로 한글 처리
                "uploaded_by": str(current_user.id)
            }
        )

        return {
            "success": True,
            "message": "동영상이 성공적으로 업로드되었습니다",
            "data": {
                "file_path": file_path,
                "file_url": file_url,
                "original_filename": file.filename
            }
        }

    except Exception as e:
        logger.error(f"Video upload error: {e}")
        raise HTTPException(status_code=500, detail=f"동영상 업로드 실패: {str(e)}")


@router.delete("/delete/{file_path:path}", summary="파일 삭제")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    R2에서 파일을 삭제합니다.

    - **file_path**: 삭제할 파일 경로
    """
    try:
        # 파일 존재 확인
        if not r2_service.file_exists(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        # 파일 삭제
        r2_service.delete_file(file_path)

        logger.info(f"File deleted by user {current_user.id}: {file_path}")

        return {
            "success": True,
            "message": "파일이 성공적으로 삭제되었습니다",
            "data": {
                "file_path": file_path
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File delete error: {e}")
        raise HTTPException(status_code=500, detail=f"파일 삭제 실패: {str(e)}")


@router.get("/url/{file_path:path}", summary="파일 URL 조회")
async def get_file_url(
    file_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    파일의 공개 URL을 조회합니다.

    - **file_path**: 파일 경로
    """
    try:
        # 파일 존재 확인
        if not r2_service.file_exists(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        file_url = r2_service.get_file_url(file_path)

        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "file_url": file_url
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file URL error: {e}")
        raise HTTPException(status_code=500, detail=f"URL 조회 실패: {str(e)}")


@router.get("/presigned-url/{file_path:path}", summary="임시 접근 URL 생성")
async def get_presigned_url(
    file_path: str,
    expiration: int = 3600,
    current_user: User = Depends(get_current_active_user)
):
    """
    파일의 임시 접근 URL (Presigned URL)을 생성합니다.

    - **file_path**: 파일 경로
    - **expiration**: URL 만료 시간 (초, 기본 1시간)
    """
    try:
        presigned_url = r2_service.generate_presigned_url(
            file_path=file_path,
            expiration=expiration
        )

        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "presigned_url": presigned_url,
                "expires_in": expiration
            }
        }

    except Exception as e:
        logger.error(f"Generate presigned URL error: {e}")
        raise HTTPException(status_code=500, detail=f"임시 URL 생성 실패: {str(e)}")


@router.get("/list", summary="파일 목록 조회")
async def list_files(
    prefix: str = "",
    max_keys: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    R2 버킷의 파일 목록을 조회합니다.

    - **prefix**: 파일 경로 접두사 (폴더 필터)
    - **max_keys**: 최대 조회 개수
    """
    try:
        files = r2_service.list_files(prefix=prefix, max_keys=max_keys)

        return {
            "success": True,
            "data": {
                "files": files,
                "count": len(files),
                "prefix": prefix
            }
        }

    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=f"파일 목록 조회 실패: {str(e)}")
