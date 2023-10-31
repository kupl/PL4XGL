import pickle
from language import *
from data_loader import *
from connected import *
from synthesis.btm_up_synthesis_GC import *
import argparse
import os
from util.eval_val import search_hyperparameters, find_max
from store_predictions import store_predictions


def eval_acc_explainability(dataset):
  if dataset == "BBBP":
    data = load_BBBP()
  elif dataset == "MUTAG":
    data = load_MUTAG()
  elif dataset == "BACE":
    data = load_BACE()
  else:
    raise Exception("Not Implemented")

  test_graph_to_scores = {}
  score_pgm_sets= [set(), set()]
  
  print("=======================================================")
  (default_label, fitted_label, amplify, val_threshold) = search_hyperparameters(data, dataset)
  print("=======================================================")


  print("Default label : {}".format(default_label))
  print("Fitted label : {}".format(fitted_label))
  print("Amplify : {}".format(amplify))
  print("Threshold : {}".format(val_threshold))
  
  default_GDL_pgm = GDL()
  default_GDL_pgm.nodeVars = [{},{}]
  default_GDL_pgm.edgeVars = [({},0,1)]
    
  for _, test_graph in enumerate(data.test_graphs):
    test_graph_to_scores[test_graph] = [(-1, None), (-1, None)]
    test_graph_to_scores[test_graph][default_label] = (0.0, default_GDL_pgm)

  
  files = os.listdir("datasets/{}/learned_GDL_programs/bu".format(dataset))        
  for _, pkl in enumerate(files):
    with open('datasets/{}/learned_GDL_programs/bu/{}'.format(dataset, pkl), 'rb') as f:
      learned_set = pickle.load(f)
    for _, val in enumerate(learned_set):
      label = val[0]
      learned_GDL_pgm = val[1]
      score = val[2]
      chosen_graphs = val[3]
      chosen_val_graphs = chosen_graphs & data.val_graphs 
      if len(chosen_val_graphs) < val_threshold:
        continue
      if label == fitted_label:
        score = score * amplify
      score_pgm_sets[label].add((score, learned_GDL_pgm))        
      for _, test_graph in enumerate(chosen_graphs & data.test_graphs):
        if test_graph_to_scores[test_graph][label][0] < score:
          test_graph_to_scores[test_graph][label] = (score, learned_GDL_pgm)
  correct = 0

  fidelity_sum = []
  sparsity_sum = []

  generality_sum = []
  precision_sum = []

  with open("predicted/{}_predicted.pickle".format(dataset), 'rb') as f:
    graph_predictions = pickle.load(f)

  for _, test_graph in enumerate(data.test_graphs):
    score0 = test_graph_to_scores[test_graph][0][0]
    score1 = test_graph_to_scores[test_graph][1][0]
    score_list = [score0, score1]
    max_idx = find_max(score_list)
      
    if test_graph_to_scores[test_graph][max_idx][0] > 0.0:
      prediction = max_idx
      provided_GDL_program = test_graph_to_scores[test_graph][prediction][1]
      print()
      print(provided_GDL_program.nodeVars)
      print(provided_GDL_program.edgeVars)      
      matching_subgraph = find_matching_subgraph(provided_GDL_program, data.graphs[test_graph], data)

      sparsity_score = 1 - (len(matching_subgraph[0]))/(len(data.graphs[test_graph][0]))
      sparsity_sum.append(sparsity_score)
      tmp_scores = [(-1, None),(-1, None)]
      tmp_scores[prediction] = (score_list[prediction], provided_GDL_program)
      if prediction == 0:
        other_label = 1
      else:
        other_label = 0

      flag = False
      for _, (current_score, current_GDL_program) in enumerate(score_pgm_sets[other_label]):
        if current_score > tmp_scores[prediction][0] :
          if eval_GDL_program_DFS(current_GDL_program, data.graphs[test_graph], data) == True:
            # Over approximation
            # To have a fidelity score 1, this branch should be taken, but this cannot be happened
            fidelity_sum.append(1)            
            flag = True
            break
            #raise Exception("Cannot be happened")
      if flag == False:
        fidelity_sum.append(0)

      chosen_graphs = eval_GDL_program_on_graphs_GC(provided_GDL_program, data)     
      correctly_explained_predictions = chosen_graphs & graph_predictions[prediction]
      generality = len(correctly_explained_predictions)/len(graph_predictions[prediction])
      precision = len(correctly_explained_predictions)/len(chosen_graphs)   
      
      print("=============== node : {} ==================".format(test_graph))
      print("Prediction : {}".format(prediction))    
      print_GDL_program(test_graph_to_scores[test_graph][prediction][1])
      print("Score : {}".format(test_graph_to_scores[test_graph][prediction][0]))  
      print("==============================================")    
      
      generality_sum.append(generality)
      precision_sum.append(precision)
    #if test_graph_to_scores[test_graph][max_idx][0] > 0.0:

    if max_idx == data.graph_to_label[test_graph]:
      correct = correct + 1
    # else:
    #   if data.graph_to_label[test_graph] == 1:
    #     my_list[data.graph_to_label[test_graph]] += 1
    #   else:
    #     my_list[0] += 1
  print()
  print("Correct : {}".format(correct))
  print("Test Accuracy : {}".format(float(correct/len(data.test_graphs))))
  print("==========================")

  print("Fidelity : {}".format((sum(fidelity_sum) / len(fidelity_sum))))
  print("Sparsity : {}".format((sum(sparsity_sum) / len(sparsity_sum))))
  print("============================================================")
  print("Generality : {}".format((sum(generality_sum) / len(generality_sum))))
  print("Precision : {}".format((sum(precision_sum) / len(precision_sum))))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset")
  args = parser.parse_args()
  dataset = args.dataset
  store_predictions(dataset)
  print("Stored predictions")
  eval_acc_explainability(dataset)


