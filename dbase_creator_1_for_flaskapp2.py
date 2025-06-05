# Run this File once first
# It prepares the Database required for RestAPI

from main import app, db 

with app.app_context():
    db.create_all()