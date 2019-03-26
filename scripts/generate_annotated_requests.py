import argparse
import random
import json
from utils import *

def get_cps_for_mission(mi,cps):
  cps_on_mission = []
  is_executed_by = mi["property_values"]["is executed by"][0]
  for c in cps:
    if is_executed_by in c["property_values"]["is a member of"]:
      cps_on_mission.append(c)
  return cps_on_mission

def get_live_asset_inventory(lai_name, lais):
  for lai in lais:
    if lai["_label"] == lai_name:
      return lai
  return None

def get_mission(mi_name, mis):
  for mi in mis:
    if mi["_label"] == mi_name:
      return mi
  return None

def get_trust_between_partners(from_p, to_p, trusts):
  for t in trusts:
    if from_p == t["property_values"]["is from"][0] and to_p == t["property_values"]["is to"][0]:
      return float(t["property_values"]["trust value"][0])
  return None

def check_trust(trust_c_obj, trust):
  trust = float(trust)
  holds = []
  for k in trust_c_obj.keys():
    tc = float(trust_c_obj[k])
    hold = False
    if k == "gt":
      if trust > tc:
        hold = True

    elif k == "lt":
      if trust < tc:
        hold = True

    elif k == "eq":
      if trust == tc:
        hold = True

    elif k == "lte":
      if trust <= tc:
        hold = True

    elif k == "gte":
      if trust >= tc:
        hold = True

    elif k == "ne":
      if trust != tc:
        hold = True

    holds.append(hold)
  return all(holds)

# Check whether an instance conforms to a decision
def check_decision(inst, d):
  key = list(d.keys())[0]
  value = list(d.values())[0]

  if key not in inst["property_values"]:
    return True
  inst_val = inst["property_values"][key][0]

  results = []
  if "eq" in value:
    # Handle | for OR case
    if "|" in str(value["eq"]):
      splitted = str(value["eq"]).split("|")
    else:
      splitted = [str(value["eq"])]

    splitted_results = []
    for s in splitted:
      if str(inst_val) == s:
        splitted_results.append(True)
      else:
        splitted_results.append(False)
    results.append(any(splitted_results))

  if "lt" in value:
    if float(inst_val) < float(value["lt"]):
      results.append(True)
    else:
      results.append(False)

  if "gt" in value:
    if float(inst_val) > float(value["gt"]):
      results.append(True)
    else:
      results.append(False)

  if "lte" in value:
    if float(inst_val) <= float(value["lte"]):
      results.append(True)
    else:
      results.append(False)

  if "gte" in value:
    if float(inst_val) >= float(value["gte"]):
      results.append(True)
    else:
      results.append(False)

  if "ne" in value:
    # Handle | for OR case
    if "|" in str(value["ne"]):
      splitted = str(value["ne"]).split("|")
    else:
      splitted = [str(value["ne"])]

    splitted_results = []
    for s in splitted:
      if str(inst_val) != s:
        splitted_results.append(True)
      else:
        splitted_results.append(False)
    results.append(any(splitted_results))

  return all(results)


def check_mission_environment(d, mi):
  key = list(d.keys())[0]
  value = list(d.values())[0]
  envs = mi["property_values"]["is executed in"]
  env = ""
  for e in envs:
    if "eci_" not in e:
      env = e
  results = []

  if key == "eq":
    # Handle | for OR case
    if "|" in str(value):
      splitted = str(value).split("|")
    else:
      splitted = [str(value)]

    splitted_results = []
    for s in splitted:
      if env == s:
        splitted_results.append(True)
      else:
        splitted_results.append(False)
    results.append(any(splitted_results))

  if key == "ne":
    # Handle | for OR case
    if "|" in str(value):
      splitted = str(value).split("|")
    else:
      splitted = [str(value)]

    splitted_results = []
    for s in splitted:
      if env != s:
        splitted_results.append(True)
      else:
        splitted_results.append(False)
    results.append(any(splitted_results))

  return all(results)

def check_weather(condition, comparison):
  key = list(comparison.keys())[0]
  value = list(comparison.values())[0]
  contains = condition["property_values"]["contains"]
  results = []

  for c in contains:
    if key in c:
      weather = get_instance_details(c)
      results.append(check_decision(weather, {"value": comparison[key]}))
  return all(results)


def check_ec(d, mi):
  envs = mi["property_values"]["is executed in"]
  env = ""
  for e in envs:
    if "eci_" in e:
      env = e
  eci = get_instance_details(env)

  results = []
  for k in d.keys():
    if k == "weather score":
      results.append(check_decision(eci,{"weighted average": d[k]}))
    else:
      results.append(check_weather(eci, {k: d[k]}))

  return all(results)

def check_asset_type(live_asset, decision):
  key = list(decision.keys())[0]
  value = list(decision.values())[0]
  asset = get_instance_details(live_asset["property_values"]["is an instantiation of"][0])
  if key == "type":
    return check_decision(asset, {"is of type": value})
  else:
    return False

def check_asset_worth(live_asset, decision):
  key = list(decision.keys())[0]
  value = list(decision.values())[0]
  asset = get_instance_details(live_asset["property_values"]["is an instantiation of"][0])
  if key == "worth":
    return check_decision(asset, {"worth": value})
  else:
    return False

def check_asset_ALFUS_score(live_asset, decision):
  key = list(decision.keys())[0]
  value = list(decision.values())[0]
  asset = get_instance_details(live_asset["property_values"]["is an instantiation of"][0])
  if key == "ALFUS score":
    return check_decision(asset, {"is capable of operating at": value})
  else:
    return False

def check_mission_type(live_asset, decision):
  mi = get_instance_details(live_asset["property_values"]["belongs to"][0])
  m = get_instance_details(mi["property_values"]["is supporting"][0])
  return check_decision(m, {"is an instance of": decision})


