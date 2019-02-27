import numpy as np
from utils import *

def get_cap_constr(aa_type, alfus_score, base_aa_constraints):
  cap = ""
  constr = ""
  for c in base_aa_constraints:
    _score = c["property_values"]["ALFUS score"][0]
    _type = c["property_values"]["describes"][0]

    if (_score == alfus_score and _type == aa_type):
      cap = c["property_values"]["capability"][0]
      constr = c["property_values"]["constraint"][0]
      break
  return(cap,constr)

def generate_capability_constraints(assets, alfus_scores, autonomous_assets):
  # For each asset, get it's overall alfus score then get base constraint for this alfus
  # score and asset type
  # then create a capability constraint that maps the two together.
  base_aa_constraints = get_ce_instances('base autonomous asset capability constraint')

  ce_to_upload = []
  for idx, a in enumerate(assets):
    alf_score = alfus_scores[a[0]]
    alf_score_name = alf_score["_label"]
    alf_score_val = alf_score["property_values"]["overall score"][0]
    aa_type = autonomous_assets[a[1]]["_label"]
    name = 'autonomous_constraint_'+str(idx)
    aa_name = 'aa_'+str(idx)

    # Get capability and constraint for this type and alfus score
    cap, constr = get_cap_constr(aa_type,alf_score_val,base_aa_constraints)
    sen = """
          there is an asset capability constraint named '{name}' that
            describes the autonomous asset '{aa_name}' and
            has the value '{cap}' as capability and
            has the value '{constr}' as constraint.
          """.format(name=name, aa_name=aa_name, cap=cap, constr=constr)

  ce_to_upload.append(sen)
  upload_ce(ce_to_upload)

def generate_autonomous_assets():
  # For each autonomous asset type, for each alfus score
  alfus_scores = get_ce_instances('ALFUS score')
  autonomous_assets = get_ce_instances('autonomous asset type')

  alfs = list(range(len(alfus_scores)))
  aa = list(range(len(autonomous_assets)))

  full = [alfs,aa]
  combos = np.array(np.meshgrid(*full)).T.reshape(-1,len(full))

  ce_to_upload = []
  for idx, c in enumerate(combos):
    name = 'aa_'+str(idx)
    aa_type = autonomous_assets[c[1]]["_label"]
    alf_s = alfus_scores[c[0]]["_label"]
    # calculate worth
    base_worth = int(autonomous_assets[c[1]]["property_values"]["base worth"][0])
    worth = base_worth + int(alfus_scores[c[0]]["property_values"]["overall score"][0])
    sen = """
          there is an autonomous asset named '{name}' that 
            is of type the autonomous asset type '{aa_type}' and
            is capable of operating at the ALFUS score '{alf_s}' and
            has the value '{worth}' as worth.
          """.format(name=name, aa_type=aa_type, alf_s=alf_s, worth=worth)
    ce_to_upload.append(sen)

  upload_ce(ce_to_upload)

  # Generate capability constraints for each asset
  generate_capability_constraints(combos, alfus_scores, autonomous_assets)

if __name__ == '__main__':
  generate_autonomous_assets()
