from util import hook
from util import isis as irc

@hook.command
def who(inp, nick="", msg="", chan="", isis=None):
    try:
        handle = msg.split(" ")[1]
        row = irc.handle_to_email(isis, handle)
        if row:
            return row
        else:
            return "idk that person"
    except:
        return "idk that person"