from django import template
import markdown as markdown_lib
from markdown.util import etree
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension

register = template.Library()

@register.filter
def markdown(text):
    return markdown_lib.markdown(text, extensions=['sane_lists', 'nl2br'], safe_mode='escape')

class LeafLinePattern(Pattern):
    def handleMatch(self, m):
        el = etree.Element('hr')
        el.set('class', 'leaf-line')
        return el

class SeasoningMarkdownExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('leaflinepattern', LeafLinePattern('-o-'), '_end')
        

@register.filter
def markdown_safe(text):
    return markdown_lib.markdown(text, extensions=['sane_lists', 'nl2br', SeasoningMarkdownExtension()])