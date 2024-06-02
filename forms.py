from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, ValidationError, URL, Regexp
from enums import States, Genres

facebook_url_regex = r'(?:(?:http|https):\/\/)?(?:www.)?(facebook|fb).com?'

def validate_phone(form, field):
    if len(field.data) < 10:
        raise ValidationError('Invalid phone number.')



class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=States.items()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[validate_phone])
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # DONE implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genres.items()
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[
            URL(),
            Regexp(
                facebook_url_regex,
                0,
                message="Invalid facebook URL format.")])
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=States.items()
    )
    phone = StringField(
        # DONE implement validation logic for phone
        'phone', validators=[validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=Genres.items()
    )
    facebook_link = StringField(
        # DONE implement enum restriction (I guess this for validate facebook
        # url)
        'facebook_link', validators=[URL(), Regexp(facebook_url_regex, 0, message="Invalid facebook URL format.")]
    )

    website_link = StringField(
        'website_link'
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description'
    )
