version = 'r14' # version reported by stewbot

"""
2010-06-29 r14
	- BREAKING CHANGE: replaced config.debug* options for straight-to-file state
	  dumping with new config.components.exceptionLogger. The config.debug*
	  lines can be safely removed from configuration files without replacement
	  to send exceptions to ERROR_LOG.txt in the bot directory.
	- abstracted string encoding, fixed encoding crash when logging non-latin
	  characters.
	
2010-06-28 r13
	- added configurable logging/output (messages can now be sent to console, file, or nowhere);
	- prefer packaged modules over system modules (resolves version conflicts);
	- added stewbot version number.

2010-05-15 r12
	- updated CentralAuth scraping for interface changes.

2010-05-13 r11
	- disabled !activity for en.wikipedia.

2010-04-30 r10
	- added randomized exit messages.

2010-04-27 r9
	- bugfix: reblockIfChanged did nothing if reblock=false.

2010-04-18 r8
	- bugfix: when hiding an account that is already suppressed, treat 'suppressed' as 'hidden'
	  to avoid implicitly reducing hide level.

2010-04-17 r7
	- added !getblocks command;
	- show edit count in !stab* output;
	- added IP support in Browser::getBlockStatus(), which now returns array;
	- added Browser::getGlobalBlocks() & Browser::getCentralAuthStatus();
	- bugfix: page creations counted twice in !stab output if they're also top edits.

2010-04-15 r6
	- bugfix: exception when processing queue range with multiple gaps.

2010-04-11 r5
	- updated CentralAuth scraping for new interface;
	- added !globalOversight command (requires new CentralAuth interface);
	- removed disabled global account deletion;
	- moved to DefaultSettings & validated __config__ scheme;
	- fixed HTTP parser bug when '<br/>' has no space before the slash;
	- updated /modules/mechanize.

2010-04-06 r4
	- updated for MediaWiki API change: https://bugzilla.wikimedia.org/show_bug.cgi?id=23076 .

2010-03-29 r3
	- packaged irclib and simplejson into /modules/.
	- added SSL for IRC.

2010-03-27 r2
	- bugfix: commands can be queued for !commit even if they're configured as uncommittable (issue #5).

2010-03-26 r1
	- now open-source; initial commit.
"""