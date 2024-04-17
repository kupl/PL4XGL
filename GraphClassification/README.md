# PL4XGL for graph classification

 
The learned model (GDL programs) is saved in `dataset/<dataset>/learend_GDL_programs` folder where `<dataset>` can be one of the following node classification benchmarks:

```
"MUTAG", "BBBP", "BACE"
```


### Reproducing the results of PL4XGL in Figure 11 of our paper and Figure 2 of our supplementary material:


For reproducing the fidelity, sparsity, generality, and precision of _PL4XGL_ presented in Figure 11 of our paper and Figure 2 in our supplementary material, type:

```sh
$ python explanation.py -d <dataset>
```

For example, if you type `python explanation.py -d MUTAG`, you will see the results as follows:

```
...
=================================
Test graph : 124

-------------- GDL program  --------------
node v0
node v1 {0: (-99, 0)}
node v2
node v3
node v4
node v5
node v6
node v7
node v8
edge (v0, v1)
edge (v1, v2)
edge (v2, v3) {0: (-99, 0)}
edge (v2, v4) {0: (-99, 0)}
edge (v4, v5)
edge (v5, v6)
edge (v6, v7)
edge (v7, v8) {0: (-99, 0)}
target graph
------------------------------------------
Sparsity : 0.5263157894736843
Fidelity : 0.0
Generality : 0.7741935483870968
Precision : 1.0
==============================================

==========================
Test graphs : 20
Correctly classified graphs : 20
Accuracy : 1.0
==========================

Average
Sparsity : 0.5018860422965955
Fidelity : 0.0
Generality : 0.4964997759856631
Precision : 1.0
```

The results say that

- Our model classified a test graph (index of the graph is 124 in the MUTAG dataset) using a GDL program.
- The sparsity, fidelity, generality, and precision score of the provided explanation are 0.52, 0.0, 0.77, and 1.0, respectively.
- There are 20 test graphs in the dataset
- Our model accurately classified 20 test graphs of them
- The accuracy of our model is 1.0 (i.e., 20/20)
- The average sparsity, fidelity, generality, and precision score of the provided explanations is 0.50, 0.0, 0.49, and 1.0, respectively.


### Reproducing the result of PL4XGL in Table 3:

The following command reproduce the accuracy of PL4XGL presented in Table 3 of our paper.

```sh
$ python eval.py -d <dataset>
```


It will produce the classification accuracy and elapsed time (classification time):

```
--------------------
Test graphs : 20
Correctly classified grpahs : 20
Test Accuracy : 1.0
--------------------
Elapsed time: 0:00:08.905332
```


### Train model:

If you wan to reproduce the training, type the following command:

```sh
$ python learn.py -d <dataset> -c <numcores>
```


``<numcores>`` determines the number of core used in training (default value is set to 1).

For example, if you want to learn the GDL programs for the "BA-Shapes" dataset using 4 cores, type:

```sh
$ python learn.py -d MUTAG -c 64
```


At the end of learning, the learning script prints the following:

```
...
======================================
#Used cores : 64
Total training time: 0:05:41.444973
======================================
```
The above result says that the learning used 64 cores and the learning procedure took about 5 minutes.


