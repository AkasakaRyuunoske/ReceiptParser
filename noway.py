import base64

import requests

if __name__ == "__main__":
    print(f"Starting querying model LLAVA")
    url = "http://localhost:11434/api/generate"

    with open("config/media/receipt_parser/IMG20260412161515.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(url, json={
        "model": "llava",
        "prompt": "Describe this image",
        "images": [image_base64]
    })

    print(response.json()["response"])
