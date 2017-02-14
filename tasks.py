import subprocess
from pathlib import Path

from invoke import task

from common import site_dir, build_dir, site_root
from render import render_template
from app import app


@task
def serve(ctx):
    """
    Serve the site at localhost:8000 so that you can see the results of your
    changes without building.

    """
    app.run(port=8000, debug=True)


@task
def serve_build(ctx):
    """
    Serve the contents of the build/ directory.

    """
    run('cd {} && python -m http.server'.format(build_dir))


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
    import shutil

    clean(ctx)

    client = app.test_client()

    # Generate HTML files using Flask.
    for url in get_build_urls():
        dest = build_dir / Path(url).relative_to(site_root) / 'index.html'
        print(dest)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('wb') as fp:
            data = client.get(url).data
            fp.write(data)

    # Copy static files.
    for src in site_dir.rglob('*?.*'):
        dest = build_dir / src.relative_to(site_dir)
        print(dest)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(src), str(dest))


@task
def publish(ctx):
    """
    Publish the web site to GitHub Pages.

    """
    build(ctx)
    run('ghp-import -n -p {}'.format(build_dir))


def run(cmd):
    subprocess.call(cmd, shell=isinstance(cmd, str))


def get_build_urls():
    """
    Return a sequence of URLs to generate HTML files from.

    """
    yield site_root
    for i in range(1, 3):
        yield '{}lesson-{}/'.format(site_root, i)
        yield '{}lesson-{}/slides/'.format(site_root, i)
