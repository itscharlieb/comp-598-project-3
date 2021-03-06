
import os, os.path, time, platform, random, csv
import numpy as np
from constants import *

class PerformanceTimer:
    def __init__(self):
        self.times={}
        self.last_time=time.time()
        self.last_label="start"

    def tick(self,label):
        t=time.time()
        delta=t-self.last_time
        self.last_time=t

        if self.last_label not in self.times:
            self.times[self.last_label]=[delta,1]
        self.times[self.last_label][0]+=delta
        self.times[self.last_label][1]+=1

        self.last_label=label

    def report(self):
        for key in self.times:
            t,count=self.times[key]
            print_color(key.upper(),COLORS.GREEN)
            print_color("%s ms (%s times)"%(round(1000*t/count,5),count),COLORS.YELLOW)

def save_report(report):
    doubles=["accuracy","predictions","success count","fail count"]
    keys=["validation size","validation ratio","nn size","learning rate","back count","normalized",
            "random","final learning rate","duration","batch size"]
    for d in doubles:
        keys.append("train "+d)
        keys.append("valid "+d)
    keys.sort()

    items=[]
    for key in keys:
        if key in report:
            item=str(report[key]).replace(",",";").replace(" ","")
            items.append(item)
        else:
            items.append("ERROR")
            print_color("Warning: save report partially failed. key '%s' not in report."%key,COLORS.RED)

    header=",".join(keys)
    filename=LOGFOLDER+os.sep+"hyperparameters.csv"
    data=""
    if not os.path.isdir(LOGFOLDER):
        os.mkdir(LOGFOLDER)
    if not os.path.isfile(filename):
        with open(filename,"w") as f:
            f.write(header+"\n")
    with open(filename,"a") as f:
        f.write(",".join(items)+"\n")

def neuronize(Y):
    #convert Y=[[2],[0],[1]...] to Y=[[0,0,1],[1,0,0],[0,1,0]...], or does nothing if Y=[[1],[0] ...]
    highest=-1
    for i in Y:
        highest=i[0] if i[0]>highest else highest
    if highest==1:
        return Y

    highest=int(highest)
    
    new_y=[[1 if i[0]==j else 0 for j in range(highest+1)] for i in Y]
    return new_y

def get_data_2csv(csv_train,csv_valid,validation_ratio,has_header=True,normalize=False):
    #ignores the first column, optionally ignores the first row (has_header)
    if validation_ratio<0 or validation_ratio>1:
        raise ValueError("bad validation ratio")
    X,Y=[],[]
    with open(csv_train,"r") as f:
        reader=csv.reader(f,delimiter=",")
        if has_header:
            next(reader)
        for line in reader:
            X.append([float(i) for i in line[1:]])

    if normalize:
        X=np.array(X)
        X-=X.mean()
        X/=X.std()

    with open(csv_valid,"r") as f:
        reader=csv.reader(f,delimiter=",")
        if has_header:
            next(reader)
        for line in reader:
            Y.append([float(i) for i in line[1:]])

    XY=[(X[i],Y[i]) for i in range(len(X))]
    random.shuffle(XY)
    
    count=round(validation_ratio*len(X))
    X_train=[a[0] for a in XY[:count]]
    Y_train=[a[1] for a in XY[:count]]
    X_valid=[a[0] for a in XY[count:]]
    Y_valid=[a[1] for a in XY[count:]]

    return X_train,Y_train,X_valid,Y_valid

def get_data_1csv(csv_name,validation_ratio,has_header=True):
    if validation_ratio<0 or validation_ratio>1:
        raise ValueError("bad validation ratio")
    X,Y=[],[]
    with open(csv_name,"r") as f:
        lines= f.readlines()
    if has_header:
        lines=lines[1:]
    random.shuffle(lines)
    X=[[float(i) for i in line.strip().split(",")[1:]] for line in lines]
    Y=[[float(line[0])] for line in lines]
    
    count=round(validation_ratio*len(X))
    X_train=X[:count]
    Y_train=Y[:count]
    X_valid=X[count:]
    Y_valid=Y[count:]

    return X_train,Y_train,X_valid,Y_valid

def add_filename_prefix_to_path(prefix,source):
    #given prefix="test-" and source="/path/to/thingy.csv", returns "/path/to/test-thingy.csv
    split=source.split(os.sep)
    pieces=split[:-1]+[prefix+split[-1]]
    return os.sep.join(pieces)

class Timer:
    #easy way to show updates every X number of seconds for big jobs.
    def __init__(self,interval):
        self.start_time=time.time()
        self.last_time=self.start_time
        self.interval=interval

    def tick(self,text):
        if time.time()>self.last_time+self.interval:
            self.last_time=time.time()
            print_color(text,COLORS.YELLOW)

    def stop(self,label):
        print_color("%s took %s seconds."%(label,round(time.time()-self.start_time,1)),COLORS.YELLOW)

def print_color(text,color=0,end="\n"):
    if platform.system()!="Linux":
        print(text,end=end)
    prefix=""
    if color:
        prefix+="\033[%sm"%(color-10)

    print(prefix+text+"\033[0m",end=end)

