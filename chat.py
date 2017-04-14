#coding:utf-8

import urllib2
import json
import base64
import requests
import pack_wave

class cRobot:
    def __init__(self):
        self.apiKey = "MWZ5zcIx5drugAMBx8Mu0rxO"
        self.secretKey = "37f46c3dda263a26597f6af9ef44fe24"
        self.auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" \
                        + self.apiKey + "&client_secret=" + self.secretKey

        self.audio2text_url='http://vop.baidu.com/server_api'
        self.mtoken=self.__get_token()

        self.TR_secret="298204673dbbf749"
        self.TR_apiKey="06c2949cee984912ac49a75c13c00ae5"
        self.TR_url="http://www.tuling123.com/openapi/api"

        self.text2audio_url="http://tsn.baidu.com/text2audio"



    def __get_token(self):
        res = urllib2.urlopen(self.auth_url)
        json_data = res.read()
        return json.loads(json_data)['access_token']

    def audio2text(self,sound,RATE,cuid):
        f_len=len(sound)*2
        audio_data_base64=base64.b64encode(sound)
        header={#'Content-Type':'application/json',
                    'Content-Type':' audio/pcm; rate=8000',
                    'Content-Length': f_len
                }
        upload={'format':'wav',
                'rate':RATE,
                'channel':1,
                'token':self.mtoken,
                'cuid':cuid,
                'len':f_len,
                'speech':audio_data_base64,
                }
        r=requests.post(self.audio2text_url,data=json.dumps(upload),headers=header)
        text=json.loads(r.text)
        text=text['result'][0]
        print text
        return text
    def text2text(self,atext,cuid,location="四川省成都市"):
         payload={"key":self.TR_apiKey,
                "info": atext,
                 "loc":location,
                 "userid":cuid}

         r=requests.post(self.TR_url,payload)
         text=json.loads(r.text)
         print text['code'],text['text']
         code=text['code']
         res=''
         if code==100000:
                res=text['text']
         if code==200000:
                res=text['text']+u'但是我们没办法显示给你'
         if code==302000:
                res=text['text']
                newslist=text['list']
                count=0
                for i in newslist:
                        count+=1
                        res+=u'来自'+i['source']+u'的新闻：'+i['article']+u'。'
                        if count >3:
                                break

         if code==308000:
                res=text['text']+text['list'][0]['name']+u',需要使用'+text['list'][0]['info']+u'。'

         print res
         return res
    def text2MP3(self,text,cuid):
        res_text_utf=text.encode('utf-8')
        _res_text_utf=urllib2.quote(res_text_utf)
        res=urllib2.urlopen(self.text2audio_url+"?"+"tex="+_res_text_utf+"&lan=zh"+"&cuid="+cuid+"&ctp=1&tok="+self.mtoken)
        buffer=res.read()
        return buffer

    def chat(self,sound,cuid="aaaaaaa",location="四川省成都市"):
        sound_wave=pack_wave.pack2wavefile(sound)
        atext=self.audio2text(sound=sound_wave,RATE=8000,cuid=cuid)
        btext=self.text2text(atext=atext,cuid=cuid)
        res_MP3=self.text2MP3(text=btext,cuid=cuid)
        return res_MP3
