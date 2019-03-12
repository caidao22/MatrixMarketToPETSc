#!/usr/bin/env python

import fnmatch
import os
import sys

matrixFileList = []
for root, dirnames, filenames in os.walk(sys.argv[1].rstrip('/')) : # remove trailing slash
  for filename in fnmatch.filter(filenames, '*.mtx') :
    datafile = os.path.splitext(filename)[0]
    if datafile == root.split("/")[-1] : # finding only A matrix
      print ('adding '+filename)
      matrixFileList.append(os.path.join(root, filename))

processedFileList = []
f = open("group_name.txt","w+")
f2 = open("overwriting.txt","w+")
mydict = {}
for matrixFile in matrixFileList :
  matName = matrixFile.replace("/",".")
  groupName = matName.split(".")[-4]
  matName = matName.split(".")[-2]
  size = os.path.getsize(matrixFile)
  if (size>1073741824) :
    print(matrixFile+' is too large: ')
  mydict[matName] = groupName
  f.write(groupName+" "+matName+"\n")
  if matName in processedFileList :
    f2.write(groupName+" "+matName+"\n")
  processedFileList.append(matName)
f.close()
f2.close()

f = open("output.txt","r")
f2 = open("output_g.txt","w+")
for line in f :
  matName = line.split()[0]
  f2.write(mydict[matName]+' '+line)
f.close()
f2.close()
