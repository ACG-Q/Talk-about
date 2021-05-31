import requests
import re
import threading
import json
import datetime
import time

# 禅道 ZenTao
ZENTAOURL = None
# 开源
KAIYUAN = "/zentao/my/"
# 禅道版本
VESION = "禅道12.3"

# 定时
Time = None

# 正则
VesionRegex = "class='icon-zentao'></i>(.*)</"
InFoRegex = "class=\"row tiles\">(.*?)class=\".*?block-flowchart"
InFosRegex = "class=\"tile-title\">(.*?)</div>.*?class=\"tile-amount\">(.*?)</"
NameRegex = "class='user-name'>(.*?)</"

# 推送
PushMsg = None
PushWebHook = None
PushNumber = []

# 头部
headers = None

# MsgType
ERR = "error"
WARN = "warning"
INFO = "info"
DEBUG = "debug"

MsgTypes = {
    ERR:"[ERR]",
    WARN:"[WARN]",
    INFO:"[INFO]",
    DEBUG:"[DEBUG]"
}


def pushToDingTalk():
    _loggin(INFO,"开始推送")
    try:
        Json = {
            "msgtype": "text",
            "text": {
                "content": PushMsg
            },
            "at":{
                "atMobiles":PushNumber,
                "isAtAll": False
            }
        }
        newheaders = {
            'Content-Type': 'application/json'
        }
        if PushWebHook:
            response = requests.post(PushWebHook, data=json.dumps(Json), headers=newheaders)
            response.raise_for_status()
            _loggin(DEBUG,f"发送成功,Http Code:{response.status_code}")
    except requests.exceptions.HTTPError as exc:
        _loggin(ERR,"消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
        raise
    except requests.exceptions.ConnectionError:
        _loggin(ERR,"消息发送失败，HTTP connection error!")
        raise
    except requests.exceptions.Timeout:
        _loggin(ERR,"消息发送失败，Timeout error!")
        raise
    except requests.exceptions.RequestException:
        _loggin(ERR,"消息发送失败, Request Exception!")
        raise

def getInfo():
    global PushMsg
    _loggin(INFO,"开始获取信息")
    try:
        if ZENTAOURL:
            url = ZENTAOURL + KAIYUAN
            response = requests.get(url,headers=headers)
            # print(response.text)
            vesion = re.search(VesionRegex,response.text,re.M|re.I).group(1).replace(" ", "")
            # print(vesion)
            PushMsg += f"\n禅道版本:{vesion}\000\t"
            _loggin(INFO,f"禅道版本:{vesion}")
            if VESION == vesion:
                name = re.search(NameRegex,response.text,re.M|re.I).group(1)
                # print(f"用户名：{name}")
                PushMsg += f"By {name}\n"
                info = re.search(InFoRegex,response.text,re.S).group()
                infos = re.finditer(InFosRegex,info,re.MULTILINE | re.IGNORECASE | re.VERBOSE | re.DOTALL)
                for matchNum, match in enumerate(infos, start=1):
                    Num = _getNum(match.group(2))
                    if matchNum in [1,2,3]:
                        if Num > 0:
                            # PushMsg += "❗"
                            _loggin(INFO,f"{match.group(1)}\t数量:{Num}")
                            PushMsg += f"{match.group(1)}\000\t数量:{Num}\n"
                        else:
                            # PushMsg += "✨"
                            _loggin(INFO,f"{match.group(1)}\t数量:{Num}")
                            PushMsg += f"{match.group(1)}\000\t数量:{Num}\n"
                    else:
                        _loggin(INFO,f"{match.group(1)}\t数量:{Num}")
                        PushMsg += f"{match.group(1)}\000\t数量:{Num}\n"
                PushMsg += f"推送时间：{_getTime()}"
    except BaseException as error:
        # print(f"推送失败:{error}")
        _loggin(ERR,error)

def autoRun():
    # print("开始设置定时器")
    _loggin(INFO,"开始设置定时器")
    try:
        now_time = datetime.datetime.now()
        next_time = now_time + datetime.timedelta(days=+1)
        next_year = next_time.date().year
        next_month = next_time.date().month
        next_day = next_time.date().day
        if Time:
            next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+Time, "%Y-%m-%d %H:%M:%S")
            timer_start_time = (next_time - now_time).total_seconds()
            t = threading.Timer(timer_start_time,_autoRun)
            t.start()
            # print(f"距离下次运行:{next_time}")
            _loggin(INFO,f"距离下次运行:{next_time}")
    except BaseException as error:
        # print(f"设置定时器失败:{error}")
        _loggin(ERR,error)
    
def _autoRun():
    _getSetting()
    # 获取信息，并推送钉钉机器人
    getInfo()
    pushToDingTalk()
    # 开启下一轮定时
    if Time:autoRun()

def _getSetting():
    global Time,ZENTAOURL,PushMsg,PushWebHook,headers,PushNumber
    path = "setting.json"
    # print(f"开始获取配置")
    _loggin(INFO,"开始获取配置")
    setting = {
        "Timing":None,
        "Url":None,
        "PushKey":"禅道推送信息",
        "PushNumber":[],
        "PushWebHook":None,
        "Cookie":None,
        "Default":{
            "Headers":{
                "Cookie":None
            }
        }
    }
    try:
        with open("setting.json",encoding="utf-8") as f:
            setting = json.load(f)
    except BaseException as error:
        # print(f"配置获取失败:{error}")
        _loggin(ERR,error)
    finally:
        Time = " "+str(setting["Timing"])
        ZENTAOURL = setting["Url"]
        PushMsg = setting["PushKey"]
        PushNumber = setting["PushNumber"]
        PushWebHook = setting["PushWebHook"]
        headers = setting["Default"]["Headers"]
        headers["Cookie"] = setting["Cookie"]

def _getNum(NumInFo):
    return int(re.match('<a.*>(.*)',NumInFo).group(1) if re.match('<a.*>(.*)',NumInFo) else NumInFo)

def _getTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def _loggin(iden,msg):
    if iden.lower() in MsgTypes:
        print(f"{_getTime()} {MsgTypes[iden.lower()]} {msg}")
    else:
        print(f"{_getTime()} {iden} {msg}")

_autoRun()
