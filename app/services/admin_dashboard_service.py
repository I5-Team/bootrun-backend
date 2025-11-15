from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.schemas.admin import (
    DashboardStats, DailyStats, RevenueStats, CourseStats, CategoryStats
)


class AdminDashboardService:
    """관리자 대시보드 통계 서비스"""

    @staticmethod
    async def get_stats(db: AsyncSession) -> DashboardStats:
        """
        대시보드 주요 통계 조회

        Returns:
            DashboardStats: 모든 필드가 초기화된 통계 객체
        """
        try:
            # 전체 사용자 수
            total_users_result = await db.execute(
                text("SELECT COUNT(*) as count FROM users")
            )
            total_users = total_users_result.scalar() or 0

            # 전체 강의 수
            total_courses_result = await db.execute(
                text("SELECT COUNT(*) as count FROM courses WHERE is_published = true")
            )
            total_courses = total_courses_result.scalar() or 0

            # 전체 등록 수
            total_enrollments_result = await db.execute(
                text("SELECT COUNT(*) as count FROM enrollments")
            )
            total_enrollments = total_enrollments_result.scalar() or 0

            # 활성 등록 수
            active_enrollments_result = await db.execute(
                text("""
                    SELECT COUNT(*) as count FROM enrollments
                    WHERE expires_at > NOW()
                """)
            )
            active_enrollments = active_enrollments_result.scalar() or 0

            # 전체 매출
            total_revenue_result = await db.execute(
                text("""
                    SELECT COALESCE(SUM(final_amount), 0) as total
                    FROM payments
                    WHERE status = 'completed'
                """)
            )
            total_revenue = total_revenue_result.scalar() or 0

            # 대기 중인 환불
            pending_refunds_result = await db.execute(
                text("""
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM refunds
                    WHERE status = 'pending'
                """)
            )
            pending_refunds = pending_refunds_result.scalar() or 0

            # 오늘의 방문자
            today_visitors_result = await db.execute(
                text("""
                    SELECT COUNT(DISTINCT ip_address) as count
                    FROM user_activity
                    WHERE DATE(created_at) = CURDATE()
                """)
            )
            today_visitors = today_visitors_result.scalar() or 0

            # 오늘의 조회수
            today_views_result = await db.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM user_activity
                    WHERE DATE(created_at) = CURDATE()
                """)
            )
            today_views = today_views_result.scalar() or 0

            # 오늘의 매출
            today_revenue_result = await db.execute(
                text("""
                    SELECT COALESCE(SUM(final_amount), 0) as total
                    FROM payments
                    WHERE status = 'completed' AND DATE(paid_at) = CURDATE()
                """)
            )
            today_revenue = today_revenue_result.scalar() or 0

            return DashboardStats(
                total_users=total_users,
                total_courses=total_courses,
                total_enrollments=total_enrollments,
                active_enrollments=active_enrollments,
                total_revenue=int(total_revenue) if total_revenue else 0,
                pending_refunds=int(pending_refunds) if pending_refunds else 0,
                today_visitors=today_visitors,
                today_views=today_views,
                today_revenue=int(today_revenue) if today_revenue else 0
            )
        except Exception:
            # 에러 발생 시 모든 필드를 0으로 초기화하여 반환
            return DashboardStats(
                total_users=0,
                total_courses=0,
                total_enrollments=0,
                active_enrollments=0,
                total_revenue=0,
                pending_refunds=0,
                today_visitors=0,
                today_views=0,
                today_revenue=0
            )

    @staticmethod
    async def get_daily_stats(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DailyStats]:
        """
        일별 통계 조회

        Args:
            db: 데이터베이스 세션
            start_date: 시작 날짜 (None이면 기본값 사용)
            end_date: 종료 날짜 (None이면 기본값 사용)

        Returns:
            List[DailyStats]: 일별 통계 리스트 (데이터 없으면 빈 리스트)
        """
        try:
            # 기본값 설정
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=30)

            result = await db.execute(
                text("""
                    SELECT
                        DATE(ua.created_at) as date,
                        COUNT(DISTINCT ua.ip_address) as visitors,
                        COUNT(*) as views,
                        COALESCE(SUM(p.final_amount), 0) as revenue,
                        COALESCE(COUNT(DISTINCT CASE WHEN e.created_at::date = DATE(ua.created_at) THEN e.id END), 0) as enrollments,
                        COALESCE(COUNT(DISTINCT CASE WHEN u.created_at::date = DATE(ua.created_at) THEN u.id END), 0) as new_users
                    FROM user_activity ua
                    LEFT JOIN payments p ON DATE(p.paid_at) = DATE(ua.created_at) AND p.status = 'completed'
                    LEFT JOIN enrollments e ON DATE(e.created_at) = DATE(ua.created_at)
                    LEFT JOIN users u ON DATE(u.created_at) = DATE(ua.created_at)
                    WHERE DATE(ua.created_at) BETWEEN :start_date AND :end_date
                    GROUP BY DATE(ua.created_at)
                    ORDER BY DATE(ua.created_at)
                """),
                {"start_date": start_date, "end_date": end_date}
            )

            rows = result.fetchall()
            if not rows:
                return []

            return [
                DailyStats(
                    date=row[0],
                    visitors=row[1] or 0,
                    views=row[2] or 0,
                    revenue=int(row[3]) if row[3] else 0,
                    enrollments=row[4] or 0,
                    new_users=row[5] or 0
                )
                for row in rows
            ]
        except Exception:
            # 에러 발생 시 빈 리스트 반환
            return []

    @staticmethod
    async def get_revenue_stats(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[RevenueStats]:
        """
        매출 통계 조회

        Args:
            db: 데이터베이스 세션
            start_date: 시작 날짜 (None이면 기본값 사용)
            end_date: 종료 날짜 (None이면 기본값 사용)

        Returns:
            List[RevenueStats]: 매출 통계 리스트 (데이터 없으면 빈 리스트)
        """
        try:
            # 기본값 설정
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=30)

            result = await db.execute(
                text("""
                    SELECT
                        DATE(p.paid_at) as date,
                        COALESCE(SUM(CASE WHEN p.status = 'completed' THEN p.final_amount ELSE 0 END), 0) as revenue,
                        COUNT(CASE WHEN p.status = 'completed' THEN 1 END) as payment_count,
                        COALESCE(SUM(CASE WHEN r.status = 'completed' THEN r.amount ELSE 0 END), 0) as refund_amount,
                        COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as refund_count,
                        COALESCE(SUM(CASE WHEN p.status = 'completed' THEN p.final_amount ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN r.status = 'completed' THEN r.amount ELSE 0 END), 0) as net_revenue
                    FROM payments p
                    LEFT JOIN refunds r ON p.id = r.payment_id
                    WHERE DATE(p.paid_at) BETWEEN :start_date AND :end_date
                    GROUP BY DATE(p.paid_at)
                    ORDER BY DATE(p.paid_at)
                """),
                {"start_date": start_date, "end_date": end_date}
            )

            rows = result.fetchall()
            if not rows:
                return []

            return [
                RevenueStats(
                    date=row[0],
                    revenue=int(row[1]) if row[1] else 0,
                    payment_count=row[2] or 0,
                    refund_amount=int(row[3]) if row[3] else 0,
                    refund_count=row[4] or 0,
                    net_revenue=int(row[5]) if row[5] else 0
                )
                for row in rows
            ]
        except Exception:
            # 에러 발생 시 빈 리스트 반환
            return []

    @staticmethod
    async def get_course_stats(
        db: AsyncSession,
        category_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CourseStats]:
        """
        강의별 통계 조회

        Args:
            db: 데이터베이스 세션
            category_type: 카테고리 타입 (None이면 모든 강의)
            start_date: 시작 날짜 (None이면 제약 없음)
            end_date: 종료 날짜 (None이면 제약 없음)

        Returns:
            List[CourseStats]: 강의별 통계 리스트 (데이터 없으면 빈 리스트)
        """
        try:
            query = """
                SELECT
                    c.id as course_id,
                    c.title as course_title,
                    cat.name as category_name,
                    COUNT(DISTINCT e.id) as total_enrollments,
                    COUNT(DISTINCT CASE WHEN e.expires_at > NOW() THEN e.id END) as active_enrollments,
                    COALESCE(AVG(e.progress_rate), 0) as avg_progress,
                    COUNT(DISTINCT CASE WHEN e.is_completed = true THEN e.id END) as completion_count,
                    COALESCE(
                        COUNT(DISTINCT CASE WHEN e.is_completed = true THEN e.id END) * 100.0 /
                        NULLIF(COUNT(DISTINCT e.id), 0),
                        0
                    ) as completion_rate,
                    COALESCE(SUM(p.final_amount), 0) as total_revenue
                FROM courses c
                LEFT JOIN categories cat ON c.category_id = cat.id
                LEFT JOIN enrollments e ON c.id = e.course_id
                LEFT JOIN payments p ON e.user_id = p.user_id AND c.id = p.course_id AND p.status = 'completed'
                WHERE c.is_published = true
            """

            params = {}

            # 카테고리 필터
            if category_type:
                query += " AND cat.type = :category_type"
                params["category_type"] = category_type

            # 날짜 필터
            if start_date:
                query += " AND e.created_at >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND e.created_at <= :end_date"
                params["end_date"] = end_date

            query += " GROUP BY c.id, c.title, cat.name ORDER BY total_enrollments DESC"

            result = await db.execute(text(query), params)
            rows = result.fetchall()

            if not rows:
                return []

            return [
                CourseStats(
                    course_id=row[0],
                    course_title=row[1],
                    category_name=row[2],
                    total_enrollments=row[3] or 0,
                    active_enrollments=row[4] or 0,
                    avg_progress=float(row[5]) if row[5] else 0.0,
                    completion_count=row[6] or 0,
                    completion_rate=float(row[7]) if row[7] else 0.0,
                    total_revenue=int(row[8]) if row[8] else 0
                )
                for row in rows
            ]
        except Exception:
            # 에러 발생 시 빈 리스트 반환
            return []

    @staticmethod
    async def get_category_stats(db: AsyncSession) -> List[CategoryStats]:
        """
        카테고리별 통계 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            List[CategoryStats]: 카테고리별 통계 리스트 (데이터 없으면 빈 리스트)
        """
        try:
            result = await db.execute(
                text("""
                    SELECT
                        cat.id as category_id,
                        cat.name as category_name,
                        COUNT(DISTINCT c.id) as course_count,
                        COUNT(DISTINCT e.id) as total_enrollments,
                        COALESCE(SUM(p.final_amount), 0) as total_revenue,
                        COALESCE(
                            AVG(CASE WHEN e.is_completed = true THEN 100.0 ELSE 0 END),
                            0
                        ) as avg_completion_rate
                    FROM categories cat
                    LEFT JOIN courses c ON cat.id = c.category_id AND c.is_published = true
                    LEFT JOIN enrollments e ON c.id = e.course_id
                    LEFT JOIN payments p ON e.user_id = p.user_id AND c.id = p.course_id AND p.status = 'completed'
                    GROUP BY cat.id, cat.name
                    ORDER BY total_enrollments DESC
                """)
            )

            rows = result.fetchall()
            if not rows:
                return []

            return [
                CategoryStats(
                    category_id=row[0],
                    category_name=row[1],
                    course_count=row[2] or 0,
                    total_enrollments=row[3] or 0,
                    total_revenue=int(row[4]) if row[4] else 0,
                    avg_completion_rate=float(row[5]) if row[5] else 0.0
                )
                for row in rows
            ]
        except Exception:
            # 에러 발생 시 빈 리스트 반환
            return []