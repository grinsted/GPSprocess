# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 11:03:55 2018

@author: aslak
"""


import subprocess
import re
from dateutil.parser import parse
import datetime
import numpy as np
import os
import pathlib
import settings

teqc = settings.teqc


def get_meta(input_file):
    #
    # This function calls teqc +meta input_file and parses the returned meta data from stdout & stderr
    #
    # The result is returned as a dictionary
    #
    p = subprocess.Popen([teqc,'+meta',input_file], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if not p.returncode==0: 
        raise Exception('teqc_error', 'teqc returned a non-zero errorcode')
        
    #parse stdout
    meta = re.findall(r'(.*):\s+(.*\S)\s*', out)
    meta = {item[0]:item[1] for item in meta}
    #meta['stdout'] = out
    #meta['stderr'] = err
    #meta['returncode'] = p.returncode     
    
    meta['start date & time'] = parse(meta['start date & time'])
    meta['final date & time'] = parse(meta['final date & time'])
    
    meta['file size (bytes)'] = int(meta['file size (bytes)'])
    meta['sample interval'] = float(meta['sample interval'])
    meta['possible missing epochs'] = int(meta['possible missing epochs'])
    meta['antenna latitude (deg)'] = float(meta['antenna latitude (deg)'])
    meta['antenna longitude (deg)'] = float(meta['antenna longitude (deg)'])
    meta['antenna elevation (m)'] = float(meta['antenna elevation (m)'])
    meta['antenna height (m)'] = float(meta['antenna height (m)'])

    #parse stderr for "survey starts".... Always append End.
    starts = re.findall(r'survey starts @ (.*) GPS time',err)
    starts = list(map(lambda s: parse(s),starts))
    if not starts:
        starts.append(meta['start date & time'])
    starts.append(meta['final date & time'])
    
    meta['survey starts'] = starts
    
    return meta


def convert_and_split(input_file, min_time_delta=datetime.timedelta(0,5,0), join_small_gaps=datetime.timedelta(0,5,0)):
    
    rinexfiles=[]
    
    meta = get_meta(input_file)
    starts = meta['survey starts']
    unit = settings.units[meta['receiver ID number']]
    
    #combine starts if they are less than xx min appart. 
    dt = np.diff(starts)
    eliminate = (dt[0:-1]<join_small_gaps).nonzero()  
    starts = np.delete(starts, np.add(eliminate,1))
    
    for (ix,start) in enumerate(starts[:-1]):
        end = starts[ix+1]
        if (end-start<min_time_delta):
            print('skipping short survey...')
            continue 
        
        outputname = '{}_{:%Y-%m-%d_%H%M}'.format(unit,start)
        
        outputname = os.path.join(settings.folders['rinex'],
                                  str(start.year),
                                  unit,
                                  outputname)
        
        
        pathlib.Path(os.path.dirname(outputname)).mkdir(parents=True, exist_ok=True)
        output = subprocess.check_output([teqc,'+meta',input_file],universal_newlines=True,stderr=subprocess.STDOUT)
    
        with open(outputname + '.rnx', 'w') as f:
#            subprocess.call([teqc,'+C2','+L5','+L6','+L7','+L8', \
#                             '-st', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(start), \
#                             '-e', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(starts[ix+1]), \
#                             '+nav',outputname + '.gps', input_file],stdout = f)
            subprocess.call([teqc, \
                             '-st', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(start), \
                             '-e', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(starts[ix+1]), \
                             input_file],stdout = f)            
        rinexfiles.append(outputname + '.rnx')
        print(' -> ' + outputname + '.rnx')
    return rinexfiles
    

if __name__ == '__main__':
   
    q =  get_meta(r'C:\Users\ag\HugeData\EGRIP\EGRIP2018\testingteqc\DBX\egrip_1304_0723_194812.m00')
    print(q)



