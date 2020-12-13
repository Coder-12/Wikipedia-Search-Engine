# -*- coding: cp1252 -*-
import sys
import re
import time
from nltk.stem import PorterStemmer
from collections import defaultdict
from heapq import heapify, heappush, heappop
from bisect import bisect
from math import log10
from operator import itemgetter

# Global variable declaration

match_words=["title","ref","category","body","link","infobox"]
stemCache=dict()
priority={}
Secondary_Index=[]
is_field_query=0
N=0       # doc count
dname={}   

# Binary search scheme

def index_search(x,y):
  l=0
  r=len(x)-1
  while l<=r:
    mid=int((l+r)/2)
    if x[mid].split("=")[0] < y:
      l=mid+1
    elif x[mid].split("=")[0] == y:
      return mid
    else:
      r=mid-1
  return l

# condition check

for word in match_words:
  if word[0]=="b":
    priority[word[0]]=1
  elif word[0]=="t":
    priority[word[0]]=1000
  else:
    priority[word[0]]=60

# Parse query provided

def Parse_Query(Query):
  global is_field_query,stemCache
  
  dict={}
  processed_query=list()
  if ":" in Query:
    for word in match_words:
       if word in Query and is_field_query==0:
          is_field_query=1
       dict[word]=word[0]
  
  if is_field_query:  
    Query=Query.split()
    for q in Query:
      if ":" in q:
        cat,word=q.split(":")
        word=word.lower()
        word=re.sub(r'[.,;_?()"/\']',' ',word)
        word=re.sub(r'[^\x00-\x7F]+',' ',word)
        if word not in stemCache:
          stemCache[word]=ps.stem(word)
        word=stemCache[word]
        if cat in dict:
          processed_query.append((word,dict[cat]))
        else:
          processed_query.append((word,"b"))
      else:
        q=q.lower()
        q=re.sub(r'[.,;_?()"/\']',' ',q)
        q=re.sub(r'[^\x00-\x7F]+',' ',q)   
        if q not in stemCache:
          stemCache[q]=ps.stem(q)
        q=stemCache[q]
        processed_query.append((q,"b"))
  else:
     Query=Query.lower()
     Query=re.sub(r'[.,;_?()"/\']',' ',Query)
     Query=re.sub(r'[^\x00-\x7F]+',' ',Query)   
     words_Of_query=Query.split(" ")
     for word in words_Of_query:
       if word not in stemCache:
          stemCache[word]=ps.stem(word)
       word=stemCache[word]
       if len(word)>0 and stopwords[word]!=1:
         processed_query.append(word)
  
  return processed_query

# Search document that best match query and return top 10 doc

def search(Query):
  global N,priority,dname
  
  if_idf=defaultdict(int)
  top_results=list()
  if is_field_query:
    for word,cat in Query:
      pos=bisect(Secondary_Index,word)
      if pos>=1 and Secondary_Index[pos-1]==word:
        pos-=1
        if pos==0:
          pos+=1
        if  pos==len(Secondary_Index)-1 and  Secondary_Index[pos]==word:
          pos+=1

      with open("./Data/mergefiles/index"+str(pos)+".txt","r") as fp:
        file=fp.readlines()
      fp.close()

      listOfwords=file[index_search(file,word)].split("=")[1].split(",")
      parsed_word=list()
      for word in listOfwords:
        if cat in word:
          parsed_word.append(word)
      if len(parsed_word)==0: parsed_word=listOfwords

      for word in parsed_word:
        dno,index_info=word.split(":")
        doc=index_info.split("#")
        tf=0
        for c in doc:
           tf+=int(c[1:])*int(priority[c[0]])

        tf_idf[dno]+=float(log10(1+tf))*float(log10(N/len(parsed_word)))

    topdoc=sorted(tf_idf.items(),key=lambda item:item[1],reverse=1)[0:10]
    for doc in topdoc:
      dno,_=doc
      top_results.append(dname[dno])

  else:
    for word in Query:
      flag=0
      pos=bisect(Secondary_Index,word)
      if pos>=1 and Secondary_Index[pos-1]==word:
        flag=1
        pos-=1
        if pos==0:
          pos+=1
        if  pos==len(Secondary_Index)-1 and  Secondary_Index[pos]==word:
          pos+=1
       
        with open("./Data/mergefiles/index"+str(pos)+".txt","r") as fp:
           file=fp.read()
        fp.close()

        if flag:
          sIndex=file.find(word+"=")
        else:
          sIndex=file.find("\n"+word+"=")
        eIndex=data.find("\n",sIndex+1)
        listOfwords=file[sIndex:eIndex].split("=")[1].split(",")
        for word in listOfwords:
           dno,index_info=word.split(":")
           doc=index_info.split("#")
           tf=0
           for c in doc:
              tf+=int(c[1:])*int(priority[c[0]])

           tf_idf[dno]+=float(log10(1+tf))*float(log10(N/len(listOfwords)))

    topdoc=sorted(tf_idf.items(),key=lambda item: item[1],reverse=1)[0:10]
    for doc in topdoc:
      dno,_=doc
      top_results.append(dname[dno])
      
  return top_results

def main():
    global N,is_field_query,dname
    
    with open("Title.txt","r") as fp:
      lines=fp.readlines()
      for line in lines:
        dno,cat=line.split("#")
        dname[dno]=cat[:cat.rfind(":")]
        N+=1

    with open("./Data/mergefiles/secondary.txt","r") as fp:
      for line in fp:
        Secondary_Index.append(line.split()[0])
    fp.close()

    while (1):
      Query=Input("Ënter query to be search: ")
      start_time=timeit.default_timer()
      tokens_of_query=parse_query(Query)
      try:
        best_result=search(tokens_of_query)
        finish_time=timeit.default_timer()
        for r in best_result: 
           print(r)
        print()
        print("Time taken: ",(finish_time-start_time))
        
      except:
        print("Rephrase query (Error)")

if __name__=="__main__":
    main()
