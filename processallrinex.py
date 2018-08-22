# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 10:52:01 2018

@author: aslak
"""

import teqctool 
import gnssproducts
import settings
import subprocess
import os
import pathlib
import glob


rinexfolder = settings.folders['rinex'] #+ r'\2018\unit5'
outputfolder = settings.folders['output']
atx = os.path.join(settings.folders['GNSSproducts'],'igs14.atx')

pattern='*.??o'

for filename in glob.iglob(os.path.join(rinexfolder,'**',pattern), recursive=True):
    if os.stat(filename).st_size<50: 
        continue

    print()
    print('Input file: {}'.format(filename))
    
    meta = teqctool.get_meta(filename)
    unit = settings.units[meta['receiver ID number']]
    start = meta['start date & time']
    
    outputname = '{}_{:%Y-%m-%d_%H%M}.txt'.format(unit,start)
    
    outputname = os.path.join(outputfolder,
                              str(start.year),
                              unit,
                              outputname)
    
    pathlib.Path(os.path.dirname(outputname)).mkdir(parents=True, exist_ok=True)
    
    print(' - Output file: {}'.format(outputname))
    
    
    sp3 = gnssproducts.productfiles('COD_EPH',meta['start date & time'],meta['final date & time'])
    clk = gnssproducts.productfiles('COD_CLK',meta['start date & time'],meta['final date & time'])
#    ionex = gnssproducts.productfiles('IGR_TEC',meta['start date & time'],meta['final date & time'])
#    dcb = gnssproducts.productfiles('COD_DCB_P1P2',meta['start date & time'],meta['final date & time'])
    
    print(' - sp3' + repr(sp3))
    print(' - clk' + repr(clk))
    #simple process
    #gLAB -input:obs madr2000.06o -input:sp3 igs13843.sp3 -input:ant igs_pre1400.atx -filter:meas carrierphase -filter:nav static
    
    command = [settings.gLAB, '-input:obs', filename,
               '-input:ant', atx,
               '-filter:meas', 'carrierphase',
               '-filter:nav', 'static',
               '-filter:backward',
               #'-pre:cs:l1c1',
               '-pre:dec','30',
               #'-pre:setrecpos','SetGeod', '75.75', '-36.53', '2725',
               #'-pre:setrecpos','calculateUSERGeod', '75.75', '-36.53', '2725', #i get no error estimates if i use this w calculate
               '-pre:setrecpos','calculate', #i get no error estimates if i use this w calculate
               #'-model:iono','IONEX',
               '-print:none','-print:output','-print:summary',
               '--summary:waitfordaystart',
               '-output:file', outputname]  
    for file in sp3:
        command.append('-input:orb')
        command.append(file)
    for file in clk:
        command.append('-input:clk')
        command.append(file)
#    for file in ionex:
#        command.append('-input:inx')
#        command.append(file)
#    for file in ionex:
#        command.append('-input:dcb')
#        command.append(file)
    
    
    print(' - processing...')
    print(subprocess.check_output(command,stderr = subprocess.STDOUT))
    
    pos = os.stat(outputname).st_size - 1200
    with open(outputname) as f:
        if pos>0:
            f.seek(pos)
        print(f.read())
    
    #break

    
    
    
    

