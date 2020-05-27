 

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


suppressMessages(library(ggplot2))
suppressMessages(library(multcomp))
suppressMessages(library(nlme))
suppressMessages(library(pastecs))
suppressMessages(library(reshape))
suppressMessages(library(tidyverse))
suppressMessages(library(sjPlot))
suppressMessages(library(sjmisc))
suppressMessages(library(jsonlite))
suppressMessages(library(stringr))

options(warn=-1)


print("GeneratingPlots...")

cbPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

resultsLog <- read.csv(file="GIMMESims/results.csv", header=TRUE, sep=",")
resultsLog <- resultsLog[resultsLog$iteration > 19,]


# plot strategies
avg <- aggregate(abilityInc ~ iteration*algorithm , resultsLog , mean)
avgPerRun <- aggregate(abilityInc ~ iteration*algorithm*run , resultsLog , mean)
sdev <- aggregate(abilityInc ~ iteration*algorithm , avgPerRun , sd)


upBound <- max(avg$abilityInc[avg$algorithm == "accurate"])
avg$abilityInc[avg$algorithm == "accurate"] <- upBound

print(sdev)
avg$linetype <- ""

avg$linetype[avg$algorithm != "accurate"] <- "solid"
avg$linetype[avg$algorithm == "accurate"] <- "dashed"



plot <- ggplot(avg, aes(x = iteration, y=abilityInc, group=algorithm, color=algorithm))
plot <- plot + geom_errorbar(width=.1, aes(ymin=avg$abilityInc-sdev$abilityInc, 
	ymax=avg$abilityInc+sdev$abilityInc))
plot <- plot + geom_line(stat="identity",linetype = avg$linetype, size=0.8)
plot <- plot + labs(x = "Iteration", y = "avg. Ability Increase", color="Algorithm") + 
				theme(axis.text = element_text(size = 15), 
				axis.title = element_text(size = 15, face = "bold")) 
plot <- plot + scale_colour_manual(values=cbPalette) + scale_x_continuous(labels = 1:20, breaks = 20:39)


suppressMessages(ggsave(sprintf("plots/simulationsResultsAbilityInc.png"), height=6, width=10, units="in", dpi=500))

