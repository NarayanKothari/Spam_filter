import re
import glob
import random
import numpy  
import sys
def OrganizeData():
    TrainSpam=[]
    TrainHam=[]
    TestSpam=[]
    TestHam=[]
    for filename in glob.glob('/home/narayan/Documents/spam filter/enron1/spam/*'):
        R=random.uniform(0,1) 
        if R>0.8:
            TestSpam.append(filename)
        else:
            TrainSpam.append(filename)
    
    for filename in glob.glob('/home/narayan/Documents/spam filter/enron1/ham/*'):
        R=random.uniform(0,1) 
        if R>0.8:
            TestHam.append(filename)
        else:
            TrainHam.append(filename)
    return (TrainHam,TrainSpam,TestHam,TestSpam)


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

TrainHam,TrainSpam,TestHam,TestSpam=OrganizeData()
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

SpamVectorTest=VectorizeDataSet(Dict,Count,TestSpam)
HamVectorTest=VectorizeDataSet(Dict,Count,TestHam)
Prior=float(len(TrainSpam))/len(Train)
sumv=0
no=0
tp=0
tn=0
fn=0
fp=0
#print len(HamVectorTrain)
for Mail in HamVectorTest:
    if(NaiveBayes(Mail,p,q,Prior)>0):
        tn=tn+1
    else:
        fp=fp+1
    print tn, fp
for Mail in SpamVectorTest:
    if(NaiveBayes(Mail,p,q,Prior)<0):
        tp=tp+1
    else:
        fn=fn+1
    print tp,fn
prec = float(tp)/float(tp+fp)
recall = float(tp)/float(tp+fn)
f_one = float(2*prec*recall)/float(prec+recall)
acc = float(tp+tn)/float(tp+tn+fp+fn)
print float(sumv)/len(HamVectorTest)
print "prec=",prec
print "rec= ", recall
print f_one
print acc