

# A collection of small python scripts to aid in processing our stake network. #



Workflow: 
* Drop all the receiver files in an "originaldata" folder (can be changed in settings)
* run convertalltorinex to generate a bunch of teqc batch scripts to convert and split the files on survey start messages. These will then 
* run processallrinex to run gLab processing (autodownloading needed data files)


Folder structure (can be changed in settings):
* originaldata <- a place to drop the data files 
* bin <- a place to drop binary dependencies 
* GNSSproducts (SP3,CLK,DCB,.. are autodownloaded to this folder)
* output


Dependencies:
* URL_LIST.txt from RTKLIB
* misc servers for ephemerides files etc
* gunzip & tar 
* teqc (for converting receiver files to rinex and getting meta data for rinex files)
* gAGE [glab](http://www.gage.upc.edu/gLAB) (for the actual processing). 