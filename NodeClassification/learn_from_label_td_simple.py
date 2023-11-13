import pickle
import argparse
from language import *
from jargon import *
from synthesis.simple_learn import learn_sentences
from data_loader import *
from graph_additional_learn import *




def learn(dataset, target_label):
  data = data_loader(dataset)

  data.original_labeled_nodes = data.train_nodes & data.label_to_nodes[target_label]
  data.left_nodes = data.train_nodes & data.label_to_nodes[target_label]


  learned_GDL_programs_set = learn_sentences(data)
 

  #print(data.default_score)
  if data.is_one_hot == True:
    additional_GDL_programs = additional_learn_GDL_programs(data)
    learned_GDL_programs_set = learned_GDL_programs_set | additional_GDL_programs

  learned_tuples_set = set()
  for learned_GDL_program in learned_GDL_programs_set:
    chosen_nodes = eval_GDL_program_NC_DFS(learned_GDL_program, data)
    chosen_train_nodes = chosen_nodes & data.train_nodes    
    score = float(len(data.original_labeled_nodes & chosen_train_nodes) / (len(chosen_train_nodes) + data.epsilon))
    learned_tuple = (target_label, learned_GDL_program, score, frozenset(chosen_nodes))
    learned_tuples_set.add(learned_tuple)
  with open('datasets/{}/learned_GDL_programs/td/learned_GDL_programs_for_label_{}.pickle'.format(dataset, target_label), 'wb') as f:
    pickle.dump(learned_tuples_set, f, pickle.HIGHEST_PROTOCOL)
    

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset")
  parser.add_argument('-l', '--label', help="target label")
  
  args = parser.parse_args()

  print(f"name: {args.dataset}")
  dataset = args.dataset
  label = int(args.label)
  
  learn(dataset, label)  
