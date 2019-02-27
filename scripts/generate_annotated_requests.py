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
    asset_decisions = decision_parsed["asset"]
    asset_props_hold = []
    for d in asset_decisions:
      key = list(d.keys())[0]
      value = list(d.values())[0]

      if rla["property_values"][key][0] == value:
        asset_props_hold.append(True)
      else:
        asset_props_hold.append(False)

    asset_props_hold_all = all(asset_props_hold)

    # decide if trust holds
    t_holds = False
    trust_decision = decision_parsed["trust"]
    if trust_decision["comparison"] == "gt":
      if trust > trust_decision["value"]:
        t_holds = True

    if asset_props_hold_all and t_holds:
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
  parser.add_argument('--decision', metavar='D', type=str, default='{"trust": {"comparison":"gt", "value": 0.49}, "asset": [{"available to use": "yes"}]}',
                      help='boolean condition used to evaluate approve/reject')

  parser.add_argument('--num_requests', metavar='R', type=int, default=100,
                      help='number of requests to generate. Default 100')

  args = parser.parse_args()
  decision = args.decision
  num_req = args.num_requests
  generate_annotated_requests(decision, num_req)
