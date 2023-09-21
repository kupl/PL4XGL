# PL4XGL for graph classification

### Requirement:

* python >= 3.8.8



### Train model:

```sh
$ python learn.py -d <dataset> -c <numcores>
```

dataset can be "MUTAG", "BBBP", "BACE". numcores determines the number of core used for training (default value is set to 1).

The learned GDL programs will be stored in dataset/$<$dataset$>$/learend_GDL_programs

### Eval model :

```sh
$ python eval.py -d <dataset>
```


### Eval explainability:

```sh
$ python explainability.py -d <dataset>
```

