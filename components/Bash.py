# -*- coding: utf-8  -*-
#######################################################
##	Bash
##	Provides methods that return random quotes taken from <http://meta.wikimedia.org/wiki/Bash>.
#######################################################
import sys
import random
from BaseClass import BaseClass

###################
## Bash class
###################
class Bash( BaseClass ):
	###########################################################################
	##	Constructor
	##	Seeds random, builds list of quotes
	###########################################################################
	def __init__(self, logger):
		BaseClass.__init__( self, logger = logger )
		self.trace()

		random.seed()

		self.new = [
			# direct quotes
			'<Pathoschild> You can do tabs in Python, but you can\'t mix tab and space indenting.   * Mike_lifeguard weeps   <Mike_lifeguard> why did nobody tell me?',
			'<Prodego> Razorflame: btw, there are no quotes of me because I am a non-funny person',
			' <DerHexer> where have all the stewbots gone | long time passing | where have all the stewbots gone | long time ago | where have all the stewbots gone | *poof* picked them everyone | when will he ever come back | when will he ever come back',

			# <http://meta.wikimedia.org/wiki/Bash>
			'<Werdna> When all is said and done on Wikipedia, a hell of a lot more is said than done.',
			'<chowbok> What\'s an "almost monopoly"? Is that like "slightly pregnant"?',
			'<Nilfanion> {{PD-Magic}}: This image is ineligible for copyright and therefore is in the public domain, because it consists entirely of information created by magic.',
			'<ElNino^> Why the fuck is Bambi a male in the cartoon but a female in porno?',
			'<Warm_fuzzies> I for one welcome our new sexually transmitted overlords',
			'<Gwern> when I was working on Helpdesk-l, we literally got emails telling us that we accidentally left our articles publicly editable.',
			'<kaiti> lmao, if you search for "porn" in Windows XP\'s Help and Support program, it recommends the article on how to use Internet Explorer.',
			'<DavidGerard> personally, I agree with everything DavidGerard says and think you should all stfu. <DavidGerard> we can vote on it. <DavidGerard> I agree too.',
			'<Lunaway> You know you\'ve got too many tabs open when you manage to edit-conflict yourself.',
			'<Zero1328> I\'ve had one dream about editing Wikipedia, and it was pretty scary. Every time I made an edit I got an edit conflict. I couldn\'t make any changes at all.',
			'<Shadow42> bastique: They\'re raping my sprinklers!',
			'<TehKewl1> omgwtfbbqlolaslsendpixd00dipwntj00andj00arenolonger1337lolroflmaopwntpwnt. <TehKewl1> I mean.... hi.',
			'<01:46> TehKewl1 has left #wikipedia ("/me has been on irc too long"). <01:46> TehKewl1 has joined #wikipedia.',
			'<wmarsh> Heh, I apparently violated the established protocol for editting a page, established by editors of that page. The thing is, the page is in my own userspace.',
			'<ice_cream> ok ok i\'ll chill.',
			'<Luna-San> I heard a rumor that Wikipedia\'s server farm is powered by setting a bunch of kids up with giant hampster wheels and telling them their garage band\'s article is up for AfD.',
			'<Luna-San> I\'ve just run into a gang logo that is now officially available under the terms of the GFDL.   <Luna-San> ...they don\'t seem very thuggish anymore',
			'<kaiti> i went to read about chatzilla bugs <kaiti> and firefox crashed.',
			'<NiklasNordblad> editing is life. :D   <GerardM> well then I have a life.',
			'<SushiGeek> Dmcsleep needs to have a lanyard that he can wear around his neck that beeps loudly when somebody needs a checkuser.   <SushiGeek> so when he\'s sleeping somebody can go "BEEP BEEP CHECKUSER".',
			'* helix84 still wonders if someone is still messing with his patch.   <RealGrouchy> nicotine not flowing?',
			'* brion needs a dual-core oven',
			'<brion> it\'s xmas, so i\'m going to be nice and not WONTFIX this feature request just yet',
			'<brion> http://bugzilla.wikimedia.org/show_bug.cgi?id=42 ... appropriate somehow',
			'<gmaxwell> Sorry. The wikimedia orbital space laser is controlled by toolserver, as a result it seldom works.',
			'<barklund> you say there are more than 1 db request at a time? :)   <intgr> Nah, Wikipedia can\'t be that popular.',
			'<Simetrical> Now, why do we have wikis for extinct languages again?   <larne> Simetrical: because the foundation\'s mission is to distribute knowledge to dead people.',
			'<VoiceOfAll> yes, all straight socks   <VoiceOfAll> (as opposed to gay socks)',
			'<flyingparchment> when official people are saying the same things as me trolling on irc, i think we might have operational issues',
			'<gwern> what viagra spam would cats get? \'is ur d1ck not spiny enuff? does she only mewl and not yowl when you pull backwards? get premium V I A G R A now, meow!\'',
			'<Aviator> i wonder why the stable server is such an unstable server',
			'<[21655]> it\'s called Sense of Humour. Your copy must have expired... <[21655]> ...may I recommend version 2.0 w/ added sarcasm?',
			'* drini has some theory about the vandalbots on enwiki a few years ago, you know  those "OMG SHANEL HAS HUGE BOOBS" thing.   <drini> I think the bot master was pathoschild hitting on shanel',
			'<Species8472> Jimbo? Isn\'t that the guy banned for editting articles about himself?',
			'* kylu hms... kylu\'s bedroom is oddly enough nearly all browns and tans.   * kylu supposes that\'s why kylu\'s so boring. ;.;   <harej> kylu has an ubunturoom',
			'<_mary_kate_> something is wrong with the fi.wikipedia. instead of being written in a human language, it\'s just full of weird letters.',
			'<mattbuck> The following is an announcement on behalf of Wikimedia Commons: People of wikipedia, if you don\'t want to see a penis, DON\'T SEARCH FOR PENIS. Thankyou, that is all.',
			'<Until_It_Sleeps> .count I really suck, because my penis   <SoxBot> I really suck, because my penis has 7 contributions. For more info, see http://toolserver.org/~soxred93/ec/I_really_suck%2C_because_my_penis',
			'<NuclearWarfare> !delete [[zh-yue:??????]] r=Vandalism.   <Dellieplagiat> NuclearWarfare: [[zh-yue:??????]] has been scheduled for termination.   <kylu> y\'know, there\'s something kinda ominous about "NuclearWarfare: [[zh-yue:(something in chinese)]] has been scheduled for termination".',
			'<Ironholds> right, what general subject should I write an article on  <Neurolysis> my enormous member  <Ironholds> isn\'t that a stub?',
			'<slakr> "You\'re such an idiot for thinking I violated WP:CIVIL and WP:NPA. You\'re clearly an asshole for even making that assumption"',
			'<Thrawn> if you\'re hated by WR, that means you\'re probably doing an excellent job',
			'<La_Pianista> Did you know that Debussy once wrote a piece called, "Jimbo\'s Lullaby"?  <Freudian|Sleep> was it then renamed to "Sagner\'s Co-Lullaby"?',

			# <https://bugzilla.wikimedia.org/quips.cgi?action=show>
			'[quip] I spent a minute looking at my own code by accident. I was thinking "What the hell is this guy doing?"',
			'<jwales> What good is having a war mongering President if we can\'t invade Estonia to kill spammers? I AM JOKING DO NOT QUOTE ME ON THAT. :-)',
			'<Raul654> come on, isn\'t anyone here an admin on meta?   <BillyH> I think Raul654 is.',
			'<AlexS> Dear diary: No wikipedia today. Had to go outside and see real people again.',
			'<ilya> I don\'t know what to do and where to go. Outer world seems uneditable.',
			'<snoyes> looking for NPOV female; 5k - 10k edits, to edit together, nothing long-term just a couple of one-night contributions.',
			'<TimShell> Is there an IRC client that has a command that will allow me to physically hurt another user, because I would find that useful',
			'<TimStarling> It was a bad idea. The users made me do it.',
			'<TimStarling> I know how the MediaWiki namespace works, I invented it.',
			'<TimStarling> globals are magical structures, like little winged monkeys that fly your data from wherever it is generated to wherever it is needed.',
			'<TimStarling> temporary solutions have a terrible habit of becoming permanent, around here.',
			'<brion> well breaking wikipedia gets real fucking old :)',
			'<kylu> I suspect wikipedia has resulted in more than one broken human husk staring vacantly at flickering screens in darkened basement rooms somewhere, the eyeless sockets of the long-departed locked onto some imperceptible virtual distance, where a lost soul travels the lonely off-roads away from the information superhighway. the smell of ozone and Dorito crumbs the only comfort to that former person\'s parents, the Diet Coke long ago having gone flat.',
		]
		self.old = []

		self.chloe_new = [
			'Moosh!',
			'Jesse tinky!',
			'Where Jessenel? :(',
			'So sad, so lost. :(',
			'Noooo, Chlo� perfect! :D',
			'*pout*',
			'Dat gwandad, a pain!',
			'Chlo� hungwy!',
			'Where Michael be?',
			'Chlo� 5 years old. Chlo� go school!',
			'Germs-a-gone',
			'Germs est parti!',
			'No naughty chair! >:(',
			'Chloe play game! >:(',
			'Mommy come get me? :(',
			'Look nel! Look nel!',
			'Opsicle, opsicle! :o',
			'Play fish game! >:(',
			'Hmph. Not fair!'
		]
		self.chloe_old = []
		
		self.exit_new = [
			'Laaaaze. :D',
			'Wai so srs? ._.',
			':(',
			'I\'ll remember this.',
			'Acknowledged. Safely putting away knives... done.',
			'So flee youthful passions and pursue righteousness, faith, love, and peace, along with those who call on the Operator from a pure heart.'
		]


	###########################################################################
	##	Quote selection methods
	###########################################################################
	###################
	##	Return specified quote from list of unused quotes, move it to used list
	###################
	def get( self, id ):
		self.trace()

		# validate
		if not self.isInt( id ):
			return 'error: id must be an integer.'
		if int( id ) < 0 or int( id ) >= len( self.new ):
			return 'error: no such quote id.'
		id = int( id )

		# select quote
		quote = self.new[id]
		self.old.append( self.new.pop(id) )

		# cycle when empty
		if len(self.new) == 0:
			self.new = self.old
			self.old = []

		return quote


	###################
	##	Return a random quote
	###################
	def random( self ):
		self.trace()

		i = random.randint( 0, len(self.new) - 1 )
		return self.get( i )


	###################
	##	Return first matching quote
	###################
	def find( self, search ):
		self.trace()

		search = str( search ).lower()

		# search new
		for i in range( len(self.new) ):
			if self.new[i].lower().find( search ) != -1:
				return self.get( i )

		# search old
		for i in range( len(self.old) ):
			if self.old[i].lower().find( search ) != -1:
				return self.old[i]

		# no match
		return 'no quote matched your search.'

	###################
	##	Return Chlo�quote
	###################
	def chloe( self ):
		self.trace()

		# get quote, move to old list
		i     = random.randint( 0, len(self.chloe_new) - 1 )
		quote = self.chloe_new[i]
		self.chloe_old.append( self.chloe_new.pop(i) )

		# cycle when empty
		if len(self.chloe_new) == 0:
			self.chloe_new = self.chloe_old
			self.chloe_old = []

		# return value
		return quote

	###################
	##	Return random exit message
	###################
	def exitMessage( self ):
		self.trace()
		
		i = random.randint( 0, len(self.exit_new) - 1 )
		return self.exit_new[i]


	###################
	##	Return string with given probability, else random quote
	###################
	def stringOrRandom( self, string, probability ):
		if random.random() <= probability:
			return string
		else:
			return self.random()
