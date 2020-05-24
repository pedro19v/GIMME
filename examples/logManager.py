from abc import ABC, abstractmethod


class LogManager(ABC):

	def __init__(self):
		pass

	@abstractmethod
	def writeToLog(self, database, table, argsNValues):
		pass


# ----------------------------------------------------------
   

class SilentLogManager(LogManager):

	def __init__(self):
		pass

	def writeToLog(self, database, table, argsNValues):
		pass

class DebugLogManager(LogManager):

	def __init__(self):
		pass

	def writeToLog(self, database, table, argsNValues):
		pass




# ----------------------------------------------------------



class MongoDBLogManager(LogManager):

	def __init__(self):
		pass

	def writeToLog(self, database, table, argsNValues):
		pass



# ----------------------------------------------------------

import csv
import os

class CSVLogManager(LogManager):

	def __init__(self, filePath):
		self.filePath = filePath
		self.wroteHeader = False

	def writeToLog(self, database, table, argsNValues):
		newFilePath = self.filePath + database +"/"
		if not os.path.exists(newFilePath):
			self.wroteHeader = False;
			os.makedirs(newFilePath)
		newFilePath = newFilePath + table + ".csv"

		with open(newFilePath, "a", newline='') as csvfile:
			fieldnames = list(argsNValues.keys())
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			if not self.wroteHeader:
				writer.writeheader()
				self.wroteHeader = True

			writer.writerow(argsNValues)
