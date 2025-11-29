import json
import os
import asyncio
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any

from ..service import DownloadService
from ..service.google_drive_service import GoogleDriveService
from ..model import DateRange

class AutomationController:
    def __init__(self, config_path: str = "automation_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.download_service = DownloadService()
        
        # Initialize Drive service if enabled
        self.drive_service = None
        if self.config.get("google_drive_enabled", False):
            self.drive_service = GoogleDriveService(
                self.config.get("service_account_file", "service_account.json")
            )

    def _load_config(self) -> Dict[str, Any]:
        """Load automation configuration"""
        if not os.path.exists(self.config_path):
            print(f"⚠️ Config file {self.config_path} not found. Using defaults.")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {str(e)}")
            return {}

    async def run_daily_download(self):
        """Execute the daily download routine"""
        # Set timezone to Peru (UTC-5)
        from datetime import timedelta, timezone
        peru_tz = timezone(timedelta(hours=-5))
        now_peru = datetime.now(peru_tz)
        
        print(f"🚀 Starting automated download routine at {now_peru}")
        
        reports = self.config.get("reports", [])
        if not reports:
            print("⚠️ No reports configured for automation")
            return

        today = now_peru.date()
        
        # Set date range to strictly today as requested
        date_range = DateRange(start=today, end=today)
        
        for report_config in reports:
            try:
                cartilla_id = report_config.get("cartilla_id")
                fundo_code = report_config.get("fundo_code")
                abbreviation = report_config.get("abbreviation", f"RPT_{cartilla_id}")
                local_path = report_config.get("local_path", "downloads")
                drive_folder_id = report_config.get("drive_folder_id")
                
                print(f"📥 Downloading report: {abbreviation} (Cartilla {cartilla_id}) for date {today}")
                
                # Download
                responses = await self.download_service.download_all_reports(
                    date_range=date_range,
                    cartillas=[cartilla_id],
                    fundo_code=fundo_code
                )
                
                if not responses:
                    print(f"⚠️ No data found for {abbreviation}")
                    continue
                
                # Process downloaded file
                response = responses[0] # We only requested one cartilla
                
                # Generate filename: [Abbr]_[Date]_[Time].xlsx
                # Using Peru time for the filename timestamp as well
                timestamp = now_peru.strftime("%Y%m%d_%H%M%S")
                new_filename = f"{abbreviation}_{timestamp}.xlsx"
                
                # Ensure directory exists
                save_dir = Path(local_path)
                save_dir.mkdir(parents=True, exist_ok=True)
                
                final_path = save_dir / new_filename
                
                # Save file
                with open(final_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Saved locally: {final_path}")
                
                # Upload to Drive if enabled
                if self.drive_service and drive_folder_id:
                    print(f"☁️ Uploading to Drive folder {drive_folder_id}...")
                    file_id = self.drive_service.upload_file(str(final_path), drive_folder_id)
                    if file_id:
                        print(f"✅ Uploaded to Drive. ID: {file_id}")
                    else:
                        print("❌ Drive upload failed")
                        
            except Exception as e:
                print(f"❌ Error processing report {report_config.get('abbreviation')}: {str(e)}")
        
        print(f"🏁 Automated routine completed at {datetime.now(peru_tz)}")
