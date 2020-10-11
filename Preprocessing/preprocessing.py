# -*- coding: utf-8 -*-
"""
@author: Olga Klimashevska
This script preprocesses string data from a CSV file and saves the new data to a new CSV file.
This CSV file must have an ID in the 1st column and a string in the 2nd column.

Dependencies:
- checkParam.py

TODO:
[-] fix preprocess(numbers='base').
"""

import os
from os.path import basename
import sys
import argparse

import unicodedata

import re

from word2number import w2n

import nltk
from nltk.corpus import stopwords
try:
    set(stopwords.words('english'))
except:
    nltk.download('stopwords')

import pandas as pd

# Change this if you are running this on Unix.
UNIX = False

# in order to fix "pandas.errors.ParserError: field larger than field limit (131072)"
if UNIX:
    import csv
    csv.field_size_limit(sys.maxsize)

import checkParam


PWD = os.getcwd()


STOP_WORDS = set(stopwords.words('english')) # here we assume that we work only in English
# STOP_WORDS
"""
{'m', 'which', 'about', 'mustn', 'after', 'whom', 'a', 'both', "shouldn't", 'you', 'd', "you're", 've', 'are', 'doing', 'itself', 'myself', 'don', 'out', 'further', 'through', 'on', 'been', 'an', 'i', 'needn', "hasn't", 'then', 'not', 'very', 'hadn', 'with', 'most', 'its', 'up', "doesn't", 'they', 'didn', 'before', 'll', 'aren', 'ours', 'it', 'should', 'those', 'against', "don't", 'who', 'under','do', 'off', 'such', 'himself', 'and', 'other', 'for', 'why', 't', 'too', 'be',
'does', 'because', 'during', 'them', 'when', "hadn't", 'ourselves', "wasn't", 'o', 'few', 'what', "won't", 'into', 'is', 'if', 'over', "weren't", 'couldn', "you'd", 'her', 'mightn', 'how', "it's", 'there', 'any', 'yours', 'has', "should've", 'to', 'these', 'him', 'only', 'each', 'can', 'until', 're', "couldn't", 'he','so', "aren't", 'weren', 'the', 'themselves', 'while', 'yourself', 'haven', 'she', 'between', 'now', 'once', 'me', 'doesn', 'more', 'again', 'being', 'wasn', 'yourselves', "haven't", 'wouldn', 'we', 'or', "needn't", 'hasn', 'y', 'as', 'same', 'shan', 'just', 'his', 'will', "wouldn't", "you've", 's', 'am', "shan't", 'this', 'some', 'in', 'own', 'was', 'theirs', 'than', 'your', "she's", 'hers', 'down', "didn't", 'from', "isn't", 'had', 'having', 'shouldn', 'herself', 'no', 'nor', 'but', 'were', 'their', 'of', 'isn', 'below', 'where', 'won', "mustn't", 'that', "you'll", 'all', 'above', 'did', 'ma', 'my', "that'll", 'here', 'ain', 'have', 'at', 'our', "mightn't", 'by'}
"""

# This function encodes a unicode string *s* to ascii string.
def unicodeProc(s):
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore') # this returns <class 'bytes'>
    s = s.decode('ASCII')                                          # this returns <class 'str'>
    return s


