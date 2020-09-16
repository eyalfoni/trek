from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, IntegerField, SelectField, DecimalField
from wtforms.fields.html5 import DateField, DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, Length, Optional
from app.models import User


ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class AddListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # description = StringField('Title', validators=[DataRequired()])
    image = FileField('Attach a picture', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_image(self, image):
        if image.data.filename == '':
            return
        if not self.allowed_file(image.data.filename):
            raise ValidationError("Image file extension must be: {}".format(', '.join(ALLOWED_EXTENSIONS)))

    def validate_price(self, price):
        if not 0 < price.data < 10000000:
            raise ValidationError("Price must be between $0 and $10,000,000")

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class AddTripForm(FlaskForm):
    title = StringField('Create new trip', validators=[DataRequired()], render_kw={"placeholder": "Trip name"})
    submit = SubmitField('Add Trip', render_kw={"class": "add_trip_submit"})

    def validate_title(self, title):
        # TODO - add better validation
        if '-' in title.data:
            raise ValidationError('Please only include letters or numbers.')


class AddFlightForm(FlaskForm):
    flight_number = StringField('Flight Number', validators=[DataRequired()])
    departure_time = DateTimeLocalField('Departure Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    arrival_time = DateTimeLocalField('Arrival Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    submit_flight = SubmitField('Add Flight')

    def validate_departure_time(self, departure_time):
        if departure_time.data >= self.arrival_time.data:
            raise ValidationError('Arrival time must be after departure time.')


class AddStayForm(FlaskForm):
    name = StringField('Hotel Name', id='pac-input', render_kw={"placeholder": "Enter hotel name", "class": "form-control"}, validators=[DataRequired()])
    check_in_date = DateField('Check In', render_kw={"class": "form-control"}, validators=[DataRequired()])
    check_out_date = DateField('Check Out', render_kw={"class": "form-control"}, validators=[DataRequired()])
    submit_stay = SubmitField('Add Stay', render_kw={"class": "btn btn-default"})

    def validate_check_in_date(self, check_in_date):
        if check_in_date.data >= self.check_out_date.data:
            raise ValidationError('Check out date must be after check in date.')


class AddSupplyItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = DecimalField('Price', validators=[Optional()], default=0.0)
    cost_estimate = DecimalField('Estimated Price', validators=[Optional()], default=0.0)
    dri = SelectField('Lead Person', coerce=int)
    notes = TextAreaField('Notes')
    submit = SubmitField('Add Supplies')


event_type_choices = [('other', 'Other'), ('restaurant', 'Restaurant'), ('bar', 'Bar'), ('museum', 'Museum')]


class AddEventForm(FlaskForm):
    name = StringField('Event Name', render_kw={"placeholder": "Enter event name", "class": "form-control"}, validators=[DataRequired()])
    location = StringField('Location', id='event-input', render_kw={"placeholder": "Enter location", "class": "form-control"}, validators=[Optional()])
    event_type = SelectField('Type', render_kw={"class": "form-control"}, choices=event_type_choices, validators=[DataRequired()])
    start_time = DateTimeLocalField('Start Time', render_kw={"class": "form-control"}, validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_time = DateTimeLocalField('End Time', render_kw={"class": "form-control"}, validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    submit_event = SubmitField('Add Activity', render_kw={"class": "btn btn-default"})

    def validate_departure_time(self, departure_time):
        if departure_time.data >= self.arrival_time.data:
            raise ValidationError('End time must be after start time.')


class AddPostForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Add Post')


class AddCommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Add Comment')
