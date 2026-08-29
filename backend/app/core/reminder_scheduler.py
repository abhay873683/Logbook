import asyncio
import logging

from app.core.database import SessionLocal

from app.services.reminder_service import (
    process_due_reminders,
)


logger = logging.getLogger(__name__)


REMINDER_SCHEDULER_INTERVAL_SECONDS = 30


_scheduler_task = None


async def reminder_scheduler_loop():
    while True:
        db = SessionLocal()

        try:
            result = (
                await process_due_reminders(
                    db,
                    user_id=None,
                    limit=100,
                )
            )

            if result["processed"] > 0:
                logger.info(
                    "Reminder scheduler processed %s reminders",
                    result["processed"],
                )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Reminder scheduler cycle failed"
            )

        finally:
            db.close()

        await asyncio.sleep(
            REMINDER_SCHEDULER_INTERVAL_SECONDS
        )


def start_reminder_scheduler():
    global _scheduler_task

    if (
        _scheduler_task is None
        or _scheduler_task.done()
    ):
        _scheduler_task = asyncio.create_task(
            reminder_scheduler_loop()
        )

    return _scheduler_task


async def stop_reminder_scheduler():
    global _scheduler_task

    if _scheduler_task is None:
        return

    if not _scheduler_task.done():
        _scheduler_task.cancel()

        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass

    _scheduler_task = None
