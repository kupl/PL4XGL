import copy
import pickle
from language import *

def find_max_0(my_list):
  max_idx = -1
  max_val = -1

  for i in range(len(my_list)):
    if my_list[i][0] > max_val:
      max_idx = i
      max_val = my_list[i][0]

  return max_idx

def find_max(my_list):
  max_idx = -1
  max_val = -1

  for i in range(len(my_list)):
    if my_list[i] > max_val:
      max_idx = i
      max_val = my_list[i]
  return max_idx


def zeros(data):
  lst = []
  for i in range(len(data.label_to_nodes)):
    lst.append(0)
  return lst


def eval_validation(node_scores, data):
  correct = 0
  incorrect_label_len = zeros(data)
  for _, val_node in enumerate(data.val_nodes):
    if sum(node_scores[val_node]) == 0:
      continue    
    max_idx = find_max(node_scores[val_node])
    if max_idx == data.node_to_label[val_node]:
      correct = correct + 1
    else:
      incorrect_label_len[max_idx] += 1
  fitted_label = find_max(incorrect_label_len)
  return (correct, fitted_label)



def map_val_nodes_to_scores(data, dataset):
  val_node_to_scores = {}
  label_len = len(data.label_to_nodes)
  described_val_nodes = set()
  for _, val_node in enumerate(data.val_nodes):
    val_node_to_scores[val_node] = zeros(data)
  for my_label in range(label_len):    
    with open('datasets/{}/learned_GDL_programs/td/learned_GDL_programs_for_label_{}.pickle'.format(dataset, my_label), 'rb') as f:
      learned_tuples_set = pickle.load(f) 
    for _, learned_tuple in enumerate(learned_tuples_set):
      label = learned_tuple[0]
      score = learned_tuple[2]
      chosen_nodes = learned_tuple[3]
      chosen_val_nodes = chosen_nodes & data.val_nodes
      described_val_nodes = described_val_nodes | chosen_val_nodes
      for _, val_node in enumerate(chosen_val_nodes):
        if val_node_to_scores[val_node][label] < score:
          val_node_to_scores[val_node][label] = score
  return (val_node_to_scores, described_val_nodes)



def find_default_and_fitted_label(data, dataset):
  left_nodes = copy.deepcopy(data.val_nodes)
  (val_node_to_scores, described_val_nodes) = map_val_nodes_to_scores(data, dataset)
  (_, fitted_label) = eval_validation(val_node_to_scores, data)

  left_nodes = left_nodes - described_val_nodes
  
  left_nodes_list = zeros(data)
  left_nodes_len = 0
  for _, node in enumerate(left_nodes):
    left_nodes_len += 1
    left_nodes_list[data.node_to_label[node]] += 1
  default_label = find_max(left_nodes_list)
  return (default_label, fitted_label, left_nodes_len)


def find_val_threshold(default_label, fitted_label, amplify, val_threshold, data, dataset):
  val_node_to_scores = {}
  label_len = len(data.label_to_nodes)
  for _, val_node in enumerate(data.val_nodes):
    val_node_to_scores[val_node] = zeros(data)
    val_node_to_scores[val_node][default_label] = 0.01
  for my_label in range(label_len):
    with open('datasets/{}/learned_GDL_programs/td/learned_GDL_programs_for_label_{}.pickle'.format(dataset, my_label), 'rb') as f:
      learned_tuples_set = pickle.load(f) 
    for _, learned_tuple in enumerate(learned_tuples_set):
      label = learned_tuple[0]
      learned_GDL_pgm = learned_tuple[1]
      score = learned_tuple[2]
      chosen_nodes = learned_tuple[3]  
      chosen_val_nodes = chosen_nodes & data.val_nodes
      if len(chosen_val_nodes) < val_threshold:
        continue  
      if label == fitted_label:
        score = score * amplify
      for _, val_node in enumerate(chosen_nodes & data.val_nodes):
        if val_node_to_scores[val_node][label] < score:
          val_node_to_scores[val_node][label] = score
  (correct, _) = eval_validation(val_node_to_scores, data)
  return correct
  



def search_hyperparameters(data, dataset):
  default_label = 0
  best_correct = 0
  fitted_label = 0
  best_amplify = 1.0
  best_val_threshold = 0
  (default_label, fitted_label, left_nodes_len) = find_default_and_fitted_label(data, dataset)
  amplify_candidates = [1.0, 0.98, 0.94, 0.92, 0.90]


  (node_scores, _) = map_val_nodes_to_scores(data, dataset)
  print("Default lable :{}".format(default_label))
  print("Fitted lable :{}".format(fitted_label))

  amplify_candidates = [0.90, 0.92, 0.94, 0.96, 0.98, 1.0]
  for _, amplify in enumerate(amplify_candidates):
    tmp_node_scores = copy.deepcopy(node_scores)
    for _, val_node in enumerate(data.val_nodes):
      score = tmp_node_scores[val_node][fitted_label]
      score = score * amplify
      tmp_node_scores[val_node][fitted_label] = score
    (correct, _) = eval_validation(tmp_node_scores, data)
    print()
    print("Amplify : {}".format(amplify))
    print("Correct : {}".format(correct))

    if correct >= best_correct:
      best_correct = correct
      best_amplify = amplify
  

      
  print("Default_lablel : {}".format(default_label))
  print("Fitted_label : {}".format(fitted_label))
  print("Best amplify : {}".format(best_amplify))
  val_nodes_len_thresholds = []
  for i in range(5):
    val_nodes_len_thresholds.append(int(data.epsilon * i))
  val_nodes_len_thresholds = list(set(val_nodes_len_thresholds))
  for _, threshold in enumerate(val_nodes_len_thresholds):
    correct = find_val_threshold(default_label, fitted_label, amplify, threshold, data, dataset)
    if correct >= best_correct:
      best_correct = correct
      best_val_threshold = threshold
      
      
  print("Default label : {}".format(default_label))
  print("Fitted label : {}".format(fitted_label))
  print("Best amplify : {}".format(best_amplify))
  print("Best threshold : {}".format(best_val_threshold))
  val_score = best_correct - left_nodes_len
  print("======================================")
  print("Val Score : {}".format(val_score))
  print("======================================")
  return (default_label, fitted_label, best_amplify, best_val_threshold)