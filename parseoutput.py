# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 13:39:52 2018

@author: aslak
"""





import io
import re
import pandas as pd
import matplotlib.pyplot as plt

def read_glab_output(inputfile):
    with open(inputfile, 'r') as file:
        contents=file.read()
    #grep ERROR
    errors = re.findall('^ERROR.*$',contents,re.MULTILINE)
    if errors:
        raise(Exception('gLAB error','\n'.join(errors)))

    #grep OUTPUT rows
    outputlines = re.findall('^OUTPUT.*$',contents,re.MULTILINE)
    outputlines = io.StringIO('\n'.join(outputlines))

    columnnames = ['rowtype',
                'Year', 'DOY', 'Seconds of day',
                'convergence', #Square root of the sum of the covariance matrix. 
                'X pos', 'Y pos', 'Z pos',
                'X pos - a priori X pos', 'Y pos - a priori Y pos', 'Z pos - a priori Z pos',
                'X error', 'Y error', 'Z error', 
                'latitude', 'longitude', 'height',
                'North - a priori pos', 'East - a priori pos', 'Up - a priori pos',
                'North error', 'East error', 'Up error',
                'GDOP', 'PDOP', 'TDOP', 'HDOP', 'VDOP', 
                'ZTD', 'ZTD - nominalZTD', 'ZTD error',
                'Number of sats', 
                'Processing mode', 'field29', 'field30', 'field31']

    data = pd.read_table(outputlines, names=columnnames,
                         header = None, comment=r'#',delim_whitespace=True)
    return data


if __name__ == '__main__':
   
    inputfile = r'C:\Users\ag\Documents\GitHub\GPSprocess\output\2017\unit1\unit1_2017-07-31_1216.txt'
    inputfile = r'C:\Users\ag\Documents\GitHub\GPSprocess\output\2018\unit1\unit1_2018-07-31_1357.txt'
    # inputfile = r'C:\Users\ag\Documents\GitHub\GPSprocess\output\2017\unit1\unit1_2017-07-26_1139.txt'
    data=read_glab_output(inputfile)
    data.iloc[-1]
#    plt.semilogy(data['convergence'])
    #plt.plot(data['longitude'],data['latitude'],'.-')
    #plt.plot(data.iloc[-2:]['longitude'],data.iloc[-2:]['latitude'],'rx')
    #plt.draw()
    
    plt.plot((data['latitude']-data['latitude'][10])*111e3,data['North error'],'.-')
    