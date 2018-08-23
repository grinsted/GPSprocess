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
    meta = re.findall(r'^([^\n:]*):([^\n]*)$', out,re.RegexFlag.MULTILINE)
    meta = {item[0]:item[1].strip() for item in meta}
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
    starts.append(meta['final date & time']+datetime.timedelta(seconds=10))
    
    meta['survey starts'] = starts
    
    return meta


def convert_and_split(input_file, min_time_delta=datetime.timedelta(minutes=5), join_small_gaps=datetime.timedelta(minutes=5)):
    
    rinexfiles=[]
    
    meta = get_meta(input_file)
    starts = meta['survey starts']
    unit = settings.units[meta['receiver ID number']]
    
    #combine starts if they are less than xx min appart. 
    dt = np.diff(starts)
    eliminate = (dt[0:-1]<join_small_gaps).nonzero()
    starts = np.delete(starts, np.add(eliminate,1))
    
    for (ix,start) in enumerate(starts[:-1]):
        end = starts[ix+1]-datetime.timedelta(seconds=10)
        if (end-start<min_time_delta):
            print('skipping short survey...')
            continue 
        
        outputfolder = os.path.join(settings.folders['rinex'],
                                  str(start.year),
                                  unit)
        
        pathlib.Path(outputfolder).mkdir(parents=True, exist_ok=True)
        
        if (end-start.replace(second=0,hour=0,minute=0)<datetime.timedelta(days=1)):
            #if it does not span midnight:
            outputname = '{}_{:%Y-%m-%d_%H%M}'.format(unit,start)
            outputname = os.path.join(outputfolder,outputname)
            obsfile = outputname + '.{:%y}o'.format(start)
            navfile = outputname + '.{:%y}n'.format(start)
            command=[teqc,
                     '-leica','mdb',
                     '-st', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(start), 
                     '-e', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(end),
                     '+obs', obsfile,
                     '+nav', navfile,
                     input_file]
            if os.stat(obsfile).st_size==0: 
                os.remove(obsfile)
                os.remove(navfile)
#            else:
#            m = get_meta(obsfile)
#            print(m)
#            return
            print(' -> {} dt={}'.format(obsfile,end-start))
        else: 
            outputname = '{}_{:%Y%m%d%H%M}_bin_'.format(unit,start)
            outputname = os.path.join(outputfolder,outputname)
            command=[teqc,
                     '-leica','mdb',
                     '-st', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(start), 
                     '-e', '{:%Y_%m_%d:%H:%M:%S.%f}'.format(end),
                     '-tr','d',
                     '+obs', '+','+nav', '+','-tbin','1d',
                     outputname,
                     input_file]
            print(' -> ' + outputname + 'ddd0.YYo')
#        print(' '.join(command))
        print(subprocess.check_output(command))


if __name__ == '__main__':
   
    q =  get_meta(r'originaldata\GPS1 180801\DBX\Default_8632_0731_190123.m00')
    print(q)
    convert_and_split(r'originaldata\GPS1 180801\DBX\Default_8632_0731_190123.m00')

    



