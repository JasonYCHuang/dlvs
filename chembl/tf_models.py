"""
Script that trains Tensorflow Multitask models on ChEMBL 
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import numpy as np
import deepchem as dc
from chembl_datasets import load_chembl
import timeit

# Set numpy seed
np.random.seed(123)

###Load data###
shard_size = 2000
print("About to load ChEMBL data.")
chembl_tasks, datasets, transformers = load_chembl(shard_size=shard_size,
                                                   featurizer="ECFP", set="5thresh", split="random")
train_dataset, valid_dataset, test_dataset = datasets

print("ChEMBL_tasks")
print(len(chembl_tasks))
print("Number of compounds in train set")
print(len(train_dataset))
print("Number of compounds in validation set")
print(len(valid_dataset))
print("Number of compounds in test set")
print(len(test_dataset))

###Create model###
n_layers = 3
nb_epoch = 10
model = dc.models.TensorflowMultiTaskRegressor(
    len(chembl_tasks), train_dataset.get_data_shape()[0],
    layer_sizes=[1000]*n_layers, dropouts=[.25]*n_layers,
    weight_init_stddevs=[.02]*n_layers,
    bias_init_consts=[1.]*n_layers, learning_rate=.0003,
    penalty=.0001, penalty_type="l2", optimizer="adam", batch_size=100,
    seed=123, verbosity="high")

#Use R2 classification metric
metric = dc.metrics.Metric(dc.metrics.pearson_r2_score, task_averager=np.mean)

start = timeit.default_timer()

print("Training model")
model.fit(train_dataset, nb_epoch=nb_epoch)

train_time = timeit.default_timer() - start

start = timeit.default_timer()

train_scores = model.evaluate(train_dataset, [metric], transformers)
valid_scores = model.evaluate(valid_dataset, [metric], transformers)
test_scores = model.evaluate(test_dataset, [metric], transformers)

eval_time = timeit.default_timer() - start

print("Train scores")
print(train_scores)

print("Validation scores")
print(valid_scores)

print("Test scores")
print(test_scores)

print('Train time: %.1fm' % (train_time/60.))
print('Eval time: %.1fm' % (eval_time/60.))
