#! -*- coding: UTF-8 -*-
"""
    脚本功能：
        - 扫码登陆B站，缓存cookie
        - 保存登陆凭证到PotPlayer的配置文件
        - 搭配该项目使用 https://github.com/chen310/BilibiliPotPlayer

    使用方法：
        1. 安装Python，并安装所需要的库
        2. 修改参数config_file，指向PotPlayer的配置文件，也可以直接复制到配置文件路径
        3. 执行脚本，扫描二维码，扫描成功后，会自动保存登陆凭证到PotPlayer的配置文件
        4. 关闭PotPlayer，重新打开，即可正常使用B站登录功能

    代码参考：
    【【python爬虫】获取B站cookie教程，生成cookie文件，各大网站（某乎，某音，某博等）cookie均可保存（附源码）】
    https://www.bilibili.com/video/BV1Ue41197vz/?share_source=copy_web&vd_source=b22e943fdbf4809cf6c3520fdfb6ed86

    注意：
    1. 脚本会缓存cookies到脚本所在文件夹的cookie文件夹中，文件名为bilibili.cookies。
    2. 缓存文件涉及登陆凭证，请勿泄露。
    3. 脚本仅供学习交流使用，请勿用于商业用途。

    时间：2025-05-22
    作者：lyd
    github: https://github.com/luyuduan/get_bilibili_cookie

"""

import json
import os
from http.cookiejar import LWPCookieJar
from io import BytesIO
from os import path
from re import findall
from threading import Thread
from time import sleep
from tkinter import StringVar, Tk, messagebox
from tkinter.ttk import Button, Label

import requests
from PIL import Image, ImageTk
from qrcode import QRCode
from qrcode.image.pil import PilImage
from requests.cookies import RequestsCookieJar
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning


