# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
import secrets
import string
import logging

from app.models.user import User, UserRole, Gender, SocialProvider
from app.models.progress import Enrollment, Progress
from app.models.payment import Payment
from app.models.certificate import Certificate
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    PasswordChangeRequest,
    EmailChangeRequest,
    EmailChangeConfirm,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserProfileResponse,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ActivityResponse,
    NotificationResponse,
)
from app.schemas.common import (
    PaginatedResponse,
    ProfileImageUploadResponse,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    verify_password_reset_token,
    decode_token,
)
from app.exceptions.base import (
    LoginFailedError,
    EmailAlreadyExistsError,
    NotFoundError,
    BadRequestError,
    UnauthorizedError,
    VerificationCodeInvalidError,
    ForbiddenError,
)
from app.utils.constants import (
    EMAIL_VERIFICATION_CODE_LENGTH,
    EMAIL_VERIFICATION_CODE_EXPIRY_MINUTES,
    REDIS_KEY_EMAIL_VERIFICATION,
    REDIS_KEY_PASSWORD_RESET,
    REDIS_KEY_LOGIN_ATTEMPTS,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_LOCKOUT_DURATION,
    DEFAULT_PROFILE_IMAGE,
)
from app.utils.helpers import (
    calculate_age,
    calculate_total_pages,
    calculate_offset,
    get_current_utc_datetime,
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        redis_client: Optional[Any] = None
    ):
        self.db = db
        self.redis = redis_client

    async def register_user(
        self,
        data: UserCreate
    ) -> UserResponse:
        existing_user = await self._get_user_by_email(data.email)
        if existing_user:
            raise EmailAlreadyExistsError('이미 존재하는 이메일입니다')

        existing_nickname = await self._check_nickname_exists(
            data.nickname
        )
        if existing_nickname:
            raise BadRequestError('이미 사용 중인 닉네임입니다')

        hashed_pwd = hash_password(data.password)

        new_user = User(
            email=data.email,
            password_hash=hashed_pwd,
            nickname=data.nickname,
            gender=data.gender,
            birth_date=data.birth_date,
            profile_image=data.profile_image,
            role=UserRole.STUDENT,
            social_provider=(
                data.provider if data.provider else SocialProvider.EMAIL
            ),
            social_id=data.social_id,
            is_active=True,
            is_email_verified=False,
            created_at=get_current_utc_datetime(),
            updated_at=get_current_utc_datetime(),
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        logger.info(
            f'신규 사용자 등록: {new_user.email} (ID: {new_user.id})'
        )

        return UserResponse.model_validate(new_user)

    async def send_verification_code(
        self,
        email: str
    ) -> str:
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundError('사용자를 찾을 수 없습니다')

        if user.is_email_verified:
            raise BadRequestError('이미 인증된 이메일입니다')

        code = self._generate_verification_code()

        if self.redis:
            key = REDIS_KEY_EMAIL_VERIFICATION.format(email=email)
            await self.redis.setex(
                key,
                EMAIL_VERIFICATION_CODE_EXPIRY_MINUTES * 60,
                code
            )

        logger.info(f'이메일 인증 코드 생성: {email}')

        return code

    async def verify_email(
        self,
        email: str,
        code: str
    ) -> None:
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundError('사용자를 찾을 수 없습니다')

        if user.is_email_verified:
            raise BadRequestError('이미 인증된 이메일입니다')

        if self.redis:
            key = REDIS_KEY_EMAIL_VERIFICATION.format(email=email)
            stored_code = await self.redis.get(key)

            if not stored_code or stored_code != code:
                raise VerificationCodeInvalidError(
                    '인증 코드가 올바르지 않습니다'
                )

            await self.redis.delete(key)

        user.is_email_verified = True
        user.updated_at = get_current_utc_datetime()

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f'이메일 인증 완료: {email}')

    async def login(
        self,
        data: UserLogin
    ) -> TokenResponse:
        user = await self._get_user_by_email(data.email)
        if not user:
            raise LoginFailedError(
                '이메일 또는 비밀번호가 일치하지 않습니다'
            )

        if self.redis:
            await self._check_login_attempts(user.id)

        if not user.password_hash:
            raise LoginFailedError(
                '소셜 로그인 계정입니다. 해당 소셜 로그인을 사용해주세요'
            )

        if not verify_password(data.password, user.password_hash):
            if self.redis:
                await self._increment_login_attempts(user.id)
            raise LoginFailedError(
                '이메일 또는 비밀번호가 일치하지 않습니다'
            )

        if not user.is_active:
            raise ForbiddenError('비활성화된 계정입니다')

        if self.redis:
            await self._reset_login_attempts(user.id)

        user.last_login = get_current_utc_datetime()
        await self.db.commit()
        await self.db.refresh(user)

        access_token = create_access_token(data={'sub': str(user.id)})
        refresh_token = create_refresh_token(data={'sub': str(user.id)})

        logger.info(f'로그인 성공: {user.email} (ID: {user.id})')

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
            user=UserResponse.model_validate(user)
        )

    async def logout(
        self,
        user_id: int
    ) -> None:
        user = await self.get_user_by_id(user_id)
        logger.info(f'로그아웃: 사용자 ID {user_id}')

    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> TokenResponse:
        payload = decode_token(refresh_token, token_type='refresh')

        if not payload:
            raise UnauthorizedError(
                '유효하지 않거나 만료된 리프레시 토큰입니다'
            )

        user_id = payload.get('sub')
        if not user_id:
            raise UnauthorizedError('토큰에서 사용자 정보를 찾을 수 없습니다')

        user = await self.get_user_by_id(int(user_id))

        access_token = create_access_token(data={'sub': str(user.id)})
        new_refresh_token = create_refresh_token(
            data={'sub': str(user.id)}
        )

        logger.info(f'토큰 갱신: 사용자 ID {user_id}')

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type='bearer',
            user=UserResponse.model_validate(user)
        )

    async def social_login(
        self,
        provider: SocialProvider,
        social_id: str,
        email: str,
        nickname: Optional[str] = None
    ) -> TokenResponse:
        user = await self._get_user_by_social_id(provider, social_id)

        if not user:
            user = await self._get_user_by_email(email)

            if user:
                if user.social_provider != provider:
                    raise BadRequestError(
                        f'이 이메일은 이미 {user.social_provider.value} '
                        f'계정으로 가입되어 있습니다'
                    )
            else:
                generated_nickname = (
                    nickname if nickname
                    else await self._generate_unique_nickname(email)
                )

                user = User(
                    email=email,
                    nickname=generated_nickname,
                    social_provider=provider,
                    social_id=social_id,
                    role=UserRole.STUDENT,
                    is_active=True,
                    is_email_verified=True,
                    gender=Gender.OTHER,
                    birth_date=datetime(2000, 1, 1).date(),
                    created_at=get_current_utc_datetime(),
                    updated_at=get_current_utc_datetime(),
                )

                self.db.add(user)
                await self.db.commit()
                await self.db.refresh(user)

                logger.info(
                    f'소셜 로그인 신규 가입: {email} '
                    f'(Provider: {provider.value})'
                )

        if not user.is_active:
            raise ForbiddenError('비활성화된 계정입니다')

        user.last_login = get_current_utc_datetime()
        await self.db.commit()
        await self.db.refresh(user)

        access_token = create_access_token(data={'sub': str(user.id)})
        refresh_token = create_refresh_token(data={'sub': str(user.id)})

        logger.info(
            f'소셜 로그인 성공: {user.email} '
            f'(Provider: {provider.value})'
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
            user=UserResponse.model_validate(user)
        )

    async def get_user_by_id(
        self,
        user_id: int
    ) -> User:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError('사용자를 찾을 수 없습니다')

        return user

    async def get_user_profile(
        self,
        user_id: int
    ) -> UserProfileResponse:
        user = await self.get_user_by_id(user_id)

        total_study_time = await self._calculate_total_study_time(user_id)

        enrollment_expires_at = (
            await self._get_earliest_enrollment_expiry(user_id)
        )

        profile = UserProfileResponse.model_validate(user)
        profile.total_study_time = total_study_time
        profile.enrollment_expires_at = enrollment_expires_at

        return profile

    async def update_profile(
        self,
        user_id: int,
        data: UserUpdate
    ) -> UserResponse:
        user = await self.get_user_by_id(user_id)

        if data.nickname and data.nickname != user.nickname:
            exists = await self._check_nickname_exists(data.nickname)
            if exists:
                raise BadRequestError('이미 사용 중인 닉네임입니다')
            user.nickname = data.nickname

        if data.gender:
            user.gender = data.gender

        if data.birth_date:
            user.birth_date = data.birth_date

        if data.profile_image is not None:
            user.profile_image = data.profile_image

        if data.password and data.password_confirm:
            if data.password != data.password_confirm:
                raise BadRequestError('비밀번호가 일치하지 않습니다')
            user.password_hash = hash_password(data.password)

        user.updated_at = get_current_utc_datetime()

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f'프로필 업데이트: 사용자 ID {user_id}')

        return UserResponse.model_validate(user)

    async def upload_profile_image(
        self,
        user_id: int,
        file: UploadFile
    ) -> ProfileImageUploadResponse:
        user = await self.get_user_by_id(user_id)

        max_size = 5 * 1024 * 1024
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > max_size:
            raise BadRequestError(
                '파일 크기는 5MB를 초과할 수 없습니다'
            )

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            raise BadRequestError(
                '지원되지 않는 파일 형식입니다. '
                'JPG, PNG, GIF, WEBP만 업로드 가능합니다'
            )

        import uuid
        file_extension = file.filename.split('.')[-1]
        new_filename = f'{uuid.uuid4()}.{file_extension}'

        image_url = f'/uploads/profiles/{new_filename}'

        user.profile_image = image_url
        user.updated_at = get_current_utc_datetime()
        await self.db.commit()

        logger.info(f'프로필 이미지 업로드: 사용자 ID {user_id}')

        return ProfileImageUploadResponse(
            image_url=image_url,
            file_size=file_size,
            uploaded_at=get_current_utc_datetime()
        )

    async def delete_profile_image(
        self,
        user_id: int
    ) -> None:
        user = await self.get_user_by_id(user_id)

        user.profile_image = DEFAULT_PROFILE_IMAGE
        user.updated_at = get_current_utc_datetime()
        await self.db.commit()

        logger.info(f'프로필 이미지 삭제: 사용자 ID {user_id}')

    async def change_password(
        self,
        user_id: int,
        data: PasswordChangeRequest
    ) -> None:
        user = await self.get_user_by_id(user_id)

        if not user.password_hash:
            raise BadRequestError(
                '소셜 로그인 계정은 비밀번호를 변경할 수 없습니다'
            )

        if not verify_password(
            data.current_password,
            user.password_hash
        ):
            raise BadRequestError('현재 비밀번호가 일치하지 않습니다')

        if data.new_password != data.new_password_confirm:
            raise BadRequestError('새 비밀번호가 일치하지 않습니다')

        user.password_hash = hash_password(data.new_password)
        user.updated_at = get_current_utc_datetime()

        await self.db.commit()

        logger.info(f'비밀번호 변경: 사용자 ID {user_id}')

    async def request_password_reset(
        self,
        email: str
    ) -> str:
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundError('사용자를 찾을 수 없습니다')

        if not user.password_hash:
            raise BadRequestError(
                '소셜 로그인 계정은 비밀번호 재설정을 할 수 없습니다'
            )

        reset_token = create_password_reset_token(user.id)

        if self.redis:
            key = REDIS_KEY_PASSWORD_RESET.format(user_id=user.id)
            await self.redis.setex(
                key,
                30 * 60,
                reset_token
            )

        logger.info(f'비밀번호 재설정 요청: {email}')

        return reset_token

    async def confirm_password_reset(
        self,
        data: PasswordResetConfirm
    ) -> None:
        user_id = verify_password_reset_token(data.reset_token)
        if not user_id:
            raise UnauthorizedError(
                '유효하지 않거나 만료된 토큰입니다'
            )

        user = await self.get_user_by_id(user_id)

        if user.email != data.email:
            raise BadRequestError('이메일이 일치하지 않습니다')

        if data.new_password != data.password_confirm:
            raise BadRequestError('비밀번호가 일치하지 않습니다')

        user.password_hash = hash_password(data.new_password)
        user.updated_at = get_current_utc_datetime()

        await self.db.commit()

        if self.redis:
            key = REDIS_KEY_PASSWORD_RESET.format(user_id=user.id)
            await self.redis.delete(key)

        logger.info(f'비밀번호 재설정 완료: 사용자 ID {user_id}')

    async def request_email_change(
        self,
        user_id: int,
        new_email: str
    ) -> str:
        user = await self.get_user_by_id(user_id)

        if user.email == new_email:
            raise BadRequestError('현재 이메일과 동일합니다')

        existing = await self._get_user_by_email(new_email)
        if existing:
            raise EmailAlreadyExistsError('이미 존재하는 이메일입니다')

        code = self._generate_verification_code()

        if self.redis:
            key = REDIS_KEY_EMAIL_VERIFICATION.format(email=new_email)
            await self.redis.setex(
                key,
                EMAIL_VERIFICATION_CODE_EXPIRY_MINUTES * 60,
                code
            )

        logger.info(
            f'이메일 변경 요청: 사용자 ID {user_id}, '
            f'새 이메일 {new_email}'
        )

        return code

    async def confirm_email_change(
        self,
        user_id: int,
        data: EmailChangeConfirm
    ) -> None:
        user = await self.get_user_by_id(user_id)

        if self.redis:
            key = REDIS_KEY_EMAIL_VERIFICATION.format(
                email=data.new_email
            )
            stored_code = await self.redis.get(key)

            if not stored_code or stored_code != data.verification_code:
                raise VerificationCodeInvalidError(
                    '인증 코드가 올바르지 않습니다'
                )

            await self.redis.delete(key)

        user.email = data.new_email
        user.is_email_verified = True
        user.updated_at = get_current_utc_datetime()

        await self.db.commit()

        logger.info(f'이메일 변경 완료: 사용자 ID {user_id}')

    async def delete_account(
        self,
        user_id: int,
        password: Optional[str] = None,
        confirm_deletion: bool = False
    ) -> None:
        if not confirm_deletion:
            raise BadRequestError('탈퇴 확인이 필요합니다')

        user = await self.get_user_by_id(user_id)

        if user.password_hash and password:
            if not verify_password(password, user.password_hash):
                raise BadRequestError('비밀번호가 일치하지 않습니다')

        active_enrollments = await self.db.execute(
            select(func.count(Enrollment.id)).where(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.is_active == True,
                    Enrollment.expired_at > get_current_utc_datetime()
                )
            )
        )
        if active_enrollments.scalar() > 0:
            raise BadRequestError(
                '진행 중인 강의가 있어 탈퇴할 수 없습니다'
            )

        user.is_active = False
        user.updated_at = get_current_utc_datetime()

        await self.db.commit()

        logger.info(f'계정 비활성화: 사용자 ID {user_id}')

    async def restore_account(
        self,
        email: str,
        password: str
    ) -> None:
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundError('사용자를 찾을 수 없습니다')

        if user.is_active:
            raise BadRequestError('이미 활성화된 계정입니다')

        if not user.password_hash:
            raise BadRequestError(
                '소셜 로그인 계정은 복구할 수 없습니다'
            )

        if not verify_password(password, user.password_hash):
            raise BadRequestError('비밀번호가 일치하지 않습니다')

        deleted_date = user.updated_at
        now = get_current_utc_datetime()
        days_since_deletion = (now - deleted_date).days

        if days_since_deletion > 30:
            raise BadRequestError('복구 가능 기간이 지났습니다')

        user.is_active = True
        user.updated_at = get_current_utc_datetime()

        await self.db.commit()

        logger.info(f'계정 복구: {email}')

    async def get_user_activities(
        self,
        user_id: int,
        activity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[ActivityResponse]:
        user = await self.get_user_by_id(user_id)

        activities = []

        if not activity_type or activity_type == 'enrollment':
            enrollments = await self.db.execute(
                select(Enrollment)
                .where(Enrollment.user_id == user_id)
                .order_by(desc(Enrollment.created_at))
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            for enrollment in enrollments.scalars():
                activities.append(ActivityResponse(
                    id=enrollment.id,
                    activity_type='enrollment',
                    title='강의 수강 등록',
                    description=f'강의 ID: {enrollment.course_id}',
                    created_at=enrollment.created_at,
                    related_id=enrollment.course_id
                ))

        if not activity_type or activity_type == 'payment':
            payments = await self.db.execute(
                select(Payment)
                .where(Payment.user_id == user_id)
                .order_by(desc(Payment.created_at))
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            for payment in payments.scalars():
                activities.append(ActivityResponse(
                    id=payment.id,
                    activity_type='payment',
                    title='결제 완료',
                    description=f'금액: {payment.amount}원',
                    created_at=payment.created_at,
                    related_id=payment.id
                ))

        total = len(activities)
        total_pages = calculate_total_pages(total, page_size)

        return PaginatedResponse(
            success=True,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=activities
        )

    async def get_user_notifications(
        self,
        user_id: int,
        is_read: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[NotificationResponse]:
        user = await self.get_user_by_id(user_id)

        notifications = []

        total = len(notifications)
        total_pages = calculate_total_pages(total, page_size)

        return PaginatedResponse(
            success=True,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=notifications
        )

    async def mark_notification_as_read(
        self,
        user_id: int,
        notification_id: int
    ) -> NotificationResponse:
        user = await self.get_user_by_id(user_id)

        raise NotFoundError('알림을 찾을 수 없습니다')

    async def mark_all_notifications_as_read(
        self,
        user_id: int
    ) -> None:
        user = await self.get_user_by_id(user_id)

        logger.info(f'모든 알림 읽음 처리: 사용자 ID {user_id}')

    async def get_user_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        user = await self.get_user_by_id(user_id)

        total_study_time = await self._calculate_total_study_time(user_id)

        enrollments_query = select(func.count(Enrollment.id)).where(
            and_(
                Enrollment.user_id == user_id,
                Enrollment.is_active == True
            )
        )
        enrollments_result = await self.db.execute(enrollments_query)
        total_enrollments = enrollments_result.scalar() or 0

        completed_query = select(func.count(Enrollment.id)).where(
            and_(
                Enrollment.user_id == user_id,
                Enrollment.is_active == True,
                Enrollment.progress_rate >= 100
            )
        )
        completed_result = await self.db.execute(completed_query)
        completed_courses = completed_result.scalar() or 0

        certificates_query = select(func.count(Certificate.id)).where(
            Certificate.user_id == user_id
        )
        certificates_result = await self.db.execute(certificates_query)
        total_certificates = certificates_result.scalar() or 0

        payments_query = select(func.count(Payment.id)).where(
            Payment.user_id == user_id
        )
        payments_result = await self.db.execute(payments_query)
        total_payments = payments_result.scalar() or 0

        return {
            'user_id': user_id,
            'total_study_time_minutes': total_study_time,
            'total_enrollments': total_enrollments,
            'completed_courses': completed_courses,
            'total_certificates': total_certificates,
            'total_payments': total_payments,
            'member_since': user.created_at,
            'last_login': user.last_login,
        }

    async def check_access_period(
        self,
        user_id: int,
        course_id: int
    ) -> Dict[str, Any]:
        query = select(Enrollment).where(
            and_(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
                Enrollment.is_active == True
            )
        )
        result = await self.db.execute(query)
        enrollment = result.scalar_one_or_none()

        if not enrollment:
            return {
                'has_access': False,
                'message': '수강 등록이 필요합니다',
            }

        now = get_current_utc_datetime()
        expired_at = enrollment.expired_at

        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)

        if now > expired_at:
            return {
                'has_access': False,
                'expired_at': expired_at,
                'message': '수강 기간이 만료되었습니다',
            }

        days_remaining = (expired_at - now).days

        return {
            'has_access': True,
            'expired_at': expired_at,
            'days_remaining': days_remaining,
            'message': f'수강 가능 (남은 기간: {days_remaining}일)',
        }

    async def _get_user_by_email(
        self,
        email: str
    ) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_by_social_id(
        self,
        provider: SocialProvider,
        social_id: str
    ) -> Optional[User]:
        query = select(User).where(
            and_(
                User.social_provider == provider,
                User.social_id == social_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _check_nickname_exists(
        self,
        nickname: str
    ) -> bool:
        query = select(User).where(User.nickname == nickname)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _calculate_total_study_time(
        self,
        user_id: int
    ) -> int:
        query = select(func.sum(Progress.watched_seconds)).where(
            Progress.user_id == user_id
        )
        result = await self.db.execute(query)
        total_seconds = result.scalar() or 0
        return int(total_seconds / 60)

    async def _get_earliest_enrollment_expiry(
        self,
        user_id: int
    ) -> Optional[datetime]:
        query = (
            select(Enrollment.expired_at)
            .where(
                and_(
                    Enrollment.user_id == user_id,
                    Enrollment.is_active == True
                )
            )
            .order_by(Enrollment.expired_at.asc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _generate_verification_code(self) -> str:
        return ''.join(
            secrets.choice(string.digits)
            for _ in range(EMAIL_VERIFICATION_CODE_LENGTH)
        )

    async def _generate_unique_nickname(
        self,
        email: str
    ) -> str:
        base_nickname = email.split('@')[0][:10]
        nickname = base_nickname

        counter = 1
        while await self._check_nickname_exists(nickname):
            nickname = f'{base_nickname}{counter}'
            counter += 1

        return nickname

    async def _check_login_attempts(
        self,
        user_id: int
    ) -> None:
        if not self.redis:
            return

        key = REDIS_KEY_LOGIN_ATTEMPTS.format(user_id=user_id)
        attempts = await self.redis.get(key)

        if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
            raise BadRequestError(
                '로그인 시도 횟수를 초과했습니다. '
                '나중에 다시 시도해주세요'
            )

    async def _increment_login_attempts(
        self,
        user_id: int
    ) -> None:
        if not self.redis:
            return

        key = REDIS_KEY_LOGIN_ATTEMPTS.format(user_id=user_id)
        attempts = await self.redis.get(key)

        if attempts:
            await self.redis.incr(key)
        else:
            await self.redis.setex(key, LOGIN_LOCKOUT_DURATION, 1)

    async def _reset_login_attempts(
        self,
        user_id: int
    ) -> None:
        if not self.redis:
            return

        key = REDIS_KEY_LOGIN_ATTEMPTS.format(user_id=user_id)
        await self.redis.delete(key)
