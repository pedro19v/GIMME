
class LogManager(ABC):

	def __init__(self):
		pass

	@abstractmethod
    def writeToLog(database, table, argsNValues):
		pass


# ----------------------------------------------------------
   

class SilentLogManager(LogManager):

	def __init__(self):
		pass

	@abstractmethod
    def writeToLog(database, table, argsNValues):
		pass

class DebugLogManager(LogManager):

	def __init__(self):
		pass

	@abstractmethod
    def writeToLog(database, table, argsNValues):
		pass




# ----------------------------------------------------------



class MongoDBLogManager(LogManager):

	def __init__(self):
		pass

	@abstractmethod
    def writeToLog(database, table, argsNValues):
		pass



# ----------------------------------------------------------

import csv

class CSVLogManager(LogManager):

	def __init__(self):
		self.wroteHeader = False;

	@abstractmethod
    def writeToLog(database, table, argsNValues):
    	with open(table+".csv", "wb") as csvfile:
		    fieldnames = argsNValues.keys
		    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		    if(!self.wroteHeader):
		    	writer.writeheader()
		    	self.wroteHeader = True
		    	
		    writer.writerow(argsNValues)
