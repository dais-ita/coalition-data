from generate_alfus_scores import generate_alfus_scores
from generate_autonomous_assets import generate_autonomous_assets
from generate_environmental_conditions import generate_environmental_conditions
from generate_mission_instances import generate_mission_instances
from generate_assets import generate_live_asset_inventories, generate_live_assets
from generate_annotated_requests import generate_annotated_requests
from generate_flattened_requests import flatten

import argparse

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Generate Data')
  parser.add_argument('--granularity', metavar='G', type=int, default=2,
                      help='number of values between min and max' + 
                      ' to generate for each environmental condition. Default 2')

  parser.add_argument('--num_assets', metavar='A', type=int, default=2,
                      help='number of assets to generate per coalition partner per mission. Default 2')

  parser.add_argument('--bb_string', metavar='B', type=str, 
    default='-4.7479366381,40.6454468805,-4.6508215605,40.6900208682',
    help='swlon,swlat,nelon,nelat bounding box for asset generation')

  parser.add_argument('--decision', metavar='D', type=str, default='{"trust": { "gt": 0.3 },"asset": {"type": {"eq": "CAV"}, "available to use": { "eq": "yes" },"risk of adversarial compromise": { "lt": 40 }},"mission environment": {"eq": "urban|mountain" }, "mission type": {"eq": "logistical resupply"}, "environmental conditions": {"weather score": {"gt":0.2}, "wind speed level": {"lt": 30}}}',
                      help='boolean condition used to evaluate approve/reject')

  parser.add_argument('--num_requests', metavar='R', type=int, default=100,
                      help='number of requests to generate. Default 100')

  args = parser.parse_args()
  g = args.granularity
  num_a = args.num_assets
  bb = args.bb_string
  decision = args.decision
  num_req = args.num_requests

  generate_environmental_conditions(g=g)
  generate_alfus_scores()
  generate_mission_instances()
  generate_autonomous_assets()
  lais = generate_live_asset_inventories()
  generate_live_assets(num_a, lais, bb)
  generate_annotated_requests(decision, num_req)
  flatten()