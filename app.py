import requests, json, os

from flask import Flask, request, jsonify

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
host = app.config.get("HOST")

# generate access token dynamically
def get_access_token(session_uuid):
    SESSION_URL = f"https://live.captureone.com/api/v1/session/establish/{session_uuid}/"
    data = {"cloud_session_uuid":f"{session_uuid}"}
    response = requests.post(SESSION_URL, json=data)
    auth_data = json.loads(response.text)

    return auth_data["access_token"]

@app.route("/get_images", methods = ['POST'])
def get_images():
    try: 
        # Get the url from request
        url = request.get_json().get('url')
        eventId = request.get_json().get('eventId')
        status = request.get_json().get('status')
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
        return jsonify({ "image_urls": images_urls, "eventId": eventId, "status": status })
    except Exception as err:
        return jsonify({ "msg" : str(err) })

if __name__ == '__main__':
    app.run(host=host, port=8000, threaded=True)
