import numpy as np
import csv
import pandas as pd

class SentimentCorpus:
    
    def __init__(self, train_per=0.8, dev_per=0, test_per=0.2):
        '''
        prepare dataset
        1) build feature dictionaries
        2) split data into train/dev/test sets 
        '''
        X, y, feat_dict, feat_counts, X_NH = build_dicts()
        self.nr_instances = y.shape[0]
        self.nr_features = X.shape[1]
        self.X = X
        self.y = y
        self.feat_dict = feat_dict
        self.feat_counts = feat_counts
        self.X_NH = X_NH

        train_y, dev_y, test_y, train_X, dev_X, test_X, train_X_NH, test_X_NH = split_train_dev_test(self, self.X, self.y, self.X_NH, train_per, dev_per, test_per)
        self.train_X = train_X
        self.train_y = train_y
        self.dev_X = dev_X
        self.dev_y = dev_y
        self.test_X = test_X
        self.test_y = test_y
        self.train_X_NH = train_X_NH
        self.test_X_NH = test_X_NH

def split_train_dev_test(self, X, y, X_NH, train_per, dev_per, test_per):
    if (train_per + dev_per + test_per) > 1:
        print ("train/dev/test splits should sum to one")
        return
    dim = y.shape[0]
    split1 = int(dim * train_per)
    
    if dev_per == 0:
        train_y, test_y = np.vsplit(y, [split1])
        dev_y = np.array([])
        train_X = X[0:split1,:]
        test_X = X[split1:,:]
        dev_X = np.array([])
        train_X_NH = X_NH[0:split1]
        test_X_NH = X_NH[split1:]
        dev_X_NH = np.array([])     
    else:
        split2 = int(dim*(train_per+dev_per))
        train_y,dev_y,test_y = np.vsplit(y,(split1,split2))
        train_X = X[0:split1,:]
        dev_X = X[split1:split2,:]
        test_X = X[split2:,:]
        
    return train_y,dev_y,test_y,train_X,dev_X,test_X,train_X_NH,test_X_NH

def build_dicts():
    '''
    builds feature dictionaries
    ''' 
    #set the test size
    test_size = 30000
    remove_word_count = 5 # if feature count less than this, remove it 
    feat_counts = {}
    col_list = ["tweet"]
    folder = "train_data/"
    files_to_red = ["twitter_improve_positive.csv", "twitter_improve_negative.csv", "test_improve_positive.csv", "test_improve_negative.csv"]
    # build feature dictionary with counts
    nr_pos = 0
    #leng = 0
    pos_file = pd.read_csv(folder+files_to_red[0], usecols=col_list)
    for line in pos_file["tweet"]:
        if type(line) is type(1.0):
            continue
        if "\"" in line:
            continue
        line.replace("\'", "")
        toks = line.split(" ")
        nr_pos += 1
        if nr_pos >= test_size:
            break
        #leng += len(toks)
        for feat in toks:
            name, counts = feat.split(":")
            name.replace('\'', '')
            if len(name) <= 1:
                continue
            if name not in feat_counts:
                feat_counts[name] = 0
            feat_counts[name] += int(counts)
    
    nr_neg = 0
    neg_file = pd.read_csv(folder+files_to_red[1], usecols=col_list)
    for line in pos_file["tweet"]:
        if type(line) is type(1.0):
            continue
        if "\"" in line:
            continue
        line.replace("\'", "")
        toks = line.split(" ")
        nr_neg += 1
        if nr_neg >= test_size:
            break
        #leng += len(toks)
        for feat in toks:
            name, counts = feat.split(":")
            name.replace('\'', '')
            if len(name) <= 1:
                continue
            if name not in feat_counts:
                feat_counts[name] = 0
            feat_counts[name] += int(counts)
    #print("average lenth:", leng/40000)
    # remove all features that occur less than 5 (threshold) times
    to_remove = []
    for key, value in feat_counts.items():
        if value < remove_word_count:
            to_remove.append(key)
    for key in to_remove:
        del feat_counts[key]

    # map feature to index
    feat_dict = {}
    i = 0
    for key in feat_counts.keys():
        feat_dict[key] = i
        i += 1
        #print(key)

    nr_feat = len(feat_counts) 
    nr_instances = nr_pos + nr_neg
    X = np.zeros((nr_instances, nr_feat), dtype=float)
    y = np.vstack((np.zeros([nr_pos,1], dtype=int), np.ones([nr_neg,1], dtype=int)))

    pos_file = pd.read_csv(folder+files_to_red[0], usecols=col_list)
    nr_pos = 0
    for line in pos_file["tweet"]:
        if type(line) is type(1.0):
            continue
        if "\"" in line:
            continue
        if nr_pos >= test_size:
            break
        line.replace("\'", "")
        toks = line.split(" ")
        for feat in toks:
            name, counts = feat.split(":")
            if name in feat_dict:
                X[nr_pos,feat_dict[name]] = int(counts)
        nr_pos += 1
    
    neg_file = pd.read_csv(folder+files_to_red[1], usecols=col_list)
    nr_neg = 0
    for line in neg_file["tweet"]:
        if type(line) is type(1.0):
            continue
        if "\"" in line:
            continue
        if nr_neg >= test_size:
            break
        line.replace("\'", "")
        toks = line.split(" ")
        for feat in toks:
            name, counts = feat.split(":")
            if name in feat_dict:
                X[nr_pos+nr_neg,feat_dict[name]] = int(counts)
        nr_neg += 1
    
    X_NH = []

    pos_file = pd.read_csv(folder+files_to_red[2], usecols=col_list)
    nr_pos = 0
    for line in pos_file["tweet"]:
        if type(line) is type(1.0):
            continue
        if "\"" in line:
            continue
        #print(line)
        line.replace("\'", "")
        if nr_pos >= test_size:
            break
        toks = str(line).split(" ")
        X_NH.append(toks)
        nr_pos += 1

    neg_file = pd.read_csv(folder+files_to_red[3], usecols=col_list)
    nr_neg = 0
    for line in neg_file["tweet"]:
        if type(line) is type(1.0):
            continue
        if "\"" in line:
            continue
        line.replace("\'", "")
        if nr_neg >= test_size:
            break
        toks = str(line).split(" ")
        X_NH.append(toks)
        nr_neg += 1

    # shuffle the order, mix positive and negative examples
    new_order = np.arange(nr_instances)
    np.random.seed(0) # set seed
    np.random.shuffle(new_order)
    X = X[new_order,:]
    y = y[new_order,:]
    X_NH = [X_NH[i] for i in new_order]
    #print(X[0])
    # for i in range(len(X[0])):
    #     if X[0][i] > 0:
    #         print(list (feat_dict.keys()) [list (feat_dict.values()).index (i)])
    # print(X_NH[0])
    return X, y, feat_dict, feat_counts, X_NH











