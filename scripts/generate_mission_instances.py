import datetime
import numpy as np
from utils import *

def generate_mission_instances():

  # generate for each mission environment, each environmental condition instance at different times.
  mission_environments = get_ce_instances('mission environment')
  environmental_condition_instances = get_ce_instances('environmental condition instance')
  missions = get_ce_instances('mission')
  coalitions = get_ce_instances('coalition')

  # Generate missions at 4 times during the day for the current day
  now = datetime.datetime.now()
  year = now.year
  month = now.month
  day = now.day

  date_str = "{year}-{month}-{day}".format(year=year, month=month, day=day)
  times = ["08:00", "12:00", "16:00", "22:00"]
  dates = []
  for t in times:
    time_str = date_str + " " + t
    dates.append(time_str)

  me = list(range(len(mission_environments)))
  eci = list(range(len(environmental_condition_instances)))
  mi = list(range(len(missions)))
  dt = list(range(len(dates)))
  co = list(range(len(coalitions)))

  full = [me,eci,mi,dt,co]
  combos = np.array(np.meshgrid(*full)).T.reshape(-1,len(full))

  print(len(combos), ' mission instances')

  ce_to_upload = []
  for idx, c in enumerate(combos):
    name = 'mi_'+str(idx)
    _mi = missions[c[2]]["_label"]
    _co = coalitions[c[4]]["_label"]
    _me = mission_environments[c[0]]["_label"]
    _eci = environmental_condition_instances[c[1]]["_label"]
    _dt = dates[c[3]]
    sen = """
          there is a mission instance named '{name}' that 
            is an instance of the mission '{_mi}' and 
            is executed by the coalition '{_co}' and 
            is executed in the mission environment '{_me}' and
            is executed in the environmental condition instance '{_eci}' and
            has the value '{_dt}' as start time.
          """.format(name=name, _mi=_mi, _co=_co, _me=_me, _eci=_eci, _dt=_dt)
    ce_to_upload.append(sen)

  upload_ce(ce_to_upload)

if __name__ == '__main__':
  generate_mission_instances()
