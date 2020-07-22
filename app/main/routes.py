from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.main.forms import AddTripForm, AddFlightForm, AddStayForm
from app.models import User, Trip, Flight, Stay, Event
from flask_login import current_user, login_required
from datetime import datetime
from app.main import bp
from app.utils.date_utils import to_utc_time, stays_to_cal_events, flights_to_cal_events


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/trips', methods=['GET', 'POST'])
@login_required
def index():
    form = AddTripForm()
    if form.validate_on_submit():
        trip = Trip(title=form.title.data)
        trip.travelers.append(current_user)
        db.session.add(trip)
        db.session.commit()
        flash('Your trip has been added!')
        return redirect(url_for('main.index'))
    return render_template('index.html', trips=current_user.trips, form=form)


@bp.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/trip/<id>', methods=['GET', 'POST'])
@login_required
def trip_view(id):
    flight_form = AddFlightForm()
    stay_form = AddStayForm()
    trip = Trip.query.filter_by(id=id).first_or_404()
    if current_user not in trip.travelers:
        return render_template('errors/404.html')

    if flight_form.validate_on_submit():
        flight = Flight(
            code=flight_form.flight_number.data,
            user_id=current_user.id,
            trip_id=trip.id,
            start_datetime=to_utc_time(flight_form.departure_time.data),
            end_datetime=to_utc_time(flight_form.arrival_time.data)
        )
        db.session.add(flight)
        db.session.commit()
        flash('Your flight has been added!')
        return redirect(url_for('main.trip_view', id=id))
    if stay_form.validate_on_submit():
        stay = Stay(
            name=stay_form.name.data,
            user_id=current_user.id,
            trip_id=trip.id,
            start_date=stay_form.check_in_date.data,
            end_date=stay_form.check_out_date.data
        )
        db.session.add(stay)
        db.session.commit()
        flash('Your stay has been added!')
        return redirect(url_for('main.trip_view', id=id))
    return render_template(
        'trip.html',
        trip=trip,
        flight_form=flight_form,
        stay_form=stay_form,
        travelers=trip.travelers
    )


@bp.route('/travelers/<id>')
@login_required
def travelers_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    if current_user not in trip.travelers:
        return render_template('errors/404.html')
    trip_url = request.url_root + 'invite/' + str(trip.id)
    return render_template(
        'travelers.html',
        trip=trip,
        travelers=trip.travelers,
        trip_url=trip_url
    )


@bp.route('/invite/<id>')
@login_required
def invite_landing_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    if current_user not in trip.travelers:
        trip.travelers.append(current_user)
        db.session.add(trip)
        db.session.commit()
    return redirect(url_for('main.trip_view', id=id))


@bp.route('/event')
@login_required
def get_event_details():
    event_id = request.args.get('id', type=int)
    event_type = request.args.get('type')
    if event_type == "flight":
        flight = Flight.query.filter_by(id=event_id).first_or_404()
        user = User.query.filter_by(id=flight.user_id).first_or_404()
        res = {
            'flight_code': flight.code,
            'departure': str(flight.start_datetime),
            'arrival': str(flight.end_datetime),
            'user_name': user.first_name + ' ' + user.last_name
        }
    else:
        stay = Stay.query.filter_by(id=event_id).first_or_404()
        user = User.query.filter_by(id=stay.user_id).first_or_404()
        res = {
            'stay_name': stay.name,
            'check_in': str(stay.start_date),
            'check_out': str(stay.end_date),
            'user_name': user.first_name + ' ' + user.last_name
        }
    return jsonify(result=res)


@bp.route('/events')
@login_required
def get_events_for_cal():
    # TODO - clean this up
    trip_id = request.args.get('trip_id', type=int)
    event_type = request.args.get('event_type')
    travelers = request.args.get('travelers')
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    flights = db.session.query(Flight).filter_by(trip_id=trip.id).all()
    stays = db.session.query(Stay).filter_by(trip_id=trip.id).all()
    if travelers:
        travelers = travelers.split(',')
        traveler_ids = list(map(int, travelers))
        flights = [f for f in flights if f.user_id in traveler_ids]
        stays = [s for s in stays if s.user_id in traveler_ids]
    # events = db.session.query(Event).filter_by(trip_id=trip.id).all()
    stays_as_cal_events = stays_to_cal_events(stays)
    flights_as_cal_events = flights_to_cal_events(flights)
    if event_type == 'all':
        cal_events = stays_as_cal_events + flights_as_cal_events
    elif event_type == 'flights':
        cal_events = flights_as_cal_events
    else:
        cal_events = stays_as_cal_events
    return jsonify(result=cal_events)


@bp.route('/discussion/<id>')
@login_required
def discussion_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    return render_template('discussion.html', trip=trip)
