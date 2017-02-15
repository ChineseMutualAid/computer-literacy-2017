from flask import Flask, redirect, send_from_directory, url_for

from common import site_dir, build_dir, site_root
from render import render_template, get_doc


app = Flask(__name__)


@app.route('/')
def redirect_to_site_root():
    return redirect(site_root)


@app.route(site_root)
def home():
    return render_template('index.html')


@app.route(site_root + 'lesson-<int:num>/')
def lesson(num):
    return render_template('lesson.html', doc=get_doc(num))


@app.route(site_root + 'lesson-<int:num>/slides/')
def slides(num):
    return render_template('slides.html', doc=get_doc(num))


@app.route(site_root + '<path:path>')
def static_files(path):
    filepath = site_dir / path
    if filepath.exists():
        return send_from_directory(str(site_dir), path)
    else:
        return 'Page not found', 404


def get_build_urls():
    """
    Return a sequence of URLs to generate HTML files from.

    """
    with app.test_request_context():
        yield url_for('home')
        for i in range(1, 5):
            yield url_for('lesson', num=i)
            yield url_for('slides', num=i)
