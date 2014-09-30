"""
remember.py: written by Scaevolus 2010
"""

import string
import re
import random
from util import hook


def db_init(db):
    db.execute("create table if not exists memory(chan, word, data, nick)")
    db.commit()


def get_memory(db, chan, word):
    row = db.execute("select data from memory where chan=? and word=lower(?)", (chan, word)).fetchall()
    if row > 0:
        return random.choice(row)[0]
    else:
        return None


@hook.command
@hook.command("r")
@hook.command("learn")
def remember(inp, nick='', chan='', db=None):
    ".remember <word> [+]<data> s/<before>/<after> -- maps word to data in the memory, or does a string replacement (not regex)"
    db_init(db)

    append = False
    replacement = False

    try:
        head, tail = inp.split(None, 1)
    except ValueError:
        return remember.__doc__

    db.execute("insert into memory(chan, word, data, nick) values (?,lower(?),?,?)", (chan, head, tail, nick))
    db.commit()

    return 'done.'


@hook.command
@hook.command("f")
def forget(inp, chan='', db=None):
    ".forget <word> -- forgets the mapping that word had"

    db_init(db)
    data = get_memory(db, chan, inp)

    if not chan.startswith('#'):
        return "I won't forget anything in private."

    if data:
        db.execute("delete from memory where chan=? and word=lower(?)",
                   (chan, inp))
        db.commit()
        return 'forgot `%s`' % data.replace('`', "'")
    else:
        return "I don't know about that."


@hook.regex(r'^\. ?(.+)')
def question(inp, chan='', say=None, db=None):
    ".<word> -- shows what data is associated with word"
    db_init(db)

    data = get_memory(db, chan, inp.group(1).strip())
    if data:
        print data
        say(data)
