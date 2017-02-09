from flask import Flask, send_from_directory

from common import site_dir, build_dir
from render import render_template


app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    filepath = site_dir / path

    if filepath.is_dir():
        index_path = filepath / 'index.html'
        if index_path.exists():
            return render_template(index_path.relative_to(site_dir))

    if filepath.exists():
        return send_from_directory(str(site_dir), path)

    return 'Page not found', 404
