import json
from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.auth.forms import RegistrationForm
from app.main.forms import AddTripForm, AddFlightForm, AddStayForm, AddSupplyItemForm, AddEventForm
from app.models import User, Trip, Flight, Stay, SupplyItem, Event
from flask_login import current_user, login_required, login_user
from datetime import datetime
from app.main import bp
from app.utils.date_utils import to_utc_time, stays_to_cal_events, flights_to_cal_events, events_to_cal_events, get_cal_start_date
from wtforms.fields import Label


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
    event_form = AddEventForm()
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
    if event_form.validate_on_submit():
        event = Event(
            name=event_form.name.data,
            user_id=current_user.id,
            trip_id=trip.id,
            start_datetime=to_utc_time(event_form.start_time.data),
            end_datetime=to_utc_time(event_form.end_time.data)
        )
        db.session.add(event)
        db.session.commit()
        flash('Your event has been added!')
        return redirect(url_for('main.trip_view', id=id))
    return render_template(
        'trip.html',
        trip=trip,
        flight_form=flight_form,
        stay_form=stay_form,
        event_form=event_form,
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


@bp.route('/invite/<id>', methods=['GET', 'POST'])
def invite_landing_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    form.submit.label = Label(field_id="submit_label", text="Join the trip!")
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data.title(),
            last_name=form.last_name.data.title()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        trip.travelers.append(user)
        db.session.add(trip)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.trip_view', id=id))
    return render_template('invite.html', trip=trip, form=form)


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
    elif event_type == "stay":
        stay = Stay.query.filter_by(id=event_id).first_or_404()
        user = User.query.filter_by(id=stay.user_id).first_or_404()
        res = {
            'stay_name': stay.name,
            'check_in': str(stay.start_date),
            'check_out': str(stay.end_date),
            'user_name': user.first_name + ' ' + user.last_name
        }
        keys = ['website', 'formatted_address', 'international_phone_number']
        if stay.location is not None:
            for key in keys:
                if key in stay.location:
                    res.update({key: stay.location[key]})
        res = render_template('stay.html', res=res, stay=stay)
        return res
    else:
        event = Event.query.filter_by(id=event_id).first_or_404()
        user = User.query.filter_by(id=event.user_id).first_or_404()
        res = {
            'event_name': event.name,
            'start_time': str(event.start_datetime),
            'end_time': str(event.end_datetime),
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
    flights = db.session.query(Flight).filter_by(trip_id=trip.id).order_by(Flight.start_datetime.asc()).all()
    stays = db.session.query(Stay).filter_by(trip_id=trip.id).order_by(Stay.start_date.asc()).all()
    events = db.session.query(Event).filter_by(trip_id=trip.id).order_by(Event.start_datetime.asc()).all()
    start_date = get_cal_start_date(flights, stays, events)
    if travelers:
        travelers = travelers.split(',')
        traveler_ids = list(map(int, travelers))
        flights = [f for f in flights if f.user_id in traveler_ids]
        stays = [s for s in stays if s.user_id in traveler_ids]
        events = [e for e in events if e.user_id in traveler_ids]
    stays_as_cal_events = stays_to_cal_events(stays)
    flights_as_cal_events = flights_to_cal_events(flights)
    events_as_cal_events = events_to_cal_events(events)
    if event_type == 'all':
        cal_events = stays_as_cal_events + flights_as_cal_events + events_as_cal_events
    elif event_type == 'flights':
        cal_events = flights_as_cal_events
    elif event_type == 'stays':
        cal_events = stays_as_cal_events
    else:
        cal_events = events_as_cal_events
    return jsonify(result=dict(events=cal_events, start_date=start_date))


@bp.route('/discussion/<id>')
@login_required
def discussion_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    return render_template('discussion.html', trip=trip)


@bp.route('/supplies_view/<id>', methods=['GET', 'POST'])
@login_required
def supplies_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    form = AddSupplyItemForm()
    form.dri.choices = [(t.id, t.first_name+' '+t.last_name) for t in trip.travelers]
    if form.validate_on_submit():
        supply_item = SupplyItem(
            name=form.name.data,
            user_id=form.dri.data,
            trip_id=trip.id,
            cost=form.cost.data,
            cost_estimate=form.cost_estimate.data,
            notes=form.notes.data
        )
        db.session.add(supply_item)
        db.session.commit()
        flash('Your supplies has been added!')
        return redirect(url_for('main.supplies_view', id=id))
    supplies = SupplyItem.query.filter_by(trip_id=id).all()
    return render_template('supplies.html', trip=trip, supplies=supplies, form=form)


@bp.route('/supplies/<trip_id>/<supply_id>', methods=['GET', 'POST'])
@login_required
def supply_view(trip_id, supply_id):
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    form = AddSupplyItemForm()
    form.dri.choices = [(t.id, t.first_name+' '+t.last_name) for t in trip.travelers]
    form.submit.label = Label(field_id="submit_label", text="Save")
    supply_item = SupplyItem.query.filter_by(id=supply_id).first_or_404()
    if form.validate_on_submit():
        supply_item.name = form.name.data
        supply_item.user_id = form.dri.data
        supply_item.cost = form.cost.data
        supply_item.cost_estimate = form.cost_estimate.data
        supply_item.notes = form.notes.data
        db.session.commit()
        flash('Your supplies has been saved!')
        return redirect(url_for('main.supplies_view', id=trip_id))
    elif request.method == 'GET':
        form.name.data = supply_item.name
        form.dri.data = supply_item.user_id
        form.cost.data = supply_item.cost
        form.cost_estimate.data = supply_item.cost_estimate
        form.notes.data = supply_item.notes
    return render_template('supply.html', form=form, trip=trip, supply=supply_item)


@bp.route('/complete_supplies/<trip_id>/<supply_id>')
@login_required
def complete_supplies(trip_id, supply_id):
    supplies = SupplyItem.query.filter_by(id=supply_id).first_or_404()
    supplies.is_done = True
    db.session.commit()
    flash('Supplies added!')
    return redirect(url_for('main.supplies_view', id=trip_id))


@bp.route('/add/<resource_type>/<trip_id>', methods=['POST'])
@login_required
def add_resource(resource_type, trip_id):
    location_json = json.loads(request.form['place'])
    stay = Stay(
        name=location_json['name'],
        user_id=current_user.id,
        trip_id=trip_id,
        start_date=request.form['check_in_date'],
        end_date=request.form['check_out_date'],
        location=location_json
    )
    db.session.add(stay)
    db.session.commit()
    return jsonify({})
