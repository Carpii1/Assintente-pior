import requests, json, sys
url='http://127.0.0.1:8000/chat'
payload={'message':'Oi'}
try:
    resp=requests.post(url, json=payload)
    print('Status', resp.status_code)
    print('Body', resp.text)
except Exception as e:
    print('Error', e)
    sys.exit(1)
