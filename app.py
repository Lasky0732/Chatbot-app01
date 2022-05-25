from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
)
import sqlite3 as db
import pandas as pd
import re
import requests
import random
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi('66pKRvRusZN5lGBXMMqg7GZOPSHcrUCxzkLwFwX2h99FS6VRO1xgYUVbgBx9e4ogw8q8AhCK5f0DX6jr4P6/j9up3hlCY5qUagxQEe1VbyQ6i9hcrChj/kYKHGxNNA9V9J1j3gBfq4aJoSvKg2MAwQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('89313b029a713def6f5b3071afe7febf')

def get_news():
    text=''
    try:
        #url='https://tw.news.yahoo.com/most-popular'
        url='https://tw.news.yahoo.com/'
        r=requests.get(url)
        soup=BeautifulSoup(r.text, 'lxml')
        cfs=soup.find_all('div',class_="Cf")
        domain_url='https://tw.news.yahoo.com/'
        datas=[]
        datas=[[cf.find('h3').text.strip(),cf.find('div',class_="C(#959595) Fz(13px) C($c-fuji-grey-f)! D(ib) Mb(6px)").text.strip(),domain_url+cf.find('a').get('href')] for cf in cfs]
        df=pd.DataFrame(datas,columns=['標題','來源','連結'])
        for i in range(5):
            text+=df['標題'][i]+'\n'+'來源:'+df['來源'][i]+'\n'+df['連結'][i]+'\n'
            text+='------------------------------------\n'
    except:
        text+='功能維護中'
        
    return text
def stop_work():
    try:
        #url='https://www.dgpa.gov.tw/typh/daily/nds.html'
        url='https://rbdkd67zcc92ou2hpwdvxa-on.drv.tw/www/test_table1.html'
        r = requests.get(url)
        r.encoding='utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        trs=soup.find(id="Table").find_all('tr')
        data=''
        for tr in trs[:-1]:
            for td in tr.find_all('td'):
                data+=(td.text.strip())
                data+='\n'
            data+='---------------------------------\n'
    except:
        data+='功能維護中'
    return data

# def CJK_cleaner(string): #移除特殊字元，僅保留英數字及中日韓統一表意文字(CJK Unified Ideographs)
#     filters = re.compile(u'[^0-9a-zA-Z\u4e00-\u9fff]+', re.UNICODE)
#     return filters.sub('', string) #remove special characters

def Search(message):
    text=''
    blockade=['%',';','"']
    if message[0] in blockade:
        text+='不可以做壞事喔!'
    else:
        try:
            if len(message)>1:
                conn = db.connect("nevaldownload.db")
                df= pd.read_sql(f'SELECT novelName, novelWriter, novelUrl FROM blog WHERE novelName LIKE "%{str(message)}%"',conn)
                conn.close()
                if len(df) !=0:
                    for i in range(len(df)):
                        text+=df['novelName'][i]+'\n'
                        text+='作者:'+df['novelWriter'][i]+'\n'
                        text+=df['novelUrl'][i]+'\n'
                        text+='\n'
                else:
                    text+='無資料'
            else:
                text+='搜尋書名字數至少兩個字'
        except:
            text+='功能維護中'
    respond=TextSendMessage(text=text)
    return respond
    
    
def Control(message):
    text=[]
    if message == '#使用說明':
        text.append(TextSendMessage(text='輸入想要尋找的書名(至少輸入兩個字)'))
        text.append(TextSendMessage(text='指令格式 #(指令文字)'))
        respond = text
    elif message =='#Hello':
        texts=['Hello','你好','Hi 很高興見到你','歡迎使用','如果有機會我會...啊!!!原來你在 Hello 剛剛我沒說什麼']
        text.append(TextSendMessage(text=texts[random.randrange(5)]))
        respond =text
    elif message == '#sudo rm -rf':
        text.append(TextSendMessage(text='你是不是想毀了我!!!'))
        text.append(TextSendMessage(text='想得美!!!'))
        respond = text
    elif message == '#好康的圖':
        cv=random.randrange(2)
        image_text=['不可以色色','圖勒?']
        image_link=['https://i.imgur.com/IFMFsr4.png','https://imgur.com/J77AOY1.png']
        text.append(TextSendMessage(text=image_text[cv]))
        text.append(ImageSendMessage(original_content_url=image_link[cv], preview_image_url=image_link[cv]) )
        respond = text
    elif message == '#最新停班停課消息':
        text.append(TextSendMessage(text=stop_work()))
        text.append(TextSendMessage(text='目前資料來自測試網站'))
        respond = text
    elif message == '#最新Yahoo新聞':
        text.append(TextSendMessage(text=get_news()))
        respond = text    
    else:
        respond =TextSendMessage(text='無相關指令!')
    return respond


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #print("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    
    message = event.message.text
    if '#' in message[0]:
        line_bot_api.reply_message(event.reply_token,Control(message))
    else:
        # message=CJK_cleaner(message)
        line_bot_api.reply_message(event.reply_token,Search(message))
    
    

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ.get('PORT', 5000))
