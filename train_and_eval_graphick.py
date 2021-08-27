import pickle
import networkx as nx
import numpy as np
from graphick import *
from learn_graphick import *

import sys, os
#import json


#datasets = 'overview_example'
#datasets = 'cora'
datasets = 'citeseer'

with open('datasets/{}/A.pickle'.format(datasets),'rb') as f:
  A = pickle.load(f)
with open('datasets/{}/X.pickle'.format(datasets),'rb') as f:
  X = pickle.load(f)
with open('datasets/{}/Y.pickle'.format(datasets),'rb') as f:
  Y = pickle.load(f)
with open('datasets/{}/tr.pickle'.format(datasets),'rb') as f:
  train_nodes = pickle.load(f)
with open('datasets/{}/va.pickle'.format(datasets),'rb') as f:
  val_nodes = pickle.load(f)
with open('datasets/{}/te.pickle'.format(datasets),'rb') as f:
  test_nodes = pickle.load(f)

print("Load Data Done")
 
label_len = len(Y[0])
feature_len = len(X[0])
node_len = len(X)



if os.path.isfile('datasets/{}/succ_node_to_nodes.pickle'.format(datasets)):
  with open('datasets/{}/succ_node_to_nodes.pickle'.format(datasets),'rb') as f:
    succ_node_to_nodes = pickle.load(f) 
  with open('datasets/{}/pred_node_to_nodes.pickle'.format(datasets),'rb') as f:
    pred_node_to_nodes = pickle.load(f) 
  with open('datasets/{}/node_to_nodes.pickle'.format(datasets),'rb') as f:
    node_to_nodes = pickle.load(f) 

else:
  print("There is no node to nodes map we generate it")
  succ_node_to_nodes = {}
  pred_node_to_nodes = {}
  node_to_nodes = {}

  for i in range(node_len):
    succ_node_to_nodes[i] = set()
    pred_node_to_nodes[i] = set()
    node_to_nodes[i] = set()
  
  for i in range(node_len):
    for j in range(node_len):
      if A[i][j] > 0 and i != j:
        succ_node_to_nodes[i].add(j)
        pred_node_to_nodes[j].add(i)
        node_to_nodes[j].add(i)
        node_to_nodes[i].add(j)
  
  with open('datasets/{}/succ_node_to_nodes.pickle'.format(datasets), 'wb') as f:
    pickle.dump(succ_node_to_nodes, f, pickle.HIGHEST_PROTOCOL)
  with open('datasets/{}/pred_node_to_nodes.pickle'.format(datasets), 'wb') as f:
    pickle.dump(pred_node_to_nodes, f, pickle.HIGHEST_PROTOCOL)
  with open('datasets/{}/node_to_nodes.pickle'.format(datasets), 'wb') as f:
    pickle.dump(node_to_nodes, f, pickle.HIGHEST_PROTOCOL)




print("Load Adj Map Done")

data_set_complexity = feature_len * node_len
#print(data_set_complexity)
node_label = {}
label_nodes = {}


for node in range(node_len):
  for label in range(label_len):
    if not label in label_nodes:
      label_nodes[label] = set() 
    if Y[node][label] > 0:
      label_nodes[label].add(node)
      node_label[node] = label


node_score_sum = {}


val_test_nodes = val_nodes | test_nodes

for _, node in enumerate(val_test_nodes):  
  node_score_sum[node] = []
  for i in range(label_len):
    node_score_sum[node].append(0)

