from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()

def setup_db(app):
    app.config.from_object('config')
    db.app = app
    migrate = Migrate(app, db)
    db.init_app(app)
    return db


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