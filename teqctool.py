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
    try:
        meta['sample interval'] = float(meta['sample interval'])
    except ValueError:
        meta['sample interval'] = 0.0
        
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







if __name__ == '__main__':
   
    q =  get_meta(r'..\2018\GPS1 180801\DBX\Default_8632_0731_190123.m00')
#    q  = get_meta(r'..\2015\CardNo3\DBX\testdtu3_6213_0327_102404.m00')
    print(q)
    
    q = get_meta(r'..\2018\GPS10 180801\Rinex\unit10_EG-N-012_2080.18o')
    print(q)
    
    



