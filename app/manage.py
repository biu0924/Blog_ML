from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, BlogPost

cli = FlaskGroup(create_app=create_app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(User(username="admin", email="admin@example.com", password="admin"))
    db.session.commit()

if __name__ == "__main__":
    cli()