source("https://bioconductor.org/biocLite.R")

biocLite(pkgs=c("copynumber"), suppressAutoUpdate= TRUE, ask = FALSE, suppressUpdates= TRUE)
install.packages(pkgs="sequenza",
                 repos=c("http://cran.rstudio.com")
)
