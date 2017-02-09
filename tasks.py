import subprocess
from invoke import task

from common import site_dir, build_dir
from render import render_template


@task
def serve(ctx):
    from app import app
    app.run(port=8000, debug=True)


@task
def serve_build(ctx):
    run('cd {} && python -m http.server'.format(build_dir))


DOWNLOAD_FILES = """
https://raw.githubusercontent.com/hakimel/reveal.js/master/css/reveal.css
https://raw.githubusercontent.com/hakimel/reveal.js/master/css/theme/black.css
https://raw.githubusercontent.com/hakimel/reveal.js/master/js/reveal.js
""".strip().splitlines()

@task
def download_dependencies(ctx):
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
            copy_or_generate(src, dest)


@task
def publish(ctx):
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
