# install.packages("stringr", dep = TRUE, repos = 'http://cran.rstudio.com/')
# install.packages("ggplot2", dep=TRUE, repos = "http://cran.us.r-project.org")
suppressMessages(library(ggplot2))
suppressMessages(library(stringr))
suppressMessages(library(dplyr))

options(warn=-1)


print("GeneratingPlots...")

# do.call(file.remove, list(list.files("./plots/", full.names = TRUE)))

# resultsLog <- read.csv(file="GIMMESims/results.csv", header=TRUE, sep=",")
# resultsLog <- resultsLog[resultsLog$iteration > 19,]
# resultsLog <- resultsLog[complete.cases(resultsLog),]

# print(sprintf("nRuns: %d", nrow(unique(resultsLog[c("simsID","run")]))))

# # plot strategies
# avg <- aggregate(abilityInc ~ iteration*algorithm , resultsLog, mean)
# avgPerRun <- aggregate(abilityInc ~ iteration*algorithm*run*simsID , resultsLog , mean)
# sdev <- aggregate(abilityInc ~ iteration*algorithm , avgPerRun , sd)


# # un <- unique(resultsLog[c("simsID","run","algorithm")])
# # print(un %>% count(simsID,algorithm), n=Inf)


# # upBound <- max(avgPerRun$abilityInc[avgPerRun$algorithm == "accurate"]) #for maximum of all runs
# upBound <- max(avg$abilityInc[avg$algorithm == "accurate"]) #for the maximum average value of all runs (more fair)
# avg$abilityInc[avg$algorithm == "accurate"] <- upBound
# sdev$abilityInc[sdev$algorithm == "accurate"] <- 0


# save(avg, file = "avg.Rdata")
# save(sdev, file = "sdev.Rdata")

load(file = "avg.Rdata")
load(file = "sdev.Rdata")

buildAbIncPlots <- function(logAvg, logSDev, plotName, colors = NULL){

	plot <- ggplot(logAvg, aes(x = iteration, y=abilityInc, group=algorithm, color=algorithm, alpha = 0.8))
	plot <- plot + geom_errorbar(width=.1, aes(ymin=logAvg$abilityInc-logSDev$abilityInc, 
		ymax=logAvg$abilityInc+logSDev$abilityInc), size = 0.8)

	plot <- plot + geom_line(aes(linetype=factor(logAvg$linetype)), size = 1.5)
	plot <- plot + scale_linetype_manual(values=c("solid" = 1, "dashed" = 2), name = "linetype") + guides(linetype = FALSE)
	
	plot <- plot + labs(x = "Iteration", y = "avg. Ability Increase", color="Algorithm") + 
					theme(axis.text = element_text(size = 30), 
					axis.title = element_text(size = 35, face = "bold"), 
					legend.title = element_blank(), 
					legend.text = element_text(size=30), 
					legend.position = 'bottom')

	plot <- plot + scale_x_continuous(labels = 1:20, breaks = 20:39) + scale_alpha(guide=FALSE)
	if(!is.null(colors)){
		plot <- plot + scale_color_manual(values = colors)
	}
	suppressMessages(ggsave(sprintf("plots/%s.png", plotName), height=7, width=15, units="in", dpi=500))
}




# cmp average ability increase of sim anneal, hillclimb, pure random and accurate
currAvg = 	avg[avg$algorithm=="GIMME" | 
				# avg$algorithm=="GIMME_SA" | 
				avg$algorithm=="GIMMENoBoot" | 
				# avg$algorithm=="GIMMENoBoot_SA" | 
				# avg$algorithm=="GIMME_AS" | 
				# avg$algorithm=="GIMMENoBoot_AS" | 
				avg$algorithm=="random" |
				avg$algorithm=="accurate",]

currSdev = sdev[sdev$algorithm=="GIMME" | 
				# sdev$algorithm=="GIMME_SA" | 
				sdev$algorithm=="GIMMENoBoot" | 
				# sdev$algorithm=="GIMMENoBoot_SA" | 
				# sdev$algorithm=="GIMME_AS" | 
				# sdev$algorithm=="GIMMENoBoot_AS" | 
				sdev$algorithm=="random" |
				sdev$algorithm=="accurate",]


