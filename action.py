# -*- encoding: utf-8 -*-
"""
@FILE    :   action.py
@DSEC    :   网易云音乐签到刷歌脚本
@AUTHOR  :   Secriy
@DATE    :   2021/05/27
@VERSION :   2.5
"""

import os
import requests
import base64
import sys
import binascii
import argparse
import random
import hashlib
from Crypto.Cipher import AES
import json


# Get the arguments input.
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("phone", help="Your Phone Number.")
    parser.add_argument("password", help="The plaint text or MD5 value of the password.")
    parser.add_argument("-s", dest="sc_key", nargs=1, help="The SCKEY of the Server Chan.")
    parser.add_argument("-t", dest="tg_bot_key", nargs=2, help="The Token and Chat ID of your telegram bot.")
    parser.add_argument("-b", dest="bark_key", nargs=1, help="The key of your bark app.")
    parser.add_argument("-w", dest="wecom_key", nargs=3, help="Your Wecom ID, App-AgentID and App-Secrets.")
    parser.add_argument("-p", dest="push_plus_key", nargs=1, help="The token of your pushplus account.")
    args = parser.parse_args()

    return {
        "phone": args.phone,
        "password": args.password,
        "sc_key": args.sc_key,
        "tg_bot_key": args.tg_bot_key,
        "bark_key": args.bark_key,
        "wecom_key": args.wecom_key,
        "push_plus_key": args.push_plus_key,
    }


# Get custom playlist.txt
def get_playlist():
    path = sys.path[0] + "/playlist.txt"
    try:
        file = open(path)
    except FileNotFoundError:
        return []
    lines = file.readlines()
    return lines


# Calculate the MD5 value of text
def calc_md5(text):
    md5_text = hashlib.md5(text.encode(encoding="utf-8")).hexdigest()
    return md5_text


# AES Encrypt
def aes_encrypt(text, sec_key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(sec_key.encode("utf8"), 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text.encode("utf8"))
    ciphertext = str(base64.b64encode(ciphertext), encoding="utf-8")
    return ciphertext


# RSA Encrypt
def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(text.encode("utf-8").hex(), 16) ** int(pub_key, 16) % int(modulus, 16)
    return format(rs, "x").zfill(256)


class Push:
    def __init__(self, text):
        self.text = text

    # Server Chan Turbo Push
    def server_chan_push(self, arg):
        url = "https://sctapi.ftqq.com/%s.send" % arg[0]
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        content = {"title": "网易云打卡", "desp": self.text}
        ret = requests.post(url, headers=headers, data=content)
        print("ServerChan: " + ret.text)

    # Telegram Bot Push
    def telegram_push(self, arg):
        url = "https://api.telegram.org/bot{0}/sendMessage".format(arg[0])
        data = {
            "chat_id": arg[1],
            "text": self.text,
        }
        ret = requests.post(url, data=data)
        print("Telegram: " + ret.text)

    # Bark Push
    def bark_push(self, arg):
        data = {"title": "网易云打卡", "body": self.text}
        headers = {"Content-Type": "application/json;charset=utf-8"}
        url = "https://api.day.app/{0}/?isArchive={1}".format(arg[0], arg[1])
        ret = requests.post(url, json=data, headers=headers)
        print("Bark: " + ret.text)

    # PushPlus Push
    def push_plus_push(self, arg):
        url = "http://www.pushplus.plus/send?token={0}&title={1}&content={2}&template={3}".format(
            arg[0], "网易云打卡", self.text, "html"
        )
        ret = requests.get(url)
        print("pushplus: " + ret.text)

    # Wecom Push
    def wecom_id_push(self, arg):
        body = {
            "touser": "@all",
            "msgtype": "text",
            "agentid": arg[1],
            "text": {"content": self.text},
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
        }
        access_token = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(str(arg[0]), arg[2])
        ).json()["access_token"]
        res = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(access_token),
            data=json.dumps(body),
        )
        ret = res.json()
        if ret["errcode"] != 0:
            print("微信推送配置错误")
        else:
            print("Wecom: " + ret)


