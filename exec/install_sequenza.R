#!/services/tools/R-3.2.1/bin/R


packages <- c("readr", "iotools", "seqminer", "devtools", "copynumber")

setRepositories(graphics = FALSE, ind = 1:6)
chooseCRANmirror(graphics = FALSE, ind = 2)

install.packages(packages)

library(devtools) 

install_git("https://bitbucket.org/sequenza_tools/sequenza.git",
    branch="cleanup")
