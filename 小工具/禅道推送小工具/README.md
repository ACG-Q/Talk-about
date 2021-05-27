# 禅道推送

每日定时推送禅道信息至钉钉

# 设置

```Setting.json
{

    "Cookie":"禅道用户Cookie",
    "PushWebHook":"钉钉推送：https://oapi.dingtalk.com/robot/send?access_token=xx",
    "PushKey":"禅道推送信息",
    "Url":"禅道的域名",
    "Timing":"定时 例子:07:00:00",
    "Default":{
        "Headers":{
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7",
            "Cache-Control":"no-cache",
            "DNT":"1",
            "Host":"test.dfrobot.top:5000",
            "Pragma":"no-cache",
            "Proxy-Connection":"keep-alive",
            "Referer":"禅道的域名",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"自己的User-Agent"
        }
    }
}
```

# 推送信息

```
禅道推送信息
禅道版本:禅道12.3  Byxx(xx代指你在禅道上的名称)
我的任务  数量:0
我的BUG  数量:0
我的需求  数量:0
未关闭的项目  数量:14
未关闭的产品  数量:2
推送时间：2021-05-27 07:00:02
```

## 钉钉机器人

- 第一步：添加机器人，选中 `自定义`机器人
- 第二步：设置关键词：`推送`
