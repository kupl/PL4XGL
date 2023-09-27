from multiprocessing.pool import ThreadPool
import argparse
import sys, os
from data_loader import *

def execute_command_td(dataset: str, label: int):
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
  for i in range(int(labels)):
    my_labels.append(str(i))
  pool = ThreadPool(labels)
  for label in my_labels:
    pool.apply_async(execute_command_td, (dataset, label))

  pool.close()
  pool.join()


