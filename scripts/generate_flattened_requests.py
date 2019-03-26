from utils import *

def get_trust_between_partners(from_p, to_p, trusts):
  for t in trusts:
    if from_p == t["property_values"]["is from"][0] and to_p == t["property_values"]["is to"][0]:
      return float(t["property_values"]["trust value"][0])
  return None

def flatten():
  asset_requests = get_ce_instances('asset request')
  ce_to_upload = []
  csv_rows = []

  # Pull down all asset requests, then for each request
  for idx,ar in enumerate(asset_requests):
    # get asset details
    props = ar["property_values"]
    result = props["result"][0]
    timestamp = props["timestamp"][0]
    requestor = props["is requested by"][0]
    la_requesting = props["is requesting"][0]

    la_details = get_instance_details(la_requesting)["property_values"]
    lat = la_details["latitude"][0]
    lng = la_details["longitude"][0]
    risk = la_details["risk of adversarial compromise"][0][:-1]
    available_to_use = la_details["available to use"][0]
    asset_id = la_details["is an instantiation of"][0]
    physical_constraint = "inactive"
    if "is physically constrained by" in la_details:
      physical_constraint = "active"

    this_asset = get_instance_details(asset_id)
    asset_details = this_asset["property_values"]
    worth = asset_details["worth"][0]
    high_level_asset_types = this_asset["direct_concept_names"]
    if "autonomous asset" in high_level_asset_types:
      asset_type = "autonomous asset"
    elif "virtual asset" in high_level_asset_types:
      asset_type = "virtual asset"
    else:
      asset_type = "physical asset"

    if "is of type" in asset_details and len(asset_details["is of type"]) > 0:
      asset_sub_type = asset_details["is of type"][0]
    else:
      asset_sub_type = this_asset["_label"]


    if "is capable of operating at" in asset_details and len(asset_details["is capable of operating at"]) > 0:
      is_capable_of_operating_at = asset_details["is capable of operating at"][0]
      alfus_details = get_instance_details(is_capable_of_operating_at)["property_values"]
      alfus_score = alfus_details["overall score"][0]
    else:
      alfus_score = '-1'
    
    # get mission details
    belongs_to = la_details["belongs to"][0]
    mi = get_instance_details(belongs_to)["property_values"]
    owner = mi["belongs to"][0]
    is_supporting = mi["is supporting"][0]
    m = get_instance_details(is_supporting)["property_values"]
    m_type = m["is an instance of"][0]
    is_e_in = m["is executed in"]
    wa = None
    me = None
    for env in is_e_in:
      tmp = get_instance_details(env)
      if "environmental condition instance" in tmp["direct_concept_names"]:
        wa = tmp["property_values"]["weighted average"][0]
      elif "mission environment" in tmp["direct_concept_names"]:
        me = tmp["_label"]

    # get trust
    trusts = get_ce_instances('trust relationship')
    trust = str(get_trust_between_partners(owner,requestor,trusts))

    # build up new flattened asset request and store in ce
    sen = """
          there is a flattened asset request named 'far_{idx}' that
            has the value '{asset_lat}' as asset lat and
            has the value '{asset_lng}' as asset lng and
            has the value '{timestamp}' as timestamp and
            has the value '{requestor}' as requestor and
            has the value '{asset_type}' as asset type and
            has the value '{asset_sub_type}' as asset sub type and
            has the value '{asset_risk}' as asset risk of adversarial compromise and
            has the value '{asset_available}' as asset available to use and
            has the value '{asset_worth}' as asset worth and
            has the value '{asset_alfus_score}' as asset alfus score and
            has the value '{asset_owner}' as asset owner and
            has the value '{trust}' as trust between owner requestor and
            has the value '{m_type}' as mission type and
            has the value '{weather_score}' as weather score and
            has the value '{me}' as mission environment and
            has the value '{physical_constraint}' as physical constraint and
            has the value '{result}' as result.
          """.format(idx=idx, asset_lat=lat, asset_lng=lng, timestamp=timestamp, 
            requestor=requestor, asset_type=asset_type, asset_sub_type=asset_sub_type, asset_risk=risk,
            asset_available=available_to_use, asset_worth=worth, asset_alfus_score=alfus_score,
            asset_owner=owner, trust=trust, m_type=m_type, weather_score=wa, me=me, 
            physical_constraint=physical_constraint, result=result)
    # print(sen)
    csv_rows.append([lat, lng, timestamp, requestor, asset_type, asset_sub_type, 
      risk, available_to_use, worth, alfus_score, owner, trust, m_type,
      wa, me, physical_constraint, result])

    ce_to_upload.append(sen)
  upload_ce(ce_to_upload)

  # generate csv file
  header = ['asset_lat','asset_lng','timestamp','requestor','asset_type','asset_sub_type','asset_risk',
            'asset_available', 'asset_worth', 'asset_alfus_score', 'asset_owner', 'trust', 'mission_type',
            'weather_score', 'mission environment', 'physical constraint', 'result']
  header_str = ','.join(header)
  f = open('coalition-data.csv', 'w')
  f.write(header_str+'\n')
  

  # write each line of array
  for l in csv_rows:
    f.write(','.join(l) +'\n')
  f.close()

if __name__ == '__main__':
  flatten()
