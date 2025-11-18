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
        total_users = await db.execute(text("SELECT COUNT(*) FROM users"))
        total_users = total_users.scalar() or 0

        total_courses = await db.execute(text("SELECT COUNT(*) FROM courses WHERE is_published = true"))
        total_courses = total_courses.scalar() or 0

        total_enrollments = await db.execute(text("SELECT COUNT(*) FROM enrollments"))
        total_enrollments = total_enrollments.scalar() or 0

        active_enrollments = await db.execute(text("SELECT COUNT(*) FROM enrollments WHERE expires_at > NOW()"))
        active_enrollments = active_enrollments.scalar() or 0

        total_revenue = await db.execute(text("SELECT COALESCE(SUM(final_amount), 0) FROM payments WHERE status = 'completed'"))
        total_revenue = total_revenue.scalar() or 0

        pending_refunds = await db.execute(text("SELECT COALESCE(SUM(amount), 0) FROM refunds WHERE status = 'pending'"))
        pending_refunds = pending_refunds.scalar() or 0

        today_visitors = await db.execute(text("SELECT COUNT(DISTINCT ip_address) FROM user_activity WHERE CAST(created_at AS DATE) = CURRENT_DATE"))
        today_visitors = today_visitors.scalar() or 0

        today_views = await db.execute(text("SELECT COUNT(*) FROM user_activity WHERE CAST(created_at AS DATE) = CURRENT_DATE"))
        today_views = today_views.scalar() or 0

        today_revenue = await db.execute(text("SELECT COALESCE(SUM(final_amount), 0) FROM payments WHERE status = 'completed' AND CAST(paid_at AS DATE) = CURRENT_DATE"))
        today_revenue = today_revenue.scalar() or 0

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

    @staticmethod
    async def get_daily_stats(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DailyStats]:
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        result = await db.execute(
            text("""
                SELECT
                    CAST(ua.created_at AS DATE) as date,
                    COUNT(DISTINCT ua.ip_address) as visitors,
                    COUNT(*) as views,
                    COALESCE(SUM(p.final_amount), 0) as revenue,
                    COALESCE(COUNT(DISTINCT CASE WHEN CAST(e.created_at AS DATE) = CAST(ua.created_at AS DATE) THEN e.id END), 0) as enrollments,
                    COALESCE(COUNT(DISTINCT CASE WHEN CAST(u.created_at AS DATE) = CAST(ua.created_at AS DATE) THEN u.id END), 0) as new_users
                FROM user_activity ua
                LEFT JOIN payments p ON CAST(p.paid_at AS DATE) = CAST(ua.created_at AS DATE) AND p.status = 'completed'
                LEFT JOIN enrollments e ON CAST(e.created_at AS DATE) = CAST(ua.created_at AS DATE)
                LEFT JOIN users u ON CAST(u.created_at AS DATE) = CAST(ua.created_at AS DATE)
                WHERE CAST(ua.created_at AS DATE) BETWEEN :start_date AND :end_date
                GROUP BY CAST(ua.created_at AS DATE)
                ORDER BY CAST(ua.created_at AS DATE)
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

    @staticmethod
    async def get_revenue_stats(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[RevenueStats]:
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        result = await db.execute(
            text("""
                SELECT
                    CAST(p.paid_at AS DATE) as date,
                    COALESCE(SUM(CASE WHEN p.status = 'completed' THEN p.final_amount ELSE 0 END), 0) as revenue,
                    COUNT(CASE WHEN p.status = 'completed' THEN 1 END) as payment_count,
                    COALESCE(SUM(CASE WHEN r.status = 'completed' THEN r.amount ELSE 0 END), 0) as refund_amount,
                    COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as refund_count,
                    COALESCE(SUM(CASE WHEN p.status = 'completed' THEN p.final_amount ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN r.status = 'completed' THEN r.amount ELSE 0 END), 0) as net_revenue
                FROM payments p
                LEFT JOIN refunds r ON p.id = r.payment_id
                WHERE CAST(p.paid_at AS DATE) BETWEEN :start_date AND :end_date
                GROUP BY CAST(p.paid_at AS DATE)
                ORDER BY CAST(p.paid_at AS DATE)
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

    @staticmethod
    async def get_course_stats(
        db: AsyncSession,
        category_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CourseStats]:
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
        if category_type:
            query += " AND cat.type = :category_type"
            params["category_type"] = category_type.value if hasattr(category_type, 'value') else category_type
        if start_date:
            query += " AND CAST(e.created_at AS DATE) >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND CAST(e.created_at AS DATE) <= :end_date"
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

    @staticmethod
    async def get_category_stats(db: AsyncSession) -> List[CategoryStats]:
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