# coalition-data
This repository contains a conceptual model and generated dataset as presented in the publication "Knowledge Representation and Dataset Generationfor Generative Policy Evaluation".

## Installation 
A Docker image is provided for quick setup.
```
docker build -t coalition-model .
docker run -it -p 8080:8080 coalition-model:latest
```
This runs a [Controlled English](https://github.com/ce-store/ce-store) store accessible via the URL: [http://localhost:8080/ce-store/ui](http://localhost:8080/ce-store/ui). Navigate to this URL and load the DAIS-ITA local sentence set.

## Generating data
Data can then be generated by running the `generate_data.py` script within the scripts folder. This script accepts the following command line options:
```
  --granularity G   number of values between min and max to generate for each
                    environmental condition. Default 2
  --num_assets A    number of assets to generate per coalition partner per
                    mission. Default 2
  --bb_string B     swlon,swlat,nelon,nelat bounding box for asset generation.
  --decision D      boolean condition used to evaluate approve/reject
  --num_requests R  number of requests to generate. Default 100
  ```