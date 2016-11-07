#!/usr/bin/env Rscript

library(scales)
library(ggplot2)
library(RColorBrewer)

args <- commandArgs(trailingOnly=TRUE)

output_pdf <- args[1]

data <- read.table("data.txt", header=FALSE)
colnames(data) <- c("X", "Utilization")

pdf(output_pdf, height=2.5, width=5)

data$X = data$X / 10 # To seconds.

# Below gives the warning
# Removed XXXX rows containing non-finite values (stat_ecdf).
# because we bound the data and ggplot produces infinite values
# outside of that range. Since this is safe, suppress it so we
# don't worry about it.
options(warn = -1)
	ggplot(data, aes(x=X, y=Utilization)) +
    geom_line() +
		xlab("Time (s)") +
		ylab("Network Utilization")
options(warn = 0)

junk <- dev.off()
