# -*- coding: cp1252 -*-
import sys
import re
import time
from nltk.stem import PorterStemmer
from collections import defaultdict
from heapq import heapify, heappush, heappop

isdone=[0 for i in range(1965)]
index_files=["./Data/index_"+str(i)+".txt" for i in range(1,1965,1)]
num_of_index_files=len(index_files)
chunk_size=100000
processed_index_file=0
secondary_index={}
index_file_ptr={}
row={}
listOfwords={}
heap=[]
tot=0
inverted_index=defaultdict()

def store_primery_index_info():
  global processed_index_file
  processed_index_file+=1
  flag=1
  index_file="./Data/mergefiles/"+"ïndex"+str(processed_index_file)+".txt"
  with open(index_file,"w") as fp:
    for i in sorted(inverted_index):
      if flag:
        secondary_index[i]=processed_index_file
        flag=0
      fp.write(str(i)+"="+inverted_index[i]+"\n")

def main():
    while isdone.count(0)!=num_of_index_files:
        word=heappop(heap)
        tot+=1
        for i in range(num_of_index_files):
          if (isdone[i] and listOfwords[i][0]==word):
            if word not in inverted_index:
              inverted_index[word]=listOfwords[i][1]
            else:
              inverted_index[word]+=","+listOfwords[i][1]
            row[i]=index_file_ptr[i].readline().strip()
            if row[i]:
              listOfwords[i]=row[i].split("=")
              if listOfwords[i][0] not in heap:
                heappush(heap,listOfwords[i][0])
            else:
              isdone[i]=0
              index_file_ptr[i].close()
        if (tot>=chunk_size):
          store_primery_index_info()
          tot=0
          inverted_index.clear()

        store_primery_index_info()

        with open("./Data/mergefiles/"+"secondary.txt","w") as fp:
            for i in sorted(secondary_index):
              fp.write(str(i)+" "+str(secondary_index[i])+"\n")

if __name__=="__main__":
    main()
    
