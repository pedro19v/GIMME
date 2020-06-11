# install.packages("stringr", dep = TRUE, repos = 'http://cran.rstudio.com/')
# install.packages("ggplot2", dep=TRUE, repos = "http://cran.us.r-project.org")
suppressMessages(library(ggplot2))
suppressMessages(library(stringr))
suppressMessages(library(dplyr))

options(warn=-1)


print("GeneratingPlots...")

do.call(file.remove, list(list.files("./plots/", full.names = TRUE)))

resultsLog <- read.csv(file="GIMMESims/results.csv", header=TRUE, sep=",")
resultsLog <- resultsLog[resultsLog$iteration > 19,]
resultsLog <- resultsLog[complete.cases(resultsLog),]


# plot strategies
avg <- aggregate(abilityInc ~ iteration*algorithm , resultsLog, mean)
avgPerRun <- aggregate(abilityInc ~ iteration*algorithm*run*simsID , resultsLog , mean)
sdev <- aggregate(abilityInc ~ iteration*algorithm , avgPerRun , sd)

print(sprintf("nRuns: %d", nrow(unique(resultsLog[c("simsID","run")]))))

un <- unique(resultsLog[c("simsID","run","algorithm")])
print(un %>% count(simsID,algorithm), n=Inf)


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
					theme(axis.text = element_text(size = 20), 
					axis.title = element_text(size = 30, face = "bold"), legend.title=element_text(size=20), legend.text=element_text(size=20))
	# plot <- plot + ylim(0.335, 0.41) 
	plot <- plot + scale_x_continuous(labels = 1:20, breaks = 20:39)
	suppressMessages(ggsave(sprintf("plots/%s.png", plotName), height=6, width=15, units="in", dpi=500))
}




# cmp average ability increase of sim anneal, hillclimb, pure randmon and accurate
currAvg = avg[
			  avg$algorithm=="GIMME" | 
			  avg$algorithm=="GIMME_SA" | 
			  avg$algorithm=="GIMMENoBoot" | 
			  avg$algorithm=="GIMMENoBoot_SA" | 
			  avg$algorithm=="GIMME_AS" | 
			  avg$algorithm=="GIMMENoBoot_AS" | 
			  avg$algorithm=="random" |
			  avg$algorithm=="accurate"
			  ,]

currSdev = sdev[sdev$algorithm=="GIMME" | 
			  sdev$algorithm=="GIMME_SA" | 
			  sdev$algorithm=="GIMMENoBoot" | 
			  sdev$algorithm=="GIMMENoBoot_SA" | 
			  avg$algorithm=="GIMME_AS" | 
			  avg$algorithm=="GIMMENoBoot_AS" | 
			  sdev$algorithm=="random" |
			  sdev$algorithm=="accurate",]

levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMENoBoot"] <- "GIMME (no bootstrap)" 

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

levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMEOld"] <- "GIMME 3D" 
levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMENoBoot"] <- "GIMME 4D" 

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

levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMEOld"] <- "GIMME 3D" 
levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMENoBoot"] <- "GIMME 4D" 

buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityGIPDims")


# cmp average ability increase of GIMME and GIMME EP
currAvg = avg[avg$algorithm=="GIMMENoBoot" | 
			  avg$algorithm=="GIMMEEP",]

currSdev = sdev[sdev$algorithm=="GIMMENoBoot" |  
			    sdev$algorithm=="GIMMEEP",]

levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMENoBoot"] <- "GIMME (no bootstrap)" 
levels(currAvg$algorithm)[levels(currAvg$algorithm) == "GIMMEEP"] <- "GIMME (extr. prfs)" 			  
buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityEP")





avg <- aggregate(profDiff ~ iteration*algorithm , resultsLog , mean)
avgPerRun <- aggregate(profDiff ~ iteration*algorithm*run , resultsLog , mean)
sdev <- aggregate(profDiff ~ iteration*algorithm , avgPerRun , sd)

avg$linetype <- ""

avg$linetype[avg$algorithm != "accurate"] <- "solid"
avg$linetype[avg$algorithm == "accurate"] <- "dashed"

# plot average profileDiff
plot <- ggplot(avg, aes(x = iteration, y=profDiff, group=algorithm, color=algorithm))
plot <- plot + geom_errorbar(width=.1, aes(ymin=avg$profDiff-sdev$profDiff, 
	ymax=avg$profDiff+sdev$profDiff))
plot <- plot + geom_line(stat="identity",linetype = avg$linetype, size=0.8)
plot <- plot + labs(x = "Iteration", y = "avg. Ability Increase", color="Algorithm") + 
				theme(axis.text = element_text(size = 15), 
				axis.title = element_text(size = 15, face = "bold"))
plot <- plot + scale_x_continuous(labels = 1:20, breaks = 20:39)
plot <- plot + ylim(0.2, 0.6) 
suppressMessages(ggsave(sprintf("plots/simulationsResultsProfDiff.png"), height=6, width=10, units="in", dpi=500))



