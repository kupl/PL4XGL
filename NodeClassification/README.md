# PL4XGL for node classification


The learned model (GDL programs) is saved in `dataset/<dataset>/learend_GDL_programs` folder where `<dataset>` can be one of the following node classification benchmarks:

```
"Wisconsin", "Texas", "Cornell", "BA-Shapes", "Tree-Cycles"
```


### Reproducing the results of PL4XGL in Figure 11 of our paper and Figure 2 of our supplementary material:


For reproducing the fidelity, sparsity, generality, and precision of _PL4XGL_ presented in Figure 11 of our paper and Figure 2 in our supplementary material, type:

```sh
$ python explanation.py -d <dataset>
```

For example, if you type `python explanation.py -d BA-Shapes`, you will see the results as follows:

```
...
============================================================
Test node : 125

-------------- GDL program  --------------
node v0
node v1 {0: (12.0, 78.0)}
node v2 {0: (12.0, 78.0)}
edge (v1, v0)
edge (v2, v0)
target node v1
------------------------------------------
Sparsity : 0.9702970297029703
Fidelity : 0.0
Generality : 0.9700996677740864
Precision : 1.0
============================================================

==============================================================
Test Nodes : 70
Accurately Classified Nodes : 67
Accuracy : 0.9571428571428572
==============================================================

Average
Sparsity : 0.901350573847475
Fidelity : 0.0
Generality : 0.9508541911256545
Precision : 0.9998357963875205
```

The results say that

- Our model classified a test node (index of the node is 125 in the BA-Shapes dataset) using a GDL program (the program is the same program with the program for 'Label 0' in Table 2 of our paper).
- The sparsity, fidelity, generality, and precision score of the provided explanation are 0.97, 0.0, 0.97, and 1.0, respectively.
- There are 70 test nodes in the dataset
- Our model accurately classified 67 nodes of them
- The accuracy of our model is 0.957 (i.e., 67/70)
- The average sparsity, fidelity, generality, and precision score of the provided explanations is 0.90, 0.0, 0.95, and 0.99, respectively.


### Reproducing the result of PL4XGL in Table 3:

The following command reproduce the accuracy of PL4XGL presented in Table 3 of our paper.

```sh
$ python eval.py -d <dataset>
```


For example, `$ python eval.py -d Wisconsin` will produce the classification accuracy and elapsed time (classification time) as follows:

```
==============================================================
Test Nodes : 25
Accurately Classified Nodes : 22
Accuracy : 0.88
==============================================================
Elapsed time: 0:00:02.158994
```



### Train model:

If you wan to reproduce the training, type the following command:

```sh
$ python learn.py -d <dataset> -c <numcores>
```


``<numcores>`` determines the number of core used in training (default value is set to 1).

For example, if you want to learn the GDL programs for the "BA-Shapes" dataset using 4 cores, type:

```sh
$ python learn.py -d BA-Shapes -c 4
```


At the end of learning, the learning script prints the following:

```
======================================
#Used cores : 4
Total training time: 0:00:06.470596
======================================
```
The above result says that the learning used 4 cores and the learning procedure took 6 seconds.


