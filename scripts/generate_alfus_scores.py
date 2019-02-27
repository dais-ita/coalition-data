import numpy as np
from utils import upload_ce

def generate_alfus_scores():
  mc = list(range(0,4))
  ec = list(range(0,4))
  hi = list(range(0,4))
  full = [mc,ec,hi]
  combos = np.array(np.meshgrid(*full)).T.reshape(-1,len(full))
  ce_to_upload = []

  for idx,c in enumerate(combos):
    score = sum(c)
    _mc = c[0]
    _ec = c[1]
    _hi = c[2]
    if score == 0:
      band = 'band 0'
    elif score >= 1 and score <= 3:
      band = 'band 1-3'
    elif score >= 4 and score <= 6:
      band = 'band 4-6'
    elif score >= 7 and score <= 9:
      band = 'band 7-9'

    name = 'alfus_'+str(idx)
    sen = """
          there is an ALFUS score named '{name}' that
            has the value '{score}' as overall score and
            is within the ALFUS level band '{band}' and
            has the value '{_mc}' as mission complexity score and
            has the value '{_ec}' as environmental complexity score and
            has the value '{_hi}' as human independence score.
          """.format(name=name, score=str(score), band=band,
            _mc=str(_mc), _ec=str(_ec), _hi=str(_hi))
    ce_to_upload.append(sen)

  # create level 10 case
  last_combo = len(combos)
  last_name = 'alfus_'+str(last_combo)
  sen_10 = """
        there is an ALFUS score named '{last_name}' that
          has the value '10' as overall score and
          is within the ALFUS level band 'band 10' and
          has the value '3.3333' as mission complexity score and
          has the value '3.3333' as environmental complexity score and
          has the value '3.3333' as human independence score.
        """.format(last_name=last_name)
  ce_to_upload.append(sen_10)

  upload_ce(ce_to_upload)

if __name__ == '__main__':
  generate_alfus_scores()
