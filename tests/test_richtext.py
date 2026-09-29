"""Emphasis in prose: the smallest markup that can go wrong.

Eleven lessons wrote ``*this*`` and got the asterisks printed, because every
prose label in the application was plain text. The conversion that fixed it is
four lines long, which is the point -- the failure modes of a markup converter
all come from doing more than the content needs.
"""

from __future__ import annotations

import pytest

from odesuite_app.richtext import emphasise, plain


def test_emphasis_becomes_italics():
    assert emphasise("the *shapes* of F") == "the <i>shapes</i> of F"


def test_two_marked_phrases_in_one_paragraph():
    assert emphasise("*this* and *that*") == "<i>this</i> and <i>that</i>"


def test_a_single_word_between_markers_is_enough():
    assert emphasise("*a*") == "<i>a</i>"


def test_a_convolution_star_is_not_emphasis():
    """``f * g and g * f`` appears in the Laplace unit, and italicising the
    middle of it would be the worst possible reading. Both markers stand
    against a space, and that is what the rule turns on."""
    text = "the same either way: f * g and g * f"
    assert emphasise(text) == text
    assert plain(text) == text


def test_a_lone_marker_is_left_where_it_is():
    """An unbalanced marker prints, and that is better than swallowing the
    rest of the paragraph into italics."""
    assert emphasise("2 * 3 = 6") == "2 * 3 = 6"
    assert emphasise("a *stray marker") == "a *stray marker"


@pytest.mark.parametrize("text", [
    "the equilibrium (x*, y*) moves",
    "Linearise x' = 2*x - x*y at the origin",
    "x* = 2/3 and y* = 1/3",
])
def test_an_asterisk_glued_to_a_symbol_is_mathematics(text):
    """An equilibrium x* or a product 2*x is not a marker: both used to come
    out with the text between two of them set in italics."""
    assert emphasise(text) == text
    assert plain(text) == text


def test_emphasis_still_sits_against_punctuation():
    assert emphasise("(*not* this)") == "(<i>not</i> this)"
    assert emphasise("is *exactly*, and") == "is <i>exactly</i>, and"


def test_markup_in_the_content_cannot_become_markup_on_the_screen():
    assert emphasise("a < b and c > d") == "a &lt; b and c &gt; d"
    assert emphasise("<i>hand-written</i>") == "&lt;i&gt;hand-written&lt;/i&gt;"
    assert emphasise("Navier & Stokes") == "Navier &amp; Stokes"


def test_escaping_happens_before_the_italics_are_inserted():
    """Otherwise the tags this function adds would themselves be escaped."""
    assert emphasise("*a < b*") == "<i>a &lt; b</i>"


def test_the_plain_form_keeps_the_words_and_drops_the_markers():
    assert plain("the *shapes* of F") == "the shapes of F"
    assert plain("no markers here") == "no markers here"


def test_nothing_at_all_survives_unchanged():
    for text in ("", " ", "\n"):
        assert emphasise(text) == text
        assert plain(text) == text
