from markdown import Markdown
from re import compile

#ATTR_LIST = compile(r"""\{[:]?[ ]?(#|\.){1,1}[^}]*\}|(?!\\)\{[A-Za-z]+=[^}]*\}""")
ATTR_LIST = compile(r"(?<!\\)\{(?:[:]?[ ]?(?:#|\.)[^}]*)\}|(?!\\)\{[A-Za-z]+=[^}]*\}")

def _eliminate_attr_list(markdown_content: str):
    return ATTR_LIST.sub('', markdown_content)

def parse(text):
    markdown = Markdown(extensions=[
        'pymdownx.extra', 'codehilite', 'pymdownx.smartsymbols', 'pymdownx.magiclink', 'pymdownx.striphtml',
        'pymdownx.emoji', 'pymdownx.details', 'pymdownx.betterem', 'pymdownx.keys'
    ])
    return markdown.convert(_eliminate_attr_list(text))
