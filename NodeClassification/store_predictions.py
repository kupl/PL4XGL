import pickle
import json
from language import *
from data_loader import *
from util import search_hyperparameters, find_max_0



def store_predictions(dataset):
  data = data_loader(dataset)
  all_nodes = data.test_nodes | data.val_nodes | data.train_nodes
  label_len = len(data.label_to_nodes)
  print(label_len)

  
  print("=======================================================")
  (default_label, fitted_label, amplify, val_threshold) = search_hyperparameters(data, dataset)
  print("=======================================================")
  print("Default label : {}".format(default_label))
  print("Fitted label : {}".format(fitted_label))
  print("Amplify : {}".format(amplify))
  print("Val threshold : {}".format(val_threshold))  
  default_GDL_pgm = GDL()
  default_GDL_pgm.nodeVars = [{}]
  default_GDL_pgm.edgeVars = []
  chosen_nodes = eval_GDL_program_NC_DFS(default_GDL_pgm, data)
  
  all_node_to_scores = {}
  for _, node in enumerate(all_nodes):
    all_node_to_scores[node] = []
    for label in range(label_len):
      all_node_to_scores[node].append((-1, None))
    all_node_to_scores[node][default_label] = (0.0, default_GDL_pgm)
  
  for my_label in range(label_len):
    print("Processing label {}".format(my_label))
    with open('datasets/{}/learned_GDL_programs/td/learned_GDL_programs_for_label_{}.pickle'.format(dataset, my_label), 'rb') as f:
      learned_tuples_set = pickle.load(f) 
    check_redundant_GDL_program = set()
    print()
    print("Label : {}".format(my_label))
    print()
    for _, learned_tuple in enumerate(learned_tuples_set):
      label = learned_tuple[0]
      learned_GDL_pgm = learned_tuple[1]
      score = learned_tuple[2]
      chosen_nodes = learned_tuple[3]

      key = (json.dumps(learned_GDL_pgm.nodeVars), json.dumps(learned_GDL_pgm.edgeVars))
      if key in check_redundant_GDL_program:
        continue
      else:
        check_redundant_GDL_program.add(key)
      chosen_val_nodes = chosen_nodes & data.val_nodes
      if len(chosen_val_nodes) < val_threshold:
        continue
      if label == fitted_label:
        score = score * amplify
        
      for _, node in enumerate(chosen_nodes):
        if all_node_to_scores[node][label][0] < score:
          all_node_to_scores[node][label] = (score, learned_GDL_pgm)

  predicted_nodes = []
  for i in range(len(data.label_to_nodes)):
    predicted_nodes.append(set())
  for _, node in enumerate(all_nodes):
    prediction = find_max_0(all_node_to_scores[node])    
    predicted_nodes[prediction].add(node)

  with open('predicted/{}_predicted.pickle'.format(dataset), 'wb') as f:
    pickle.dump(predicted_nodes, f)
  print()
  print()
  print("Done")
  for i in range(len(data.label_to_nodes)):
    print(" Label {} len : {}".format(i, len(predicted_nodes[i])))
  print("Predictions are stored in : predicted/{}_predicted.pickle".format(dataset))      
  