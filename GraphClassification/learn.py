from multiprocessing.pool import ThreadPool
import argparse, pickle
import os
import datetime



def execute_command_bu(dataset: str, graph: int):
  cmd = "python3 learn_from_instance_bu.py -d {} -g {}".format(dataset, graph)
  print(cmd)
  os.system(cmd)



def clean(dataset: str):
  cmd = "rm -r datasets/{}/learned_GDL_programs/bu/*".format(dataset)
  os.system(cmd)
  #cmd = "mkdir datasets/{}/learned_GDL_programs/bu".format(dataset)
  #os.system(cmd)


if __name__ == '__main__':
  parser = argparse.ArgumentParser() 
  parser.add_argument('-d', '--dataset', default = "MUTAG", help="input dataset: MUTAG, BBBP, BACE")
  parser.add_argument('-c', '--cores', default = "1", help="num cores, default = 1")
  #parser.add_argument('-a', '--algorithm', const = 1, help="top-down or bottom-up")
  
  args = parser.parse_args()
  dataset = args.dataset
  cores = int(args.cores)
  print("Dataset : {}".format(dataset))  
  print("Cores : {}".format(cores))
  clean(dataset)

  with open("datasets/{}/tr.pickle".format(dataset), 'rb') as f:
     train_graphs = pickle.load(f)
  pool = ThreadPool(cores)  
  start = datetime.datetime.now()  
  for graph in train_graphs:
    pool.apply_async(execute_command_bu, (dataset, graph,))
  pool.close()
  pool.join()

  finish = datetime.datetime.now()
  elapsed = finish - start  
  print()
  print("======================================")
  print("#Used cores : {}".format(cores))
  print("Total training time: {}".format(elapsed))
  print("======================================")

 
