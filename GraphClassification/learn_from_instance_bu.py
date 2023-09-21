import pickle
from data_loader import load_MUTAG, load_BBBP, load_BACE 
from btm_up_synthesis_GC import synthesis_bu
import argparse
import datetime
import os,sys


# learn a GDL program from a target graph (target_graph)
def learn(dataset, target_graph):
  if dataset == 'BBBP':
    data = load_BBBP()
  elif dataset == 'MUTAG':
    data = load_MUTAG()
  elif dataset == 'BACE':
    data = load_BACE()
  else:
    raise Exception("Not Implemented")

  data.target_graph = target_graph
  data.target_label = data.graph_to_label[target_graph]
  if data.target_label == -1:
    data.target_label = 0
    
  #training graphs having the same label with the target graph
  data.target_labeled_graphs = data.train_graphs & data.label_to_graphs[data.target_label]
  start = datetime.datetime.now()  
  tuple_set = synthesis_bu(data)
  finish = datetime.datetime.now()
  elapsed = finish - start    
  if len(tuple_set) == 0:
    print("No learned GDL program")
    return
  #print("Target Graph : {}".format(target_graph))  
  #print("Target Label : {}".format(data.target_label))
  print("Elapsed time: {}".format(elapsed))
  if not os.path.exists('datasets/{}/learned_GDL_programs/bu'.format(dataset)):
    cmd = "mkdir datasets/{}/learned_GDL_programs/bu".format(dataset)
    os.system(cmd)
  with open('datasets/{}/learned_GDL_programs/bu/learned_GDL_program_from_{}.pickle'.format(dataset, target_graph), 'wb') as f:
    pickle.dump(tuple_set, f)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset")
  #parser.add_argument('-e', '--epsilon', help="input epsilon")
  #parser.add_argument('-x', '--expect', help="input expectation")
  parser.add_argument('-g', '--target_graph', help="target train graph")
  args = parser.parse_args()
  target_graph = int(args.target_graph)
  dataset = args.dataset
  learn(dataset, target_graph)

