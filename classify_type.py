#!/usr/bin/env python

import scipy.io
import fnmatch
import os
import sys

if (len(sys.argv)!=2) :
  print('Usage : python '+sys.argv[0]+' pathToMatrixFiles')
  exit(1)

freal = open("real.txt","w")
fpat = open("pattern.txt","w")
matrixFileList = []
for root, dirnames, filenames in os.walk(sys.argv[1].rstrip('/')) : # remove trailing slash
  for filename in fnmatch.filter(filenames, '*.mtx') :
    matName = root.split("/")[-1]
    groupName = root.split("/")[-2]
    submatName = os.path.splitext(filename)[0]
    if submatName != root.split("/")[-1] and submatName != root.split("/")[-1]+'_b' : # pass if not A matrix or b vector
      continue
    matrixFile = os.path.join(root, filename)
    (rows,cols,_,_,field,_) = scipy.io.mminfo(matrixFile)
    if cols!=1 and submatName.split("_")[-1] != 'b' : # finding A matrix
      if field == 'real':
         freal.write(groupName+' '+matName+'\n')
      if field == 'pattern':
         fpat.write(groupName+' '+matName+'\n')
freal.close()
fpat.close()
