"""
Database layer for tracking automation executions and metrics
Uses SQLAlchemy with async support
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, JSON
from datetime import datetime
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class AutomationExecution(Base):
    """Track automation rule executions"""

    __tablename__ = "automation_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(255), nullable=False, index=True)
    ticket_id = Column(String(50), nullable=False, index=True)
    trigger_event = Column(String(100))
    execution_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    details = Column(JSON)  # Stores additional context as JSON


class DuplicateCandidate(Base):
    """Track duplicate detection results"""

    __tablename__ = "duplicate_candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), nullable=False, index=True)
    candidate_ticket_id = Column(String(50), nullable=False, index=True)
    similarity_score = Column(Float)
    detection_method = Column(String(50))  # 'ai_embedding', 'string_match'
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)
    reviewer = Column(String(255))
    is_duplicate = Column(Boolean)


class SLATracking(Base):
    """Track SLA compliance for tickets"""

    __tablename__ = "sla_tracking"

    ticket_id = Column(String(50), primary_key=True)
    priority = Column(String(10))
    sla_start_time = Column(DateTime)
    sla_target_time = Column(DateTime)
    sla_status = Column(String(20))  # 'on_track', 'at_risk', 'breached'
    warning_sent = Column(Boolean, default=False)
    breach_escalation_sent = Column(Boolean, default=False)
    last_check = Column(DateTime, default=datetime.utcnow)


class TicketMetric(Base):
    """Store calculated metrics for tickets"""

    __tablename__ = "ticket_metrics"

    ticket_id = Column(String(50), primary_key=True)
    created_date = Column(DateTime)
    first_assigned_date = Column(DateTime)
    dev_start_date = Column(DateTime)
    pr_created_date = Column(DateTime)
    qa_start_date = Column(DateTime)
    closed_date = Column(DateTime)

    # Calculated fields (in hours)
    time_to_assign_hours = Column(Integer)
    time_to_dev_hours = Column(Integer)
    cycle_time_hours = Column(Integer)

    # Counts
    state_transition_count = Column(Integer, default=0)
    reassignment_count = Column(Integer, default=0)
    qa_failure_count = Column(Integer, default=0)

    # Categorization
    request_type = Column(String(50))
    priority = Column(String(10))
    epic_key = Column(String(50))
    team = Column(String(100))


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def log_automation_execution(
    rule_name: str,
    ticket_id: str,
    trigger_event: str,
    success: bool = True,
    error_message: str = None,
    execution_time_ms: int = None,
    details: dict = None
):
    """Log an automation rule execution"""
    try:
        async with async_session() as session:
            execution = AutomationExecution(
                rule_name=rule_name,
                ticket_id=ticket_id,
                trigger_event=trigger_event,
                success=success,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                details=details
            )
            session.add(execution)
            await session.commit()

    except Exception as e:
        logger.error(f"Failed to log automation execution: {e}")


async def log_duplicate_candidate(
    ticket_id: str,
    candidate_ticket_id: str,
    similarity_score: float,
    detection_method: str
):
    """Log a duplicate detection result"""
    try:
        async with async_session() as session:
            duplicate = DuplicateCandidate(
                ticket_id=ticket_id,
                candidate_ticket_id=candidate_ticket_id,
                similarity_score=similarity_score,
                detection_method=detection_method
            )
            session.add(duplicate)
            await session.commit()

    except Exception as e:
        logger.error(f"Failed to log duplicate candidate: {e}")


async def get_automation_stats(days: int = 30) -> dict:
    """Get automation execution statistics for the last N days"""
    from sqlalchemy import select, func
    from datetime import timedelta

    try:
        async with async_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Total executions
            result = await session.execute(
                select(func.count(AutomationExecution.id))
                .where(AutomationExecution.execution_timestamp >= cutoff_date)
            )
            total_executions = result.scalar()

            # Success rate
            result = await session.execute(
                select(func.count(AutomationExecution.id))
                .where(AutomationExecution.execution_timestamp >= cutoff_date)
                .where(AutomationExecution.success == True)
            )
            successful_executions = result.scalar()

            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0

            # Executions by rule
            result = await session.execute(
                select(
                    AutomationExecution.rule_name,
                    func.count(AutomationExecution.id).label('count')
                )
                .where(AutomationExecution.execution_timestamp >= cutoff_date)
                .group_by(AutomationExecution.rule_name)
            )

            by_rule = {row.rule_name: row.count for row in result}

            return {
                "period_days": days,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": total_executions - successful_executions,
                "success_rate": round(success_rate, 2),
                "executions_by_rule": by_rule
            }

    except Exception as e:
        logger.error(f"Failed to get automation stats: {e}")
        return {}
