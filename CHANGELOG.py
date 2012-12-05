"""
2012-12-03 r23
	- added support for IPv6 addresses in commands (Issue #18)

2011-04-01 r22
	- new configuration: toggle handling of !commit command;
	- use new API modules for getGlobalRights;
	- use new API modules for getGlobalDetails (merged from getGlobalAccounts and getGlobalEdits);
	- simplified package design.

2011-03-29 r21
	- bugfix: Wikimedia handler assigned incorrect family for betwikiversity.

2011-03-01 r20
	- bugfix: global edit count parsing broken in MW1.17wmf;
	- added command parameter trimming.

2010-11-20 r19
	- !stabhide conflict detection algorithm revamped;
	- !stabhide now has 'hard' option to hide accounts even if they have edits.

2010-10-17 r18
	- Wikimedia.py: fixed handling of special *wikimedia wikis.

2010-08-09 r17
	- !stabhide overrides no-local-block list.

2010-08-08 r16
	- !stab no longer blocks on enwikibooks, per
	  http://lists.wikimedia.org/pipermail/foundation-l/2010-August/060447.html

2010-07-13 r15
	- now raises ValueError when user is assigned multiple access levels in config;
	- overrode StrictDict iterators to never iterate over internal __name__ item.

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
