"""
기존 Enrollment의 progress_rate를 시간 기반으로 재계산하는 스크립트

사용법:
    python scripts/recalculate_progress_rates.py
"""
import asyncio
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import async_session_maker
from app.models.progress import Enrollment, Progress
from app.models.course import Course, Chapter, Lecture


async def recalculate_all_progress_rates():
    """모든 Enrollment의 progress_rate를 시간 기반으로 재계산"""

    async with async_session_maker() as db:
        # 모든 활성 Enrollment 조회
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.is_active == True)
        )
        enrollments = result.scalars().all()

        print(f"Starting recalculation for {len(enrollments)} enrollments...")

        updated_count = 0
        skipped_count = 0

        for enrollment in enrollments:
            # Course 조회
            course_result = await db.execute(
                select(Course).where(Course.id == enrollment.course_id)
            )
            course = course_result.scalar_one_or_none()

            if not course or course.total_duration == 0:
                print(f"  [SKIP] Enrollment {enrollment.id}: Course {enrollment.course_id} total_duration=0")
                skipped_count += 1
                continue

            # 해당 코스의 모든 lecture_id 수집
            lecture_ids_result = await db.execute(
                select(Lecture.id)
                .join(Chapter, Lecture.chapter_id == Chapter.id)
                .where(Chapter.course_id == course.id)
            )
            lecture_ids = [row[0] for row in lecture_ids_result.all()]

            # 총 시청 시간 계산
            if lecture_ids:
                watched_result = await db.execute(
                    select(func.sum(Progress.watched_seconds))
                    .where(
                        Progress.user_id == enrollment.user_id,
                        Progress.lecture_id.in_(lecture_ids)
                    )
                )
                total_watched = watched_result.scalar() or 0
            else:
                total_watched = 0

            # 시간 기반 진행률 계산
            old_progress_rate = enrollment.progress_rate
            new_progress_rate = (total_watched / course.total_duration * 100) if course.total_duration > 0 else 0
            new_progress_rate = min(new_progress_rate, 100.0)

            # 업데이트
            enrollment.progress_rate = new_progress_rate
            updated_count += 1

            print(f"  [OK] Enrollment {enrollment.id} (User {enrollment.user_id}, Course {enrollment.course_id}): "
                  f"{old_progress_rate:.1f}% -> {new_progress_rate:.1f}%")

        # 커밋
        await db.commit()

        print(f"\nRecalculation complete!")
        print(f"  Updated: {updated_count}")
        print(f"  Skipped: {skipped_count}")


if __name__ == "__main__":
    asyncio.run(recalculate_all_progress_rates())
