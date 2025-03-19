import time
import requests
import logging
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_url = "https://qfhtiiep7dmkfhnzcfh7lqmdou0snrhg.lambda-url.us-west-2.on.aws/"
base_url_sql_server = "https://5js3bnz5dpjhznip3gkyeruylu0isazh.lambda-url.us-west-2.on.aws/"
completeBaseUrl = "https://jcfx3zhzo7nzt5ez4prlkvv2ky0inwaj.lambda-url.us-west-2.on.aws/"


app = FastAPI()

def fetch_with_retry(url, data, attempt=1):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your_token_here'
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        resp_data = response.json()
        if 'result_set' not in resp_data or not resp_data['result_set']:
            if attempt < 3:
                logger.warning(f"Attempt {attempt} failed, retrying in 5 seconds...")
                time.sleep(5)
                return fetch_with_retry(url, data, attempt + 1)
            else:
                return resp_data
        return resp_data
    except Exception as e:
        logger.error("Error during fetch_with_retry: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cron_cache2")
def cron_cache2():
    try:
        data = fetch_with_retry(base_url + 'fetchExternalIdWithIsSpecialsReport', {}, 1)
        if "result_set" not in data or len(data["result_set"]) == 0:
            return {"message": "Records not found"}

        PATH_ARR = ["report2"]
        for externalid_item in data["result_set"]:
            for path_item in PATH_ARR:
                try:
                    url = f"{completeBaseUrl}{path_item}?Generate=1&id={externalid_item['externalid']}"
                    response = requests.get(url)
                    response.raise_for_status()
                    logger.info("Report fetched and cached for externalid: %s", externalid_item['externalid'])
                except Exception as error:
                    logger.error("Error fetching report: %s", error)
                    return {"message": "Excel is not cached in S3"}
        return {"message": "Excel is now cached in S3"}
    except Exception as e:
        logger.error("Error in cron_cache2: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
