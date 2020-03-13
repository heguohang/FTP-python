#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : hgh

import socketserver
import hashlib
import os
from core import upload
from core import auth


# socketserver
class MyTCPServer(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while True:
                self.data = self.request.recv(1024).decode()   # 接受来自客户端的账号的登录信息
                auth_result = auth.User_auth().auth(self.data)   # 进行用户验证
                status_code = auth_result[0]
                if status_code == "400" or status_code == "403.11":
                    self.request.send(status_code.encode())  # 用户名不存在或密码错误
                    continue
                self.request.send(status_code.encode())   # 用户认证成功
                self.user_db_info = auth_result[1]        # 获取用户的数据库信息
                self.home_path = self.user_db_info['homepath']
                self.current_path = self.user_db_info['homepath']  # 登陆成功后立即定义一个“当前路径”变量，供后面创建目录，切换目录使用
                while True:
                    self.cmd = self.request.recv(1024).decode()   # 接收客户端的上传或下载命令
                    self.cmd_action = self.cmd.split()[0]
                    if hasattr(self, self.cmd_action):
                        func = getattr(self, self.cmd_action)
                        func(self.cmd)
                    else:
                        self.request.send("401".encode())  # 命令不存在
        except ConnectionResetError as e:
            self.request.close()
            print(e)


    """服务端可以提供的命令"""
    def put(self, cmd):
        """
        接受客户端的上传文件命令
        :param self:
        :param cmd: eg: put filename
        :return:
        """
        filename = cmd.split()[1]
        fileName = filename.split("\\")[-1]  # 文件的名称
        home_file = os.path.join(self.current_path, fileName)    # 判断当前路径下是否有上传的文件名
        self.request.send("000".encode())  # 系统交互码
        total_size = self.request.recv(1024).decode()  # 上传文件大小
        remain_size = self.accountRemainSize()  # 获得账户剩余大小
        if remain_size > int(total_size):
            if os.path.isfile(home_file):
                self.request.send("202".encode())   # 创建的文件已经存在
                self.request.recv(1024)   # 等待ack指令
                has_recvd_size = os.stat(home_file).st_size   # 已经接收的大小
                self.request.send(str(has_recvd_size).encode())
            else:
                has_recvd_size = 0
                self.request.send("402".encode())  # 创建的文件不存在
            # 开始接受客户端的数据
            recvd_size = 0
            m = hashlib.md5()
            with open(home_file, "ab") as fa:
                while recvd_size != int(total_size) - has_recvd_size:    # 循环接受来自的文件数据
                    data = self.request.recv(1024)
                    m.update(data)
                    recvd_size += len(data)
                    fa.write(data)
                self.request.send(m.hexdigest().encode())   # 发送接收到的文件的md5
        else:
            self.request.send("413".encode())  # 磁盘空间不够用

    def get(self,cmd):
        """
        接受客户端的上传文件命令
        :param self:
        :param cmd: eg: get filename
        :return:
        """
        filename = cmd.split()[1]
        fileName = filename.split("\\")[-1]  # 文件的名称
        home_file = os.path.join(self.home_path, fileName)    # 用于判断家目录下是否有下载的文件名
        if os.path.isfile(home_file):    # 这里不用判断if status_code == "205" or status_code == "402":
            total_size = os.stat(home_file).st_size  # 因为如果接收到客户端的状态码，服务端一定要先去找文件是否存在
            self.request.send("206".encode())  # 服务端有客户需要下载的文件
            has_send_size = self.request.recv(1024).decode()
            self.request.send(str(total_size).encode())
            self.request.recv(1024)  # 粘包
            send_md5 = upload.Breakpoint().transfer(home_file, int(has_send_size), total_size, self.request)
            self.request.recv(1024)  # 粘包
            self.request.send(send_md5.encode())
        else:
            self.request.send("402".encode())  # 服务端文件不存在


    def accountRemainSize(self):
        """
        统计登录用户可用目录大小
        :return:
        """
        account_path = self.user_db_info["homepath"]
        print("homepath:", account_path,)
        limitsize = self.user_db_info['limitsize']
        used_size = 0
        for root, dirs, files in os.walk(account_path):
            used_size += sum([os.path.getsize(os.path.join(root, filename))for filename in files])
        return limitsize - used_size

    def mkdir(self, cmd):
        """
        创建目录，支持创建级联目录
        :param cmd:
        :return:
        """
        dir = cmd.split()
        dir_path = os.path.join(self.current_path, dir[-1])
        if len(dir) == 2:
            if not os.path.isdir(dir_path):
                try:
                    os.mkdir(dir_path)
                except FileNotFoundError as e:
                    os.makedirs(dir_path)   # 创建级联目录
                self.request.send("200".encode())
            else:
                self.request.send("403".encode())  # 创建目录存在
        else:
            self.request.send("400".encode())

    def pwd(self, cmd):
        self.request.send(self.current_path.encode())

    def cd(self, cmd):
        dir = cmd.split()
        if len(dir) == 2:
            if dir[-1] == "..":    # 只能让用户在自己目录下操作
                if len(self.current_path) > len(self.home_path):
                    self.current_path = os.path.dirname(self.current_path)
                    self.request.send("200".encode())
                else:
                    self.request.send("403".encode())  # 请求被拒绝，没有上层目录了
            elif os.path.isdir(self.current_path + "\\" + dir[-1]):
                self.current_path = self.current_path + "\\" + dir[-1]
                self.request.send("200".encode())
            else:
                self.request.send("402".encode())
        else:
            self.request.send("400".encode())

    def ls(self, cmd):
        dirs = os.listdir(self.current_path)
        self.request.send(str(dirs).encode())



