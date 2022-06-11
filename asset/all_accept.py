import requests
r = requests.put('http://AAA.top:65472/api/v1/admin/contrib/first?k=rangwokk')
print(r)
while r.status_code == 200:
    r = requests.put('http://AAA.top:65472/api/v1/admin/contrib/first?k=rangwokk')
    print(r)
