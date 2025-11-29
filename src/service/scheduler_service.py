from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.WARNING)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = []

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
            
            trigger = CronTrigger(hour=hour, minute=minute)
            
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=id,
                name=f"Daily download at {time_str}"
            )
            print(f"📅 Job '{id}' scheduled for {time_str} daily")
            
        except ValueError:
            print(f"❌ Invalid time format: {time_str}. Use HH:MM")
        except Exception as e:
            print(f"❌ Error scheduling job: {str(e)}")