class LoginManager:
    """扫码登陆B站，保存登陆凭证"""

    def __init__(self, config_file):
        """初始化
        @param config_file: 配置文件路径
        """
        self.screen = Tk()
        self.info = StringVar()
        self.session = requests.session()
        self.btn1 = None
        self.tk_image = None
        self.cookies = None

        cookie_path = "./cookie"
        self.temp_cookie = cookie_path + "/bilibili.cookies"

        if not path.exists(config_file):
            raise FileExistsError(f"配置文件不存在，请指定配置文件路径：{config_file}")
        self.config_file = config_file

        # 缓存文件
        os.makedirs(cookie_path, exist_ok=True)

        if not path.exists(self.temp_cookie) or os.path.getsize(
                self.temp_cookie) == 0:
            with open(self.temp_cookie, "w", encoding="utf-8") as f:
                f.write("#LWP-Cookies-2.0")

        # 网络请求
        disable_warnings(category=InsecureRequestWarning)
        headers = {
            "authority":
            "api.vc.bilibili.com",
            "accept":
            "application/json, text/plain, */*",
            "accept-language":
            "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type":
            "application/x-www-form-urlencoded",
            "origin":
            "https://message.bilibili.com",
            "referer":
            "https://message.bilibili.com/",
            "sec-ch-ua":
            '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            "sec-ch-ua-mobile":
            "?0",
            "sec-ch-ua-platform":
            '"Windows"',
            "sec-fetch-dest":
            "empty",
            "sec-fetch-mode":
            "cors",
            "sec-fetch-site":
            "same-site",
            "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        }
        self.session.headers.update(headers)

        # 窗口设置
        self.screen.geometry("300x225")
        self.screen.title("扫码登陆B站")
        self.screen.resizable(False, False)  # 防止用户调整尺寸

        label_ver = Label(master=self.screen, textvariable=self.info)
        label_ver.grid(row=9, column=1, rowspan=8, columnspan=1, sticky="n")

        self.thread_it(self.login)

        self.screen.mainloop()

    def read_cookie(self):
        """读取缓存文件"""
        cookie_jar = LWPCookieJar(filename=self.temp_cookie)
        cookie_jar.load(ignore_discard=True)

        # 创建一个 RequestsCookieJar 对象
        session_cookie_jar = RequestsCookieJar()
        # 将 LWPCookieJar 中的 cookie 添加到 RequestsCookieJar 对象中
        session_cookie_jar.update(cookie_jar)
        self.session.cookies = session_cookie_jar

    def save_cookies(self):
        """保存cookies到缓存文件"""
        cookie_jar = LWPCookieJar()
        # cookie_jar.extract_cookies(self.session.cookies, cookie_jar)
        for cookie in self.session.cookies:
            cookie_jar.set_cookie(cookie)

        cookie_jar.save(filename=self.temp_cookie, ignore_discard=True)

    def is_login(self):
        """判断是否登录"""
        self.read_cookie()
        url = "https://api.bilibili.com/x/web-interface/nav"

        login_rsp = self.session.get(url, verify=False).json()
        if login_rsp["data"]["isLogin"] and login_rsp["code"] == 0:
            print(f"{login_rsp['data']['uname']}, 已登录！")
            return login_rsp, True
        else:
            return login_rsp, False

    def get_qrcode(self):
        """获取二维码"""
        qrcode_gen_url = "https://passport.bilibili.com/x/passport-login/" + \
            "web/qrcode/generate?source=main-fe-header"

        rsp = self.session.get(qrcode_gen_url, verify=False)
        rsp_json = rsp.json()
        qrcode_key = rsp_json["data"]["qrcode_key"]
        token_url = "https://passport.bilibili.com/x/passport-login/" + \
            f"web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header"

        qr = QRCode()
        qr.add_data(rsp_json["data"]["url"])
        img: PilImage = qr.make_image(image_factory=PilImage)
        pil_image_resize = img.resize((200, 200),
                                      resample=Image.Resampling.BICUBIC,
                                      box=None,
                                      reducing_gap=None)

        self.tk_image = ImageTk.PhotoImage(pil_image_resize)
        label_ver1 = Label(self.screen, image=self.tk_image)
        label_ver1.grid(row=1, column=1, rowspan=8, columnspan=1, sticky="n")

        return token_url

    def check_qrcode(self, token_url):
        """检查二维码状态"""

        qrcode_data = self.session.get(token_url).json()
        if qrcode_data["data"]["code"] == 0:
            self.session.get(qrcode_data["data"]["url"])
            self.save_cookies()
            return True, qrcode_data["data"]["message"]

        else:
            return False, qrcode_data["data"]["message"]

    def scan_code(self):
        """生成二维码"""

        check_url = self.get_qrcode()

        while True:
            ret, msg = self.check_qrcode(check_url)
            if ret:
                break
            else:
                self.info.set(msg)
                if msg == "二维码已失效":
                    self.info.set("请重新扫码")
                    self.screen.update()
                    check_url = self.get_qrcode()

            sleep(1)

    def update_config(self):
        """ 更新配置文件 """

        # 收集cookies中config需要的关键信息
        s = f"SESSDATA={self.session.cookies.get_dict().get('SESSDATA')}"

        with open(self.config_file, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
            config_dict["cookie"] = s
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)

        self.info.set("登录成功！配置文件已更新")
        self.screen.update()

    def login_success(self, resp):
        """ 登录成功后，显示头像和退出登录按钮，并更新配置文件 """

        # 登录成功，显示头像
        # 下载头像
        face_url = resp["data"]["face"]
        image_bytes = self.session.get(face_url).content
        data_stream = BytesIO(image_bytes)
        pil_image = Image.open(data_stream)
        # 显示头像
        pil_image_resize = pil_image.resize((200, 200),
                                            resample=Image.Resampling.BICUBIC,
                                            box=None,
                                            reducing_gap=None)
        self.tk_image = ImageTk.PhotoImage(pil_image_resize)
        label_img = Label(self.screen, image=self.tk_image)
        label_img.grid(row=1, column=1, rowspan=8, columnspan=1, sticky="n")

        self.info.set("登录成功！")

        # 显示退出登录按钮
        self.btn1 = Button(self.screen,
                           width=10,
                           text="退出登录",
                           command=self.cancel_login)
        self.btn1.grid(row=3, column=2)
        self.screen.update()

        self.update_config()

        # self.root.destroy()  # 自动关闭窗口

    def login_failed(self):
        """ 登录失败，重新扫码 """
        self.scan_code()

    def login(self):
        """ 登录，直到登录成功 """
        while True:
            resp, if_login = self.is_login()
            if if_login:
                self.login_success(resp)
                break
            self.login_failed()

    def thread_it(self, func, *args):
        """ 多线程 """
        thread = Thread(target=func, args=args, daemon=True)
        thread.start()

    def cancel_login(self):
        """ 注销登录 """
        msg1 = messagebox.askyesno(title="提示", message="注销后cookie将失效，是否退出登录？")
        if msg1:
            url3 = "https://passport.bilibili.com/login/exit/v2"

            with open(self.temp_cookie, "r", encoding="utf-8") as f:
                cookie_file_buf = f.read()
            bili_jct = findall(r"bili_jct=(.*?);", cookie_file_buf)[0]
            data3 = {"biliCSRF": f"{bili_jct}"}
            self.session.post(url=url3, data=data3).json()

            with open(self.temp_cookie, "w", encoding="utf-8") as f:
                f.write("#LWP-Cookies-2.0")

            if self.btn1:
                self.btn1.destroy()
                self.btn1 = None
            if self.tk_image:
                self.tk_image = None

            self.thread_it(self.login)


if __name__ == "__main__":
    # 参数修改为PotPlayer的B站配置文件路径
    login_manager = LoginManager("./Bilibili_Config.json")
