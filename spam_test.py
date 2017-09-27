import re
import glob
import random
import numpy  
import sys
def OrganizeData(Spam_dir, ham_dir):
    TrainSpam=[]
    TrainHam=[]
    for filename in glob.glob(Spam_dir):
        TrainSpam.append(filename)
    for filename in glob.glob(ham_dir): 
        TrainHam.append(filename)
    return (TrainHam,TrainSpam)

def OrganizeData_check(dir_chk):
    check = []
    for filename in glob.glob(dir_chk):
        check.append(filename)
    return (check)

class TrieNode:
    def __init__(self,key):
        self.Store=ord(key)
        self.ChildNode=[0]*26
        self.Leaf=0


def AddWord(Parent,Word,Count):
    Letter=Word[0]
    Position=ord(Letter)-97
    if Parent.ChildNode[Position]==0:
        Parent.ChildNode[Position]=TrieNode(Letter)
    if len(Word)==1:
        Parent.ChildNode[Position].Leaf=Count
    else:
        AddWord(Parent.ChildNode[Position],Word[1:],Count)    

def FindWord(Parent,Word):
    Letter=Word[0]
    Position=ord(Letter)-97
    if Parent.ChildNode[Position]==0:
        return False
    if len(Word)==1:
        Count=Parent.ChildNode[Position].Leaf
        return Count
    else:
        return FindWord(Parent.ChildNode[Position],Word[1:])   
    
def MakeEmailList(Filename):
    EmailData=open(Filename).read()
    EmailData= re.sub('[^a-zA-Z!0-9\n]', ' ', EmailData)
    b = "!"
    q = "$"
    c = "excl"
    d = "doll"
    a = "0123456789"
    num = "num "
    for char in b:
        EmailData = EmailData.replace(b,c)
    for char in q:
        EmailData = EmailData.replace(q,d)
    for char in a:
        EmailData = EmailData.replace(char,num)
    EmailWordList=EmailData.lower().split()
    return EmailWordList


def BuildDictionary(DataSet):
    Root=TrieNode('m')
    UniversalWordList=[]
    Count=1
    for Filename in DataSet:
        EmailWordList=MakeEmailList(Filename)
        for Word in EmailWordList:
            if(FindWord(Root,Word)==False):
                AddWord(Root,Word,Count)
                Count=Count+1 
    return (Root,Count)

def VectorizeDataSet(DictionaryRoot,DictionaryCount,DataSet):
    WordVector=numpy.zeros((len(DataSet),DictionaryCount))
    EmailCount=0
    for FileName in DataSet:
        EmailList=MakeEmailList(FileName)
        Count = 0
        for Word in EmailList:
            Count=FindWord(DictionaryRoot,Word)
            if Count!=False:
                WordVector[EmailCount][Count-1]=1
        EmailCount=EmailCount+1
    return WordVector
    

def EstimateProbabilityMasses(SpamVector,HamVector):
    M=len(SpamVector[0])
    SpamWordProb=numpy.zeros(M)
    for i in xrange(0,M):
        SpamWordProb[i]=float(sum(SpamVector[:,i])+0.3)/(len(SpamVector)+0.3*M)
    HamWordProb=numpy.zeros(M)
    for i in xrange(0,M):
        HamWordProb[i]=float(sum(HamVector[:,i])+0.3)/(len(HamVector)+0.3*M)
    return (SpamWordProb,HamWordProb)
print"Make sure you created two labeled folders containing corresponding spam mails and ham mails which will be used for training purpose"
Spam_dir = raw_input("Type spam folder diractory \n Example : /home/narayan/Documents/spam filter/enron1/spam/*\n")
ham_dir = raw_input("Type spam folder diractory \n Example : /home/narayan/Documents/spam filter/enron1/ham/*\n")
print"ho gaya"
TrainHam,TrainSpam =OrganizeData(Spam_dir, ham_dir)
TrainHam = TrainHam[:100]
TrainSpam = TrainSpam[:50]
Train=TrainHam+TrainSpam
(Dict,Count)=BuildDictionary(Train)
SpamVectorTrain=VectorizeDataSet(Dict,Count,TrainSpam)
HamVectorTrain=VectorizeDataSet(Dict,Count,TrainHam)
(p,q)=EstimateProbabilityMasses(SpamVectorTrain,HamVectorTrain)
#print p[1:100]

def NaiveBayes(InputVector,SpamWordProb,HamWordProb,SpamProbPrior):
    log_SpamLikelihood=0
    log_HamLikelihood=0
    for i in xrange(0,len(InputVector)):
        if InputVector[i]==0:
            log_SpamLikelihood=log_SpamLikelihood+numpy.log((1-SpamWordProb[i]))
            log_HamLikelihood=log_HamLikelihood+numpy.log((1-HamWordProb[i]))
        else:
            log_SpamLikelihood=log_SpamLikelihood+numpy.log(SpamWordProb[i])
            log_HamLikelihood=log_HamLikelihood+numpy.log(HamWordProb[i])
    #t = function{P(spam\w1,w2...)/P(Ham\w1,w2...)}
    t = -(log_SpamLikelihood+numpy.log(SpamProbPrior)-log_HamLikelihood-numpy.log(1-SpamProbPrior)) 
    return t
test_dir = raw_input("Type the directory of folder of mails you want to test \n Example : /home/narayan/Documents/spam filter/enron1/test/* \n")
Check =OrganizeData_check(test_dir)
CheckVector = VectorizeDataSet(Dict,Count,Check)
CheckVector = CheckVector[:1000]
Prior=float(len(TrainSpam))/len(Train)
lis=[]
#print len(HamVectorTrain)
for Mail in CheckVector:
    if(NaiveBayes(Mail,p,q,Prior)>0):
        print "Ham mail"
        lis.append(0)
    else:
        print "Spam mail"
        lis.append(1)
print lis
