import subprocess
from invoke import task

from common import site_dir, build_dir
from render import render_template


@task
def serve(ctx):
    """
    Serve the site at localhost:8000 so that you can see the results of your
    changes without building.

    """
    from app import app
    app.run(port=8000, debug=True)


@task
def serve_build(ctx):
    """
    Serve the contents of the build/ directory.

    """
    run('cd {} && python -m http.server'.format(build_dir))


DOWNLOAD_FILES = """
https://raw.githubusercontent.com/hakimel/reveal.js/master/css/reveal.css
https://raw.githubusercontent.com/hakimel/reveal.js/master/css/theme/black.css
https://raw.githubusercontent.com/hakimel/reveal.js/master/js/reveal.js
""".strip().splitlines()

@task
def download_dependencies(ctx):
    """
    Download the source files needed for reveal.js. You only need to do this if
    you want to upgrade to a newer version of reveal.js

    """
    import requests

    for url in DOWNLOAD_FILES:
        print(url)
        filename = url.rsplit('/', 1)[1]

        if url.endswith('.css'):
            output_file = site_dir / 'css' / filename
        else:
            output_file = site_dir / 'js' / filename

        with output_file.open('w') as fp:
            fp.write(requests.get(url).text)


@task
def clean(ctx):
    """
    Delete all files inside the build directory.

    """
    if build_dir.exists():
        run('rm -rf build/*')


@task
def build(ctx):
    """
    Build the static files for the web site and put them inside the build
    directory.

    """
    clean(ctx)
    for src in site_dir.rglob('*?.*'):
        name = src.name
        if not (name.startswith('_') or name.endswith('.md')):
            dest = build_dir / src.relative_to(site_dir)
            print(dest)
            copy_or_generate(src, dest)


@task
def publish(ctx):
    """
    Publish the web site to GitHub Pages.

    """
    build(ctx)
    run('ghp-import -n -p {}'.format(build_dir))


def run(cmd):
    subprocess.call(cmd, shell=isinstance(cmd, str))


def copy_or_generate(src, dest):
    import shutil

    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)

    if src.suffix == '.html':
        with dest.open('w') as fp:
            html = render_template(src.relative_to(site_dir))
            fp.write(html)
    else:
        shutil.copy(str(src), str(dest))

    return dest