#train
for my_label in range(label_len):
  print()
  print("============================")
  print("Learning sentences for label : {}".format(my_label))
  print("============================")
  print()
  parameter = Parameter()
  parameter.dict = dict()
  parameter.succ_node_to_nodes = succ_node_to_nodes
  parameter.pred_node_to_nodes = pred_node_to_nodes
  parameter.X_arr = X
  parameter.labeled_nodes =label_nodes[my_label] & train_nodes
  parameter.original_labeled_nodes = label_nodes[my_label] & train_nodes
  parameter.train_nodes = train_nodes
  parameter.filtered_nodes = train_nodes
  parameter.data_set_complexity = data_set_complexity

  #simple data
  if data_set_complexity < 10000:
    parameter.chosen_depth = 2
  else:
    parameter.chosen_depth = 1 
  print("Chosen Depth : {}".format(parameter.chosen_depth)) 
  #complex graph
  if node_len > 10000:
    parameter.is_complex_graph = True
  else:
    parameter.is_complex_graph = False 

  sentences = learn_sentences(parameter)

  with open('datasets/{}/learned_sentences/learned_sentences_for_{}.pickle'.format(datasets, my_label), 'wb') as f:
    pickle.dump(sentences, f, pickle.HIGHEST_PROTOCOL)
  
  check_redundant_sentence = set()

  for _, sentence in enumerate(sentences):
    key = (sentence.root, json.dumps(sentence.absList))
    if key in check_redundant_sentence:
      continue
    else:
      check_redundant_sentence.add(key)
    nodes = eval_sentence(sentence, succ_node_to_nodes, pred_node_to_nodes, X)
    score = float(len(nodes & train_nodes & label_nodes[my_label]) / (len(nodes & train_nodes) + 0.1))

    chosen_val_test_nodes = nodes & val_test_nodes
 
    for _, node in enumerate(chosen_val_test_nodes):
      node_score_sum[node][my_label] = node_score_sum[node][my_label] + score
 


def find_max(my_list):
  max_idx = -1
  max_val = 0

  for i in range(len(my_list)):
    if my_list[i] >= max_val:
      max_idx = i
      max_val = my_list[i]

  return max_idx


print("Determine hyper parameter h")
#get_hyperparemater h
best_h = -3
best_accuracy = 0

for _, my_h in enumerate([0,1,-1,2,-2]):
  known_nodes = train_nodes
  known_node_label = {}
  accurately_classified_nodes = 0
  for _, node in enumerate(known_nodes):
    if node in node_label:
      known_node_label[node] = node_label[node]
  for _, node in enumerate(val_nodes):
    my_sentences_scores = copy.deepcopy(node_score_sum[node])
    belief = []
    for i in range(label_len):
      belief.append(0)
    adj_nodes = node_to_nodes[node]
    for _, adj_node in enumerate(adj_nodes & known_nodes):
      if adj_node in node_label:
        belief[known_node_label[adj_node]] = belief[known_node_label[adj_node]] + my_h
    for k in range(label_len):
      my_sentences_scores[k] = my_sentences_scores[k] + belief[k]

    first = find_max(my_sentences_scores)
    if first == node_label[node]:
      accurately_classified_nodes = accurately_classified_nodes + 1
    known_nodes.add(node)
    known_node_label[node] = first

  if accurately_classified_nodes > best_accuracy:
    best_h = my_h
    best_accuracy = accurately_classified_nodes
print("Best h : {}".format(best_h))

h = best_h


known_nodes = val_nodes | train_nodes
known_node_label = {}
for _, node in enumerate(known_nodes):
  known_node_label[node] = node_label[node]


accurately_classified_nodes = 0
for _, node in enumerate(test_nodes):
  my_sentences_scores = node_score_sum[node]
  belief = []
  for i in range(label_len):
    belief.append(0)
  adj_nodes = node_to_nodes[node]
  for _, adj_node in enumerate(adj_nodes & known_nodes):
    if adj_node in node_label:
      belief[known_node_label[adj_node]] = belief[known_node_label[adj_node]] + h

  for k in range(label_len):
    my_sentences_scores[k] = my_sentences_scores[k] + belief[k]

  first = find_max(my_sentences_scores)

  if first == node_label[node]:
    accurately_classified_nodes = accurately_classified_nodes + 1

  known_nodes.add(node)
  known_node_label[node] = first

accuracy = float(accurately_classified_nodes/len(test_nodes))
print()
print("==============================================================")
print("Test Nodes : {}".format(len(test_nodes)))
print("Accurately Classified Nodes : {}".format(accurately_classified_nodes))
print("Accuracy : {}".format(accuracy))
print("==============================================================")















