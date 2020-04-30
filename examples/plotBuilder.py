import matplotlib.pyplot as plt
import numpy as np 
import seaborn as sns
import matplotlib.collections as collections

def buildPlot(maxNumTrainingIterations,numRealIterations,
	accurateAbilityMeans, randomAbilityMeans, randomOldAbilityMeans,
	GIMMEAbilityMeans, GIMMEOldAbilityMeans, 
	GIMMENoBootAbilityMeans, GIMMEEPAbilityMeans,

	accurateAbilitySTDev, randomAbilitySTDev, randomOldAbilitySTDev,
	GIMMEAbilitySTDev, GIMMEOldAbilitySTDev, 
	GIMMENoBootAbilitySTDev, GIMMEEPAbilitySTDev
	):

	# ----------------------- [Generate Plots] --------------------------------
	sns.set_palette(sns.color_palette("colorblind"))

	timesteps=[i+1 for i in range(maxNumTrainingIterations + numRealIterations)]
	timestepsReal=[i+1 for i in range(numRealIterations)]
	convValue=[1.0 for i in range(maxNumTrainingIterations + numRealIterations)]
	empHighestValue=[max(accurateAbilityMeans) for i in range(maxNumTrainingIterations + numRealIterations)]


	
	plt.rcParams.update({'font.size': 22})

	plt.xticks(np.arange(1, numRealIterations+1, step=1.0), fontsize=30)
	plt.yticks(fontsize=30)

	plt.errorbar(timestepsReal, GIMMEAbilityMeans[maxNumTrainingIterations:], GIMMEAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="GIMME-Bootstrap")
	plt.errorbar(timestepsReal, GIMMENoBootAbilityMeans[maxNumTrainingIterations:], GIMMENoBootAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="GIMME")
	plt.errorbar(timestepsReal, GIMMEEPAbilityMeans[maxNumTrainingIterations:], GIMMEEPAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="GIMME Extreme Person.")
	plt.errorbar(timestepsReal, GIMMEOldAbilityMeans[maxNumTrainingIterations:], GIMMEOldAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="GIMME (old GIPs)")
	plt.errorbar(timestepsReal, randomAbilityMeans[maxNumTrainingIterations:], randomAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="Random")
	plt.errorbar(timestepsReal, randomOldAbilityMeans[maxNumTrainingIterations:], randomOldAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="Random (old GIPs)")
	plt.plot(timestepsReal, empHighestValue[maxNumTrainingIterations:], linestyle= "--", linewidth=3, label="\"Perfect Information\" upper bound")

	plt.xlabel("Iteration", fontsize=40)
	plt.ylabel("avg. Ability Increase", fontsize=40)
	plt.legend(loc='lower center', fontsize=25, ncol=2)

	return plt