##
# This function returns a preprossed string *s*.
# Parameters:
#
# status = True or False, depending on whether some preprocessing has been already done,
# i.e., (1) the strings were brought to the lower case;
#       (2) punctuation marks except for "-" can be erased;
#       (3) specifial characters were eliminated/replaced.
#
# punction = True of False, depending on whether to erase punctuation marks except for "-".
#
# numbers = 'default': we keep a number as it is;
# numbers = 'base':    we bring all the numbers to the same base (numbers in words transformed to numbers in digits);
# numbers = 'token':   we do the case for n='base' and transform digit-containing strings to 'NUMBER' token.
#
# stopWords = True or False, depending on whether to eliminate the stopwords.
##
def preprocess(s, status, punctuation, numbers, stopWords):
    if status==0:   # preprocessing full pipeline
        
        # 1. everything to lower-case
        s = s.lower() 
        # cleansing of redundant parantheses
        s = s.replace('(s)','s')
        
        #print(s)

        # 2. punctuation marks
        if punctuation == 'y':    
            # punctuation marks EXCEPT FOR "-" are replaced with spaces
            # "-" is left at first since it is contained in the numbers and other compound words. 
            for i in ".,?!:;(){}[]/":
                s = s.replace(i, " ")
                
            s = s.replace(" - "," ")    # elimination of dash
            s = s.replace(" -- "," ")   # elimination of dash, another format
            
        else:
            for i in ".,?!:;(){}[]/":
                s = s.replace(i, " "+i+" ")

        #print(s)

        # 3. special character processing/elimination

        s = s.replace('&', ' and ')
        
        # "%"-related content, part 1
        s = s.replace('%', ' percent ')
        # currencies
        s = s.replace('$', ' dollar ')
        s = s.replace('€', ' euro ')
        s = s.replace('£', ' pound ')
        s = s.replace('¥', ' yen ')
        # "%"-related content, part 2
        s = s.replace(' per cent ', ' percent ')

        s = unicodeProc(s)   # dealing with unicode symbols
        
        # others
        if punctuation =='y':
            s = s.replace("'","")                    # apostrophe is eliminated
            s = re.sub("[^a-z|0-9|\-|\s]", " ", s)   # anything accept for letters, numbers, "-" or a space 
                                                     # is replaced with a space
                                                     # (e.g., a hashtag)
        else:
            # anything accept for letters, numbers, "-" , punctuation marks, apostrophe or space is replaced with a space
            # (e.g., a hashtag)
            s = re.sub("[^a-z|0-9|\-|.|,|?|!|:|;|(|)|{|}|/|\[|\]|'|\s]", " ", s)   
        
        #print(s)
    
    # 4. elimination of unnecessary spaces and splitting of string to separate words
    s = s.split()

    #print(s)
    
    # 5. dealing with numbers
    if numbers=='default':   # numbers in words and digits are not touched
        s = ' '.join(s)
    else:   # bring numbers to the same base:
            # conversion of numbers in words into numbers
        joinedString = ''    
        num = ''
        temp = ''
        s_new = ''
        i = 0
        j = 0
        while i<len(s):
            while j<len(s):
                #print(i)
                #print(j)
                joinedString = ' '.join(s[i:(j+1)])
                #print(joinedString)

                try:
                    num = w2n.word_to_num(joinedString)
                    #print('converted')
                    if num==int(joinedString):
                        #print('pure digit')
                        if i == j:
                            s_new = s_new + ' ' + joinedString
                        else:
                            s_new = s_new + ' ' + temp 
                        i = j + 1
                    else:
                        #print('no pure ditit')
                        if str(num)!=temp:
                            temp = str(num)
                        else: 
                            s_new = s_new + ' ' + temp
                            i = j
                            j = j - 1

                except:
                    #print('did not convert')
                    if i == j:
                        s_new = s_new + ' ' + joinedString
                    else:
                        s_new = s_new + ' ' + temp 
                    i = j + 1
                j = j + 1
                #print(temp)
                #print(s_new)
                #print("")
                
        
        # bring ordinals in words to ordinals in numbers
        s_new = s_new.replace(" first "," 1st ") 
        s_new = s_new.replace(" second "," 2nd ") 
        s_new = s_new.replace(" third "," 3rd ") 
        s_new = s_new.replace(" fourth "," 4th ") 
        s_new = s_new.replace(" fifth "," 5th ") 
        s_new = s_new.replace(" sixth "," 6th ") 
        s_new = s_new.replace(" seventh "," 7th ") 
        s_new = s_new.replace(" eighth "," 8th ") 
        s_new = s_new.replace(" ninth "," 9th ") 
        s_new = s_new.replace(" tenth "," 10th ")
        
        s = s_new.split()
         
        # replacement of number-containing strings with "NUMBER"
        if numbers=='token':
            for i in range(len(s)):
                if re.search("[0-9]+",s[i]):
                    s[i] = 'NUMBER'
                    
        s = ' '.join(s)    # concatanating a list of string to a single string s

    #print(s)
    
    # 6. "stop words" elimination
    if stopWords=='y':
        s = s.split()                
        for i in STOP_WORDS:
            while s.count(i)!=0:
                s.remove(i)
        s = ' '.join(s)    # concatanating a list of string to a single string s

    #print(s)
    
    return s