currAvg$algorithm[currAvg$algorithm == "accurate"] <- "Perf. Info." 
currAvg$algorithm[currAvg$algorithm == "GIMME"] <- "GIMME-Bootstrap" 
currAvg$algorithm[currAvg$algorithm == "GIMMENoBoot"] <- "GIMME" 
currAvg$algorithm[currAvg$algorithm == "random"] <- "Random" 

currAvg$linetype <- "solid" 
currAvg$linetype[currAvg$algorithm == "Perf. Info."] <- "dashed" 

buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityInc", c("#5e3c99", "dodgerblue","#75a352", "#d7191c"))




# cmp average ability increase of GIMME n-D
currAvg = avg[avg$algorithm=="GIMME1D" | 
			  avg$algorithm=="GIMME2D" | 
			  avg$algorithm=="GIMMEOld" | 
			  avg$algorithm=="GIMMENoBoot" | 
			  avg$algorithm=="GIMME5D" | 
			  avg$algorithm=="GIMME6D" |
			  avg$algorithm=="random",]
		
currSdev = sdev[sdev$algorithm=="GIMME1D" | 
				sdev$algorithm=="GIMME2D" | 
				sdev$algorithm=="GIMMEOld" | 
				sdev$algorithm=="GIMMENoBoot" | 
				sdev$algorithm=="GIMME5D" | 
				sdev$algorithm=="GIMME6D" | 
				sdev$algorithm=="random",]


currAvg$algorithm[currAvg$algorithm == "GIMME1D"] <- "GIMME 1D" 
currAvg$algorithm[currAvg$algorithm == "GIMME2D"] <- "GIMME 2D" 
currAvg$algorithm[currAvg$algorithm == "GIMME5D"] <- "GIMME 5D" 
currAvg$algorithm[currAvg$algorithm == "GIMME6D"] <- "GIMME 6D" 
currAvg$algorithm[currAvg$algorithm == "GIMMEOld"] <- "GIMME 3D" 
currAvg$algorithm[currAvg$algorithm == "GIMMENoBoot"] <- "GIMME 4D"
currAvg$algorithm[currAvg$algorithm == "random"] <- "Random" 

currAvg$linetype <- "solid"
currAvg$linetype[currAvg$algorithm == "Random"] <- "dashed" 

currAvg$algorithm <- factor(currAvg$algorithm, levels=c(sort(unique(currAvg[,"algorithm"]))))
buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityGIPDims")




# cmp average ability increase of GIMME and GIMME EP
currAvg = avg[avg$algorithm=="GIMMENoBoot" | 
			  avg$algorithm=="GIMMEEP",]

currSdev = sdev[sdev$algorithm=="GIMMENoBoot" |  
			    sdev$algorithm=="GIMMEEP",]

currAvg$linetype <- "solid" 
currAvg$algorithm[currAvg$algorithm == "GIMMENoBoot"] <- "GIMME" 
currAvg$algorithm[currAvg$algorithm == "GIMMEEP"] <- "GIMME (extr. prfs)" 			  
buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityEP", c("dodgerblue", "#d7191c"))




# cmp average ability increase of GIMME with different accuracy est
currAvg = avg[
			  avg$algorithm=="GIMME" | 
			  avg$algorithm=="GIMME_LowAccuracyEst" | 
			  avg$algorithm=="GIMME_HighAccuracyEst"
			  ,]

currSdev = sdev[ 
			  sdev$algorithm=="GIMME" | 
			  sdev$algorithm=="GIMME_LowAccuracyEst" | 
			  sdev$algorithm=="GIMME_HighAccuracyEst"
			  ,]

currAvg$linetype <- "solid" 
currAvg$algorithm[currAvg$algorithm == "GIMME"] <- "GIMME-Bootstrap\n (\u03B3 = 0.1)" 
currAvg$algorithm[currAvg$algorithm == "GIMME_LowAccuracyEst"] <- "GIMME-Bootstrap\n (\u03B3 = 0.2)" 
currAvg$algorithm[currAvg$algorithm == "GIMME_HighAccuracyEst"] <- "GIMME-Bootstrap\n (\u03B3 = 0.05)"  
currAvg$algorithm <- factor(currAvg$algorithm, levels=sort(unique(currAvg[,"algorithm"]), decreasing=TRUE))
buildAbIncPlots(currAvg, currSdev, "simulationsResultsAccuracyComp", c("skyblue", "dodgerblue", "navy"))





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



