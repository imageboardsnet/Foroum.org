from flask import Flask, jsonify, request, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from scraper import scrape_site, scrape_site_with_selenium
from db_manager import db, Topic
from sutils import epoch_to_relative_time
import os
import srender

# Move global variables outside
scheduler = None
scraped_data = {}

SITES_TO_SCRAPE = {
    'onche': {
        'url': 'https://onche.org/forum/1/blabla-general',
        'parser': 'parse_onche'
    },
    'avenoel': {
        'url': 'https://avenoel.org/forum',
        'parser': 'parse_avenoel'
    },
    'village': {
        'url': 'https://village.cx/village',
        'parser': 'parse_village'
    },
    'jeuxvideo': {
        'url': 'https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm',
        'parser': 'parse_jeuxvideo'
    },
    '2sucres': {
        'url': 'https://2sucres.org/forums/1/1',
        'parser': 'parse_2sucres'
    }
}

def get_all_scraped(raw=False):
    """
    Return at least 5 topics per forum/website, then fill the rest with the most replied topics.
    If `raw` is True, return the raw list of topics instead of a JSON response.
    """
    # Fetch all unique site keys
    site_keys = db.session.query(Topic.site_key).distinct().all()
    site_keys = [key[0] for key in site_keys]

    # Collect at least 5 topics per site
    topics = []
    for site_key in site_keys:
        site_topics = Topic.query.filter_by(site_key=site_key).order_by(Topic.timestamp.desc()).limit(5).all()
        topics.extend(site_topics)

    # Fill the remaining slots with the most replied topics
    remaining_slots = 60 - len(topics)
    if remaining_slots > 0:
        most_replied_topics = Topic.query.order_by(Topic.replies.desc()).limit(remaining_slots).all()
        topics.extend(most_replied_topics)

    # Remove duplicates (in case a topic is already included in the first step)
    unique_topics = {topic.id: topic for topic in topics}.values()

    # Format the result
    result = [
        {
            'site_key': topic.site_key,
            'title': topic.title,
            'topic_url': topic.topic_url,
            'username': topic.username,
            'replies': topic.replies,
            'last_activity': topic.last_activity,
            'timestamp': topic.timestamp
        }
        for topic in unique_topics
    ]
    
    # Sort the result by last_activity (converting time strings to seconds for comparison)
    result.sort(key=lambda x: x['last_activity'], reverse=True)

    # Convert last_activity to relative time
    for topic in result:
        topic['last_activity'] = epoch_to_relative_time(topic['last_activity'])

    if raw:
        return result  # Return raw data
    return jsonify(result)  # Return JSON response


def create_app():
    app = Flask(__name__)

    # Configure the database
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    os.makedirs(db_folder, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_folder, "scraped_data.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    srender.init_app(app)

    # Create the database tables
    with app.app_context():
        db.create_all()

    def scheduled_scrape():
        print("[INFO] Starting scheduled scrape...")
        with app.app_context():
            for site_key, site_config in SITES_TO_SCRAPE.items():
                if site_key in ['jeuxvideo', '2sucres','onche','avenoel']:  # Use Selenium for jeuxvideo and 2sucres
                    print(f"[INFO] Using Selenium for site: {site_key}")
                    scrape_site_with_selenium(site_key, site_config)
                else:
                    print(f"[INFO] Using scrap for site: {site_key}")
                    scrape_site(site_key, site_config)
        print("[INFO] Scraping completed.")

    # Initialize and start scheduler
    global scheduler
    if not scheduler:
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=scheduled_scrape, trigger='interval', minutes=1)
        scheduler.start()

    @app.route('/')
    def home():
        topics = get_all_scraped(raw=True)
        return srender.render_topic(topics)

    @app.route('/about')
    def about():
        return srender.render_about()

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/robots.txt')
    def robots():
        return send_from_directory(os.path.join(app.root_path, 'static'),'robots.txt', mimetype='text/plain')

    @app.errorhandler(404)
    def page_not_found(e):
        return srender.render_404()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
