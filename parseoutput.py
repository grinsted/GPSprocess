# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 13:39:52 2018

@author: aslak
"""





import io
import re
import pandas as pd
import matplotlib.pyplot as plt
import glob
import settings
import datetime
import os

def read_glab_output(inputfile):
    with open(inputfile, 'r') as file:
        contents=file.read()
    #grep ERROR
    errors = re.findall('^ERROR.*$',contents,re.MULTILINE)
    if errors:
        raise(Exception('gLAB error','\n'.join(errors)))
        
        
    #station name 
#    INFO INPUT Station marker: EG-C-200
    stationname = re.search('^INFO INPUT Station marker: (.*)$',contents,re.MULTILINE)
    if stationname: 
        stationname = stationname.group(1)
    else:
        stationname = ''    

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
    data['datetime'] = pd.to_datetime({'year': data['Year'], 'month': 1, 'day': 1, 'second': data['Seconds of day']}) + pd.to_timedelta(data['DOY']-1,'D')
    return (stationname,data)



def make_table_of_all():
    rootdir = settings.folders['output']
    pattern = '*.glab'
    
    D = pd.DataFrame(columns=['id', 'datetime','lat','lon','z','sigmaE', 'sigmaN', 'sigmaZ'])
    
    for filename in glob.iglob(os.path.join(rootdir,'**',pattern), recursive=True):
        print('Input file: {}'.format(filename))
        (stationname,data) = read_glab_output(filename)
        if stationname.lower().find('kinematic')>=0:
            continue
        if data.size<2:
            continue
#        dt = np.diff(data['datetime']) / np.timedelta64(1, 's')
#        ix = dt.ravel().nonzero()
#        end_of_forward_ix = ix[-1]+1
        
        avg_time = np.mean(data['datetime'] - datetime.datetime(2000,1,1))+datetime.datetime(2000,1,1)

        row = data.iloc[-1]
        
        D.loc[D.shape[0]] = [stationname, avg_time, 
                         row['latitude'], row['longitude'], row['height'],
                         row['X error'], row['Y error'], row['Z error']
                         ]
    writer = pd.ExcelWriter(os.path.join(rootdir,'summary.xlsx'))
    D.to_excel(writer,'Summary', index = False)
    writer.save()
        
        
    return D

            
        




if __name__ == '__main__':
   
    D=make_table_of_all()
    
    inputfile = r'C:\Users\ag\HugeData\EGRIP GPS\GPSprocess\output\2017\unit3\EG-C-200_20170804_1705.txt'
    
    # inputfile = r'C:\Users\ag\Documents\GitHub\GPSprocess\output\2017\unit1\unit1_2017-07-26_1139.txt'
    (stationname,data) = read_glab_output(inputfile)
    
    d=data.iloc[-1]
    print(inputfile,d['latitude'],d['longitude'],d['height'])
#    plt.semilogy(data['convergence'])
    #plt.plot(data['longitude'],data['latitude'],'.-')
    #plt.plot(data.iloc[-2:]['longitude'],data.iloc[-2:]['latitude'],'rx')
    #plt.draw()
    
#    plt.plot((data['latitude']-data['latitude'][10])*111e3,data['North error'],'.-')
    