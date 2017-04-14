import urllib2
import getAudio_test as getAudio
import json
import base64
import requests
import time

RATE=getAudio.RATE

def get_token():
    apiKey = "MWZ5zcIx5drugAMBx8Mu0rxO"
    secretKey = "37f46c3dda263a26597f6af9ef44fe24"

    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;

    res = urllib2.urlopen(auth_url)
    json_data = res.read()
    return json.loads(json_data)['access_token']
mtoken=get_token()
sound=getAudio.record_to_file("demo333.wav")
f_len=len(sound)*2

audio_data_base64=base64.b64encode(sound)
header={#'Content-Type':'application/json',
            'Content-Type':' audio/pcm; rate=8000',
            'Content-Length': f_len
        }
upload={'format':'wav',
        'rate':RATE,
        'channel':1,
        'token':mtoken,
        'cuid':'dangsugouitest',
        'len':f_len,
        'speech':audio_data_base64,
        }

url='http://vop.baidu.com/server_api'

t1=time.time()
r=requests.post(url,data=json.dumps(upload),headers=header)
text=json.loads(r.text)
text=text['result'][0]
t2=time.time()
print t2-t1
print text

