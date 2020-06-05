 

# install.packages("multcomp", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("nlme", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("pastecs", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("reshape", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("tidyverse", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("sjPlot", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("sjmisc", dep = TRUE, repos = 'http://cran.us.r-project.org')
# install.packages("jsonlite", dep = TRUE, repos = 'http://cran.rstudio.com/')
# install.packages("stringr", dep = TRUE, repos = 'http://cran.rstudio.com/')
# install.packages("ggplot2", dep=TRUE, repos = "http://cran.us.r-project.org")


# suppressMessages(library(ggplot2))
# suppressMessages(library(multcomp))
# suppressMessages(library(nlme))
# suppressMessages(library(pastecs))
# suppressMessages(library(reshape))
# suppressMessages(library(tidyverse))
# suppressMessages(library(sjPlot))
# suppressMessages(library(sjmisc))
# suppressMessages(library(jsonlite))
# suppressMessages(library(stringr))

suppressMessages(library(ggplot2))
suppressMessages(library(stringr))

options(warn=-1)


print("GeneratingPlots...")


resultsLog <- read.csv(file="GIMMESims/results.csv", header=TRUE, sep=",")
resultsLog <- resultsLog[resultsLog$iteration > 19,]

# print(resultsLog)

# plot strategies
avg <- aggregate(abilityInc ~ iteration*algorithm , resultsLog, mean)
avgPerRun <- aggregate(abilityInc ~ iteration*algorithm*run , resultsLog , mean)
sdev <- aggregate(abilityInc ~ iteration*algorithm , avgPerRun , sd)


upBound <- max(avg$abilityInc[avg$algorithm == "accurate"])
avg$abilityInc[avg$algorithm == "accurate"] <- upBound
sdev$abilityInc[sdev$algorithm == "accurate"] <- 0

avg$linetype <- ""

avg$linetype[avg$algorithm != "accurate"] <- "solid"
avg$linetype[avg$algorithm == "accurate"] <- "dashed"



buildAbIncPlots <- function(logAvg, logSDev, plotName){

	plot <- ggplot(logAvg, aes(x = iteration, y=abilityInc, group=algorithm, color=algorithm))
	plot <- plot + geom_errorbar(width=.1, aes(ymin=logAvg$abilityInc-logSDev$abilityInc, 
		ymax=logAvg$abilityInc+logSDev$abilityInc))
	plot <- plot + geom_line(stat="identity",linetype = logAvg$linetype, size=0.8)
	plot <- plot + labs(x = "Iteration", y = "avg. Ability Increase", color="Algorithm") + 
					theme(axis.text = element_text(size = 15), 
					axis.title = element_text(size = 15, face = "bold"))
	# plot <- plot + ylim(0.335, 0.41) 
	plot <- plot + scale_x_continuous(labels = 1:20, breaks = 20:39)
	suppressMessages(ggsave(sprintf("plots/%s.png", plotName), height=6, width=10, units="in", dpi=500))
}


# cmp average ability increase of sim anneal, hillclimb, pure randmon and accurate
currAvg = avg[avg$algorithm=="GIMME" | 
			  # avg$algorithm=="GIMME_SA" | 
			  avg$algorithm=="GIMMENoBoot" | 
			  # avg$algorithm=="GIMMENoBoot_SA" | 
			  avg$algorithm=="random" |
			  avg$algorithm=="accurate",]

currSdev = sdev[sdev$algorithm=="GIMME" | 
			  # sdev$algorithm=="GIMME_SA" | 
			  sdev$algorithm=="GIMMENoBoot" | 
			  # sdev$algorithm=="GIMMENoBoot_SA" | 
			  sdev$algorithm=="random" |
			  sdev$algorithm=="accurate",]

buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityInc")


# cmp average ability increase of Random, RandomOld, GIMME and GIMMEOld
currAvg = avg[avg$algorithm=="random" | 
			  avg$algorithm=="randomOld" | 
			  avg$algorithm=="GIMMENoBoot" |
			  avg$algorithm=="GIMMEOld",]

currSdev = sdev[sdev$algorithm=="random" | 
			    sdev$algorithm=="randomOld" | 
			    sdev$algorithm=="GIMMENoBoot" |
			    sdev$algorithm=="GIMMEOld",]

buildAbIncPlots(currAvg, currSdev, "oldVsNewResultsAbilityInc")


# cmp average ability increase of GIMME n-D
currAvg = avg[avg$algorithm=="GIMME1D" | 
			  avg$algorithm=="GIMME2D" | 
			  avg$algorithm=="GIMMEOld" | 
			  avg$algorithm=="GIMMENoBoot" | 
			  avg$algorithm=="GIMME5D" | 
			  avg$algorithm=="GIMME6D",]
		
currSdev = sdev[sdev$algorithm=="GIMME1D" | 
				sdev$algorithm=="GIMME2D" | 
				sdev$algorithm=="GIMMEOld" | 
				sdev$algorithm=="GIMMENoBoot" | 
				sdev$algorithm=="GIMME5D" | 
				sdev$algorithm=="GIMME6D",]

buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityGIPDims")


# cmp average ability increase of GIMME and GIMME EP
currAvg = avg[avg$algorithm=="GIMMENoBoot" | 
			  avg$algorithm=="GIMMEEP",]

currSdev = sdev[sdev$algorithm=="GIMMENoBoot" |  
			    sdev$algorithm=="GIMMEEP",]
			  
buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityEP")








# avg <- aggregate(profDiff ~ iteration*algorithm , resultsLog , mean)
# avgPerRun <- aggregate(profDiff ~ iteration*algorithm*run , resultsLog , mean)
# sdev <- aggregate(profDiff ~ iteration*algorithm , avgPerRun , sd)

# avg$linetype <- ""

# avg$linetype[avg$algorithm != "accurate"] <- "solid"
# avg$linetype[avg$algorithm == "accurate"] <- "dashed"

# # plot average profileDiff
# plot <- ggplot(avg, aes(x = iteration, y=profDiff, group=algorithm, color=algorithm))
# plot <- plot + geom_errorbar(width=.1, aes(ymin=avg$profDiff-sdev$profDiff, 
# 	ymax=avg$profDiff+sdev$profDiff))
# plot <- plot + geom_line(stat="identity",linetype = avg$linetype, size=0.8)
# plot <- plot + labs(x = "Iteration", y = "avg. Ability Increase", color="Algorithm") + 
# 				theme(axis.text = element_text(size = 15), 
# 				axis.title = element_text(size = 15, face = "bold"))
# plot <- plot + scale_x_continuous(labels = 1:20, breaks = 20:39)
# plot <- plot + ylim(0.2, 0.6) 
# suppressMessages(ggsave(sprintf("plots/simulationsResultsProfDiff.png"), height=6, width=10, units="in", dpi=500))



