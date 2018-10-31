

import os
#folder where all downloadable data products are stored

folders = {'GNSSproducts': 'GNSSproducts',
           'output': os.path.join('..','output'),
           'rinex': '..',
           'originaldata': '..'}




#executables:  

if os.name == 'nt':
	teqc = r'bin\teqc.exe'
	gLAB = r'c:\glab\win\glab.exe' 
	tar = r'bin\tar.exe'
	gunzip = r'bin\gunzip.exe'
else:
	teqc = r'bin/linux/teqc'
	gLAB = r'bin/linux/gLAB_linux' 
	tar = r'tar'
	gunzip = r'gunzip'



projection = '+init=EPSG:3413 +units=m' #this is only used in the very end for velocities.


# convert receiver ID (from teqc) to CIC unit number

        
units = { '468632': 'unit1',
        '459807': 'unit2',
        '466213': 'unit3',
        '350089': 'unit4',
        '451304': 'unit5',
        '460054': 'unit6',
        '460087': 'unit7',
        '462385': 'unit8',
        '450542': 'unit9',
        '461306': 'unit10'
        }
