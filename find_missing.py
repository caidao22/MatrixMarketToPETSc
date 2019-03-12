#!/usr/bin/env python

import scipy.io
import fnmatch
import os
import sys
import re
import numpy as np
from shutil import copyfile
import errno

dirs = os.environ['PETSC_DIR']
sys.path.insert(0, dirs+'/lib/petsc/bin/pythonscripts/')
sys.path.insert(0, dirs+'/lib/petsc/bin/')

import PetscBinaryIO

missing = 'missing'

def grep(path, regex) :
  regObj = re.compile(regex)
  res = []
  for root, dirs, fnames in os.walk(path) :
    for fname in fnames :
      if regObj.match(fname) :
        res.append(os.path.join(root, fname))
  return res

if (len(sys.argv)!=2) :
  print('Usage : python '+sys.argv[0]+' pathToMatrixFiles')
  exit(1)


processedFileList = []
f = open("output_g.txt","r")
for line in f :
  groupName = line.split()[0]
  matName = line.split()[1]
  processedFileList.append((groupName,matName)) 
f.close()

if not os.path.exists(missing) :
  os.makedirs(missing)

matrixFileList = []
for root, dirnames, filenames in os.walk(sys.argv[1].rstrip('/')) : # remove trailing slash
  for filename in fnmatch.filter(filenames, '*.mtx') :
    matName = root.split("/")[-1]
    groupName = root.split("/")[-2]
    if (groupName,matName) in processedFileList:
      continue
    submatName = os.path.splitext(filename)[0]
    if submatName != root.split("/")[-1] and submatName != root.split("/")[-1]+'_b' : # pass if not A matrix or b vector
      continue

    matrixFile = os.path.join(root, filename)
    (rows,cols,_,_,_,_) = scipy.io.mminfo(matrixFile)
    dirpath = os.path.join(missing,groupName)
    if not os.path.exists(dirpath) :
      os.makedirs(dirpath)
    dst = os.path.join(dirpath,filename)
    try :
      if cols!=1 and submatName.split("_")[-1] != 'b' : # finding A matrix
        print 'adding '+matrixFile
#        matrixFileList.append(os.path.join(root, filename))
        copyfile(matrixFile, dst)
      elif cols == 1 : # b vector
        print 'adding '+matrixFile
        copyfile(matrixFile, dst)
    except IOError, e :
      print 'Error handling file '+matrixFile
      if e.errno != errno.ENOENT:
        raise
#      if os.path.isfile(outputfile) :
#        os.remove(outputfile)
#        print 'File has been removed'

# if not os.path.exists(converted) :
#   os.makedirs(converted)

