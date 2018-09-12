

# A collection of python scripts used to automate our PPP GNSS processing. #



Workflow: 
* Drop all the receiver files in an "originaldata" folder (can be changed in settings)
* run convertalltorinex to generate a bunch of teqc batch scripts to convert and split the files on survey start messages. These should be manually modified with the help of the field logbook.
* run processallrinex to run gLab processing (autodownloading needed data files)


Folder structure (can be changed in settings):
* originaldata <- a place to drop the leica *.m00 data files 
* bin <- a place to drop binary dependencies (teqc,glab,tar,gunzip)
* GNSSproducts (SP3,CLK,DCB,.. are autodownloaded to this folder)
* output <- where the glab reports will be organized.


Dependencies:
* URL_LIST.txt from RTKLIB
* misc servers for ephemerides files etc
* gunzip & tar 
* teqc (for converting receiver files to rinex and getting meta data for rinex files)
* gAGE [glab](http://www.gage.upc.edu/gLAB) (for the actual processing). 