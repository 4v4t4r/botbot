from util import hook
from util import isis as irc

import smtplib
import socket
import re
import email.utils
import base64
import hmac
from email.base64mime import encode as encode_base64
from sys import stderr

class PlainSmtp(smtplib.SMTP):
    def login(self, user, password):
        """Log in on an SMTP server that requires authentication.

        The arguments are:
            - user:     The user name to authenticate with.
            - password: The password for the authentication.

        If there has been no previous EHLO or HELO command this session, this
        method tries ESMTP EHLO first.

        This method will return normally if the authentication was successful.

        This method may raise the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
         SMTPAuthenticationError  The server didn't accept the username/
                                  password combination.
         SMTPException            No suitable authentication method was
                                  found.
        """

        def encode_cram_md5(challenge, user, password):
            challenge = base64.decodestring(challenge)
            response = user + " " + hmac.HMAC(password, challenge).hexdigest()
            return encode_base64(response, eol="")

        def encode_plain(user, password):
            return encode_base64("\0%s\0%s" % (user, password), eol="")


        AUTH_PLAIN = "PLAIN"
        AUTH_CRAM_MD5 = "CRAM-MD5"
        AUTH_LOGIN = "LOGIN"

        self.ehlo_or_helo_if_needed()

        if not self.has_extn("auth"):
            raise SMTPException("SMTP AUTH extension not supported by server.")

        # Authentication methods the server supports:
        authlist = self.esmtp_features["auth"].split()

        # List of authentication methods we support: from preferred to
        # less preferred methods. Except for the purpose of testing the weaker
        # ones, we prefer stronger methods like CRAM-MD5:
        preferred_auths = [AUTH_PLAIN, AUTH_LOGIN]

        # Determine the authentication method we'll use
        authmethod = None
        for method in preferred_auths:
            if method in authlist:
                authmethod = method
                break

        if authmethod == AUTH_CRAM_MD5:
            (code, resp) = self.docmd("AUTH", AUTH_CRAM_MD5)
            if code == 503:
                # 503 == 'Error: already authenticated'
                return (code, resp)
            (code, resp) = self.docmd(encode_cram_md5(resp, user, password))
        elif authmethod == AUTH_PLAIN:
            (code, resp) = self.docmd("AUTH",
                AUTH_PLAIN + " " + encode_plain(user, password))
        elif authmethod == AUTH_LOGIN:
            (code, resp) = self.docmd("AUTH",
                "%s %s" % (AUTH_LOGIN, encode_base64(user, eol="")))
            if code != 334:
                raise SMTPAuthenticationError(code, resp)
            (code, resp) = self.docmd(encode_base64(password, eol=""))
        elif authmethod is None:
            raise SMTPException("No suitable authentication method found.")
        if code not in (235, 503):
            # 235 == 'Authentication successful'
            # 503 == 'Error: already authenticated'
            raise SMTPAuthenticationError(code, resp)
        return (code, resp)

@hook.api_key("mail")
@hook.command("mail")
def mail(inp, nick="", chan="", isis=None, api_key=None):
    if not isinstance(api_key, dict) or any(key not in api_key for key in ('username', 'password')):
        return "error: api keys not set"

    handle, msg = inp.split(None, 1)

    addr = irc.handle_to_email(isis, handle)
    if addr:
        mail = PlainSmtp('isis.poly.edu', 25)
        mail.starttls()
        mail.login(api_key['username'], api_key['password'])

        text = """From: botbot <botbot@isis.poly.edu>
To: <{0}>
Subject: New IRC message from {1} in {3}

You have a new message from {1}:

{2}
""".format(addr, nick, msg, chan)

        sender = "botbot@isis.poly.edu"
        recv = [addr]
        try:
            mail.sendmail(sender, recv, text)
            return "Sent"
        except:
            return "Something went wrong..."
    else:
        return "I don't have their email address"

