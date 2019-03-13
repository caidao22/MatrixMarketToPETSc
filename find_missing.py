#!/usr/bin/env python

import scipy.io
import fnmatch
import os
import sys
import re
import numpy as np
from shutil import copyfile
import errno
from subprocess import call

dirs = os.environ['PETSC_DIR']
sys.path.insert(0, dirs+'/lib/petsc/bin/pythonscripts/')
sys.path.insert(0, dirs+'/lib/petsc/bin/')

import PetscBinaryIO

exe = os.path.join(dirs,'src/mat/examples/tests/ex72')

missing = 'missing'

if (len(sys.argv)!=2) :
  print 'Usage : python '+sys.argv[0]+' pathToMatrixFiles'
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

convertedFileList = []
for root, dirnames, filenames in os.walk(missing) :
  for filename in fnmatch.filter(filenames, '*.dat') :
    convertedFileList.append(filename.rsplit("_", 1)[0])

#matrixFileList = []
for root, dirnames, filenames in os.walk(sys.argv[1].rstrip('/')) : # remove trailing slash
  for filename in fnmatch.filter(filenames, '*.mtx') :
    matName = root.split("/")[-1]
    groupName = root.split("/")[-2]
    if (groupName,matName) in processedFileList:
      continue
    submatName = os.path.splitext(filename)[0]
    if submatName in convertedFileList: # pass if already converted
      continue
    if submatName != root.split("/")[-1] and submatName != root.split("/")[-1]+'_b' : # pass if not A matrix or b vector
      continue

    matrixFile = os.path.join(root, filename)
    (rows,cols,_,_,field,_) = scipy.io.mminfo(matrixFile)
    if field != 'real':
      continue
    dirpath = os.path.join(missing,groupName)
    if not os.path.exists(dirpath) :
      os.makedirs(dirpath)
    dst = os.path.join(dirpath,filename)
    try :
      if cols!=1 and submatName.split("_")[-1] != 'b' : # finding A matrix
        print 'converting '+matrixFile
#        matrixFileList.append(os.path.join(root, filename))
#        copyfile(matrixFile, dst)
        outputfile = dirpath+'/'+submatName+'_'+str(int(rows))+'x'+str(int(cols))+'.dat'
        call([exe,'-fin',matrixFile,'-fout',outputfile])
      elif cols == 1 : # b vector
        print 'converting '+matrixFile
#        copyfile(matrixFile, dst)
        outputfile = dirpath+'/'+submatName+'_'+str(int(rows))+'.dat'
        mfile = open(outputfile,'w')
        A = scipy.io.mmread(matrixFile)
        # PetscBinaryIO.PetscBinaryIO().writeVec(mfile,A.toarray()) # sometimes A is in sparse format, thus needs to be converted
        PetscBinaryIO.PetscBinaryIO().writeVec(mfile,A) # sometimes A is in sparse format, thus needs to be converted
        mfile.close()
    except IOError, e :
      print 'Error converting file '+matrixFile
      if e.errno != errno.ENOENT:
        raise
#      if os.path.isfile(outputfile) :
#        os.remove(outputfile)
#        print 'File has been removed'

# if not os.path.exists(converted) :
#   os.makedirs(converted)

