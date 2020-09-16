import json
from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.auth.forms import RegistrationForm
from app.main.forms import AddTripForm, AddFlightForm, AddStayForm, AddSupplyItemForm, AddEventForm, AddPostForm, AddCommentForm
from app.models import User, Trip, Flight, Stay, SupplyItem, Event, Post, Comment
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
    all_trips = current_user.trips
    trips_result = []
    for trip in all_trips:
        flights = Flight.query.filter_by(trip_id=trip.id).all()
        stays = Stay.query.filter_by(trip_id=trip.id).all()
        events = Event.query.filter_by(trip_id=trip.id).all()
        trip_start_date = get_cal_start_date(flights, stays, events, iso_format=False)
        trip_obj = {
            'id': trip.id,
            'title': trip.title,
            'num_travelers': len(trip.travelers),
            'num_events': len(events),
            'num_stays': len(stays),
            'num_flights': len(flights),
            'start_date': trip_start_date.strftime('%B %Y')
        }
        trips_result.append(trip_obj)
    if form.validate_on_submit():
        trip = Trip(title=form.title.data)
        trip.travelers.append(current_user)
        db.session.add(trip)
        db.session.commit()
        flash('Your trip has been added!')
        return redirect(url_for('main.trip_view', id=trip.id))
    return render_template('trips.html', trips=current_user.trips, form=form, trips_result=trips_result)


