import requests

ce_store_base_url = 'http://localhost:8080/ce-store'
# ce_store_base_url = 'http://ce-store-paams2019.eu-gb.mybluemix.net/ce-store'

print('Using CE Store: {ce_store_base_url}'.format(ce_store_base_url=ce_store_base_url))

def get_ce_instances(instance_name):
  url = ce_store_base_url + '/concepts/'+instance_name+'/instances?style=full'
  instances = requests.get(url).json()
  return instances

def upload_ce(sentences):
  url = ce_store_base_url+'/stores/DEFAULT/sources/generalCeForm?showStats=true&action=save'
  post_str = " "
  post_str = post_str.join(sentences)
  r = requests.post(url, data=post_str).json()
  if 'alerts' in r and len(r['alerts']['errors']) == 0 and r['structured_response']['invalid_sentences'] == 0:
    return {"ok": True}  
  else:
    print('Error')
    print(r)
    return {"ok": False}

def get_instance_details(iid):
  url = ce_store_base_url + '/instances/'+iid
  instances = requests.get(url).json()
  return instances