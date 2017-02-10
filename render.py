import re
from pathlib import Path

from mako.lookup import TemplateLookup
import markdown2
from pyquery import PyQuery
from lxml import etree

from common import site_dir, site_root


lookup = TemplateLookup(directories=[str(site_dir)], strict_undefined=True)


def render_template(template_file, **kwargs):
    kwargs.update(
        ROOT=site_root,
        PATH=site_dir / template_file,
        render_markdown_file=render_markdown_file,
        render_slides=render_slides,
    )
    tmpl = lookup.get_template(str(template_file))
    return tmpl.render(**kwargs)


def render_markdown(text):
    text = replace_h1(text)
    html = markdown2.markdown(text)
    doc = PyQuery(html)
    for link in doc('a.external'):
        link.set('target', '_blank')

    return doc_to_string(doc)


def render_markdown_file(markdown_file):
    return render_markdown(markdown_file.read_text())


def render_slides(markdown_file):
    html = render_markdown_file(markdown_file)
    html = html[5:-6]       # get rid of enclosing div
    html = html.replace('<hr>', '</section>\n<section>')
    html = '<div class="slides"><section>\n{}\n</section></div>'.format(html)

    doc = PyQuery(html)

    # Make sure that images are scaled correctly inside slides. That only can
    # only happen if img elements are not children of p elements.
    for img in doc('img'):
        img.attrib['class'] = 'stretch'
        parent = img.getparent()
        if parent.tag == 'p':
            parent.getparent().replace(parent, img)

    return doc_to_string(doc)


def replace_h1(text):
    """
    Replace all h1 elements with h2 elements in the given markdown text
    (excluding the first h1). We do this because reveal.js renders h1 elements
    extremely large.

    """
    def gen():
        found_first = False
        for line in text.splitlines():
            if re.match(r'^# ', line):
                if found_first:
                    yield '#' + line
                    continue
                found_first = True

            yield line

    return '\n'.join(gen())


def doc_to_string(doc):
    return etree.tostring(doc[0], encoding='unicode', method='html')
