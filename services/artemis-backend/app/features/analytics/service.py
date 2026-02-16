"""Service layer for analytics feature."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from supabase import Client

from app.core.logging import get_logger
from app.features.analytics.repository import AnalyticsRepository
from app.features.analytics.schemas import (
    AnalyticsSummary,
    DailyPlanStats,
    PomodoroTrendPoint,
    PomodoroTrendResponse,
    ProductivityScore,
    TaskDistributionResponse,
    TaskQuadrantStats,
    TimeRange,
)

logger = get_logger(__name__)


class AnalyticsService:
    """Service layer for analytics operations."""

    def __init__(self, db: Client) -> None:
        """Initialize service with database client."""
        self.repository = AnalyticsRepository(db)

    def get_pomodoro_trends(
        self,
        period: TimeRange = TimeRange.WEEK,
    ) -> PomodoroTrendResponse:
        """Get pomodoro completion trends for the specified period."""
        logger.info("analytics.pomodoro_trends_requested", period=period.value)

        today = datetime.now(UTC).date()
        days = self._get_days_for_period(period)
        start_date = today - timedelta(days=days - 1)

        try:
            sessions = self.repository.get_pomodoro_sessions_in_range(start_date, today)

            # Group by date
            by_date: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "minutes": 0})

            for session in sessions:
                session_date = session.get("started_at", "")[:10]  # Extract YYYY-MM-DD
                by_date[session_date]["count"] += 1
                by_date[session_date]["minutes"] += session.get("duration_minutes", 25)

            # Build data points for all days in range
            data_points: list[PomodoroTrendPoint] = []
            current = start_date
            while current <= today:
                date_str = current.isoformat()
                stats = by_date.get(date_str, {"count": 0, "minutes": 0})
                data_points.append(
                    PomodoroTrendPoint(
                        date=date_str,
                        count=stats["count"],
                        total_minutes=stats["minutes"],
                    )
                )
                current += timedelta(days=1)

            total_pomodoros = sum(p.count for p in data_points)
            total_minutes = sum(p.total_minutes for p in data_points)
            avg_per_day = total_pomodoros / days if days > 0 else 0

            logger.info(
                "analytics.pomodoro_trends_computed",
                period=period.value,
                total=total_pomodoros,
                data_points=len(data_points),
            )

            return PomodoroTrendResponse(
                period=period,
                data_points=data_points,
                total_pomodoros=total_pomodoros,
                total_minutes=total_minutes,
                average_per_day=round(avg_per_day, 2),
            )

        except Exception as e:
            logger.error(
                "analytics.pomodoro_trends_failed",
                error=str(e),
                exc_info=True,
            )
            raise

    def get_task_distribution(self) -> TaskDistributionResponse:
        """Get task distribution by Eisenhower quadrant."""
        logger.info("analytics.task_distribution_requested")

        try:
            summary = self.repository.get_tasks_summary()
            quadrant_stats = summary["quadrant_stats"]

            quadrants = [
                TaskQuadrantStats(
                    quadrant=q,
                    total=stats["total"],
                    completed=stats["completed"],
                    completion_rate=(
                        round(stats["completed"] / stats["total"] * 100, 1)
                        if stats["total"] > 0
                        else 0.0
                    ),
                )
                for q, stats in quadrant_stats.items()
            ]

            total = summary["total"]
            completed = summary["completed"]
            overall_rate = round(completed / total * 100, 1) if total > 0 else 0.0

            logger.info(
                "analytics.task_distribution_computed",
                total=total,
                completed=completed,
            )

            return TaskDistributionResponse(
                quadrants=quadrants,
                total_tasks=total,
                total_completed=completed,
                overall_completion_rate=overall_rate,
            )

        except Exception as e:
            logger.error(
                "analytics.task_distribution_failed",
                error=str(e),
                exc_info=True,
            )
            raise

    def get_summary(self, period: TimeRange = TimeRange.WEEK) -> AnalyticsSummary:
        """Get comprehensive analytics summary."""
        logger.info("analytics.summary_requested", period=period.value)

        today = datetime.now(UTC).date()
        days = self._get_days_for_period(period)
        start_date = today - timedelta(days=days - 1)

        try:
            # Pomodoro stats
            sessions = self.repository.get_pomodoro_sessions_in_range(start_date, today)
            total_pomodoros = len(sessions)
            total_minutes = sum(s.get("duration_minutes", 25) for s in sessions)
            avg_pomodoros = total_pomodoros / days if days > 0 else 0

            # Task stats
            tasks = self.repository.get_tasks_in_range(start_date, today)
            tasks_created = len(tasks)
            tasks_completed = sum(1 for t in tasks if t.get("status") == "completed")
            task_completion_rate = (
                round(tasks_completed / tasks_created * 100, 1) if tasks_created > 0 else 0.0
            )

            # Daily plan stats
            daily_plan_stats = self._compute_daily_plan_stats(start_date, today)

            # Productivity score
            productivity_score = self._compute_productivity_score(
                avg_pomodoros_per_day=avg_pomodoros,
                task_completion_rate=task_completion_rate,
                plan_completion_rate=daily_plan_stats.average_completion_rate,
                period=period,
                start_date=start_date,
            )

            logger.info(
                "analytics.summary_computed",
                period=period.value,
                pomodoros=total_pomodoros,
                tasks=tasks_created,
                score=productivity_score.score,
            )

            return AnalyticsSummary(
                period=period,
                start_date=start_date,
                end_date=today,
                total_pomodoros=total_pomodoros,
                total_focus_minutes=total_minutes,
                average_pomodoros_per_day=round(avg_pomodoros, 2),
                tasks_created=tasks_created,
                tasks_completed=tasks_completed,
                task_completion_rate=task_completion_rate,
                daily_plan_stats=daily_plan_stats,
                productivity_score=productivity_score,
            )

        except Exception as e:
            logger.error(
                "analytics.summary_failed",
                error=str(e),
                exc_info=True,
            )
            raise

    def _get_days_for_period(self, period: TimeRange) -> int:
        """Get number of days for time range."""
        return {
            TimeRange.DAY: 1,
            TimeRange.WEEK: 7,
            TimeRange.MONTH: 30,
        }.get(period, 7)

    def _compute_daily_plan_stats(
        self,
        start_date: date,
        end_date: date,
    ) -> DailyPlanStats:
        """Compute daily plan statistics."""
        plans = self.repository.get_daily_plans_in_range(start_date, end_date)

        if not plans:
            return DailyPlanStats(
                total_plans=0,
                plans_completed=0,
                average_completion_rate=0.0,
                tasks_planned=0,
                tasks_completed=0,
            )

        # Collect all task IDs from plans
        all_task_ids: list[str] = []
        for plan in plans:
            if plan.get("major_task_id"):
                all_task_ids.append(plan["major_task_id"])
            all_task_ids.extend(plan.get("medium_task_ids") or [])
            all_task_ids.extend(plan.get("small_task_ids") or [])

        # Get task completion status
        tasks_data = self.repository.get_task_by_ids(all_task_ids)
        completed_ids = {t["id"] for t in tasks_data if t.get("status") == "completed"}

        # Calculate per-plan completion
        completion_rates: list[float] = []
        total_planned = 0
        total_completed = 0

        for plan in plans:
            plan_task_ids: list[str] = []
            if plan.get("major_task_id"):
                plan_task_ids.append(plan["major_task_id"])
            plan_task_ids.extend(plan.get("medium_task_ids") or [])
            plan_task_ids.extend(plan.get("small_task_ids") or [])

            plan_total = len(plan_task_ids)
            plan_completed = sum(1 for tid in plan_task_ids if tid in completed_ids)

            total_planned += plan_total
            total_completed += plan_completed

            if plan_total > 0:
                completion_rates.append(plan_completed / plan_total * 100)

        avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0.0
        plans_completed = sum(1 for r in completion_rates if r >= 100)

        return DailyPlanStats(
            total_plans=len(plans),
            plans_completed=plans_completed,
            average_completion_rate=round(avg_completion, 1),
            tasks_planned=total_planned,
            tasks_completed=total_completed,
        )

    def _compute_productivity_score(
        self,
        avg_pomodoros_per_day: float,
        task_completion_rate: float,
        plan_completion_rate: float,
        period: TimeRange,
        start_date: date,
    ) -> ProductivityScore:
        """Compute productivity score (0-100) based on multiple factors."""
        # Target: 4 pomodoros per day is considered good
        pomodoro_score = min(avg_pomodoros_per_day / 4 * 100, 100)

        # Task completion contributes directly
        task_score = task_completion_rate

        # Plan completion contributes
        plan_score = plan_completion_rate

        # Weighted average
        weights = {
            "pomodoro": 0.4,
            "task_completion": 0.35,
            "plan_completion": 0.25,
        }

        score = (
            pomodoro_score * weights["pomodoro"]
            + task_score * weights["task_completion"]
            + plan_score * weights["plan_completion"]
        )

        # Compute trend vs previous period
        trend, trend_pct = self._compute_trend(period, start_date)

        return ProductivityScore(
            score=round(score),
            components={
                "focus_sessions": round(pomodoro_score, 1),
                "task_completion": round(task_score, 1),
                "plan_adherence": round(plan_score, 1),
            },
            trend=trend,
            trend_percentage=trend_pct,
        )

    def _compute_trend(
        self,
        _period: TimeRange,
        _current_start: date,
    ) -> tuple[str, float]:
        """Compute trend compared to previous period."""
        # For simplicity, return stable for now
        # A full implementation would compare with previous period
        return ("stable", 0.0)
