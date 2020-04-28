import plotBuilder

import latestResults as results


plt = plotBuilder.buildPlot(results.maxNumTrainingIterations,results.numRealIterations,
	results.accurateAbilityMeans, results.randomAbilityMeans, results.randomOldAbilityMeans,
	results.GIMMEAbilityMeans, results.GIMMEOldAbilityMeans, 
	results.GIMMENoBootAbilityMeans,

	results.accurateAbilitySTDev, results.randomAbilitySTDev, results.randomOldAbilitySTDev,
	results.GIMMEAbilitySTDev, results.GIMMEOldAbilitySTDev, 
	results.GIMMENoBootAbilitySTDev,
	)

plt.show()

		
