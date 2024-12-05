from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import Anime, Genre, User, Favorite, update_user_interests, get_recommendations
from app.forms import RegistrationForm, LoginForm, FavoriteForm, SearchForm


@app.route('/search_anime', methods=['POST'])
def search_anime():
    form = SearchForm()
    favorite_form = FavoriteForm()
    search_results = []

    if form.validate_on_submit():
        query = form.query.data
        search_results = Anime.query.filter(Anime.title.ilike(f'%{query}%')).all()

    favorite_anime_ids = []
    if current_user.is_authenticated:
        favorite_anime_ids = [favorite.anime_id for favorite in current_user.favorites]

    return render_template(
        "search_results.html",
        search_results=search_results,
        favorite_form=favorite_form,
        favorite_anime_ids=favorite_anime_ids
    )

@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    anime_id = request.form.get('anime_id')
    if not anime_id:
        flash('Anime ID is missing!', 'danger')
        return redirect(url_for('home'))

    anime = Anime.query.get(anime_id)
    if not anime:
        flash('Anime not found!', 'danger')
        return redirect(url_for('home'))

    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, anime_id=anime_id).first()
    if existing_favorite:
        flash('You have already favorited this anime.', 'info')
        return redirect(url_for('home'))

    new_favorite = Favorite(user_id=current_user.id, anime_id=anime_id)
    db.session.add(new_favorite)
    db.session.commit()

    # update favorite
    update_user_interests(current_user.id)

    flash(f'{anime.title} has been added to your favorites!', 'success')
    return redirect(request.referrer or url_for('home'))

@app.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    anime_id = request.form.get('anime_id')
    if not anime_id:
        flash('Anime ID is missing!', 'danger')
        return redirect(url_for('home'))

    favorite = Favorite.query.filter_by(user_id=current_user.id, anime_id=anime_id).first()
    if not favorite:
        flash('Favorite not found!', 'danger')
        return redirect(url_for('home'))

    db.session.delete(favorite)
    db.session.commit()

    flash('The anime has been removed from your favorites.', 'success')
    return redirect(request.referrer or url_for('home'))

@app.route("/")
def home():
    sections = []

    # You might like
    if current_user.is_authenticated:
        recommended_animes = get_recommendations(current_user.id)
        if recommended_animes:
            sections.append({
                "title": "You might like",
                "background_image": recommended_animes[0].image_url if recommended_animes[0].image_url else "/static/images/placeholder.jpg",
                "animes": recommended_animes
            })

    # Top 10 rated animes
    top10_animes = Anime.query.order_by(Anime.rating.desc()).limit(10).all()
    if top10_animes:
        sections.append({
            "title": "Top 10",
            "background_image": top10_animes[0].image_url if top10_animes[0].image_url else "/static/images/placeholder.jpg",
            "animes": top10_animes
        })

    # Genres
    genres = ["Romance", "School", "Adventure", "Sci-Fi"]
    for genre_name in genres:
        genre = Genre.query.filter_by(name=genre_name).first()
        if genre and genre.animes:
            sections.append({
                "title": genre_name,
                "background_image": genre.animes[0].image_url if genre.animes[0].image_url else "/static/images/placeholder.jpg",
                "animes": genre.animes[:12]  # Limit to first 12 animes
            })

    favorite_form = FavoriteForm()

    search_form = SearchForm()

    favorite_anime_ids = []
    if current_user.is_authenticated:
        favorite_anime_ids = [favorite.anime_id for favorite in current_user.favorites]

    return render_template(
        "home.html",
        sections=sections,
        favorite_form=favorite_form,
        search_form=search_form,
        favorite_anime_ids=favorite_anime_ids
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        new_user = User(
            username=form.username.data
        )
        # Set encrypted password
        new_user.set_password(form.password.data)

        # Save to database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))  # Assuming login view exists
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # check if usr exists
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Username does not exist. Please check your username or register.', 'danger')
        elif not user.check_password(form.password.data):
            flash('Incorrect password. Please try again.', 'danger')
        else:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    favorites = user.favorites.order_by(Favorite.added_date.desc()).all()
    form = FavoriteForm()
    return render_template('user_profile.html', user=user, favorites=favorites, form=form)