##
# This function returns a preprossed string CSV from *inputFile* to *outputFolder*.
# Parameters:
#
# inputFile = path to the CSV file with string data; required: id-s in the 1st column, and strings in the 2nd column!
#
# status = True or False, depending on whether some preprocessing has been already done,
# i.e., (1) the strings were brought to the lower case;
#       (2) punctuation marks except for "-" can be erased;
#       (3) specifial characters were eliminated/replaced.
#
# punction = True of False, depending on whether to erase punctuation marks except for "-".
#
# numbers = 'default': we keep a number as it is;
# numbers = 'base':    we bring all the numbers to the same base (numbers in words transformed to numbers in digits);
# numbers = 'token':   we do the case for n='base' and transform digit-containing strings to 'NUMBER' token.
#
# stopWords = True or False, depending on whether to eliminate the stopwords.
#
# outputFolder = location for the output, i.e., preprocessed CSV file.
##
def preprocessDF(inputFile, status, punctuation, numbers, stopWords, outputFolder):
    df = pd.read_csv(inputFile, sep=None, header=None, engine='python')
    
    # getting rid of empty labels or profiles
    df = df.dropna()
    df = df.reset_index()
    df = df.drop(['index'],axis=1)
    
    df_preprocessed = {'id':[],'profile':[]}
    df_preprocessed['id'] = df[0].values.tolist()
    
    x = ''
    for i in range(len(df)):
        x = preprocess(df[1][i], status, punctuation, numbers, stopWords)
        df_preprocessed['profile'].append(x)
        
        #print((i, len(x)))
        #sys.stdout.flush()
        
        # periodic status reporting
        if (i+1) % 100 ==0:
             print(str(i+1)+' elements have already been preprocessed')
             sys.stdout.flush()
                
    df_preprocessed = pd.DataFrame(df_preprocessed) 
    
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
     
    outputFile = os.path.abspath(outputFolder+'/'+basename(inputFile)[:-4]+'-s_'+str(status)+'-p_'+punctuation+ \
                                 '-n_'+numbers+'-w_'+stopWords+'.csv')
    
    df_preprocessed.to_csv(outputFile, header=False,index=False)
    print('Strings in '+inputFile+' were preprocessed and stored in '+outputFile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocessing tool')
    parser.add_argument('-i', '--inputFile', help='path to input file')
    parser.add_argument('-s', '--status', choices = [0,1], type=int,default=0, help='0: from scratch, 1: without cleansing')
    parser.add_argument('-p', '--punctuation', choices = ['y','n'],default='y',help='y: delete punctuation, n: otherwise')
    parser.add_argument('-n', '--numbers', choices = ['default','base','token'],default ='base',help='default: no action, base: all numbers in same base, token: replace all numbers with NUMBER')
    parser.add_argument('-w', '--stopWords', choices = ['y','n'],default='y',help='y: delete punction, n: otherwise')
    parser.add_argument('-o', '--outputFolder', help='path to output folder, default to directory of input file')
    args = parser.parse_args()
    
    inputFile = args.inputFile
    status = args.status
    punctuation = args.punctuation
    numbers = args.numbers
    stopWords = args.stopWords
    outputFolder = args.outputFolder

    
    key = []   # key for typo detection
    inputFileDict = checkParam.checkParam(inputFile,'--inputFile',PWD)
    key.append(inputFileDict['key'])

    if outputFolder==None:
        outputFolder = os.path.abspath(os.path.dirname(inputFile))
        print('')
        print('--outputFolder has been set to default')
    else:
        if outputFolder[0]=='/':
            outputFolder = os.path.abspath(outputFolder)
        else:
            outputFolder = os.path.abspath(PWD+'/'+outputFolder)
            
    if not (-1 in key):   
        print("")
        print('--inputFile:    ', inputFile)
        print('--status:       ', status)
        print('--punctuation:  ', punctuation)
        print('--numbers:      ', numbers)
        print('--stopWords:    ', stopWords)
        print('--outputFolder: ', outputFolder)
        print("")
        preprocessDF(inputFile, status, punctuation, numbers, stopWords, outputFolder)
        print("")
    else:
        print("")
        print('Your parameters contain typos. Please try again')
        print("")
        parser.print_help()
        print("")
    



#preprocess(s, status, punctuation, numbers, stopWords)
"""
print("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]!  other words ten third end")
print("")

print(0,'y','default','y')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]!  other words ten third end",\
                 0,'y','default','y'))
print("")

print(0,'y','base','y')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]!  other words ten third end",\
                  0,'y','base','y'))
print("")

print(0,'n','base','y')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]!  other words ten third end",\
                  0,'n','base','y'))
print("")

print(0,'n','base','n')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]!  other words ten third end",\
                  0,'n','base','n'))
print("")

print(0,'n','token','n')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]! other words ten third end",\
                 0,'n','token','n'))
print("")

print(0,'n','token','y')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]! other words ten third end",\
                 0,'n','token','y'))
print("")

print(0,'y','token','y')
print(preprocess("This is an Example of #$% the 5th Preprocessing with Macy's version one hundred #fifty-eight[]! other words ten third end",\
                 0,'y','token','y'))
print("")
print("")
"""

"""
print("Alliance '90/The Greens")
print("")

print(0,'n','base','n')
print(preprocess("Alliance '90/The Greens",\
                 0,'n','base','n'))
print("")

print(0,'n','token','n')
print(preprocess("Alliance '90/The Greens",\
                 0,'n','token','n'))
print("")

print(0,'y','base','y')
print(preprocess("Alliance '90/The Greens !",\
                 0,'y','base','y'))
print("")

print(0,'y','base','n')
print(preprocess("Alliance '90/The Greens !",\
                 0,'y','base','n'))
print("")
"""


#print(preprocess(""))
#print(len(preprocess("")))   # 0
#print(preprocess("")=="")    # True
#print(preprocess(" "))
#print(len(preprocess(" ")))  # 0
#print(preprocess(" ")==" ")  # False
#print(preprocess(" ")=="")   # True
