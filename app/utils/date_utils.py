import pytz
from datetime import timedelta


def to_utc_time(date_time):
    # TODO - this is hardcoded for now, need to get this from client and adjust accordingly
    local = pytz.timezone("US/Eastern")
    local_dt = local.localize(date_time, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def stays_to_cal_events(stays):
    stay_cal_events = []
    for stay in stays:
        for single_date in daterange(stay.start_date, stay.end_date):
            stay_cal_events.append({
                "title": 'Stay at ' + stay.name,
                "start": single_date.strftime("%Y-%m-%d"),
                "allDay": True
            })
    return stay_cal_events


def flights_to_cal_events(flights):
    flight_cal_events = []
    for flight in flights:
        flight_cal_events.append({
            "title": 'Flight ' + flight.code + ' departs',
            "start": flight.start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "color": "green"
        })
        flight_cal_events.append({
            "title": 'Flight ' + flight.code + ' arrives',
            "start": flight.end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "color": "green"
        })
    return flight_cal_events


# https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
# yield start_date through (end_date - 1 day)
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)