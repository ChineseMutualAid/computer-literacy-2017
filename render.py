import re
from pathlib import Path

from mako.lookup import TemplateLookup
import markdown2
from pyquery import PyQuery
from lxml import etree

from common import site_dir, template_dir, site_root


lookup = TemplateLookup(
    directories=[str(template_dir)],
    strict_undefined=True,
)


def render_template(template_file, **kwargs):
    template_path = template_dir / template_file
    kwargs.update(
        ROOT=site_root,
        PATH=template_path,
    )
    tmpl = lookup.get_template(str(template_file))
    return tmpl.render(**kwargs)


def get_doc(num):
    md_file = site_dir / ('lesson-%d/slides.md' % num)
    return MarkdownDocument(md_file)


class MarkdownDocument:
    def __init__(self, md_file):
        self.title = None

        # Use the first h1 as the title. All subsequent h1's are turned into
        # h2's.
        def gen():
            for line in md_file.read_text().splitlines():
                if re.match(r'^# ', line):
                    if self.title is None:
                        self.title = line[1:].strip()
                        yield line
                    else:
                        yield '#' + line        # turn h1 into h2
                else:
                    yield line

        self.text = '\n'.join(gen())

    @property
    def html(self):
        return markdown2.markdown(self.text)

    def get_lesson_html(self):
        doc = PyQuery(self.html)
        for link in doc('a.external'):
            link.set('target', '_blank')

        for img in doc('img'):
            img.set('class', 'img-responsive')

        return doc_to_string(doc)

    def get_slides_html(self):
        html = self.html.replace('<hr />', '</section>\n<section>')
        html = '<div class="slides">\n<section>\n{}\n</section>\n</div>'.format(html)

        doc = PyQuery(html)

        # All local images must have their src attributes reference files in the
        # parent directory.
        for img in doc('img'):
            src = img.get('src')
            if not src.startswith('http'):
                img.set('src', '../' + src)

        # All links in slideshow open a new tab.
        for link in doc('a'):
            link.set('target', '_blank')

        # Make sure that images are scaled correctly inside slides. That can
        # only happen if img elements are not children of p elements.
        for img in doc('img'):
            img.attrib['class'] = 'stretch'
            parent = img.getparent()
            if parent.tag == 'p':
                parent.getparent().replace(parent, img)

        return doc_to_string(doc)


def doc_to_string(doc):
    """
    Serialize the given PyQuery object to an HTML string.

    """
    return etree.tostring(doc[0], encoding='unicode', method='html')