class Encrypt:
    def __init__(self):
        self.modulus = (
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629"
            "ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d"
            "813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7 "
        )
        self.nonce = "0CoJUm6Qyw8W8jud"
        self.pubKey = "010001"

    def encrypt(self, text):
        # Random String Generator
        sec_key = str(binascii.hexlify(os.urandom(16))[:16], encoding="utf-8")
        enc_text = aes_encrypt(aes_encrypt(text, self.nonce), sec_key)
        enc_sec_key = rsa_encrypt(sec_key, self.pubKey, self.modulus)
        return {"params": enc_text, "encSecKey": enc_sec_key}


class CloudMusic:
    def __init__(self, phone, password):
        self.session = requests.Session()
        self.enc = Encrypt()
        self.phone = phone
        self.csrf = ""
        self.nickname = ""
        self.uid = ""
        self.login_data = self.enc.encrypt(
            json.dumps({"phone": phone, "countrycode": "86", "password": password, "rememberLogin": "true"})
        )
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 "
            "Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
        }
        self.proxy = [
                {
                        'http': 'http://61.135.217.7:80',
                        'https': 'http://61.135.217.7:80',
                    },
                {
                        'http': 'http://118.114.77.47:8080',
                        'https': 'http://118.114.77.47:8080',
                    },
                {
                        'http': 'http://112.114.31.177:808',
                        'https': 'http://112.114.31.177:808',
                    },
                {
                        'http': 'http://183.159.92.117:18118',
                        'https': 'http://183.159.92.117:18118',
                    },
                {
                        'http': 'http://110.73.10.186:8123',
                        'https': 'http://110.73.10.186:8123',
                    },
                ]   

    def login(self):
        login_url = "https://music.163.com/weapi/login/cellphone"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; "
            "channel=netease; __remember_me=true;",
        }
        res = self.session.post(url=login_url, data=self.login_data, headers=headers, proxies=random.choice(self.proxy))
        ret = json.loads(res.text)
        if ret["code"] == 200:
            self.csrf = requests.utils.dict_from_cookiejar(res.cookies)["__csrf"]
            self.nickname = ret["profile"]["nickname"]
            self.uid = ret["account"]["id"]
            text = '"{nickname}" 登录成功，当前等级：{level}\n\n距离升级还需听{before_count}首歌'.format(
                nickname=self.nickname,
                level=self.get_level()["level"],
                before_count=self.get_level()["nextPlayCount"] - self.get_level()["nowPlayCount"],
            )
        else:
            text = "账号 {0} 登录失败: ".format(self.phone) + str(ret["code"])
        return text

    # Get the level of account.
    def get_level(self):
        url = "https://music.163.com/weapi/user/level?csrf_token=" + self.csrf
        res = self.session.post(url=url, data=self.login_data, headers=self.headers, proxies=random.choice(self.proxy))
        ret = json.loads(res.text)
        return ret["data"]

    # def refresh(self):
    #     url = "https://music.163.com/weapi/login/token/refresh?csrf_token=" + self.csrf
    #     res = self.session.post(url=url,
    #                             data=self.loginData,
    #                             headers=self.headers)
    #     ret = json.loads(res.text)
    #     print(ret)
    #     return ret["code"]

    def sign(self):
        sign_url = "https://music.163.com/weapi/point/dailyTask?{csrf}".format(csrf=self.csrf)
        res = self.session.post(url=sign_url, data=self.enc.encrypt('{"type":0}'), headers=self.headers, proxies=random.choice(self.proxy))
        ret = json.loads(res.text)
        if ret["code"] == 200:
            text = "签到成功，经验+" + str(ret["point"])
        elif ret["code"] == -2:
            text = "今天已经签到过了"
        else:
            text = "签到失败 " + str(ret["code"]) + "：" + ret["message"]
        return text

    def task(self, playlist):
        url = "https://music.163.com/weapi/v6/playlist/detail?csrf_token=" + self.csrf
        recommend_url = "https://music.163.com/weapi/v1/discovery/recommend/resource"
        music_lists = []
        if not playlist:
            res = self.session.post(
                url=recommend_url, data=self.enc.encrypt('{"csrf_token":"' + self.csrf + '"}'), headers=self.headers, proxies=random.choice(self.proxy)
            )
            ret = json.loads(res.text)
            if ret["code"] != 200:
                print("获取推荐歌曲失败 " + str(ret["code"]) + "：" + ret["message"])
            else:
                lists = ret["recommend"]
                music_lists = [(d["id"]) for d in lists]
        else:
            music_lists = playlist
        # 获取个人歌单
        private_url = "https://music.163.com/weapi/user/playlist?csrf_token=" + self.csrf
        pres = self.session.post(
            url=private_url,
            data=self.enc.encrypt(json.dumps({"uid": self.uid, "limit": 1001, "offset": 0, "csrf_token": self.csrf})),
            headers=self.headers,
            proxies=random.choice(self.proxy),
        )
        pret = json.loads(pres.text)
        if pret["code"] == 200:
            lists = pret["playlist"]
            music_lists.extend([(d["id"]) for d in lists])
        else:
            print("个人歌单获取失败 " + str(pret["code"]) + "：" + pret["message"])
        music_id = []
        for m in music_lists:
            res = self.session.post(
                url=url,
                data=self.enc.encrypt(json.dumps({"id": m, "n": 1000, "csrf_token": self.csrf})),
                headers=self.headers,
                proxies=random.choice(self.proxy),
            )
            ret = json.loads(res.text)
            for i in ret["playlist"]["tracks"]:
                music_id.append([i["id"], i["dt"]])
        music_count = len(music_id)  # 歌单大小
        music_amount = 500 if music_count > 500 else music_count  # 限制歌单大小
        post_data = json.dumps(
            {
                "logs": json.dumps(
                    list(
                        map(
                            lambda x: {
                                "action": "play",
                                "json": {
                                    "download": 0,
                                    "end": "playend",
                                    "id": x[0],
                                    "sourceId": "",
                                    "time": x[1] // 1000,
                                    "type": "song",
                                    "wifi": 0,
                                },
                            },
                            random.sample(music_id, music_amount),
                        )
                    )
                )
            }
        )
        res = self.session.post(url="http://music.163.com/weapi/feedback/weblog", data=self.enc.encrypt(post_data), proxies=random.choice(self.proxy))
        ret = json.loads(res.text)
        if ret["code"] == 200:
            text = "刷听歌量成功，共{0}首".format(music_amount)
        else:
            text = "刷听歌量失败 " + str(ret["code"]) + "：" + ret["message"]
        return text


