import pickle
from language import *
from data_loader import *
from connected import *
import argparse
import datetime
import os,sys
from util import search_hyperparameters, find_max


def store_predictions(dataset):
  if dataset == "BBBP":
    data = load_BBBP()
  elif dataset == "MUTAG":
    data = load_MUTAG()
  elif dataset == "BACE":
    data = load_BACE()
  else:
    raise Exception("Not Implemented")


  all_graphs = data.test_graphs | data.val_graphs | data.train_graphs
  graph_to_scores = {}
  
  print("=======================================================")
  (default_label, fitted_label, amplify, val_threshold) = search_hyperparameters(data, dataset)
  print("=======================================================")

  print("Default label : {}".format(default_label))
  print("Fitted label : {}".format(fitted_label))
  print("Amplify : {}".format(amplify))
  print("Val threshold : {}".format(val_threshold))

  default_GDL_pgm = GDL()
  default_GDL_pgm.nodeVars = [{},{}]
  default_GDL_pgm.edgeVars = [({},0,1)]  
  for _, graph in enumerate(all_graphs):
    graph_to_scores[graph] = [(-1, None), (-1, None)]
    graph_to_scores[graph][default_label] = (0.00, default_GDL_pgm)

  
  files = os.listdir("datasets/{}/learned_GDL_programs/bu".format(dataset))        
  for _, pkl in enumerate(files):
    with open('datasets/{}/learned_GDL_programs/bu/{}'.format(dataset, pkl), 'rb') as f:
      learned_tuple_set = pickle.load(f)
    for _, val in enumerate(learned_tuple_set):
      label = val[0]
      learned_GDL_pgm = val[1]
      score = val[2]
      chosen_graphs = val[3]
      chosen_val_graphs = chosen_graphs & data.val_graphs 
      if len(chosen_val_graphs) < val_threshold:
        continue
      if label == fitted_label:
        score = score * amplify
      for _, graph in enumerate(chosen_graphs):
        if graph_to_scores[graph][label][0] < score:
          graph_to_scores[graph][label] = (score, learned_GDL_pgm)

  my_list = [0,0]
  correct = 0
  my_cnt = 0
  predicted_graphs = [set(),set()] 
  for _, graph in enumerate(all_graphs):
    score0 = graph_to_scores[graph][0][0]
    score1 = graph_to_scores[graph][1][0]
    score_list = [score0, score1]
    max_idx = find_max(score_list)
    predicted_graphs[max_idx].add(graph)    

  with open('predicted/{}_predicted.pickle'.format(dataset), 'wb') as f:
    pickle.dump(predicted_graphs, f)  
  print()
  print()
  print("Done")
  print(" Label 0 len : {}".format(len(predicted_graphs[0])))
  print(" Label 1 len : {}".format(len(predicted_graphs[1])))
  print("Predictions are stored in : predicted/{}_predicted.pickle".format(dataset))
