from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable
import logging
from datetime import timedelta, timezone

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.WARNING)

class SchedulerService:
    def __init__(self):
        # Configure scheduler with Peru timezone default if possible, 
        # but CronTrigger handles timezone specifically
        self.scheduler = AsyncIOScheduler()
        self.jobs = []
        # Peru Timezone (UTC-5)
        self.peru_tz = timezone(timedelta(hours=-5))

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("🕒 Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Scheduler stopped")

    def add_daily_job(self, func: Callable, time_str: str, id: str = "daily_download"):
        """
        Add a daily job at a specific time
        
        Args:
            func: Async function to execute
            time_str: Time in "HH:MM" format (24h)
            id: Unique job ID
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            
            # Remove existing job if it exists
            if self.scheduler.get_job(id):
                self.scheduler.remove_job(id)
            
            # Use fixed offset for Peru (UTC-5) to avoid pytz dependency if not present
            trigger = CronTrigger(
                hour=hour, 
                minute=minute, 
                timezone=self.peru_tz
            )
            
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=id,
                name=f"Daily download at {time_str}"
            )
            print(f"📅 Job '{id}' scheduled for {time_str} daily (Peru Time)")
            
        except ValueError:
            print(f"❌ Invalid time format: {time_str}. Use HH:MM")
        except Exception as e:
            print(f"❌ Error scheduling job: {str(e)}")

