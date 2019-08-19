#!/services/tools/R-3.2.1/bin/R


packages <- c("readr", "iotools", "seqminer", "devtools", "copynumber")

setRepositories(graphics = FALSE, ind = 1:6)
chooseCRANmirror(graphics = FALSE, ind = 2)

install.packages(packages)

library(devtools) 

install_git("https://bitbucket.org/sequenzatools/sequenza.git",
    branch="3.0.0")
