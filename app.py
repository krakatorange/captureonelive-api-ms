import requests, json, os, uvicorn, secrets

from fastapi import FastAPI, HTTPException, Security, status
from pydantic import BaseModel
from typing import Union
from utils import get_api_key, get_generator_api_key
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
host = os.getenv("HOST")

print(host)

class ImageRequest(BaseModel):
    url: str

class UserAPIKey(BaseModel):
    userId: str

# generate access token dynamically
def get_access_token(session_uuid):
    SESSION_URL = f'https://live.captureone.com/api/v1/session/establish/{ session_uuid }/'
    data = { "cloud_session_uuid": f'{ session_uuid }' }
    response = requests.post(SESSION_URL, json=data)
    auth_data = json.loads(response.text)

    return auth_data["access_token"]

@app.post("/get_images")
async def get_images(imageRequest: ImageRequest, api_key: str = Security(get_api_key)):
    try: 
        # Get the url from request
        url = imageRequest.url
        session_uuid = url.split('/')[-1]
        access_token = get_access_token(session_uuid)
        headers = { "Authorization": f'Bearer { access_token }' }
        data = { "cloud_session_uuid": session_uuid, "order_by": 1 }

         # API endpoint
        API_URL = "https://live.captureone.com/api/v1/search/state/"

        # Sending request to api with required data
        response = requests.post(API_URL, json=data, headers=headers)
        json_data = response.text

        # Loading the returned response as json
        data = json.loads(json_data)

        # Extract all URLs from response
        images_urls = [variant["thumbnails"]["medium"]["url"] for variant in data["variants"]]

        # return the urls
        return { "image_urls": images_urls }
    except Exception as err:
        return { "msg" : str(err) }
    
@app.post("/generate_api_key")
async def get_images(userAPIKey: UserAPIKey, api_key: str = Security(get_generator_api_key)):
    userId = userAPIKey.userId
    generated_key = secrets.token_urlsafe(16)

    return { "userId": userId, "API-KEY": generated_key }

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=8000)
