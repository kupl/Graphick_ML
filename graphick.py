class Parameter:
  test_label_nodes = set() 
  sentences = set()
  node_to_nodes = {}
  X_arr = []
  labeled_nodes = set()
  feature_results = []
  train_nodes = set()
  filtered_nodes = set()
  original_labeled_nodes = set()
  covered_nodes = set()
  non_zero_features = set()

#language
class Sentence:
  absList = []
  root = 0
  def __init__(self):
    self.absList = []
    self.root = 0

def filter_eval_sentence(feature, succ_node_to_nodes, pred_node_to_nodes, X_arr, filtered_nodes):

  nodes = filter_process_target(feature, X_arr, filtered_nodes) 
  
  node_succ_nodes = {}
  node_pred_nodes = {}
  for i,val in enumerate(nodes):
    node_succ_nodes[val] = succ_node_to_nodes[val]
    node_pred_nodes[val] = pred_node_to_nodes[val]
  nodes = process_succs(feature, X_arr, nodes, node_succ_nodes, succ_node_to_nodes, feature.root+1)
  nodes = process_preds(feature, X_arr, nodes, node_pred_nodes, pred_node_to_nodes, feature.root-1)
  
  nodes = filter_redundant(feature, X_arr, nodes, succ_node_to_nodes, pred_node_to_nodes)
  
  return nodes

#evaluate target node 
def filter_process_target(feature, X_arr, filtered_nodes):
  abs_node = feature.absList[feature.root]
  nodes = filtered_nodes
  #for i, val in enumerate(X_arr):
  #  nodes.add(i)
  nodes = process_abstract_node(abs_node, nodes, X_arr)
  return nodes
#'''




#evaluate a sentence
def eval_sentence(feature, succ_node_to_nodes, pred_node_to_nodes, X_arr):

  nodes = process_target(feature, X_arr) 
  
  node_succ_nodes = {}
  node_pred_nodes = {}
  for i,val in enumerate(nodes):
    node_succ_nodes[val] = succ_node_to_nodes[val]
    node_pred_nodes[val] = pred_node_to_nodes[val]
  nodes = process_succs(feature, X_arr, nodes, node_succ_nodes, succ_node_to_nodes, feature.root+1)
  nodes = process_preds(feature, X_arr, nodes, node_pred_nodes, pred_node_to_nodes, feature.root-1)

  nodes = filter_redundant(feature, X_arr, nodes, succ_node_to_nodes, pred_node_to_nodes)

  return nodes



def filter_redundant(feature, X_arr, nodes, succ_node_to_nodes, pred_node_to_nodes):
  if len(feature.absList) < 3:
    return nodes
  elif len(feature.absList) == 3:
    if feature.root == 1:
      filtered_nodes = set()
      for _, val in enumerate(nodes):
        if exist_path(feature, X_arr, val, succ_node_to_nodes, pred_node_to_nodes):
          filtered_nodes.add(val)
      return filtered_nodes
    #elif root = 1:
    else:#root = 2
      return nodes
  else:
    print("Error : The length of sentence is greater than 3")
    return nodes


def exist_path(feature, X_arr, val, node_succ_nodes, node_pred_nodes):
  pred_nodes = node_pred_nodes[val]
  pred_nodes = process_abstract_node(feature.absList[0], pred_nodes, X_arr)
  if len(pred_nodes) > 1: 
    return True
  succ_nodes = node_succ_nodes[val]
  succ_nodes = process_abstract_node(feature.absList[2], succ_nodes, X_arr)
  if len(succ_nodes) > 1:
    return True
  
  if len(pred_nodes - succ_nodes) == 0:
    return False
  else:
    return True




'''
#evaluate a sentence
def filter_eval_sentence(feature, succ_node_to_nodes, pred_node_to_nodes, X_arr, filtered_nodes):

  nodes = filter_process_target(feature, X_arr, filtered_nodes) 
  
  node_succ_nodes = {}
  node_pred_nodes = {}
  for i,val in enumerate(nodes):
    node_succ_nodes[val] = succ_node_to_nodes[val]
    node_pred_nodes[val] = pred_node_to_nodes[val]
  nodes = process_succs(feature, X_arr, nodes, node_succ_nodes, node_to_nodes, feature.root+1)
  nodes = process_preds(feature, X_arr, nodes, node_pred_nodes, node_to_nodes, feature.root-1)
  return nodes

#evaluate target node 
def filter_process_target(feature, X_arr, filtered_nodes):
  abs_node = feature.absList[feature.root]
  nodes = filtered_nodes
  #for i, val in enumerate(X_arr):
  #  nodes.add(i)
  nodes = process_abstract_node(abs_node, nodes, X_arr)
  return nodes
'''



#evaluate a node
def process_abstract_node(abs_node, nodes, X_arr):
  filtered_nodes = set()
  if len(abs_node) == 0:
    return nodes
  for i, candidate_node in enumerate(nodes):
    flag = True
    for j, index in enumerate(abs_node):
      (bot,top) = abs_node[index]
      if X_arr[candidate_node][index] < bot or top < X_arr[candidate_node][index]:
        flag = False
        break
    if flag == True:
      filtered_nodes.add(candidate_node)
  return filtered_nodes



#evaluate target node 
def process_target(feature, X_arr):
  abs_node = feature.absList[feature.root]
  nodes = set()
  for i, val in enumerate(X_arr):
    nodes.add(i)
  nodes = process_abstract_node(abs_node, nodes, X_arr)
  return nodes


#evaluate successor nodes 
def process_succs(feature, X_arr, nodes, node_succ_nodes, node_to_nodes, idx):
  if idx == len(feature.absList):
    return nodes
  abs_node = feature.absList[idx] # (bot,top)
  filtered_nodes = set ()
  new_node_succ_nodes = {}
  for i, val in enumerate(nodes):
    succ_nodes = process_abstract_node(abs_node, node_succ_nodes[val], X_arr)
    if len(succ_nodes) > 0:
      new_node_succ_nodes[val] = set()
      filtered_nodes.add(val)
      for j, myval in enumerate(succ_nodes):
        new_node_succ_nodes[val] = new_node_succ_nodes[val] | node_to_nodes[myval]
  return process_succs(feature, X_arr, filtered_nodes, new_node_succ_nodes, node_to_nodes, idx+1)


#evaluate predecessor nodes 
def process_preds(feature, X_arr, nodes, node_pred_nodes, node_to_nodes, idx):
  if idx < 0:
    return nodes
  abs_node = feature.absList[idx] # (bot,top)
  filtered_nodes = set ()
  new_node_pred_nodes = {}
  for i, val in enumerate(nodes):
    pred_nodes = process_abstract_node(abs_node, node_pred_nodes[val], X_arr)
    if len(pred_nodes) > 0:
      new_node_pred_nodes[val] = set()
      filtered_nodes.add(val)
      for j, myval in enumerate(pred_nodes):
        new_node_pred_nodes[val] = new_node_pred_nodes[val] | node_to_nodes[myval]

  return process_preds(feature, X_arr, filtered_nodes, new_node_pred_nodes, node_to_nodes, idx-1)

