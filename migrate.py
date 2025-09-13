from app import create_app, db, migrate
from flask.cli import FlaskGroup

# Create app
app = create_app()
migrate.init_app(app, db)

# Create CLI group
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
