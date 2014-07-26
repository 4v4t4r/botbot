from util import hook, http

@hook.command
def plus(inp, nick=''):
    '''.plus <nick> -- +1 a nickname'''
    db.execute("create table if not exists plus"
               "(chan, nick, count default 0,"
               "primary key (chan, nick))")
    db.commit()

    print inp, nick