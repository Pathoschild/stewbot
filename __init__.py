#######################################################
##	__init__.py
##	Launches the bot.
##
##	To-do:
## 		- check for duplicate commands
##		- oversight global logs on !stab
##		- !nuke
##		- block on Meta when locking
##		- warning after !lock'ing an account with edits
##		- list admins by latest activity
##		- backup RC reader
#######################################################
from __config__ import config
from Stewardbot import Stewardbot

###################
## Launch bot
###################
bot = Stewardbot(
	server           = config.irc.server,
	port             = config.irc.port,
	nick             = config.irc.nick,
	user             = config.irc.user,
	password         = config.irc.password,
	channels         = config.irc.chans,
	ssl              = config.irc.ssl,
	logger           = config.components.logger
)
bot.processForever()
