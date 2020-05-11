import requests
import json
import os


def get_size():
    if 'OAuth_TOKEN' in os.environ:
        OAuth_TOKEN, DIALOG_ID = os.environ['OAuth_TOKEN'], os.environ['DIALOG_ID']
    else:
        from config import DIALOG_ID, OAuth_TOKEN

    url = "https://dialogs.yandex.net/api/v1/status"
    headers = {
        'Authorization': f"OAuth {OAuth_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def upload_image(image_url):
    if 'OAuth_TOKEN' in os.environ:
        OAuth_TOKEN, DIALOG_ID = os.environ['OAuth_TOKEN'], os.environ['DIALOG_ID']
    else:
        from config import DIALOG_ID, OAuth_TOKEN

    url = f"https://dialogs.yandex.net/api/v1/skills/{DIALOG_ID}/images"
    headers = {
        'Authorization': f"OAuth {OAuth_TOKEN}",
        'Content-Type': 'application/json'
    }
    data = {"url": image_url}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


def get_images():
    if 'OAuth_TOKEN' in os.environ:
        OAuth_TOKEN, DIALOG_ID = os.environ['OAuth_TOKEN'], os.environ['DIALOG_ID']
    else:
        from config import DIALOG_ID, OAuth_TOKEN

    url = f"https://dialogs.yandex.net/api/v1/skills/{DIALOG_ID}/images"
    headers = {
        'Authorization': f'OAuth {OAuth_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    return response.json()
