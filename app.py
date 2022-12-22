# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

db = SQLAlchemy(app)


#-------------------------------models---------------------------------


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


#-------------------------------schemas---------------------------------


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


#-------------------------------movies_CBVs---------------------------------


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)

        director_id = request.args.get('director_id')
        if director_id is not None:
            movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if genre_id is not None:
            movies = all_movies.filter(Movie.genre_id == genre_id)

        if director_id is None and genre_id is None:
            return movies_schema.dump(all_movies.all()), 200
        else:
            return movies_schema.dump(movies.all()), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Movie created", 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid : int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid: int):
        updated_rows = db.session.query(Movie).filter(Movie.id == mid).update(request.json)

        if updated_rows != 1:
            return 'Not updated', 400

        db.session.commit()
        return "", 204

    def delete(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "Movie not found", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


#-------------------------------directors_CBVs---------------------------------

@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors.all()), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Director created", 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did : int):
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid: int):
        updated_rows = db.session.query(Director).filter(Director.id == mid).update(request.json)

        if updated_rows != 1:
            return 'Not updated', 400

        db.session.commit()
        return "", 204

    def delete(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "Director not found", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204



#-------------------------------genres_CBVs---------------------------------

@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres.all()), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "Genre created", 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid : int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, gid: int):
        updated_rows = db.session.query(Genre).filter(Genre.id == gid).update(request.json)

        if updated_rows != 1:
            return 'Not updated', 400

        db.session.commit()
        return "", 204

    def delete(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return "Genre not found", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
