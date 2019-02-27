import argparse
import random
import math
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from utils import *

def gen_seq(lb,ub,g):
  if g > 1:
      actual_g = g-1
      step = int(math.ceil(((ub-lb)/float(actual_g))))
      new_lb = lb + step
      vals = [lb]
      vals = vals +list(range(new_lb,ub,step))
      vals.append(ub)
      return vals
  else:
      return lb

def generate_all_possible_combinations(vals, weights):
    full = []
    idxs = {}
    sentences = []
    for idx, val in enumerate(vals):
      full.append(vals[val])
      idxs[idx] = val
    combos = np.array(np.meshgrid(*full)).T.reshape(-1,len(vals))

    # normalise
    combos_norm = MinMaxScaler().fit_transform(combos.T).T.tolist()

    for idx, c in enumerate(combos_norm):
      name = 'eci_'+str(idx)
      sen = "there is an environmental condition instance named '{name}' that ".format(name=name)

      for c_idx, cv in enumerate(c):
        idx_of_this_feature_val = vals[idxs[c_idx]].index(combos[idx][c_idx])
        ecv_name = idxs[c_idx] +'_'+str(idx_of_this_feature_val)
        new_feature = "contains the environmental condition value '{ecv_name}' and ".format(ecv_name=ecv_name)
        sen = sen + new_feature

      # compute weighted average
      wa = round((sum(c) / float(len(vals))),4)

      sen = sen + "has the value '{wa}' as weighted average.".format(wa=str(wa))

      sentences.append(sen)
    upload_ce(sentences) 
    print(len(combos_norm))

###
# param: granularity - how many items between min and max to generate
#                      for each condition

###
def generate_environmental_conditions(g):

  # Get all environmental conditions and all directions (for wind speed)
  conditions = get_ce_instances('environmental condition')
  directions = get_ce_instances('direction')
  ce_to_upload = []
  sorted_condition_values = {}
  weights = {}
  for c in conditions:
    label = c["_label"]
    vals = c["property_values"]
    lb = int(vals["lower bound"][0])
    ub = int(vals["upper bound"][0])
    weight = int(vals["weight"][0])
    sorted_condition_values[label] = []
    weights[label] = weight

    # For each one, generate data points according to the granularity
    c_vals = gen_seq(lb,ub,g)
    
    # Store in CE as a environmental condition value (or wind speed value)
    if label != "wind speed level":
      for idx, c_val in enumerate(c_vals):
        name = label + '_'+ str(idx)
        sen = """there is a environmental condition value named '{name}' that
                instantiates the environmental condition '{label}' and 
                has the value '{c_val}' as value.
              """.format(name=name, label=label, c_val=str(c_val))
        sorted_condition_values[label].append(c_val)
        ce_to_upload.append(sen.strip())
    else:
      for idx, c_val in enumerate(c_vals):
        name = label + '_'+ str(idx)
        direction = random.choice(directions)["_label"]
        sen = """there is a wind speed condition value named '{name}' that
                instantiates the environmental condition '{label}' and 
                has the value '{c_val}' as value and
                has the value '{direction}' as direction.
              """.format(name=name, label=label, c_val=str(c_val), direction=direction)
        sorted_condition_values[label].append(c_val)
        ce_to_upload.append(sen.strip())

  # Upload to CE
  upload_ce(ce_to_upload)

  # Generate all possible combinations of conditions
  generate_all_possible_combinations(sorted_condition_values, weights)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Generate Environmental Conditions')
  parser.add_argument('--granularity', metavar='G', type=int, default=2,
                      help='number of values between min and max' + 
                      ' to generate for each environmental condition. Default 2')

  args = parser.parse_args()
  g = args.granularity
  generate_environmental_conditions(g=g)

