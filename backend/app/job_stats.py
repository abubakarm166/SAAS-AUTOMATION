from collections import Counter
from datetime import datetime, timedelta, timezone

from app.models import Job, JobStatus
from app.schemas import DailyCount, JobStatsOut


def address_count(job: Job) -> int:
    addrs = (job.inputs or {}).get("addresses") or []
    return len(addrs) if isinstance(addrs, list) else 0


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def summarize_jobs(jobs: list[Job], days: int = 14) -> JobStatsOut:
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_30 = now - timedelta(days=30)

    queued = running = completed = failed = canceled = 0
    addresses_total = 0
    addresses_completed = 0
    this_month = 0
    last_30_days = 0
    day_counts: Counter[str] = Counter()

    for job in jobs:
        status = job.status
        if status == JobStatus.queued:
            queued += 1
        elif status == JobStatus.running:
            running += 1
        elif status == JobStatus.completed:
            completed += 1
        elif status == JobStatus.failed:
            failed += 1
        elif status == JobStatus.canceled:
            canceled += 1

        n_addr = address_count(job)
        addresses_total += n_addr
        if status == JobStatus.completed:
            addresses_completed += n_addr

        created = _as_utc(job.created_at)
        if created >= month_start:
            this_month += 1
        if created >= last_30:
            last_30_days += 1
        day_counts[created.date().isoformat()] += 1

    decided = completed + failed
    success_rate = round((completed / decided) * 100, 1) if decided else 0.0

    daily: list[DailyCount] = []
    today = now.date()
    for i in range(days - 1, -1, -1):
        key = (today - timedelta(days=i)).isoformat()
        daily.append(DailyCount(date=key, count=day_counts.get(key, 0)))

    return JobStatsOut(
        total=len(jobs),
        queued=queued,
        running=running,
        completed=completed,
        failed=failed,
        canceled=canceled,
        addresses_total=addresses_total,
        addresses_completed=addresses_completed,
        success_rate=success_rate,
        this_month=this_month,
        last_30_days=last_30_days,
        daily=daily,
    )
