#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from collections import OrderedDict

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy='joined', cascade='all, delete')

    def num_upcoming_shows(self):
      num_upcoming_shows = 0
      if self.shows:
        for show in self.shows:
          if show.start_time > datetime.now():
            num_upcoming_shows += 1

      return num_upcoming_shows
    
    def parse_shows(self):
      self.past_shows = []
      self.upcoming_shows = []
      if self.shows:
        now =  datetime.now()
        for show in self.shows:
          if show.start_time <= now:
            self.past_shows.append({
              'start_time': str(show.start_time),
              'artist_id': show.Artist.id,
              'artist_name': show.Artist.name,
              'artist_image_link': show.Artist.image_link,
            })
          else:
            self.upcoming_shows.append({
              'start_time': str(show.start_time),
              'artist_id': show.Artist.id,
              'artist_name': show.Artist.name,
              'artist_image_link': show.Artist.image_link,
            })
      self.past_shows_count = len(self.past_shows)
      self.upcoming_shows_count = len(self.upcoming_shows)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy='joined', cascade='all, delete')

    def num_upcoming_shows(self):
      num_upcoming_shows = 0
      if self.shows:
        for show in self.shows:
          if show.start_time > datetime.now():
            num_upcoming_shows += 1

      return num_upcoming_shows
    
    def parse_shows(self):
      self.past_shows = []
      self.upcoming_shows = []
      if self.shows:
        now =  datetime.now()
        for show in self.shows:
          if show.start_time <= now:
            self.past_shows.append({
              'start_time': str(show.start_time),
              'venue_id': show.Venue.id,
              'venue_name': show.Venue.name,
              'venue_image_link': show.Venue.image_link,
            })
          else:
            self.upcoming_shows.append({
              'start_time': str(show.start_time),
              'venue_id': show.Venue.id,
              'venue_name': show.Venue.name,
              'venue_image_link': show.Venue.image_link,
            })
      self.past_shows_count = len(self.past_shows)
      self.upcoming_shows_count = len(self.upcoming_shows)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  # DONE: num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  d = OrderedDict()
  for venue in venues:
    d.setdefault((venue.city, venue.state), list()).append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue.num_upcoming_shows()
    })
  data = [{'city': k[0], 'state': k[1], 'venues': v} for k, v in d.items()]   

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(venues),
    "data": [{
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue.num_upcoming_shows(),
    } for venue in venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get_or_404(venue_id)
  data.genres = json.loads(data.genres) if data.genres else []
  data.parse_shows()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(meta={'csrf': False})
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/new_venue.html', form=form)

  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = json.dumps(form.genres.data),
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully listed!')
  except SQLAlchemyError:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  result = {
    'status': 200,
    'message': ''
  }
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    result['message'] = 'Venue was successfully deleted!'
  except Exception as e:
    db.session.rollback()
    result['status'] = 500
    result['message'] = 'An error occurred. Venue could not be deleted.'
  finally: 
    db.session.close()

  return result

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  data = [{'id': artist.id, 'name': artist.name} for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(artists),
    "data": [{
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': artist.num_upcoming_shows(),
    } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id
  data = Artist.query.get_or_404(artist_id)
  data.genres = json.loads(data.genres) if data.genres else []
  data.parse_shows()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  artist.genres = json.loads(artist.genres) if artist.genres else []
  form = ArtistForm(obj=artist)
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(meta={'csrf': False})

  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  try:
    form.populate_obj(artist)
    artist.genres = json.dumps(form.genres.data)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!')
  except SQLAlchemyError:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not updated.')
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  venue.genres = json.loads(venue.genres) if venue.genres else []
  form = VenueForm(obj=venue)
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(meta={'csrf': False})

  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  try:
    form.populate_obj(venue)
    venue.genres = json.dumps(form.genres.data)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except SQLAlchemyError:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not updated.')
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(meta={'csrf': False})
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/new_artist.html', form=form)
  
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = json.dumps(form.genres.data),
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully listed!')
  except SQLAlchemyError:
    # DONE: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    return render_template('forms/new_artist.html', form=form)
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  shows = db.session.query(Show, Venue, Artist).join(Venue).join(Artist)
  data = [{
    "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.start_time)
  } for show, venue, artist in shows]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  form = ShowForm(meta={'csrf': False})
  
  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/new_show.html', form=form)
  
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except SQLAlchemyError:
    # DONE: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    return render_template('forms/new_show.html', form=form)
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
