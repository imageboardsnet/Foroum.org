from datetime import datetime, timedelta

def convert_to_epoch(last_activity_raw):
    """
    Convert a custom-formatted timestamp into Unix epoch timestamp (seconds since January 1, 1970).
    Returns -1 if the conversion fails.
    """
    if not last_activity_raw:
        return -1

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

        # Convert to Unix timestamp (seconds since epoch)
        return int(last_activity_datetime.timestamp())

    except ValueError as e:
        print(f"[DEBUG] Error in convert_to_epoch: {e} for input: {last_activity_raw}")
        return -1

def epoch_to_relative_time(epoch_timestamp):
    """
    Convert a Unix epoch timestamp to relative time format (e.g., "43s", "5m", "2h", "2d").
    Returns "Unknown" if the conversion fails.
    
    Args:
        epoch_timestamp (int): Unix epoch timestamp in seconds
    
    Returns:
        str: Relative time format (e.g., "43s", "5m", "2h", "2d") or "Unknown" if conversion fails
    """

    try:
        # Convert epoch to datetime
        timestamp_datetime = datetime.fromtimestamp(epoch_timestamp)
        now = datetime.now()
        
        # Calculate time difference
        if timestamp_datetime > now:
            # Handle future timestamps
            delta = timestamp_datetime - now
        else:
            # Handle past timestamps
            delta = now - timestamp_datetime

        # Convert the time difference into a relative format
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds >= 60:
            return f"{delta.seconds // 60}m"
        else:
            return f"{delta.seconds}s"
    except (ValueError, TypeError, OSError) as e:
        print(f"[DEBUG] Error in epoch_to_relative_time: {e} for input: {epoch_timestamp}")
        return "Unknown"

def relative_time_to_epoch(relative_time):
    """
    Convert a relative time format (e.g., "43s", "5m", "2h", "2d") to Unix epoch timestamp.
    Returns -1 if the conversion fails.
    
    Args:
        relative_time (str): Time in relative format (e.g., "43s", "5m", "2h", "2d")
    
    Returns:
        int: Unix epoch timestamp in seconds or -1 if conversion fails
    """
    if not isinstance(relative_time, str) or not relative_time:
        return -1

    try:
        # Remove any whitespace
        relative_time = relative_time.strip()
        
        # Extract the number and unit
        number = int(relative_time[:-1])
        unit = relative_time[-1].lower()
        
        # Calculate seconds based on unit
        seconds = {
            's': 1,
            'm': 60,
            'h': 3600,
            'j': 86400
        }
        
        if unit not in seconds:
            raise ValueError(f"Invalid time unit: {unit}")
            
        # Calculate the datetime by subtracting the relative time from now
        now = datetime.now()
        delta = timedelta(seconds=number * seconds[unit])
        target_datetime = now - delta
        
        # Convert to Unix timestamp
        return int(target_datetime.timestamp())

    except (ValueError, TypeError, IndexError) as e:
        print(f"[DEBUG] Error in relative_time_to_epoch: {e} for input: {relative_time}")
        return -1


