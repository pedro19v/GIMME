# auxiliary structures: Adaptation
class AdaptationTask(object):
	def __init__(self, description="", minRequiredAbility=0, profile=InteractionsProfile(), tasks=numpy.empty(0)):
		self.description = description
		self.minRequiredAbility = minRequiredAbility
		self.profile = profile

class ModelsConnector(object):
	def getPlayersById(self, ids):
        raise NotImplementedError( "Should have implemented this" )

class AdaptationGroup(object):
# public:
	def __init__(self, interactionsProfile=InteractionsProfile()):
		self.interactionsProfile = interactionsProfile
		self.playerIDs = numpy.empty(0)

		self.avgPreferences = InteractionsProfile()
		self.avgPlayerState = PlayerState()

		self.tailoredTask = AdaptationTask()

	def addPlayer(playerID):
		players=numpy.append(players,playerID);
		playersSize = len(players);

		# recalculate averages
		avgPlayerState = PlayerState();

		for i in range(playersSize):
			InteractionsProfile currPlayerPreference = currPlayer->getInherentPreference();
			currPlayer = players[i];
			avgPlayerState.characteristics.engagement += currPlayer.getCurrState().characteristics.engagement / playersSize;
			avgPlayerState.characteristics.ability += currPlayer.getCurrState().characteristics.ability / playersSize;
			
			avgPreferences += currPlayerPreference / playersSize;
		

class AdaptationConfiguration(object):	
	def __init__(self, groups=numpy.empty(0)):
		self.groups = groups