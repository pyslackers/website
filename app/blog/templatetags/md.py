import markdown
from django import template
from markdown.extensions.codehilite import CodeHiliteExtension


register = template.Library()


@register.filter(is_safe=True)
def markdown_to_html(text: str) -> str:
    """Convert the input text from markdown to html"""
    return markdown.markdown(text, extensions=[
        CodeHiliteExtension(linenums=True),
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
    ])
