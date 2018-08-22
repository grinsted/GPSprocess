# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 10:30:01 2018

@author: aslak
"""

import teqctool 
import settings

rootdir = settings.folders['originaldata']
pattern='*.m00'

for filename in glob.iglob(os.path.join(rootdir,'**',pattern), recursive=True):
    print('Input file: {}'.format(filename))
    teqctool.convert_and_split(input_file=filename)