@bp.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/trip/<id>', methods=['GET', 'POST'])
@login_required
def trip_view(id):
    flight_form = AddFlightForm()
    trip = Trip.query.filter_by(id=id).first_or_404()
    num_flights = Flight.query.filter_by(trip_id=trip.id).count()
    num_stays = Stay.query.filter_by(trip_id=trip.id).count()
    num_events = Event.query.filter_by(trip_id=trip.id).count()
    if current_user not in trip.travelers:
        return render_template('errors/404.html')

    if flight_form.validate_on_submit():
        flight = Flight(
            code=flight_form.flight_number.data,
            trip_id=trip.id,
            start_datetime=to_utc_time(flight_form.departure_time.data),
            end_datetime=to_utc_time(flight_form.arrival_time.data)
        )
        flight.users.append(current_user)
        db.session.add(flight)
        db.session.commit()
        flash('Your flight has been added!')
        return redirect(url_for('main.trip_view', id=id))
    return render_template(
        'itinerary.html',
        trip=trip,
        flight_form=flight_form,
        stay_form=AddStayForm(),
        event_form=AddEventForm(),
        travelers=trip.travelers,
        num_flights=num_flights,
        num_stays=num_stays,
        num_events=num_events,
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
        if current_user not in trip.travelers:
            trip.travelers.append(current_user)
            db.session.commit()
        return redirect(url_for('main.trip_view', id=id))
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


@bp.route('/event/<trip_id>')
@login_required
def get_event_details(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    event_id = request.args.get('id', type=int)
    event_type = request.args.get('type')
    if event_type == "flight":
        flight = Flight.query.filter_by(id=event_id).first_or_404()
        result = render_template('flight.html', flight=flight, trip=trip)
        return jsonify(result=result, departure=str(flight.start_datetime), arrival=str(flight.end_datetime))
    elif event_type == "stay":
        stay = Stay.query.filter_by(id=event_id).first_or_404()
        res = {
            'stay_name': stay.name,
            'check_in': stay.start_date,
            'check_out': stay.end_date,
        }
        keys = ['website', 'formatted_address', 'international_phone_number']
        if stay.location is not None:
            for key in keys:
                if key in stay.location:
                    res.update({key: stay.location[key]})
        result = render_template('stay.html', res=res, stay=stay, trip=trip)
        return jsonify(result=result, check_in=str(stay.start_date), check_out=str(stay.end_date))
    else:
        event = Event.query.filter_by(id=event_id).first_or_404()
        user = User.query.filter_by(id=event.user_id).first_or_404()
        res = {
            'event_name': event.name,
            'start_time': event.start_datetime,
            'end_time': event.end_datetime,
            'user_name': user.first_name + ' ' + user.last_name
        }
        keys = ['website', 'formatted_address', 'international_phone_number', 'name']
        if event.location is not None:
            for key in keys:
                if key in event.location:
                    res.update({key: event.location[key]})
        result = render_template('event.html', res=res, event=event)
        return jsonify(result=result, start_time=str(event.start_datetime), end_time=str(event.end_datetime))


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
    events = db.session.query(Event).filter_by(trip_id=trip.id)
    if event_type in ['restaurant', 'bar', 'museum']:
        events = events.filter_by(event_type=event_type)
    events = events.order_by(Event.start_datetime.asc()).all()
    start_date = get_cal_start_date(flights, stays, events)
    if travelers:
        travelers = travelers.split(',')
        traveler_ids = list(map(int, travelers))
        flights = [f for f in flights for u in f.users if u.id in traveler_ids]
        stays = [s for s in stays for u in s.users if u.id in traveler_ids]
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
    if resource_type == 'hotel':
        stay = Stay(
            name=location_json['name'],
            trip_id=trip_id,
            start_date=request.form['check_in_date'],
            end_date=request.form['check_out_date'],
            location=location_json
        )
        stay.users.append(current_user)
        db.session.add(stay)
        db.session.commit()
    elif resource_type == 'event':
        event_type = None
        if request.form['event_type'] != 'other':
            event_type = request.form['event_type']
        event = Event(
            name=request.form['name'],
            user_id=current_user.id,
            trip_id=trip_id,
            start_datetime=to_utc_time(datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')),
            end_datetime=to_utc_time(datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')),
            event_type=event_type,
            location=location_json
        )
        db.session.add(event)
        db.session.commit()
    return jsonify({})


@bp.route('/join/<trip_id>/<resource_type>/<resource_id>/<action>', methods=['GET'])
@login_required
def join(trip_id, resource_type, resource_id, action):
    # TODO - make the below into a single decorator
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    if current_user not in trip.travelers:
        return render_template('errors/404.html')
    if resource_type == 'flight':
        flight = db.session.query(Flight).filter_by(id=resource_id).first_or_404()
        if action == 'add':
            flight.users.append(current_user)
            db.session.commit()
            flash('Your flight has been added!')
        elif action == 'delete':
            flight.users.remove(current_user)
            db.session.commit()
            flash('Your flight has been removed!')
        return redirect(url_for('main.trip_view', id=trip_id))
    elif resource_type == 'stay':
        stay = db.session.query(Stay).filter_by(id=resource_id).first_or_404()
        if action == 'add':
            stay.users.append(current_user)
            db.session.commit()
            flash('Your hotel has been added!')
        elif action == 'delete':
            stay.users.remove(current_user)
            db.session.commit()
            flash('Your hotel has been removed!')
        return redirect(url_for('main.trip_view', id=trip_id))
    return jsonify({})


@bp.route('/<trip_id>/flight/<flight_id>', methods=["GET", "POST"])
@login_required
def flight_view(trip_id, flight_id):
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    flight = db.session.query(Flight).filter_by(id=flight_id).first_or_404()
    flight_form = AddFlightForm()
    flight_form.submit_flight.label = Label(field_id="submit_label", text="Save")
    if flight_form.validate_on_submit():
        flight.code = flight_form.flight_number.data,
        flight.start_datetime = to_utc_time(flight_form.departure_time.data),
        flight.end_datetime = to_utc_time(flight_form.arrival_time.data)
        db.session.commit()
        flash('Your flight has been updated!')
        return redirect(url_for('main.trip_view', id=trip_id))
    elif request.method == 'GET':
        flight_form.flight_number.data = flight.code
        flight_form.departure_time.data = flight.start_datetime
        flight_form.arrival_time.data = flight.end_datetime
    return render_template('flight_edit.html', flight=flight, trip=trip, flight_form=flight_form)


@bp.route('/<id>/posts/', methods=["GET", "POST"])
@login_required
def discussion_view(id):
    trip = Trip.query.filter_by(id=id).first_or_404()
    posts = Post.query.filter_by(trip_id=id)
    form = AddPostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.body.data,
            user_id=current_user.id,
            trip_id=trip.id,
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.discussion_view', id=id))
    return render_template('posts.html', trip=trip, posts=posts, form=form)


@bp.route('/comments/<trip_id>/<post_id>', methods=['GET', 'POST'])
@login_required
def comments_view(trip_id, post_id):
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()
    comments = post.comments
    form = AddCommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.comments_view', trip_id=trip_id, post_id=post_id))
    return render_template('comments.html', trip=trip, post=post, comments=comments, form=form)