def run_task(info, phone, password):
    # Start
    app = CloudMusic(phone, password)
    # Login
    res_login = app.login()
    print(res_login, end="\n\n")
    if "400" not in res_login:
        # Sign In
        res_sign = app.sign()
        print(res_sign, end="\n\n")
        # Music Task
        res_task = app.task(get_playlist())
        print(res_task)
        print(30 * "=")
        try:
            # Push
            push = Push(res_login + "\n\n" + res_sign + "\n\n" + res_task)
            # ServerChan
            if info["sc_key"]:
                push.server_chan_push(info["sc_key"])
            # Bark
            if info["bark_key"]:
                push.bark_push(info["bark_key"])
            # Telegram
            if info["tg_bot_key"]:
                push.telegram_push(info["tg_bot_key"])
            # pushplus
            if info["push_plus_key"]:
                push.push_plus_push(info["push_plus_key"])
            # 企业微信
            if info["wecom_key"]:
                push.wecom_id_push(info["wecom_key"])
        except Exception as err:
            print(err)
    else:
        print(res_login)
    print(30 * "=")


if __name__ == "__main__":
    # Get arguments
    infos = get_args()
    phone_list = infos["phone"].split(",")
    passwd_list = infos["password"].split(",")
    # Run tasks
    for k, v in enumerate(phone_list):
        print(30 * "=")
        if not passwd_list[k]:
            break
        if len(passwd_list[k]) == 32:
            run_task(infos, phone_list[k], passwd_list[k])
        else:
            run_task(infos, phone_list[k], calc_md5(passwd_list[k]))
