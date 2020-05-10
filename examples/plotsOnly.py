import plotBuilder

import latestResults as results


plt = plotBuilder.buildPlot(results.maxNumTrainingIterations,results.numRealIterations,
	results.accurateAbilityMeans, results.randomAbilityMeans, results.randomOldAbilityMeans,
	results.GIMMEAbilityMeans, results.GIMMEOldAbilityMeans, 
	results.GIMMENoBootAbilityMeans, results.GIMMEEPAbilityMeans,

	results.accurateAbilitySTDev, results.randomAbilitySTDev, results.randomOldAbilitySTDev,
	results.GIMMEAbilitySTDev, results.GIMMEOldAbilitySTDev, 
	results.GIMMENoBootAbilitySTDev, results.GIMMEEPAbilitySTDev,

	
	results.GIMME1DAbilityMeans, results.GIMME2DAbilityMeans, results.GIMME5DAbilityMeans, results.GIMME6DAbilityMeans,
	results.GIMME1DAbilitySTDev, results.GIMME2DAbilitySTDev, results.GIMME5DAbilitySTDev, results.GIMME6DAbilitySTDev
	)

plt.show()

		
