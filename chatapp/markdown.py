"""Markdown module"""

from re import compile as re_compile
from markdown import Markdown

# ATTR_LIST = compile(r"""\{[:]?[ ]?(#|\.){1,1}[^}]*\}|(?!\\)\{[A-Za-z]+=[^}]*\}""")
ATTR_LIST = re_compile(
    r"(?<!\\)\{(?:[:]?[ ]?(?:#|\.)[^}]*)\}|(?!\\)\{[A-Za-z]+=[^}]*\}"
)


def _eliminate_attr_list(markdown_content: str):
    """Eliminate attribute lists"""
    return ATTR_LIST.sub("", markdown_content)


def parse(text):
    """Parse a markdown string into html"""
    markdown = Markdown(
        extensions=[
            "pymdownx.extra",
            "codehilite",
            "pymdownx.smartsymbols",
            "pymdownx.magiclink",
            "pymdownx.striphtml",
            "pymdownx.emoji",
            "pymdownx.details",
            "pymdownx.betterem",
            "pymdownx.keys",
        ]
    )
    return markdown.convert(_eliminate_attr_list(text))
