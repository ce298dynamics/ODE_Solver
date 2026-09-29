"""Emphasis in prose, for labels that are otherwise plain text.

The lessons write emphasis the way anyone writes it in a plain-text file, with
asterisks around the emphasised words. Set as plain text those asterisks are
printed, which reads as a typo in the content -- and eleven lessons were doing
exactly that before this existed.

The conversion is deliberately tiny. It is not Markdown: there is no bold, no
code, no links, and no nesting, because none of those appear in the content and
each one is a way for a stray character to turn into markup. The one rule that
matters is the *convolution* rule below.
"""

from __future__ import annotations

import re

__all__ = ["emphasise", "plain"]

#: A pair of asterisks each hugging the text between them. Both the opening and
#: the closing marker must sit against a non-space character, which is what
#: keeps ``f * g and g * f`` -- a convolution, in the Laplace unit -- from
#: being read as emphasis running across the middle of a sentence. Nothing
#: inside may be another asterisk, so an unbalanced marker is simply left
#: alone rather than swallowing the rest of the paragraph.
#:
#: Nor may a marker touch a letter or digit on its outer side. An asterisk
#: glued to a word is not punctuation but mathematics: the equilibrium
#: ``(x*, y*)`` of the nonlinear unit, or ``{a}*x - x*y`` in a drill prompt,
#: each of which used to come out with the middle set in italics.
_EMPHASIS = re.compile(r"(?<![\w*])\*(\S|\S[^*]*\S)\*(?![\w*])")


def _escaped(text: str) -> str:
    """`text` with the three characters Qt would read as markup neutralised.

    Done before emphasis is inserted, so content can never introduce tags --
    and after it there is nothing left to escape, since the tags are ours.
    """
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def emphasise(text: str) -> str:
    """`text` as rich text, with ``*emphasis*`` set in italics."""
    return _EMPHASIS.sub(r"<i>\1</i>", _escaped(text))


def plain(text: str) -> str:
    """`text` with the emphasis markers removed and nothing else changed.

    For anywhere the destination is not rich text -- an accessible
    description, a tooltip, a report written to a file.
    """
    return _EMPHASIS.sub(r"\1", text)
