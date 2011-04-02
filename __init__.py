"""
	Responsible for configuring and launching stewbot.
"""
from __config__ import config, documentation
from stewbot import Stewardbot

bot = Stewardbot(
	server           = config.irc.server,
	port             = config.irc.port,
	nick             = config.irc.nick,
	user             = config.irc.user,
	password         = config.irc.password,
	channels         = config.irc.chans,
	ssl              = config.irc.ssl,
	logger           = config.components.logger,
	exceptionLogger  = config.components.exceptionLogger,
	config           = config,
	documentation    = documentation
)
bot.processForever()
