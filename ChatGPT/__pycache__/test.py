import requests

updated_user = {
    "name": "KLV Updated",
    "age": 21,
    "city": "Warsaw"
}

response = requests.put(
    "http://127.0.0.1:5000/users/1",
    json=updated_user
)

print(response.json())