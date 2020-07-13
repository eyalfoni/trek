from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Length, Email
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


class AddCommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Comment')


class AddTripForm(FlaskForm):
    title = StringField('Trip Name', validators=[DataRequired()])
    submit = SubmitField('Add Trip')

    def validate_title(self, title):
        # TODO - add better validation
        if '-' in title.data:
            raise ValidationError('Please only include letters or numbers.')


class AddFlightForm(FlaskForm):
    flight_number = StringField('Flight Number', validators=[DataRequired()])
    submit = SubmitField('Add Flight')


class AddStayForm(FlaskForm):
    name = StringField('Hotel Name', validators=[DataRequired()])
    submit = SubmitField('Add Stay')

