from flask import Flask, request
from linebot.models import *
from linebot import *
import requests
import pandas as pd 
import json
from pymessenger.bot import Bot

df = pd.read_excel("tep_tepe.xlsx")
df2 = df.set_index('คำถาม')
json_str = df2.to_json(orient='index',force_ascii=False)
json_data = json.loads(json_str)

df3 = pd.read_excel("compare_data.xlsx")
df4 = df3.set_index('เปรียบเทียบ')
json_str = df4.to_json(orient='index',force_ascii=False)
json_compare = json.loads(json_str)

#LINE
channel_secret = "92e334ef24a5aa05e9737a9ec8e082ce"
channel_access_token = "19X1wIkhN4HKCdpWUsnfnjWDHPf6sZs5ljFKD/CbuGI7fWji1Xum7nF0Afcnmlg/cJ+EYPChYs703xRHV3dnw3OZR0jXWWp+vaIzWt4AnNz1JV2VxsaX6cWH4ophpFNuzIQoiijNcYokbTppCgq4yAdB04t89/1O/w1cDnyilFU="

#Facebook
ACCESS_TOKEN = "EAANZCjCWKluEBAJBXtTgo345UEzerwyG8uL6iTRbVL1DpCWC58EVQMltOM6RQ3Dlee5hKNrXaFrGEwyLX7r39Qy1sXpHMiU4NHFowNGMNVbxkAhImrnREijISKKqCZBowZCurc0zU6wCFx6fvg4FqPKXZCSa9VxQB95DGy3rRcsprFdZC0ImW"
VERIFY_TOKEN = "TSEchatbot"
bot = Bot(ACCESS_TOKEN)

def callAPI():
    link = "https://{}/.json?auth={}".format(FIREBASE_HOST,FIREBASE_AUTH)
    response = requests.get(link)
    return response.json()

def getValue(location,province,option,response):   
    try:
        
        value = "{} {}".format(response[location][province][option],SI[option] )
       
    except:
        value = "ไม่พบข้อมูล"
    return value

app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    print(body)
    req = request.get_json(silent=True, force=True)
    source = req['originalDetectIntentRequest']["source"]
    print(source)
    intent = req["queryResult"]["intent"]["displayName"]
    text = req['originalDetectIntentRequest']['payload']['data']['message']['text']
    if source == "line":
        reply_token = req['originalDetectIntentRequest']['payload']['data']['replyToken']
        id = req['originalDetectIntentRequest']['payload']['data']['source']['userId']
        disname = line_bot_api.get_profile(id).display_name
    elif source =="facebook":
        reply_token = req['originalDetectIntentRequest']['payload']['data']["sender"]['id']
        print(reply_token)
    

    if intent == "register":
        question = req["queryResult"]['parameters']["question"][0]
        major_list = []
        msg_dup = []
        for i in req["queryResult"]['parameters']["major"]:
            major_list.append(i.upper())
        msg_list = ''
        print(req["queryResult"]['parameters']["major"])
        for i in major_list:
            if json_data[question][i] not in msg_dup:
                msg_list += json_data[question][i]
                msg_dup.append(json_data[question][i])
                msg_list += "\n"
        reply(intent,text,reply_token,msg_list,source)

    elif intent == "TCAS1.2":
        question = req["queryResult"]['parameters']["question"][0]
        major = req["queryResult"]['parameters']["major"][0]
        msg = json_data[question][major]
        reply(intent,text,reply_token,msg,source)


    elif intent == "compare":
        major = req["queryResult"]['parameters']["major"][0].upper()
        major1 = req["queryResult"]['parameters']["major1"][0].upper()
        msg = json_compare[major][major1]
        reply(intent,text,reply_token,msg,source)
    


def reply(intent,text,reply_token,msg,source):
    text_message = TextSendMessage(text=msg)
    if source == "line":
        line_bot_api.reply_message(reply_token,text_message)
    else:
        bot.send_text_message(reply_token, msg)
        

def reply_en(intent,text,reply_token,id,disname,location,room):
    text_message = TextSendMessage(text=data[location][option])
    line_bot_api.reply_message(reply_token,text_message)

def reply_cloud(intent,text,reply_token,id,disname,location,option):
    text_message = TextSendMessage(text=callAPI(location,option))
    line_bot_api.reply_message(reply_token,text_message)




    
    


if __name__ == "__main__":
    app.run()