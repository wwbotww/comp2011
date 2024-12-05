from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the user
    username = db.Column(db.String(50), nullable=False, unique=True)  # Username
    password_hash = db.Column(db.String(255), nullable=False)  # Hashed password

    # Relationship fields
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')  # Anime favorited by the user
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')  # User's rating records
    interests = db.relationship('UserInterest', backref='user', lazy='dynamic')  # User's interest weights for genres

    # Set password (encrypt before saving)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Intermediate table for anime and genres
anime_genres = db.Table(
    'anime_genres',
    db.Column('anime_id', db.Integer, db.ForeignKey('animes.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

# Anime table
class Anime(db.Model):
    __tablename__ = 'animes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    # Many-to-many relationship
    genres = db.relationship('Genre', secondary=anime_genres, backref='animes')

# Genre table
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

# User rating table
class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ID of the user who rated
    anime_id = db.Column(db.Integer, db.ForeignKey('animes.id'), nullable=False)  # ID of the rated anime
    score = db.Column(db.Integer, nullable=False)  # User rating (1-10 points)
    review = db.Column(db.Text, nullable=True)  # User review (optional)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())  # Rating timestamp

# User favorite table
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ID of the user who favorited
    anime_id = db.Column(db.Integer, db.ForeignKey('animes.id'), nullable=False)  # ID of the favorited anime
    added_date = db.Column(db.DateTime, default=db.func.current_timestamp())  # Timestamp of the favorite action

    # Define relationship with Anime
    anime = db.relationship('Anime', backref='favorites')

# User interest table
class UserInterest(db.Model):
    __tablename__ = 'user_interests'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User ID
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)  # Genre ID
    interested_weight = db.Column(db.Float, nullable=False, default=0.0)  # User's interest weight for the genre


def update_user_interests(user_id):
    """
    Update a user's interest weights for genres based on their favorited animes.
    """
    user_favorites = Favorite.query.filter_by(user_id=user_id).all()
    if not user_favorites:
        return

    genre_counts = {}
    for favorite in user_favorites:
        anime = Anime.query.get(favorite.anime_id)
        for genre in anime.genres:
            genre_counts[genre.id] = genre_counts.get(genre.id, 0) + 1

    for genre_id, count in genre_counts.items():
        interest = UserInterest.query.filter_by(user_id=user_id, genre_id=genre_id).first()
        if interest:
            interest.interested_weight += count
        else:
            new_interest = UserInterest(user_id=user_id, genre_id=genre_id, interested_weight=count)
            db.session.add(new_interest)

    db.session.commit()

def get_recommendations(user_id, limit=10):
    """
    Recommend animes a user might like based on their interest weights.
    """
    user_interests = UserInterest.query.filter_by(user_id=user_id).order_by(UserInterest.interested_weight.desc()).all()
    if not user_interests:
        return []

    recommended_animes = []
    favorite_anime_ids = [fav.anime_id for fav in Favorite.query.filter_by(user_id=user_id).all()]

    for interest in user_interests:
        genre = Genre.query.get(interest.genre_id)
        if genre:
            genre_animes = Anime.query.join(anime_genres).filter(
                anime_genres.c.genre_id == genre.id,
                ~Anime.id.in_(favorite_anime_ids)
            ).order_by(Anime.rating.desc()).limit(limit).all()

            recommended_animes.extend(genre_animes)

    return list({anime.id: anime for anime in recommended_animes}.values())[:limit]