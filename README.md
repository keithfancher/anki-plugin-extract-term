Anki Plugin: Extract Term
=========================

This is a super-minimal, super-specific plugin for
[Anki](https://apps.ankiweb.net/). I hacked it together for a one-time use
situation, to normalize some data in my gigantic Japanese Anki deck.

This is not "finished" software. I don't recommend you use it. If, for some
reason, you *do* use it, **DEFINITELY** back up your deck before doing so.
This plugin can make destructive changes to your cards.

I'm uploading this mostly for my own reference, and in case it's handy for
anyone else to see what a bare-bones Anki plugin might look like.

What's it do?
-------------

For historical reasons, my Japanese Anki deck has many cards where the
`Definition` field is a composite of both a term and a definition. For
example:

> 器：物を入れる物。

This plugin simply pulls out the "term" portion ("器", in this case) and
places it in its own field, called (drumroll) `Term`. The existing
`Definition` field is left unchanged.

This simple bit of data normalization makes many deck-maintenance tasks way
easier -- particularly de-duping. (Which is especially useful if you make
heavy use of shared decks, or ever need to combine your own decks.)

How to use
----------

Again: DO NOT use this. This is for informational purposes only.

But if you *did* want to use it, in theory, you could simply copy the `.py`
file into your Anki `addons` directory.  For me at least, that's:
`~/.local/share/Anki2/addons`. Then restart Anki. You should see the "Populate
'Term' Field" menu item in your card browser. You can try running it on a few
selected cards at first, before applying it to a larger set.

You can also execute the script directly (with `python`, outside of Anki) to
run some basic automated tests. Poor man's unit testing, essentially.

But seriously: don't use this.
