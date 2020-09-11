#!/usr/bin/env python

import scipy.io
import fnmatch
import os
import sys
import re
import numpy as np
from scipy.sparse import isspmatrix

dirnames = os.environ['PETSC_DIR']
sys.path.insert(0, dirnames+'/lib/petsc/bin/pythonscripts/')
sys.path.insert(0, dirnames+'/lib/petsc/bin/')

import PetscBinaryIO

#converted = 'converted_clean'
converted = 'gpu_converted_clean'
def grep(path, regex) :
  regObj = re.compile(regex)
  res = []
  for root, dirnames, filenames in os.walk(path) :
    for filename in filenames :
      if regObj.match(filename) :
        res.append(os.path.join(root, filename))
  return res

if (len(sys.argv)!=2) :
  print('Usage : python '+sys.argv[0]+' pathToMatrixFiles')
  exit(1)

convertedFileList = []
for root, dirnames, filenames in os.walk(converted) :
  for filename in fnmatch.filter(filenames, '*.dat') :
    convertedFileList.append(filename.rsplit("_", 1)[0])

matrixFileList = []
for root, dirnames, filenames in os.walk(sys.argv[1].rstrip('/')) : # remove trailing slash
  for filename in fnmatch.filter(filenames, '*.mtx') :
    matrixFile = os.path.join(root, filename)
    matName = matrixFile.replace("/",".")
    groupName = matName.split(".")[-4]
    matName= matName.split(".")[-2]

    isconverted = False
    for existingfile in convertedFileList :
      if existingfile.startswith(groupName+'_'+matName) :
        isconverted = True
        break
    if isconverted:
        print('skipping '+matrixFile+' because it has already been converted')
        continue
    filenameNoExt = os.path.splitext(filename)[0]
    # adding only one A matrix and b vector from the folder and ignore all the others
    if filenameNoExt == root.split("/")[-1] or filenameNoExt == root.split("/")[-1]+'_b' :
      print('adding '+matrixFile)
      matrixFileList.append(matrixFile)
    else :
      print('skipping '+matrixFile+' because the file name <'+filenameNoExt+'> does not match <'+root.split("/")[-1]+'> or <'+root.split("/")[-1]+'_b>')

print('Matrices to convert: ')
for matrix in matrixFileList :
  size = os.path.getsize(matrix)
  print(matrix+' '+str(size)+' bytes')

if not os.path.exists(converted) :
  os.makedirnames(converted)

for matrixFile in matrixFileList :
  matName = matrixFile.replace("/",".")
  groupName = matName.split(".")[-4]
  matName= matName.split(".")[-2]
  (rows,cols,_,_,field,_) = scipy.io.mminfo(matrixFile)

  # select only real-valued matrices, if one chooses 'real' using the online selection tool, both real and pattern will be included.
  if field != 'real' :
     continue

  try :
    if cols!=1 and matName.split("_")[-1] != 'b' : # finding A matrix
      outputfile = converted+'/'+groupName+'_'+matName+'_'+str(rows)+'x'+str(cols)+'.dat'
      print('Outputing : '+outputfile)
      mfile = open(outputfile,'w')
      A = scipy.io.mmread(matrixFile)
      PetscBinaryIO.PetscBinaryIO().writeMatSciPy(mfile, A)
    elif cols == 1: # b vector
      outputfile = converted+'/'+groupName+'_'+matName+'_'+str(rows)+'.dat'
      print('Outputing : '+outputfile)
      mfile = open(outputfile,'w')
      A = scipy.io.mmread(matrixFile)
      if isspmatrix(A) :# sometimes A is in sparse format, thus needs to be converted
        A = A.toarray()
      PetscBinaryIO.PetscBinaryIO().writeVec(mfile, A)
    else:
      outputfile = converted+'/'+groupName+'_'+matName+'_'+str(rows)+'x'+str(cols)+'.dat'
      print('Skipping : '+outputfile+' because b is a matrix')
  except Exception as e:
    print('Error Creating file '+outputfile)
    if os.path.isfile(outputfile) :
      os.remove(outputfile)
      print('File has been removed')
