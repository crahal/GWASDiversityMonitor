# GWAS Diversity Monitor

[![Generic badge](https://img.shields.io/badge/Python-3.6-<red>.svg)](https://shields.io/)  [![Generic badge](https://img.shields.io/badge/License-MIT-blue.svg)](https://shields.io/)  [![Generic badge](https://img.shields.io/badge/Maintained-Yes-green.svg)](https://shields.io/)

### Introduction

This is a repository to accompany the GWAS Diversity Monitor, currently maintained as part of the [Leverhulme Centre for Demographic Science](http://www.demographicscience.ox.ac.uk/). The dashboard can be found at:

<div align="center"> <a href="http://www.gwasdiversitymonitor.com">http://www.gwasdiversitymonitor.com</a></div>
<br/><br/>

The interactive plots are written in [Bokeh](https://bokeh.pydata.org/en/latest) and hosted on Heroku. Grateful attributions regarding data are made to the [EMBL-EBI GWAS Catalog](https://www.ebi.ac.uk/gwas/). In summary, the dashboard visualizes a systematic interactive review of all GWAS published to date. It borrows a couple of functions from our [Scientometric Review of all GWAS](https://www.nature.com/articles/s42003-018-0261-x). This repo can be cloned and ran on-the-fly to generate a server on localhost as required. The dashboard and associated summary statistics check daily for updates from the Catalog and update with new releases.

### Prerequisites

As a pre-requisite to running the Bokeh sever, you will need a working Python 3 installation with all of the necessary dependencies detailed in [requirements.txt](https://github.com/crahal/GWASDiversityMonitor/blob/master/requirements.txt). We strongly recommend virtual environments and [Anaconda](https://www.anaconda.com/distribution/).

### Running the Code

This server is operating system independent (through the ``os`` module) and should work on Windows, Linux and OS X all the same. To run: clone this directory, ``cd`` into the directory, and then run ```bokeh serve . --show``` in a terminal to launch the server.

### Versioning

This dashboard is currently at version 0.1.0, and wholly represents a prototype. Please note: although the library logs data updates, it could be that additional dictionary based classifications are required with regards to the ```/data/support/dict_replacer_broad.tsv``` file. Please raise an issue in this repo to alert us of any necessary changes, or any suggestions which you may have in general.

### License

This work is free. You can redistribute it and/or modify it under the terms of the MIT license, subject to the conditions imposed by the [EMBL-EBI license](https://www.ebi.ac.uk/about/terms-of-use). The dashboard comes without any warranty, to the extent permitted by applicable law.

### To Do

1. Javascript callbacks to better generate the summary_statistics.html
