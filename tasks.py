from pathlib import Path

from flask import Flask, send_from_directory
from invoke import task
from mako.lookup import TemplateLookup
import markdown2
import requests

app = Flask(__name__)
site = Path('static')
build_dir = Path('build')
lookup = TemplateLookup(directories=[str(site)], strict_undefined=True)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    filepath = site / path

    if filepath.is_dir():
        index_path = filepath / 'index.html'
        if index_path.exists():
            return render(index_path.relative_to(site))

    if filepath.exists():
        return send_from_directory(str(site), path)

    return 'Page not found', 404


@task
def serve(ctx):
    app.run(port=8000, debug=True)


DOWNLOAD_FILES = """
https://raw.githubusercontent.com/hakimel/reveal.js/master/css/reveal.css
https://raw.githubusercontent.com/hakimel/reveal.js/master/css/theme/black.css
https://raw.githubusercontent.com/hakimel/reveal.js/master/js/reveal.js
""".strip().splitlines()

@task
def download_dependencies(ctx):
    for url in DOWNLOAD_FILES:
        print(url)
        filename = url.rsplit('/', 1)[1]

        if url.endswith('.css'):
            output_file = site / 'css' / filename
        else:
            output_file = site / 'js' / filename

        with output_file.open('w') as fp:
            fp.write(requests.get(url).text)


@task
def build(ctx):
    pass


@task
def publish(ctx):
    pass



def render(template_file, **kwargs):
    kwargs.update(
        PATH=site / template_file,
        render_markdown_file=render_markdown_file,
    )
    tmpl = lookup.get_template(str(template_file))
    return tmpl.render(**kwargs)


def render_markdown_file(markdown_file):
    return markdown2.markdown(markdown_file.read_text())
