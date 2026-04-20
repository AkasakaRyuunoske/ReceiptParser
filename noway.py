import base64
import datetime

import requests

if __name__ == "__main__":
    print(f"[{datetime.datetime.now()}]Starting querying model LLAVA")
    url = "http://localhost:11434/api/generate"

    with open("config/media/receipt_parser/IMG20260412161515.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(url, json={
        "model": "gemma4:e4b",
        "prompt": "Return a json file containing information on the image.",
        "images": [image_base64],
        "stream": False,
    })

    print(f"[{datetime.datetime.now()}] Got response from the model")
    print(response.json()["response"])
