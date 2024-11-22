import requests

# Endpoint dan API Key
API_KEY = "AIzaSyDv6DqLP3iukIuHRH6khP6fHcFP6A6DIuE"
URL = "https://generativelanguage.googleapis.com/v1beta2/models/chat-bison-001:generateMessage?key=" + API_KEY

# Payload untuk permintaan
payload = {
    "prompt": {
        "messages": [
            {"content": "Tulis cerita pendek tentang luar angkasa.", "author": "user"}
        ]
    }
}

# Permintaan ke API
response = requests.post(URL, json=payload)

# Cetak hasil
if response.status_code == 200:
    print(response.json()["candidates"][0]["content"])
else:
    print("Error:", response.status_code, response.text)
