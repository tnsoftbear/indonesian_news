from datetime import datetime

saved_date_iso = "2024a02-03T00:21:00"
try:
    saved_date = datetime.fromisoformat(saved_date_iso)
except:
    saved_date = None
print(saved_date)