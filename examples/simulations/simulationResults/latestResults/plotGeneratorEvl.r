# install.packages("stringi", dep = TRUE, repos = 'http://cran.rstudio.com/')
# install.packages("ggplot2", dep=TRUE, repos = "http://cran.us.r-project.org")
# install.packages("dplyr", dep=TRUE, repos = "http://cran.us.r-project.org")
suppressMessages(library(ggplot2))
suppressMessages(library(stringr))
suppressMessages(library(dplyr))

options(warn=-1)


print("GeneratingPlots...")

# do.call(file.remove, list(list.files("./plots/", full.names = TRUE)))

resultsLog <- read.csv(file="GIMMESims/resultsEvl.csv", header=TRUE, sep=",")
resultsLog <- resultsLog[resultsLog$iteration > 19,]
resultsLog <- resultsLog[complete.cases(resultsLog),]

print(sprintf("nRuns: %d", nrow(unique(resultsLog[c("simsID","run")]))))

# plot strategies
avg <- aggregate(abilityInc ~ iteration*algorithm , resultsLog, mean)
avgPerRun <- aggregate(abilityInc ~ iteration*algorithm*run*simsID , resultsLog , mean)
sdev <- aggregate(abilityInc ~ iteration*algorithm , avgPerRun , sd)

# sdev <- aggregate(abilityInc ~ iteration*algorithm , resultsLog , sd) 
# does not make sense, because it would be influenced by the learning rate of the students. 
# Instead the standard deviation should be of the average of the class, per run.



# un <- unique(resultsLog[c("simsID","run","algorithm")])
# print(un %>% count(simsID,algorithm), n=Inf)


# upBound <- max(avgPerRun$abilityInc[avgPerRun$algorithm == "accurate"]) #for maximum of all runs
# # upBound <- max(avg$abilityInc[avg$algorithm == "accurate"]) #for the maximum average value of all runs (more fair)
# avg$abilityInc[avg$algorithm == "accurate"] <- upBound
# sdev$abilityInc[sdev$algorithm == "accurate"] <- 0



buildAbIncPlots <- function(logAvg, logSDev, plotName, colors = NULL){

	plot <- ggplot(logAvg, aes(x = iteration, y=abilityInc, group=algorithm, color=algorithm, alpha = 0.8)) + geom_point()

	# plot <- plot + geom_errorbar(width=.1, aes(ymin=logAvg$abilityInc-logSDev$abilityInc, 
	# 	ymax=logAvg$abilityInc+logSDev$abilityInc), size = 0.8)

	# plot <- plot + geom_line(aes(linetype=factor(logAvg$linetype)), size = 1.5)
	plot <- plot + scale_linetype_manual(values=c("solid" = 1, "dashed" = 2), name = "linetype") + guides(linetype = FALSE)
	
	plot <- plot + labs(x = "Iteration", y = "Avg. Ability Increase", color="Algorithm") + 
					theme(axis.text = element_text(size = 30, family="Calibri"), 
					axis.title = element_text(size = 35, face = "bold", family="Calibri"), 
					legend.title = element_blank(), 
					legend.text = element_text(size=30), 
					legend.position = 'bottom',
					legend.key = element_blank(),
					panel.background = element_blank(),
					panel.grid.major = element_blank(), 
					panel.grid.minor = element_blank(),
					panel.border = element_rect(colour = "black", fill=NA, size=2.0))

	plot <- plot + scale_x_continuous(labels = 1:20, breaks = 20:39) + scale_alpha(guide=FALSE)
	if(!is.null(colors)){
		plot <- plot + scale_color_manual(values = colors)
	}
	suppressMessages(ggsave(sprintf("plots/%s.png", plotName), height=7, width=15, units="in", dpi=500))
}




# cmp average ability increase of sim anneal, hillclimb, pure random and accurate
currAvg = 	avgPerRun[
				# avg$algorithm=="GIMME" | 
				avgPerRun$algorithm=="GIMME_Evl" #|
				# avg$algorithm=="Random"
				,]

currSdev = sdev[
				# sdev$algorithm=="GIMME" | 
				sdev$algorithm=="GIMME_Evl" #|
				# sdev$algorithm=="Random"
				,]


currAvg$algorithm[currAvg$algorithm == "GIMME"] <- "GIMME-Bootstrap" 
currAvg$algorithm[currAvg$algorithm == "GIMME_Evl"] <- "GIMME GA" 
# currAvg$algorithm[currAvg$algorithm == "Random"] <- "Random" 

currAvg$linetype <- "solid" 
# currAvg$linetype[currAvg$algorithm == "Perf. Info."] <- "dashed" 

buildAbIncPlots(currAvg, currSdev, "simulationsResultsAbilityInc", c("#5e3c99", "dodgerblue","#75a352"))





