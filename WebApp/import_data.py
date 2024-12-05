import csv
from datetime import datetime
from app import app, db
from app.models import Anime, Genre

def import_anime_data(csv_file):
    """
    Import anime and genre data from a CSV file into the database.
    """
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Cache mapping of genre names to Genre instances
        genres_cache = {}

        for row in reader:
            # Process genres
            genres = row['genre'].split(', ') if row['genre'] else []
            genre_instances = []
            for genre_name in genres:
                if genre_name not in genres_cache:
                    # Check if the genre already exists in the database
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                        db.session.flush()  # Commit to generate ID
                    genres_cache[genre_name] = genre
                genre_instances.append(genres_cache[genre_name])

            # Process anime
            try:
                aired = eval(row['aired'])  # Convert string to dictionary
                release_date = datetime.strptime(aired['from'], '%Y-%m-%d').date() if aired.get('from') else None
            except:
                release_date = None

            anime = Anime(
                id=int(row['anime_id']),
                title=row['title'] or row['title_english'] or row['title_japanese'],
                description=row.get('background', '')[:500],
                release_date=release_date,
                rating=float(row['score']) if row['score'] else None,
                image_url=row['image_url']
            )
            anime.genres = genre_instances  # Associate genres
            db.session.add(anime)

        db.session.commit()
        print("Data import completed!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
        import_anime_data('data/anime_data.csv')  # Update with the path to your data file