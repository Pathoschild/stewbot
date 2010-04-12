# -*- coding: utf-8  -*-
#######################################################
##	Configuration
##	Sets constants and settings used by the bot.
#######################################################
from DefaultSettings import *

# IRC server
config.irc.server   = 'irc.freenode.net'  # The IRC network to connect to.
config.irc.port     = 6667                # The port number to connect to (usually 6667).
config.irc.ssl      = False               # Enable encrypted communication, if supported by the server. Make sure to change the port number to 70 or 7070.
config.irc.chans    = ['#stewardbot', '#stewardbot2']  # An array of channels to join.

# IRC user
config.irc.nick     = 'stewbot-clone'     # the nickname the bot will use
config.irc.user     = ''                  # the name of the IRC user account to identify as
config.irc.password = ''                  # the password of the IRC user account to identify with

# web
config.web.user     = ''                  # The wiki username to log in with.
config.web.password = ''                  # the wiki password to log in with.

# debug
config.debug.dump_file = None             # The path on the local filesystem to dump data to when an unhandled exception occurs (or None to disable dumping).
config.debug.dump_url  = None             # The URL to the dump file to show in error messages on IRC when an unhandled exception occurs (or None to disable URL).
