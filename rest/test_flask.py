import requests

data = {
    'points': [ [i, i+1] for i in range(5) ]
}
print(data)
resp = requests.put("http://localhost:5000/path", json=data)

print(resp.json())