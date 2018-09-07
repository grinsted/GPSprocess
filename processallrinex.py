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


rinexfolder = settings.folders['rinex']
outputfolder = settings.folders['output']
atx = os.path.join(settings.folders['GNSSproducts'],'igs14.atx')



pattern='*.??o'

#
#rinexfolder = r'C:\Users\ag\HugeData\EGRIP GPS\2017\Card8\CSH Rinex'
#pattern= 'GPS2017Card8-0708-daily2090.17o'
#
#
testMode= True
if testMode:
    rinexfolder = r'..\test exclude'
    outputfolder = r'..\test'
    pattern = 'unit5_*.??o'



for filename in glob.iglob(os.path.join(rinexfolder,'**',pattern), recursive=True):
    if os.stat(filename).st_size<50: 
        continue

    if not testMode:
        if filename.lower().find('csh rinex')>=0:
            continue
        if filename.lower().find('exclude')>=0:
            continue

    print()
    print('Input file: {}'.format(filename))
    
    meta = teqctool.get_meta(filename)
    unit = settings.units[meta['receiver ID number']]
    start = meta['start date & time']
    stationname = meta['station name']
    
    outputname = '{}_{:%Y%m%d_%H%M}.txt'.format(stationname,start)
    
    outputname = os.path.join(outputfolder,
                          str(start.year),
                          unit,
                          outputname)
    isKinematic = stationname.lower().find('kine')>=0
    
    
    pathlib.Path(os.path.dirname(outputname)).mkdir(parents=True, exist_ok=True)
    
    print(' - Output file: {}'.format(outputname))
    
    
    sp3 = gnssproducts.productfiles('COD_EPH',meta['start date & time'],meta['final date & time'])
    clk = gnssproducts.productfiles('COD_CLK',meta['start date & time'],meta['final date & time'])
    dcpp1p2 = gnssproducts.productfiles('COD_DCB_P1P2',meta['start date & time'],meta['final date & time'])
    dcpp1c1 = gnssproducts.productfiles('COD_DCB_P1C1',meta['start date & time'],meta['final date & time'])
    inx = gnssproducts.productfiles('IGS_TEC',meta['start date & time'],meta['final date & time'])
    
    
    
    command = [settings.gLAB, '-input:obs', filename,
                '-input:ant', atx,
                '-filter:meas', 'carrierphase',
                '-pre:dec','30',
                '-pre:setrectype', '1',  
                '--model:satphasecenter', 
                '-model:dcb:p1c1', 'strict',
                '-model:dcb:p1p2', 'DCB',
                '-print:none','-print:output','-print:summary','-print:info',
                '--summary:waitfordaystart',
                '-filter:backward',
                '-pre:setrecpos','calculate',
                '--model:arp', #do not apply antenna height offset etc. from rinex
                '-output:file', outputname]  
    
    if isKinematic:
        command.extend(['-filter:nav', 'kinematic'])
    else:
        samplerate = meta['sample interval']*30
        command.extend(['-filter:nav', 'static'])
        #command.extend(['-filter:q:dr',str(samplerate*(0.2)**2/86400)])
        
        
    
    
    for file in sp3:
        command.extend(['-input:orb', file])
    for file in clk:
        command.extend(['-input:clk', file])
    for file in dcpp1p2:
        command.extend(['-input:dcb', file])
    for file in dcpp1c1:
        command.extend(['-input:dcb', file])        
    for file in inx:
        command.extend(['-input:inx', file])                
        
    print(' '.join(command).replace(' -','\n   -'))
    
    print(' - processing...')
    returncode = subprocess.call(command,stderr = subprocess.STDOUT)
    
    if not returncode==0:
        print('ERROR in processing...')
    
    pos = os.stat(outputname).st_size - 1200
    with open(outputname) as f:
        if pos>0:
            f.seek(pos)
        print(f.read())
    
    #break

    
    
    
    

