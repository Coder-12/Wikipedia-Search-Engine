from xml.sax import ContentHandler,parse
import sys
import re
import time
from nltk.stem import PorterStemmer
from collections import defaultdict

ps=PorterStemmer()
Inverted_Index=defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
stemWords={}
limit = 5000
CountOfTokens=0
var=1

STOPWORDS=defaultdict(int)
with open('stopwords.txt','r') as f:
    for word in f:
        word=word.strip()
        STOPWORDS[word]=1

def tokenize(data):
    ListOfWords=re.findall("\d+|[\w]+",data)
    ListOfWords=[key for key in ListOfWords]
    return ListOfWords

def Create_Index(ListOfwords,dno,e):
    for word in ListOfwords:
        word=re.sub(r"[^\x00-\x7F]+",'',word)
        word=word.strip()
        if(word.isalnum() and len(word)>=3 and STOPWORDS[word]!=1):
           if word in stemWords.keys():
              word=stemWords[word]
           else:
              stemWords[word]=ps.stem(word)
              word=stemWords[word]
           if(STOPWORDS[word]!=1):
              if word in Inverted_Index:
                 if dno in Inverted_Index[word]:
                    if e in Inverted_Index[word][dno]:
                       Inverted_Index[word][dno][e]+=1
                    else:
                       Inverted_Index[word][dno][e]=1
                 else:
                    Inverted_Index[word][dno]={e:1}
              else: Inverted_Index[word]=dict({dno:{e:1}})

def Parse_Title(title,dno):
    global CountOfTokens
    title=title.lower()
    CountOfTokens+=len(tokenize(title))
    title=regExp1.sub('',title)
    title=regExp2.sub('',title)
    title=regExp3.sub('',title)
    title=regExp4.sub(' ',title)
    title=regExp5.sub('',title)
    title=regExp7.sub('',title)
    title=re.sub(r'[^\x00-\x7F]+','',title)
    words=title.split()
    new_words=list()
    for word in words:
        if(word.isalnum() and STOPWORDS[word]!=1):
           word=regExp6.sub(' ',word)
           new_words.append(word)
    Create_Index(new_words,dno,"t")


def Search_Hyperlinks(text):
    Hlinks=list()
    lines=text.split("==external links==")
    if(len(lines)>1):
       lines=lines[1].split("\n")
       for i in range(len(lines)):
           if '* [' in lines[i] or '*[' in lines[i]:
              word=""
              tword=lines[i].split(' ')
              word=[key for key in tword if 'http' not in tword]
              #for key in tword:
              #    if 'http' not in key:
              #        word.append(key)
              word=' '.join(word)
              Hlinks.append(word)
    Hlinks=tokenize(' '.join(Hlinks))
    return Hlinks

def Search_Infobox(text):
    lines=text.split("\n")
    info_text=list()
    body_text=list()
    Catagory=list()
    Hlinks=list()
    ft=1
    status=0
    for i in range(len(lines)):
        if '{{infobox' in lines[i] and not status:
           tot=0
           temp=lines[i].split('{{infobox')[1:]
           info_text.extend(temp)
           while(1):
               if(i>=len(lines)): break
               if '{{' in lines[i]:
                  cnt=lines[i].count('{{')
                  tot+=cnt
               if '}}' in lines[i]:
                  cnt=lines[i].count('}}')
                  tot-=cnt
               if(tot<=0): break
               i+=1
               if(i<len(lines)): info_text.append(lines[i])
           status=1

        elif(ft):
            if '[[catagory' in lines[i] or '==external links==' in lines[i]:
               ft=0
            else: body_text.append(lines[i])

        else:
            if '[[catagory' in lines[i]:
               try:
                  doc=lines[i].split(":")[1]
                  doc=doc[:-2]
                  Catagory.append(doc)
               except: pass

    Catagory=tokenize(' '.join(Catagory))
    info_text=tokenize(' '.join(info_text))
    body_text=tokenize(' '.join(body_text))
    return Catagory,info_text,body_text

def writeFile(Title_File,title,dno,id):
    with open(Title_File,'w') as f:
        try: f.write(str(dno)+'#'+title+':'+id+'\n')
        except: f.write(str(dno)+'#'+self.title.encode('utf-8')+':'+id.encode('utf-8')+'\n')

def write_index_File(Index_File):
   with open(Index_File,"w") as fp:
       for key,val in sorted(Inverted_Index.items()):
          s=str(key)+"="
          for x,y in sorted(val.items()):
              s+=str(x)+":"
              for x1,y1 in y.items():
                  s+=str(x1)+str(y1)+"#"
              s=s[:-1]+","
          fp.write(s[:-1]+"\n")
   fp.close()

def write_stat_File(Info_File):
   with open(Info_File,"w") as fp:
       fp.write(str(CountOfTokens)+'\n'+str(len(Inverted_Index))+'\n')
   fp.close()

def Parse_Text(text,dno):
    global CountOfTokens,var
    text=text.lower()
    CountOfTokens+=len(tokenize(text))
    hyperlinks=Search_Hyperlinks(text)
    text=text.replace('_',' ').replace(',',' ')
    Catagory,info_text,body_text=Search_Infobox(text)
    Create_Index(hyperlinks,dno,"l")
    Create_Index(Catagory,dno,"c")
    Create_Index(info_text,dno,"i")
    Create_Index(body_text,dno,"b")
    
    if(dno%limit == 0):
      index_file="./Data/INDEX_"+str(var)+".txt"
      write_index_File(index_file)
      Inverted_Index.clear()
      stemWords.clear()
      var+=1

