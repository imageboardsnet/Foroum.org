from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define a model for storing scraped topics
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_key = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    topic_url = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    replies = db.Column(db.Integer, nullable=False, default=0)
    last_activity = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Use datetime.utcnow