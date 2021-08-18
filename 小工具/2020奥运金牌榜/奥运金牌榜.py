# -*- coding:utf-8 -*-
import wx
import requests
import re
import json
import threading
import time
import random
import os

CCTV_MEDAL_LIST_API = 'https://api.cntv.cn/olympic/getOlyMedals?serviceId=pcocean&itemcode=GEN-------------------------------&t=jsonp&cb=omedals1'

def getMEDAL_LIST_JSON():
    text = {}
    try:
        res = requests.get(CCTV_MEDAL_LIST_API)
        encode = res.headers["Content-Type"]
        regexEncoding = re.findall("charset=(.*)",encode)
        guessEncoding = requests.utils.get_encodings_from_content(res.text)
        if len(regexEncoding)>0:
            res.encoding = regexEncoding[0]
        elif guessEncoding:
            res.encoding = guessEncoding
        else:
            res.encoding = res.apparent_encoding
        res.raise_for_status()
        text = res.content.decode(res.encoding,"ignore").strip('omedals1(').strip(');')
        text = json.loads(text)
    except BaseException as err:
        print(err)
    finally:
        return text

def toThree(it):
    string = str(it)
    if len(string) < 3:
        return "0" * (3 - len(string)) + string
    else:
        return string


def extractMedalList():
    medalListJson = getMEDAL_LIST_JSON()
    medals = []
    if "data" in medalListJson:
        data = medalListJson["data"]
        medalsList = data["medalsList"]
        countryImgTmp = "https://p1.img.cctvpic.com/sports/data/olympic/teamImg/"
        countryJumpTmp = "https://2020.cctv.com/medal_list/details/index.shtml?countryid="
        medals = []
        for medal in medalsList:
            rank = medal["rank"] # 排名
            gold = medal["gold"] # 金牌
            silver = medal["silver"] # 银牌
            bronze = medal["bronze"] # 铜牌
            count = medal["count"] # 总数
            countryname = medal["countryname"] # 国家名称
            countryid = medal["countryid"] # 国家图片ID
            countryImgUrl = countryImgTmp + countryid + ".png" # 国家图片URL
            countryJumpUrl = countryJumpTmp + countryid
            medals.append([rank, countryname, gold, silver, bronze, count, countryid, countryJumpUrl])
    else:
        wx.MessageBox("未获取到信息, 可能是网络原因", caption="获取信息错误", style=wx.OK)
    return medals

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='获取2020奥运金牌榜(刷新时间: 30s)', size=(441, 262),name='启动窗口',style=541072384)
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), './image/设置.png'))
        self.SetIcon(icon)
        self.main = wx.Panel(self)
        self.Centre()
        
        resetImageButton = wx.Image(os.path.join(os.path.dirname(__file__), './image/刷新.png')).Scale(40, 40).ConvertToBitmap()
        self.resetButton = wx.StaticBitmap(self.main, bitmap=resetImageButton,size=(40, 40),pos=(10, 175),name='staticBitmap',style=wx.LC_REPORT)
        self.resetButton.Bind(wx.EVT_LEFT_DOWN,self.resetButton_LMC)
        self.superTable = wx.ListCtrl(self.main,size=(400, 160),pos=(10, 10),name='listCtrl',style=9248)
        checkInfoButton = wx.Button(self.superTable,size=(80, 32),pos=(412, 37),label='查询',name='button')
        self.superTable.AppendColumn('排名', 0,50)
        self.superTable.AppendColumn('国家', 0,50)
        self.superTable.AppendColumn('金牌', 0,50)
        self.superTable.AppendColumn('银牌', 0,50)
        self.superTable.AppendColumn('铜牌', 0,50)
        self.superTable.AppendColumn('总数', 0,50)

        pushImageButton = wx.Image(os.path.join(os.path.dirname(__file__), './image/推送.png')).Scale(40, 40).ConvertToBitmap()
        self.pushButton = wx.StaticBitmap(self.main, bitmap=pushImageButton,size=(40, 40),pos=(60, 175),name='staticBitmap',style=0)
        self.pushButton.Bind(wx.EVT_LEFT_DOWN,self.pushButton_LMC)
        self.pushKey = wx.TextCtrl(self.main,size=(191, 40),pos=(220, 176),value='',name='text',style=wx.TE_MULTILINE)
        
        self.pushKey.Bind(wx.EVT_SET_FOCUS, self.pushKey_Focus)
        self.pushKey.Bind(wx.EVT_KILL_FOCUS, self.pushKey_noFocus)
        
        self.pushSelect = wx.ComboBox(self.main,value='钉钉推送',pos=(110, 175),name='comboBox',choices=['钉钉推送', '微信推送'],style=16)
        self.pushSelect.SetSize((105, 40))
        pushSelect_font = wx.Font(14,74,90,400,False,'Microsoft YaHei UI',28)
        self.pushSelect.SetFont(pushSelect_font)
        
        self.pushSelect.Bind(wx.EVT_COMBOBOX,self.pushSelect_Select)
        
        self.ddKeyPath = os.path.join(os.path.dirname(__file__), 'dd')
        self.threadId = 0
        self.medalList = []
        self.resetTable()
        self.pushSelect_Select("a")
        
    def _extractMedalList(self, id):
        while True:
            print(f"当前运行线程id: {id} ---- ")
            if self.threadId != id:
                print(f"当前线程id: {id} 结束")
                return
            medalList = extractMedalList()

            if medalList:
                if medalList != self.medalList:
                    self.superTable.DeleteAllItems()
                    for item in medalList:
                        self.superTable.Append([i for index,i in enumerate(item) if index < 6])
                    self.medalList = medalList

            time.sleep(30)
           
    def resetTable(self):
        id = random.random()
        self.threadId = id
        threading.Thread(target=self._extractMedalList, args=(id,), daemon=True).start()
       
    def _pushTable(self):
        # 获取前十
        medalList = self.medalList
        medalList = [i for index,i in enumerate(medalList) if index < 10 ]
        
        # 根据模板开始生成
        # ## 2020奥运会金牌榜(前十)
        # [第{1}名](https://p1.img.cctvpic.com/sports/data/olympic/teamImg/{medalList[6]}.png)
        # 🥇金牌: {medalList[2]}
        # 🥈银牌: {medalList[3]}
        # 🥉铜牌: {medalList[4]}
        # 🎉共计奖牌: {medalList[5]}
        # ---

        tp = "*2020奥运会金牌榜(前十)*\n"
        tpContent = ""
        for item in medalList:
            if item[6] == 'CHN':
                imgUrl = "https://emoji.emojipic.cn/pic/72/apple/flag-for-china_1f1e8-1f1f3.png"
            else:
                imgUrl = f"https://p1.img.cctvpic.com/sports/data/olympic/teamImg/{item[6]}.png"
            tpContent += f"### 第{item[0]}名 {item[1]}\
            \n![第1名]({imgUrl})\n\
            \n🥇金牌: {item[2]}\
            \n🥈银牌: {item[3]}\
            \n🥉铜牌: {item[4]}\
            \n🎉共计奖牌: {item[5]}"
            if not item == medalList[-1]:
                tpContent+="\n\n"
        content = tp + tpContent
        print(content)
        
        pushHeader = {"Content-Type": "application/json"}
        pushMsg ={"msgtype": "markdown","markdown": {"title":"2020奥运会金牌榜(前十)推送","text": content}}
        pushUrl = "https://oapi.dingtalk.com/robot/send?access_token="
        pushToken = self.pushKey.GetValue()
        caption = self.pushSelect.GetValue()
        # if caption == "钉钉推送":
        if "输入" in pushToken or "不支持" in pushToken:
            wx.MessageBox(f"不是{caption}的key", caption=caption, style=wx.OK)
            return
        url = pushUrl+pushToken
        msg = json.dumps(pushMsg)
        r = requests.post(url, headers=pushHeader, data=msg)
        info = r.json()
        print(info)
        if info["errcode"] == 0:
            wx.MessageBox("推送成功", caption=caption, style=wx.OK)
            with open(self.ddKeyPath,"w") as f:
                f.write(pushToken)
            

    def pushTable(self):
        threading.Thread(target=self._pushTable, daemon=True).start()

    def resetButton_LMC(self,event):
        print('resetButton,鼠标左键按下')
        self.resetTable()


    def pushButton_LMC(self,event):
        print('pushButton,鼠标左键按下')
        self.pushTable()
   
    def pushKey_Focus(self,event):
        print('pushKey, 获得焦点')
        if "输入" in self.pushKey.GetValue() or "不支持" in self.pushKey.GetValue():
            self.pushKey.SetValue("")
   
    def pushKey_noFocus(self,event):
        print('pushKey, 失去焦点')
        if self.pushKey.GetValue() == "":
            self.pushSelect_Select("a")
    
    def pushSelect_Select(self,event):
        selectValue = self.pushSelect.GetValue()
        if selectValue == "钉钉推送":
            ddKeyPath = self.ddKeyPath
            if os.path.exists(ddKeyPath):
                with open(ddKeyPath,"r") as f:
                    self.pushKey.SetValue(f.read())
            else:
                self.pushKey.SetValue("输入钉钉机器人的access_token即\n可.(ps: 设置关键词为'推送')")
        else:
            self.pushKey.SetValue(f"当前不支持{selectValue}")

class myApp(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show(True)
        return True

if __name__ == '__main__':
    app = myApp()
    app.MainLoop()