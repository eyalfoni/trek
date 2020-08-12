import pytz
from datetime import timedelta, date


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
                "allDay": True,
                "type": "stay",
                "event_id": str(stay.id),
                "color": "#116d9e"
            })
    return stay_cal_events


def flights_to_cal_events(flights):
    flight_cal_events = []
    for flight in flights:
        flight_cal_events.append({
            "title": 'Flight ' + flight.code + ' departs',
            "start": flight.start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "color": "#1f8c5d",
            "type": "flight",
            "event_id": str(flight.id)
        })
        flight_cal_events.append({
            "title": 'Flight ' + flight.code + ' arrives',
            "start": flight.end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "color": "#1f8c5d",
            "type": "flight",
            "event_id": str(flight.id)
        })
    return flight_cal_events


def events_to_cal_events(events):
    event_cal_events = []
    for event in events:
        dct = {
            "title": event.name,
            "start": event.start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": event.end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "color": "#11119e",
            "type": "activity",
            "event_id": str(event.id)
        }
        if event.event_type == 'restaurant':
            dct.update({"color": "#1da0c4"})
        elif event.event_type == 'bar':
            dct.update({"color": "#088523"})
        elif event.event_type == 'museum':
            dct.update({"color": "#d19406"})
        event_cal_events.append(dct)
    return event_cal_events


# https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
# yield start_date through (end_date - 1 day)
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_cal_start_date(flights, stays, events):
    default_start_date = date.today()
    if flights and flights[0].start_datetime.date() < default_start_date:
        default_start_date = flights[0].start_datetime.date()
    if stays and stays[0].start_date < default_start_date:
        default_start_date = stays[0].start_date
    if events and events[0].start_datetime.date() < default_start_date:
        default_start_date = events[0].start_datetime.date()
    return default_start_date.isoformat()
