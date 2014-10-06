from util import hook
from util import isis as irc

@hook.command
def who(inp, nick="", chan="", isis=None):
    row = irc.handle_to_email(isis, nick)
    if row:
        return row