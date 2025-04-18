from flask import render_template
from sstrings import nothing_title, nothing_description, main_title, main_description,about_title, about_description

_app = None

def init_app(app):
    global _app
    _app = app

def render_404():
    with _app.app_context():
        notfound_render = render_template('404.html')
        return render_template('index.html', 
                             content=notfound_render, 
                             title=nothing_title, 
                             description=nothing_description)

def render_topic(topics):
    with _app.app_context():
        topics_render = render_template('topics_list.html', topics=topics)
        return render_template('index.html', 
                               content=topics_render, 
                               title=main_title, 
                               description=main_description)
    
def render_about():
    with _app.app_context():
        about_render = render_template('about.html')
        return render_template('index.html', 
                               content=about_render, 
                               title=about_title, 
                               description=about_description)