import pickle
from language import *
#from top_down_learning_NC import *

import sys, os
#import json
class Data:
  def __init__(self):
    self.graph_to_label = {}
    self.graphs = set()
    self.A = []
    self.X_node = {}
    self.X_edge = {}
    self.chosen_depth = 1
    self.succ_node_to_nodes = {}
    self.pred_node_to_nodes = {}
    self.nodes_to_edge = {}
    self.feature_list = []
    self.feature_list_rev = []



def data_loader(dataset):
      
  with open('datasets/{}/X.pickle'.format(dataset),'rb') as f:
    X = pickle.load(f)
  with open('datasets/{}/Y.pickle'.format(dataset),'rb') as f:
    Y = pickle.load(f)
  with open('datasets/{}/tr.pickle'.format(dataset), 'rb') as f:
    train_nodes = pickle.load(f)
  with open('datasets/{}/te.pickle'.format(dataset), 'rb') as f:
    test_nodes = pickle.load(f)
  with open('datasets/{}/va.pickle'.format(dataset), 'rb') as f:
    val_nodes = pickle.load(f)
  
  print("Load Data Done")
   
  label_len = len(Y[0])
  feature_len = len(X[0])
  node_len = len(X)
  
  if os.path.isfile('datasets/{}/succ_node_to_nodes.pickle'.format(dataset)):
    with open('datasets/{}/succ_node_to_nodes.pickle'.format(dataset),'rb') as f:
      succ_node_to_nodes = pickle.load(f) 
    with open('datasets/{}/pred_node_to_nodes.pickle'.format(dataset),'rb') as f:
      pred_node_to_nodes = pickle.load(f) 
    with open('datasets/{}/node_to_nodes.pickle'.format(dataset),'rb') as f:
      node_to_nodes = pickle.load(f) 
  else:
    print("There is no node to nodes map we generate it")
    succ_node_to_nodes = {}
    pred_node_to_nodes = {}
    node_to_nodes = {}
  
    for i in range(node_len):
      succ_node_to_nodes[i] = set()
      pred_node_to_nodes[i] = set()
      node_to_nodes[i] = set()
    
    for i in range(node_len):
      for j in range(node_len):
        if A[i][j] > 0 and i != j:
          succ_node_to_nodes[i].add(j)
          pred_node_to_nodes[j].add(i)
          node_to_nodes[j].add(i)
          node_to_nodes[i].add(j)
    
    with open('dataset/{}/succ_node_to_nodes.pickle'.format(dataset), 'wb') as f:
      pickle.dump(succ_node_to_nodes, f, pickle.HIGHEST_PROTOCOL)
    with open('dataset/{}/pred_node_to_nodes.pickle'.format(dataset), 'wb') as f:
      pickle.dump(pred_node_to_nodes, f, pickle.HIGHEST_PROTOCOL)
    with open('dataset/{}/node_to_nodes.pickle'.format(dataset), 'wb') as f:
      pickle.dump(node_to_nodes, f, pickle.HIGHEST_PROTOCOL)
    
  data_set_complexity = feature_len * node_len
  node_to_label = {}
  label_to_nodes = {}
  
  nodes = set()
  for node in range(node_len):
    nodes.add(node)
    for label in range(label_len):
      if not label in label_to_nodes:
        label_to_nodes[label] = set() 
      if Y[node][label] > 0:
        label_to_nodes[label].add(node)
        node_to_label[node] = label

  feat_values = set()
  for i, node in enumerate(X):
    for j, feat in enumerate(X[i]):
      feat_values.add(feat)
 
  if len(set(feat_values)) == 2:
    is_one_hot = True
  else:
    is_one_hot = False

  print(is_one_hot)
  print(feat_values)
  feature_len = len(X[0])
  
  feature_list = []
  feature_list_rev = []
  min_max_features = []
  
  if is_one_hot:
    for i, feat in enumerate(X[0]):
      feature_list.append([0.0, 1.0])
      feature_list_rev.append([0.0, 1.0])
      min_max_features.append([0.0, 1.0])


  else: # not one_hot
    for i, feat in enumerate(X[0]):
      feature_list.append([])
      feature_list_rev.append([])
      min_max_features.append([])


    for i, node in enumerate(X):
      for j, feat in enumerate(X[i]):
        feature_list[j].append(X[i][j])
    for j, feat in enumerate(X[0]):
      feature_list[j] = sorted(feature_list[j])
      
      feature_list_rev[j] = copy.deepcopy(feature_list[j])
      feature_list_rev[j].reverse()
      min_max_features[j] = [(feature_list[j][0], feature_list[j][len(feature_list[j]) - 1])]


  data = Data()
  data.node_to_label = node_to_label
  data.label_to_nodes = label_to_nodes
  data.feature_list = feature_list
  data.feature_list_rev = feature_list_rev
  data.min_max_feature = min_max_features
  data.dict = dict()        
  data.is_one_hot = is_one_hot
  data.train_nodes = train_nodes
  data.val_nodes = val_nodes
  data.test_nodes = test_nodes
  data.nodes = nodes


  data.X_node = X
  data.succ_node_to_nodes = succ_node_to_nodes
  data.pred_node_to_nodes = pred_node_to_nodes
  print("Is one hot : {}".format(is_one_hot))
  if dataset == 'BA-Shapes' or dataset == 'Tree-Cycles':
    data.epsilon = 10
    data.is_undirected = True
  elif dataset == 'Wisconsin' or dataset == 'Texas' or dataset == 'Cornell':
    data.epsilon = 1
    data.is_undirected = False 
  else:
    print("Not implemented")
    raise 
  data.expected = 1.2

  #simple data
  if data_set_complexity < 10000:
    data.chosen_depth = 3 
  elif data_set_complexity < 100000:
    data.chosen_depth = 2 
  else:
    data.chosen_depth = 1 
   
  data.is_undirected = True

  return data
    
  
  
