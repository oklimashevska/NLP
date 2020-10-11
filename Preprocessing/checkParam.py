# -*- coding: utf-8 -*-
"""
@author: Olga Klimashevska
This script is a utility script that checks for 
(i) missing parameters;
(ii) existance of files;
(iii) lacking file extensions
during the command line prompting of some Python script.
"""

import os
from os.path import basename
import sys

def checkParam(p, param, pwd):
    key=1
    if p == None:
            print('')
            sys.stdout.flush()
            print('Missing required parameter: '+param)
            sys.stdout.flush()
            key=-1
            return {'p':p, 'key':key}
    if not os.path.isfile(p):
        if p[0]=='/':
            p = os.path.abspath(p)
        else:
            p = os.path.abspath(pwd+'/'+p)
        
        if not os.path.isfile(p):
            print("")
            sys.stdout.flush()
            print('File in parameter '+param+' does not exist!')
            sys.stdout.flush()
            key=-1
       
    try:
        basename(p).split('.')[1]                   
    except:
        print("")
        sys.stdout.flush()
        print('File in parameter '+param+' lacks filename extension!')
        sys.stdout.flush()
        key=-1

    return {'p':p, 'key':key}
