

A collection of small python scripts to aid in processing our stake network.



Workflow: 
* Drop all the receiver files in an "originaldata" folder
* run convertalltorinex to auto convert and split the files on survey start messages. (output named with survey datetime and unit number.)
* run processallrinex to run gLab processing (autodownloading needed data files)


Folder structure (can be changed in settings):
* originaldata <- a place to drop the data files 
* rinex
* bin <- a place to drop dependencies 
* GNSSproducts (ephemerides etc ordered in subfolders by datatype and year)
* output



Dependencies:
* URL_LIST.txt from RTKLIB
* misc servers for ephemerides files etc
* gunzip & tar 
* teqc (for converting receiver files to rinex)
* gAGE gLAB (for the actual processing)
* 