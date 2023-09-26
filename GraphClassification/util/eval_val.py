import copy
import os, sys, pickle

def find_max(my_list):
  max_idx = -1
  max_val = -1
  for i in range(len(my_list)):
    if my_list[i] > max_val:
      max_idx = i
      max_val = my_list[i]
  return max_idx


def eval_validation(graph_scores, data):
  correct = 0
  incorrect_label_len = [0, 0]
  for _, val_graph in enumerate(data.val_graphs):
    score0 =  graph_scores[val_graph][0]
    score1 =  graph_scores[val_graph][1]
    if score0 == 0 and score1 == 0:
      continue
    score_list = [score0, score1]
    max_idx = find_max(score_list)
    if max_idx == data.graph_to_label[val_graph]:
      correct = correct + 1
    else:
      incorrect_label_len[max_idx] += 1
  fitted_label = find_max(incorrect_label_len)
  return (correct, fitted_label) 


def map_val_graphs_to_scores(data, dataset):
  val_graph_to_scores = {}      
  described_val_graphs = set()
  for _, val_graph in enumerate(data.val_graphs):
    val_graph_to_scores[val_graph] = [0, 0]  
  files = os.listdir("datasets/{}/learned_GDL_programs/bu".format(dataset))        
  for _, pkl in enumerate(files):
    with open('datasets/{}/learned_GDL_programs/bu/{}'.format(dataset, pkl), 'rb') as f:
      learned_set = pickle.load(f)
    for _, learned_tuple in enumerate(learned_set):
      label = learned_tuple[0]
      learned_GDL_pgm = learned_tuple[1]
      score = learned_tuple[2]
      chosen_graphs = learned_tuple[3]
      chosen_val_graphs = chosen_graphs & data.val_graphs
      described_val_graphs = described_val_graphs | chosen_val_graphs
      for _, val_graph in enumerate(chosen_graphs & data.val_graphs):
        if val_graph_to_scores[val_graph][label] < score:
          val_graph_to_scores[val_graph][label] = score
  return (val_graph_to_scores, described_val_graphs)


def find_default_and_fitted_label(data, dataset):
  val_graph_to_scores = {}
  for _, val_graph in enumerate(data.val_graphs):
    val_graph_to_scores[val_graph] = [0, 0]

  left_graphs = copy.deepcopy(data.val_graphs)
  (val_graph_to_scores, described_val_graphs) = map_val_graphs_to_scores(data, dataset)
  (correct, fitted_label) = eval_validation(val_graph_to_scores, data)
  left_graphs = left_graphs - described_val_graphs
  left_graphs_list = [0,0]
  left_graphs_len = 0
  for _, graph in enumerate(left_graphs):
    left_graphs_len += 1
    left_graphs_list[data.graph_to_label[graph]] += 1
  #print("==============")
  #print(left_graphs_list)
  #print("==============")
  default_label = find_max(left_graphs_list)
  return (default_label, fitted_label, left_graphs_len)


def find_val_threshold(default_label, fitted_label, amplify, val_threshold, data, dataset):
  val_graph_to_scores = {}
  for _, val_graph in enumerate(data.val_graphs):
    val_graph_to_scores[val_graph] = [0, 0]
    val_graph_to_scores[val_graph][default_label] = 0.01


  #for label in range(len(data.label_to_graphs)):
  files = os.listdir("datasets/{}/learned_GDL_programs/bu".format(dataset))        
  for _, pkl in enumerate(files):
    with open('datasets/{}/learned_GDL_programs/bu/{}'.format(dataset, pkl), 'rb') as f:
      learned_set = pickle.load(f)
    for _, learned_tuple in enumerate(learned_set):
      label = learned_tuple[0]
      learned_GDL_pgm = learned_tuple[1]
      score = learned_tuple[2]
      chosen_graphs = learned_tuple[3]
      chosen_val_graphs = chosen_graphs & data.val_graphs
      if len(chosen_val_graphs) < val_threshold:
        continue
      if label == fitted_label:
        score = score * amplify
      for _, val_graph in enumerate(chosen_graphs & data.val_graphs):
        if val_graph_to_scores[val_graph][label] < score:
          val_graph_to_scores[val_graph][label] = score
  (correct, _) = eval_validation(val_graph_to_scores, data)
  return correct 


def search_hyperparameters(data, dataset):
  default_label = 0
  best_correct = 0
  fitted_label = 0
  best_amplify = 1.0
  best_val_threshold = 0
  (default_label, fitted_label, left_graphs_len) = find_default_and_fitted_label(data, dataset)

  (graph_scores, _) = map_val_graphs_to_scores(data, dataset)

  amplify_candidates = [1.0, 0.98, 0.94, 0.92, 0.90]
  best_graph_scores = copy.deepcopy(graph_scores)
  for _, amplify in enumerate(amplify_candidates):
    tmp_graph_scores = copy.deepcopy(graph_scores)
    for _, val_graph in enumerate(data.val_graphs):
      score = tmp_graph_scores[val_graph][fitted_label]
      score = score * amplify
      tmp_graph_scores[val_graph][fitted_label] = score
    (correct, _) = eval_validation(tmp_graph_scores, data)
    if correct >= best_correct:
      best_correct = correct
      best_amplify = amplify


  val_graphs_len_thresholds = []
  for i in range(5):
    val_graphs_len_thresholds.append(int(data.epsilon * i))
  val_graphs_len_thresholds = list(set(val_graphs_len_thresholds))
  for _, threshold in enumerate(val_graphs_len_thresholds):
    correct = find_val_threshold(default_label, fitted_label, amplify, threshold, data, dataset)
    if correct >= best_correct:
      best_correct = correct
      best_val_threshold = threshold


  print("Default label : {}".format(default_label))
  print("Fitted label : {}".format(fitted_label))
  print("Best amplify : {}".format(best_amplify))
  print("Best threshold : {}".format(best_val_threshold))
  val_score = best_correct - left_graphs_len
  #print()
  #print()
  print("======================================")
  print("Val Score : {}".format(val_score))
  print("======================================")
  return (default_label, fitted_label, best_amplify, best_val_threshold)







