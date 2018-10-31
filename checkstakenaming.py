# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 06:52:46 2018

@author: aslak
"""

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import datetime
import pyproj

D = pd.read_excel(r'C:\Users\ag\HugeData\EGRIP GPS\output\positions.xlsx')


t = (D['datetime']-datetime.datetime(2017,1,1))/datetime.timedelta(days=365.25)
D['x'] = D['x']-D.iloc[0]['x']+(D.iloc[-1]['x']-D.iloc[0]['x'])*10
D['y'] = D['y']-D.iloc[0]['y']+(D.iloc[-1]['y']-D.iloc[0]['y'])*10

dist = np.sqrt(D['y']**2+D['x']**2)

stakes = pd.unique(D['id'])
for stake in stakes:
    
    Di = D[D['id']==stake]
    
    xm= np.median(Di['x'])
    ym= np.median(Di['y'])
    
    dist = np.sqrt((Di['x']-xm)**2+(Di['y']-ym)**2)
    if np.any(dist>300):
        print(Di[dist>300])