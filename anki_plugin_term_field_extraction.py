# -*- coding: utf-8 -*-

# TODO: write some docs so I remember what this is all about and stuff

from anki.hooks import addHook
from aqt import mw             # main window object (mw) from aqt
from aqt.utils import showInfo # the "show info" tool from utils.py
from aqt.qt import *           # all of the Qt GUI library

# Note that every string still needs the 'u' before it, for some reason. I
# thought that wasn't a thing anymore, with Python 3? Without that, I get
# decode errors when I search the string...
TERM_FIELD_NAME = u"Term"
EXPRESSION_FIELD_NAME = u"Expression"
MEANING_FIELD_NAME = u"Meaning"
JP_COLON = u"："
US_COLON = u":"
JP_SPACE = u"　"

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

    if note[TERM_FIELD_NAME]:
        # Do nothing if Term field is already set, at least for now
        return False

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

def extractTerm(field):
    # Example inputs:
    #
    # 器：物を入れる物。
    # 連なる: たくさんの物が一列に並んで続く。切れずに続く。
    # 食べる：A thing in English.
    # something without a colon

    jpColonPosition = field.find(JP_COLON)
    usColonPosition = field.find(US_COLON)

    if jpColonPosition == -1 and usColonPosition == -1:
        # Neither found
        return None

    elif jpColonPosition != -1 and usColonPosition != -1:
        # Both found, ruh roh
        return None

    elif jpColonPosition != -1:
        # JP found
        return betterStrip(field[:jpColonPosition])

    elif usColonPosition != -1:
        # US found
        return betterStrip(field[:usColonPosition])

    # Unexpected code path, just bail...?
    return None

def betterStrip(s):
    # Strip can't deal with weird JP spaces, I guess?
    # TODO: this won't work if the term has JP spaces *inside* it...
    return s.replace(JP_SPACE, "").strip()

def executeTests():
    assert extractTerm(u"no colon here") == None
    assert extractTerm(u"both colons： here, oh jee:z") == None
    assert extractTerm(u"器：物を入れる物。") == u"器"
    assert extractTerm(u"連なる: たくさん") == u"連なる"
    assert extractTerm(u"食べる：A thing in English.") == u"食べる"
    assert extractTerm(u"  食べる  ：   A thing with regular whitespace") == u"食べる"
    assert extractTerm(u"　  食べる 　 ： 　  A thing with weird JP whitespace") == u"食べる"

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
