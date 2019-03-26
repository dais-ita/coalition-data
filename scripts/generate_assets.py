import argparse
import random
from utils import *

def generate_random_lat_lng_within(bb):
  bb_a = bb.split(',')
  swlng = float(bb_a[0])
  swlat = float(bb_a[1])
  nelng = float(bb_a[2])
  nelat = float(bb_a[3])

  # generate random lng between sw and ne
  # generate random lat between sw and ne
  rlng = random.uniform(swlng,nelng)
  rlat = random.uniform(swlat,nelat)
  return (rlat,rlng)


def select_n_assets(assets,num):
  chosen = []
  while len(chosen) < num:
    choice = random.choice(assets)
    if choice not in chosen:
      chosen.append(choice)
  return chosen

def generate_live_assets(num, lais, bb):
  assets = get_ce_instances('asset')
  ce_to_upload = []
  for lidx,lai in enumerate(lais):
    # randomly select assets for mission
    random_assets = select_n_assets(assets,num)

    for idx, ra in enumerate(random_assets):
      # currently, all assets are available to use
      name = 'live_asset_lai_'+str(lidx)+'_ra_'+str(idx)
      asset = ra["_label"]

      # generate lat/lon in bounding box.
      lat,lon = generate_random_lat_lng_within(bb)
      # generate risk between 0-40%
      risk = str(random.randint(0,41))
      # generate start time - random time after the start time (within the same day)
      start_time = lai["mi"]["property_values"]["start time"][0][:-6]

      # random time between 8,12,16,22
      hour = random.choice(["08","12","16","22"])
      time = start_time + " " + hour +":"+"00"

      sen = """
            there is a live asset named '{name}' that
              is an instantiation of the asset '{asset}' and
              belongs to the live asset inventory '{lai}' and
              has the value '{time}' as timestamp and
              has the value '{lat}' as latitude and
              has the value '{lon}' as longitude and 
              has the value '{risk}' as risk of adversarial compromise and
              has the value 'yes' as available to use.
          """.format(name = name, asset=asset, lai=lai["name"], time=time, lat=lat, lon=lon, risk=risk)
      ce_to_upload.append(sen)
  upload_ce(ce_to_upload)

def get_cps_for_mission(mi,cps):
  cps_on_mission = []
  is_executed_by = mi["property_values"]["is executed by"][0]
  for c in cps:
    if is_executed_by in c["property_values"]["is a member of"]:
      cps_on_mission.append(c)
  return cps_on_mission

def generate_live_asset_inventories():
  # For each mission instance, create asset inventory for each coalition partner
  mis = get_ce_instances('mission instance')
  cps = get_ce_instances('coalition partner')

  ce_to_upload = []
  lais = []
  for idx,mi in enumerate(mis):
    # get coalition partners for this mission
    cps_on_mission = get_cps_for_mission(mi,cps)
    for cp in cps_on_mission:
      name = mi["_label"]+'_'+cp["_label"]
      lais.append({"name":name,"mi":mi})
      sen = """
            there is a live asset inventory named '{name}' that
              belongs to the coalition partner '{cpl}' and
              is supporting the mission instance '{mil}'.
            """.format(name=name,cpl=cp["_label"], mil=mi["_label"])
      ce_to_upload.append(sen)

  upload_ce(ce_to_upload)
  return lais

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Randomly generate Live Assets for a mission instance')
  parser.add_argument('--num_assets', metavar='A', type=int, default=2,
                      help='number of assets to generate per coalition partner per mission. Default 10')

  parser.add_argument('--bb_string', metavar='B', type=str, 
    default='-4.7479366381,40.6454468805,-4.6508215605,40.6900208682',
    help='swlon,swlat,nelon,nelat bounding box for asset generation')

  args = parser.parse_args()
  num_a = args.num_assets
  bb = args.bb_string

  lais = generate_live_asset_inventories()
  generate_live_assets(num_a, lais, bb)
