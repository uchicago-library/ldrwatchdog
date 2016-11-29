from datetime import datetime, timedelta
from datetime import timedelta
from datetime import datetime
from sys import stderr

def convert_iso_to_datetime(iso_string):
    date_format = "%Y-%m-%dT%H:%M:%S"
    try:
        return datetime.strptime(iso_string.split('.')[0], date_format)
    except ValueError:
        return None

def get_date_after_x_days(date_string, minusdays):
    date_object = convert_iso_to_datetime(date_string)
    difference = date_object - timedelta(days=minusdays)
    return difference

def is_an_event_past_due(recorded_date_string, numdays):
    due_date_after_current = get_date_after_x_days(datetime.now().isoformat(), numdays)
    recorded_date_object = convert_iso_to_datetime(recorded_date_string)
    return recorded_date_object < due_date_after_current
