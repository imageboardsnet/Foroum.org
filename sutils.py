from datetime import datetime, timedelta

def convert_to_relative_time(last_activity_raw):
    """
    Convert a custom-formatted last activity timestamp (e.g., "15/04 10:41:52", "16:35:58",
    "2025-04-16T14:20:07.505Z", "4/15/2025", "5:44:28 PM", "9:27:47 AM", "9:43:19", "17/04 11:20:22") into a relative time format (e.g., "43s", "5m", "2h").
    """
    if not last_activity_raw:
        return "Unknown"

    try:
        now = datetime.now()
        
        # Clean up input
        last_activity_raw = last_activity_raw.strip()

        # Handle ISO 8601 format (e.g., "2025-04-16T14:20:07.505Z")
        if "T" in last_activity_raw and "Z" in last_activity_raw:
            last_activity_datetime = datetime.strptime(last_activity_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
        elif "/" in last_activity_raw:
            if len(last_activity_raw.strip().split()) == 1:
                # Handle date-only input (e.g., "4/15/2025", "4/16/2025")
                last_activity_datetime = datetime.strptime(last_activity_raw, "%m/%d/%Y")
            else:
                # Handle date and time input (e.g., "17/04 11:20:22", "17/04 09:42:58")
                try:
                    # Clean up any extra spaces in the date string
                    cleaned_date = ' '.join(part.strip() for part in last_activity_raw.split())
                    last_activity_datetime = datetime.strptime(cleaned_date, "%d/%m %H:%M:%S")
                    last_activity_datetime = last_activity_datetime.replace(year=now.year)
                except ValueError as e:
                    print(f"[DEBUG] Error parsing date/time: {e}")
                    raise
        elif len(last_activity_raw.split(":")) == 3:
            if "AM" in last_activity_raw or "PM" in last_activity_raw:
                # Handle time with AM/PM (e.g., "5:44:28 PM", "9:27:47 AM")
                last_activity_datetime = datetime.strptime(last_activity_raw, "%I:%M:%S %p").replace(
                    year=now.year, month=now.month, day=now.day
                )
            else:
                # Handle time-only input without AM/PM (e.g., "16:35:58", "9:43:19")
                last_activity_datetime = datetime.strptime(last_activity_raw, "%H:%M:%S").replace(
                    year=now.year, month=now.month, day=now.day
                )
        else:
            raise ValueError(f"Unrecognized date format: {last_activity_raw}")

        # If the parsed date is in the future, assume it belongs to the previous year
        if last_activity_datetime > now:
            last_activity_datetime = last_activity_datetime.replace(year=now.year - 1)

        delta = now - last_activity_datetime

        # Convert the time difference into a relative format
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds >= 60:
            return f"{delta.seconds // 60}m"
        else:
            return f"{delta.seconds}s"
    except ValueError as e:
        print(f"[DEBUG] Error in convert_to_relative_time: {e} for input: {last_activity_raw}")
        return "Unknown"