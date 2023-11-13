from multiprocessing.pool import ThreadPool
import argparse, datetime
import sys, os
from data_loader import *

def execute_command_td(dataset: str, label: int):
    #Complex dataset
    if dataset in ['Cora', 'Citeseer', 'Pubmed']:
      cmd = "python3 learn_from_label_td_simple.py -d {} -l {}".format(dataset, label)
    else:
      cmd = "python3 learn_from_label_td.py -d {} -l {}".format(dataset, label)
    print(cmd)
    os.system(cmd)

def clean(dataset):
  cmd = "rm -r datasets/{}/learned_GDL_programs/td/*".format(dataset)
  os.system(cmd)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dataset', help="input dataset : BA-Shapes, Tree-Cycles, Texas, Cornell, Wisconsin")
  parser.add_argument('-c', '--cores', default = "1", help="num cores, default = 1")
  args = parser.parse_args()
  dataset = args.dataset
  cores = int(args.cores)
  data = data_loader(dataset)
  labels = len(data.label_to_nodes)
  print(labels)
  my_labels = []
  start = datetime.datetime.now()
  for i in range(int(labels)):
    my_labels.append(str(i))
  pool = ThreadPool(labels)
  for label in my_labels:
    pool.apply_async(execute_command_td, (dataset, label))

  pool.close()
  pool.join()
  finish = datetime.datetime.now()
  elapsed = finish - start
  print()
  print("======================================")
  print("#Used cores : {}".format(cores))
  print("Total training time: {}".format(elapsed))
  print("======================================")
