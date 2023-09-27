import pickle
from language import *
from data_loader import *
import argparse
import datetime
import os,sys
import util
from util import search_hyperparameters, find_max

def eval_acc(dataset, k):
  if dataset == "BBBP":
    data = load_BBBP()
  elif dataset == "MUTAG":
    data = load_MUTAG()
  elif dataset == "BACE":
    data = load_BACE()
  else:
    raise Exception("Not Implemented")

  test_graph_to_scores = {}
  
  train_set = len(data.train_graphs)
  labeled_train_set = len(data.train_graphs & data.label_to_graphs[1])
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
  #graphs = eval_GDL_program_on_graphs_GC(default_GDL_pgm, data)

  top_k_gdl_programs = [[],[]]

  for _, test_graph in enumerate(data.test_graphs):
    test_graph_to_scores[test_graph] = [(-1, None), (-1, None)]
    test_graph_to_scores[test_graph][default_label] = (0.0, default_GDL_pgm)
  
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
      for _, test_graph in enumerate(chosen_graphs & data.test_graphs):
        if test_graph_to_scores[test_graph][label][0] < score:
          test_graph_to_scores[test_graph][label] = (score, learned_GDL_pgm)
      top_k_gdl_programs[label].append((score, learned_GDL_pgm))
  top_k_gdl_programs[0].sort(key=lambda x: x[0], reverse=True)
  top_k_gdl_programs[1].sort(key=lambda x: x[0], reverse=True)
  top_k_gdl_programs[0] = top_k_gdl_programs[0][:int(k)]
  top_k_gdl_programs[1] = top_k_gdl_programs[1][:int(k)]
  
  print("==================== label 0 ==========================")
  for i in range(int(k)):
    print()
    print("GDL program")
    print(top_k_gdl_programs[0][i][1].nodeVars)
    print(top_k_gdl_programs[0][i][1].edgeVars)
  
  print("==================== label 1 ==========================")
  for i in range(int(k)):
    print()
    print("GDL program")
    print(top_k_gdl_programs[1][i][1].nodeVars)
    print(top_k_gdl_programs[1][i][1].edgeVars)
  
  # correct = 0
  # for _, test_graph in enumerate(data.test_graphs):
  #   score0 = test_graph_to_scores[test_graph][0][0]
  #   score1 = test_graph_to_scores[test_graph][1][0]
  #   score_list = [score0, score1]
  #   prediction = find_max(score_list)
  #   print("=============== graph : {} ==================".format(test_graph))
  #   print("Prediction : {}".format(prediction))
  
  #   print_GDL_program(test_graph_to_scores[test_graph][prediction][1])
  #   print("Score : {}".format(test_graph_to_scores[test_graph][prediction][0]))  
  #   print("==============================================")    
  #   print()
  #   if prediction == data.graph_to_label[test_graph]:
  #     correct = correct + 1

  # print()
  # print()
  # print()
  # print("--------------------")  
  # print("Correct : {}".format(correct))
  # print("Test Accuracy : {}".format(float(correct/len(data.test_graphs))))
  # print("--------------------")

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset")
  parser.add_argument('-k', '--topk', help="top k programs")  
  args = parser.parse_args()
  dataset = args.dataset
  k = args.topk
  start = datetime.datetime.now()   
  eval_acc(dataset, k)
  finish = datetime.datetime.now()   
  elapsed = finish - start
  print("Elapsed time: {}".format(elapsed))