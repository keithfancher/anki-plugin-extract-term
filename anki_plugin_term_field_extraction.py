# -*- coding: utf-8 -*-

# A simple plugin that attempts to extract the actual term being defined from a
# Jalup-style definition field. In other words, if the meaning is defined as:
#
#    食べる：to eat!
#
# ...then this will extract the 「食べる」portion and plug it into a separate
# field, here called "Term". This makes it much easier to reason about these
# cards programatically, find dupes, etc.

from anki.hooks import addHook
from aqt import mw             # main window object (mw) from aqt
from aqt.utils import showInfo # the "show info" tool from utils.py
from aqt.qt import *           # all of the Qt GUI library

from HTMLParser import HTMLParser
import re

TERM_FIELD_NAME = u"Term"
EXPRESSION_FIELD_NAME = u"Expression"
MEANING_FIELD_NAME = u"Meaning"
JP_SPACE = u"　"
COLON_REGEX = ur":|：" # Note the unicode and regex combo prefix

# Stolen from: https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
# Need to remove HTML elements from input to properly extract the term from
# definitions, or the matching gets very confused...
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return u"".join(self.fed)

def stripTags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def addTermFields(nids):
    mw.checkpoint("Add Term Fields")
    mw.progress.start()

    updatedCards = 0
    for nid in nids:
        note = mw.col.getNote(nid)
        if addTermField(note):
            updatedCards = updatedCards + 1

    mw.progress.finish()
    mw.reset()
    showInfo("Updated cards: %d" % updatedCards)

def addTermField(note):
    # 1. First, try Meaning field, looking for one of the colons
    # 2. If it doesn't exist, grab from Expression field
    # 3. If term is already populated... forget it?

# TODO: Re-enable the "don't overwrite" bit, probably
#    if note[TERM_FIELD_NAME]:
        # Do nothing if Term field is already set, at least for now
#        return False

    meaning = note[MEANING_FIELD_NAME]
    term = extractTerm(meaning)

    if not term:
        # Fall back on Expression
        term = note[EXPRESSION_FIELD_NAME]

    if term:
        note[TERM_FIELD_NAME] = term
        note.flush()
        return True

    return False

def extractTerm(f):
    # Some cards that were boned due to hidden HTML tags, for reference:
    # 駄目人間、理想、警察
    field = stripTags(f)
    split = re.split(COLON_REGEX, field, re.UNICODE)
    if len(split) > 1:
        # split returns a single item -- the input -- if the target search is
        # not found. So we need to see a return array with at least 2 items in
        # it to know we got our search (the thing before the first colon).
        return betterStrip(split[0])
    else:
        return None

def betterStrip(s):
    # Strip can't deal with weird JP spaces, I guess?
    # TODO: this won't work if the term has JP spaces *inside* it...
    # (can probably use unicode-aware regex to match/replace here)
    return s.replace(JP_SPACE, u"").strip()

def executeTests():
    assert extractTerm(u"no colon here") == None
    assert extractTerm(u"both colons： here, oh jee:z") == u"both colons"
    assert extractTerm(u"器：物を入れる物。") == u"器"
    assert extractTerm(u"連なる: たくさん") == u"連なる"
    assert extractTerm(u"食べる：A thing in English.") == u"食べる"
    assert extractTerm(u"  食べる  ：   A thing with regular whitespace") == u"食べる"
    assert extractTerm(u"　  食べる 　 ： 　  A thing with weird JP whitespace") == u"食べる"
    assert extractTerm(u"<div style='fuck:butts'></div>駄目人間: useless person&amp;") == u"駄目人間" # html, w/ colon :'(
    # This test will fail until I fix the above TODO item:
#    assert extractTerm(u"　 食べる　飲む 　 ： A thing with JP whitespace mid-term") == u"食べる　飲む"

# Create the actual menu item
def setupMenu(browser):
    a = QAction("Populate 'Term' Field", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onAdd(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

# The callback that'll happen on click, with the selected card IDs
def onAdd(browser):
    addTermFields(browser.selectedNotes())

# Adds a menu item to the card browser, which will let us act only on selected
# cards rather than the entire collection
addHook("browser.setupMenus", setupMenu)

# Poor man's unit testing? Figure out how to make this better later...
executeTests()
