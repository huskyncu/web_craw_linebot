# 引入Line Messaging API相關模組
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import PostbackAction, URIAction, MessageAction, TemplateSendMessage, ButtonsTemplate
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import json
import requests
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


app = Flask(__name__)
# LINE BOT info
def get_data():
    with open('data.json','r') as f:
        data = json.load(f)
    return data
data = get_data()
line_bot_api = LineBotApi(data['channel_access_token'])
handler = WebhookHandler(data['channel_secret'])


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 定義處理收到文字訊息的函式

def monoNum(n):
    content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)
    items = list(tree.iter(tag='item'))
    title = items[n][0].text
    ptext = items[n][3].text
    ptext  = ptext.replace('<p>','').replace('</p>','\n')
    
    return title + '\n' + ptext[:-1] 

def handle_text_message(event):
    # 讀取收到的訊息內容
    user_msg = event.message.text
    if user_msg == "@本期中獎號碼":
        print(monoNum(0))
        strr = str(monoNum(0))
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=strr))
    elif user_msg == "@前期中獎號碼":
        strr = str(monoNum(1)+"\n\n"+monoNum(2))
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=strr))
    elif len(user_msg)==3 and user_msg.isdigit():
        try:
            content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
            tree = ET.fromstring(content.text)
            items = list(tree.iter(tag='item'))
            ptext = items[0][3].text
            ptext = ptext.replace('<p>','').replace('</p>','')
            temlist = ptext.split('：')
            prizelist = []
            prizelist.append(temlist[1][5:8])
            prizelist.append(temlist[2][5:8])
            for i in range(3):
                prizelist.append(temlist[3][9*i+5:9*i+8])
            sixlist = temlist[3].split('、')
            for i in range(len(sixlist)):
                prizelist.append(sixlist[i])
            message=""
            if user_msg in prizelist:
                message = '符合某獎項後三碼，請自行核對發票前五碼！\n\n'
                message +=monoNum(0)
            else:
                print(2)
                message = '很可惜，沒中獎。請輸入下一張發票最後三碼。'
            print(message)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))
        except:
            message = '讀取發票號碼發生錯誤！'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))
            
    else:
        message = '請輸入發票最後三碼進行對獎！'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))


# 將收到的事件分類處理


@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):
    handle_text_message(event)


def running():
    app.run("0.0.0.0", port = 80)


if __name__ == "__main__":
    running()