def check_asset_physical_constraint(live_asset, decision):
  d = decision["physical constraint"]
  if "is physically constrained by" in live_asset["property_values"]:
    # Physical constraint, return false if physical constraint is inactive, true if active
    if "eq" not in d:
      print('Error - eq not present in decision for physical constraint')
      return True
    elif d["eq"] == "inactive":
      return False
    else:
      return True

  else:
    # No physical constraint
    if "eq" not in d:
      print('Error - eq not present in decision for physical constraint')
      return True
    elif d["eq"] == "inactive":
      return True
    else:
      return False

# conceptualise an ~ asset request ~ REQ that
#   has the value 'T' as ~ timestamp ~ and
#   ~ is requesting ~ the live asset A and
#   ~ is requested by ~ the coalition partner P and
#   has the value 'R' as ~ result ~.
def generate_annotated_requests(decision, num_requests):
  las = get_ce_instances('live asset')
  lais = get_ce_instances('live asset inventory')
  mis = get_ce_instances('mission instance')
  cps = get_ce_instances('coalition partner')
  tr = get_ce_instances('trust relationship')

  ce_to_upload = []
  for n in range(num_requests):
    # pick random live asset
    rla = random.choice(las)
    live_asset_name = rla["_label"]

    # get live asset inventory this belongs too (and owner)
    lai = rla["property_values"]["belongs to"][0]
    lai_instance = get_live_asset_inventory(lai,lais)
    owner = lai_instance["property_values"]["belongs to"][0]

    # then mission lai is supporting, then coalition partners on mission
    # pick random coalition partner that does not own asset
    mission_supporting = lai_instance["property_values"]["is supporting"][0]
    mission_supporting_instance = get_mission(mission_supporting, mis)
    cps_on_mission = get_cps_for_mission(mission_supporting_instance, cps)
    cps_on_mission_names = [c["_label"] for c in cps_on_mission]

    cps_on_mission_names.remove(owner)
    random_request_by = random.choice(cps_on_mission_names)

    # generate random time from mission start date
    start_date = mission_supporting_instance["property_values"]["start time"][0][:-6]

    # random time between 8,12,16,22
    hour = random.choice(["08","12","16","22"])
    time = start_date + " " + hour +":"+"00"

    # get trust between partners
    trust = get_trust_between_partners(owner, random_request_by, tr)

    # decide approve reject based on decision
    decision_parsed = json.loads(decision)

    # Check asset holds
    if "asset" not in decision_parsed:
      asset_props_hold_all = True
    else:
      asset_decisions = decision_parsed["asset"]
      asset_props_hold = []
      for d in asset_decisions:
        if d == "type":
          decision_result = check_asset_type(rla, {d: asset_decisions[d]})
        elif d == "worth":
          decision_result = check_asset_worth(rla, {d: asset_decisions[d]})
        elif d == "ALFUS score":
          decision_result = check_asset_ALFUS_score(rla, {d: asset_decisions[d]})
        elif d == "physical constraint":
          decision_result = check_asset_physical_constraint(rla, {d: asset_decisions[d]})
        else:
          decision_result = check_decision(rla, {d: asset_decisions[d]})
        asset_props_hold.append(decision_result)

      asset_props_hold_all = all(asset_props_hold)

    # Check trust holds
    if "trust" not in decision_parsed:
      t_holds = True
    else:
      trust_decision = decision_parsed["trust"]
      t_holds = check_trust(trust_decision, trust)

    # Check mission environment holds
    if "mission environment" not in decision_parsed:
      me_holds = True
    else:
      me_decision = decision_parsed["mission environment"]
      me_holds = check_mission_environment(me_decision, mission_supporting_instance)

    # Check environmental condition instance holds
    if "environmental conditions" not in decision_parsed:
      eci_holds = True
    else:
      eci = decision_parsed["environmental conditions"]
      eci_holds = check_ec(eci, mission_supporting_instance)

    # Check mission type
    if "mission type" not in decision_parsed:
      mt_holds = True
    else:
      mt = decision_parsed["mission type"]
      mt_holds = check_mission_type(rla, mt)

    if asset_props_hold_all and t_holds and me_holds and eci_holds and mt_holds:
      final_decision = True
    else:
      final_decision = False

    # generate CE
    req_name = 'req_'+str(n)
    sen = """
          there is an asset request named '{req_name}' that
            has the value '{time}' as timestamp and
            is requesting the live asset '{live_asset_name}' and
            is requested by the coalition partner '{random_request_by}' and
            has the value '{final_decision}' as result.
          """.format(req_name=req_name, time=time, live_asset_name=live_asset_name, 
            random_request_by=random_request_by, final_decision=final_decision)

    ce_to_upload.append(sen)
  upload_ce(ce_to_upload)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Generate Annotated Requests')
  parser.add_argument('--decision', metavar='D', type=str, default='{"trust": { "gt": 0.3 },"asset": {"type": {"eq": "CAV"}, "worth": {"lt": 10}, "physical constraint": {"eq": "inactive"}, "available to use": { "eq": "yes" },"risk of adversarial compromise": { "lt": 40 }},"mission environment": {"eq": "urban|mountain" }, "mission type": {"eq": "logistical resupply"}, "environmental conditions": {"weather score": {"gt":0.2}, "wind speed level": {"lt": 30}}}',
                      help='boolean condition used to evaluate approve/reject')
  parser.add_argument('--num_requests', metavar='R', type=int, default=100,
                      help='number of requests to generate. Default 100')

  args = parser.parse_args()
  decision = args.decision
  num_req = args.num_requests
  generate_annotated_requests(decision, num_req)
