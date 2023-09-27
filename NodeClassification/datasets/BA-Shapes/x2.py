import sys
import copy 
import pickle
import numpy as np



with open('tr.pickle','rb') as f:
  tr = pickle.load(f)

with open('va.pickle','rb') as f:
  va = pickle.load(f)

with open('te.pickle','rb') as f:
  te = pickle.load(f)



#for _, node in enumerate(tr):
#  print(node)

#for _, node in enumerate(va):
#  print(node)

#for _, node in enumerate(te):
#  print(node)

print(len(tr))
print(len(va))
print(len(te))

print(len(te | tr | va))
print(len(te & tr & va))


sys.exit()



with open('Y.pickle','rb') as f:
  Y = pickle.load(f)
'''
print(Y)

for i, val in enumerate(Y):
  if val == [1,0,0,0,0]:
    print(0)
  elif val == [0,1,0,0,0]:
    print(1)
  elif val == [0,0,1,0,0]:
    print(2)
  elif val == [0,0,0,1,0]:
    print(3)
  elif val == [0,0,0,0,1]:
    print(4)
'''
with open('A.pickle','rb') as f:
  A = pickle.load(f)

with open('X.pickle','rb') as f:
  X = pickle.load(f)
#print(X)

for i, node in enumerate(X):
  for j, feat in enumerate(X[i]):
    if j < len(X[i])-1:
      if X[i][j] > 0:
        print("1.00 ", end='')
      else:
        print("0.00 ", end='')
    else:
      if X[i][j] > 0:
        print(1.0)
      else:
        print(0.0)

sys.exit()

#print(A)
#print(type(A))
#print(A[141])
#sys.exit()
#A = A.numpy()
#adj = A.eval()


for _, frv in enumerate(A):
  for _, tov in enumerate(A[frv]):
    print("{} {}".format(frv, tov))
#    if[i][j]

sys.exit()
#print(adj)
#print(type(adj))
#print(adj[0][0])
#print(type(adj[0][0]))
#print(adj[0][0] > 0.0)
#print(adj[0][1] > 0.0)


with open('node_to_nodes.pickle','rb') as f:
  node_to_nodes = pickle.load(f)

no_adj = set()

for _, val in enumerate(node_to_nodes):
  if len(node_to_nodes[val]) == 0:
   no_adj.add(val)

print(no_adj)
print(len(no_adj))



with open('X.pickle','rb') as f:
  X = pickle.load(f)



my_A = []

for i, val1 in enumerate(X):
  new_list = []
  for j, val2 in enumerate(X):
    new_list.append(0.0)
  my_A.append(new_list)

print(node_to_nodes[56])
#for _, fr_v in enumerate(A):
#  for _, to_v in enumerate(A[fr_v]):
for _, fr_v in enumerate(node_to_nodes):
  for _, to_v in enumerate(node_to_nodes[fr_v]):
    my_A[fr_v][to_v] = 1.0

adj = my_A

print(adj[56])
#sys.exit()


#sys.exit()



#print(X)
print(type(X))

with open('Y.pickle','rb') as f:
  Y = pickle.load(f)

#print(Y)
print(type(Y))



with open('tr.pickle','rb') as f:
  tr = pickle.load(f)

with open('va.pickle','rb') as f:
  va = pickle.load(f)

with open('te.pickle','rb') as f:
  te = pickle.load(f)

print(va)
print(len(va))
print(te)
print(len(te))

#sys.exit()


print(len(X))


y_tr = []
y_va = []
y_te = []


tr_mask = []
va_mask = []
te_mask = []
zeros = []


my_test = set()
for i in range(len(X)):
  if i in tr:
    y_tr.append(Y[i])
    y_va.append([0,0,0,0,0])
    y_te.append([0,0,0,0,0])
    tr_mask.append(True)
    va_mask.append(False)
    te_mask.append(False)

  elif i in va:
    y_tr.append([0,0,0,0,0])
    y_va.append(Y[i])
    y_te.append([0,0,0,0,0])
    tr_mask.append(False)
    va_mask.append(True)
    te_mask.append(False)

  elif i in te:
    y_tr.append([0,0,0,0,0])
    y_va.append([0,0,0,0,0])
    y_te.append(Y[i])
    tr_mask.append(False)
    va_mask.append(False)
    te_mask.append(True)
    my_test.add(i)
  else:
    print("Err")
    sys.exit()


print("")
print("")
print("Now one or Zero")
print("")
#'''
oracle = copy.deepcopy(adj)

raw = [0,0,0,0,0,0,0,0,0]

raw[0] = np.array(adj)
raw[1] = np.array(X)
raw[2] = np.array(y_tr)
raw[3] = np.array(y_va)
raw[4] = np.array(y_te)
raw[5] = np.array(tr_mask)
raw[6] = np.array(va_mask)
raw[7] = np.array(te_mask)
raw[8] = np.array(oracle)


with open('raw.pickle', 'wb') as f:
  pickle.dump(raw, f, pickle.HIGHEST_PROTOCOL)

print(type(raw[0]))
print(type(raw[1]))
print(type(raw[2]))
print(type(raw[3]))
print(type(raw[4]))
print(type(raw[5]))
print(type(raw[6]))
print(type(raw[7]))
print(type(raw[8]))
print(raw[0])
print(adj[56])

