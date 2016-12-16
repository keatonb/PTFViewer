#!/usr/bin/python
"""
Script to download Palomar Transient Factory light curves for a list of targets
for visualization with PTFViewer: https://github.com/keatonb/PTFViewer

input csv file should have format:
targetname,rad,decd
where rad and decd are the RA and Dec in decimal degrees.

WARNING: Downloads data for nearest PTF source to given coordinates, not 
necessarily for the target you want.

Learn more at https://github.com/keatonb/PTFViewer

@author: keatonb
"""
from __future__ import print_function
import sys
import os
import csv
from astropy.coordinates import SkyCoord
from PTFViewer import download_ptf

nargs = len(sys.argv)

if nargs < 2:
    print('usage: python multidownload input_file.csv [/data/directory]')
    sys.exit()
    
datadir = os.getcwd()+'/data/'
if len(sys.argv) > 2:
    datadir = sys.argv[2]
if datadir[-1] != '/':
    datadir += '/'
if not os.path.exists(datadir):
    datadir = os.getcwd()+'/data/'
    print(('Created data directory at '+datadir))
    if not os.path.exists(datadir):
        os.makedirs(datadir)
print(('Saving data to '+datadir))
        
csvname = sys.argv[1]
with open(csvname) as csvfile:
    myCSVReader = csv.DictReader(csvfile, fieldnames=['name','ra','dec'],delimiter=",", quotechar='"')
    for row in myCSVReader:
        coords = SkyCoord(float(row['ra']),float(row['dec']),frame='icrs', unit='deg')
        try:
            download_ptf(coords,name=row['name'],directory=datadir)
            print("Data saved to "+datadir+row['name']+'.xml')
        except:
            print("No data found at: "+coords.to_string())
        
