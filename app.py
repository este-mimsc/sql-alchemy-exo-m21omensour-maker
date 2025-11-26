"""Minimal Flask application setup for the SQLAlchemy assignment."""
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from extensions import db, migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):

    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    import models
    from models import User, Post

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to the Flask + SQLAlchemy assignment"})

    # ---------------- USERS ----------------
    @app.route("/users", methods=["GET", "POST"])
    def users():

        # GET  liste des utilisateurs
        if request.method == "GET":
            users = User.query.all()
            data = [
                {
                    "id": user.id,
                    "username": user.username
                }
                for user in users
            ]
            return jsonify(data)

        # POST  créer un utilisateur
        if request.method == "POST":
            body = request.get_json()

            if not body or "username" not in body:
                return jsonify({"error": "username is required"}), 400

            new_user = User(username=body["username"])
            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                "message": "User created successfully",
                "id": new_user.id,
                "username": new_user.username
            }), 201

    # ---------------- POSTS ----------------
    @app.route("/posts", methods=["GET", "POST"])
    def posts():

        # GET  liste des posts avec leur auteur
        if request.method == "GET":
            posts = Post.query.all()
            data = [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "user": {
                        "id": post.user.id,
                        "username": post.user.username
                    }
                }
                for post in posts
            ]
            return jsonify(data)

        # POST  créer un post
        if request.method == "POST":
            body = request.get_json()

            required_fields = ["title", "content", "user_id"]
            if not body or not all(field in body for field in required_fields):
                return jsonify({"error": "title, content and user_id are required"}), 400

            user = User.query.get(body["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 404

            new_post = Post(
                title=body["title"],
                content=body["content"],
                user_id=body["user_id"]
            )

            db.session.add(new_post)
            db.session.commit()

            return jsonify({
                "message": "Post created successfully",
                "id": new_post.id
            }), 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


