import requests
import json

BASE =  "http://127.0.0.1:5000/"

data = [{'name':'Nick', 'views': 15, 'likes': 10},
        {'name':'Serene', 'views': 20, 'likes': 20},
        {'name':'AJ', 'views': 25, 'likes': 30}]

for i in range(len(data)):
    response = requests.put(BASE + "video/" + str(i), data[i])
    #response = requests.patch()
    print(response.json())

input()
response = requests.delete(BASE + "video/0")
print(response)
input()
response = requests.get(BASE + "video/2")
print(response.json())
