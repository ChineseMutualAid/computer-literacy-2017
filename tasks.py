# from pathlib import Path
import subprocess

from invoke import task
import requests

from app import app


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
            output_file = site_dir / 'css' / filename
        else:
            output_file = site_dir / 'js' / filename

        with output_file.open('w') as fp:
            fp.write(requests.get(url).text)


@task
def clean(ctx):
    if build_dir.exists():
        run('rm -rf build/*')


@task
def build(ctx):
    clean(ctx)
    for src in site_dir.rglob('*?.*'):
        name = src.name
        if not (name.startswith('_') or name.endswith('.md')):
            dest = build_dir / src.relative_to(site_dir)
            print(dest)
        # dest2 = copy_or_generate(src, dest)
        # if dest2:
        #     print(dest2)


@task
def publish(ctx):
    run('ghp-import -n -p {}'.format(build_dir))


def run(cmd):
    subprocess.call(cmd, shell=isinstance(cmd, str))
