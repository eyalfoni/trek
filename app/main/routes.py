from flask import render_template, flash, redirect, url_for, request
from app import db
from app.main.forms import AddTripForm, AddFlightForm, AddStayForm
from app.models import User, Trip, Flight, Stay, Event
from flask_login import current_user, login_required
from datetime import datetime
from app.main import bp


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
            trip_id=trip.id
        )
        db.session.add(flight)
        db.session.commit()
        flash('Your flight has been added!')
    if stay_form.validate_on_submit():
        stay = Stay(
            name=stay_form.name.data,
            user_id=current_user.id,
            trip_id=trip.id
        )
        db.session.add(stay)
        db.session.commit()
        flash('Your trip has been added!')

    flights = db.session.query(Flight).filter_by(trip_id=trip.id).all()
    stays = db.session.query(Stay).filter_by(trip_id=trip.id).all()
    events = db.session.query(Event).filter_by(trip_id=trip.id).all()
    all_trip_activities = []
    for activity in [flights, stays, events]:
        if activity:
            all_trip_activities.extend(activity)
    list.sort(all_trip_activities, key=lambda a: a.created_at, reverse=True)
    return render_template(
        'trip.html',
        trip=trip,
        flight_form=flight_form,
        stay_form=stay_form,
        recent_activity=all_trip_activities
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
