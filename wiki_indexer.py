from xml.sax import ContentHandler,parse
import sys
import re
import time
from text_processing import *
from nltk.stem import PorterStemmer
from collections import defaultdict

Title_File_Name=open(sys.argv[0],'a')

# Define Sax parser Class
class Parser_Module(ContentHandler):
     def __init__(self):
         self.dno=0 
         self.Catagory="" 
         self.title=""
         self.Pagetitle=""
         self.text=""
         self.id=""
         self.f=0

     def startElement(self,tag,attributes):
         if(tag=="title"):
            self.Catagory="title"
            self.title=""
            self.f=1
         if(tag=="page"):
            self.dno+=1
            #self.Catagory="page"
         if(tag=="text"):
            self.Catagory="text"
            self.text=""
         if(tag=="id" and self.f):
            self.Catagory="id"
            self.id=""

     def endElement(self,tag):
         if(tag=="title"):
            Parse_Title(self.title,self.dno)
            self.Pagetitle=self.title
            self.title=""
            self.Catagory=""
         elif(tag=="text"):
            Parse_Text(self.text,self.dno)
            self.text=""
            self.Catagory=""
         elif(tag=="id" and self.f):
            try:
                Title_File_Name.write(str(self.dno)+"#"+self.Pagetitle+":"+self.id+"\n")
            except:
                Title_File_Name.write(str(self.dno)+"#"+self.Pagetitle.encode('utf-8')+":"+self.id.encode('utf-8')+"\n")
            self.f=0
            self.id=""
            self.Catagory=""

     def characters(self,content):
        if(self.Catagory=="text"):
           self.text+=content
        elif(self.Catagory=="title"):
           self.title+=content
        elif(self.Catagory=="id"):
           self.id+=content

print("processing...")
start=time.time()
parse_handle=Parser_Module()
for i in range(1,sys.argv[1]):
     parse("wiki"+str(i)+".xml",parse_handle)
     #print("Parsing completed and Store parse info....\n")
     write_index_File("./Data/index_"+str(var)+".txt")
end=time.time()
print("Time taken for parsing: ",end-start)

#write_stat_File("./Data/index_stat.txt")
print("Everything completed")
