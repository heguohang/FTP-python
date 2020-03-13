#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : hgh

import os
import socket
import hashlib
from core import upload
from conf import settings


class MySocketClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket()  # 创建客户端实例

    def start(self):
        self.client.connect((self.host, self.port))  # 连接服务端，localhost为回环地址，一般用于测试
        while True:
            """客户端开始输入账户信息登录"""
            name = input("\033[31m 请输入账户名: \033[0m").strip()
            pwd = input("\033[31m 请输入密码: \033[0m").strip()
            # name = "ahpu";pwd = 123456
            if not name or not pwd: continue  # 如果账户或密码为空请重新输入
            userInfo = "%s:%s" % (name, pwd)
            self.client.send(userInfo.encode())  # 向服务端发送用户信息
            status_code = self.client.recv(1024).decode()  # 接受来自服务端的http状态码
            if status_code == "400":
                print("\033[1;32m 用户名不存在，用户认证失败，请重新输入 \033[0m")
                continue   # 用户名不存在重新输入
            if status_code == "403.11":
                print("\033[1;32m 密码错误，请重新输入 \033[0m")
                continue
            if status_code == "200":
                print("\033[1;32m 登录成功\033[0m")
            self.interact()

    def interact(self):
        """
        客户端与服务端的交互接口
        :return:
        """
        while True:
            cmd = input("""请输入操作： 
            \033[1;31m
            eg:
            get filename  # 从服务端下载文件
            put filename  # 从服务端上传文件
            ls            # 查看当前目录下的文件
            cd            # 目录切换
            pwd           # 查看当前目录
            mkdir dirname # 创建目录
            >>>  \033[0m""").strip()
            cmd_action = cmd.split()[0]
            if hasattr(self, cmd_action):
                func = getattr(self, cmd_action)
                func(cmd)
            else:
                print("输入命令不存在")

    def put(self, cmd):
        """
        客户端上传文件
        :param self:
        :param cmd: 用户的操作命令  eg: put filename
        :return:
        """
        lst = cmd.split()    # 命令分割，此次只允许一次上传一个文件
        if len(lst) == 2:
            filename = lst[1]
            if os.path.isfile(filename):
                self.client.send(cmd.encode())   # 向服务端发送上传文件命令
                status_code = self.client.recv(1024).decode()
                total_size = os.stat(filename).st_size
                self.client.send(str(total_size).encode())
                status_code = self.client.recv(1024).decode()    # 接收来自服务端的http状态码，判断账户是否空间充足，文件是否存在
                if status_code == "202":
                    while True:
                        affirm_msg = input("创建的文件已经存在，请确认是否需要续传：1：续传 2：不续传：")
                        if affirm_msg == "1":
                            print("开始续传")
                            self.client.send("000".encode())    # 发送交互码，避免粘包,服务端此时需要2次连续send
                            has_send_size = self.client.recv(1024).decode()     # 已经发送给服务端的文件大小
                            send_md5 = upload.Breakpoint().transfer(filename, int(has_send_size),
                                         total_size, self.client)  # 进行文件的传输，返回此次发送数据的md5
                            recv_md5 = self.client.recv(1024).decode()   # 服务端接收到此次发送数据的md5
                            # print("\nsend",send_md5)
                            # print("recv",recv_md5)
                            if send_md5 == recv_md5:
                                print("发送数据成功")
                                break
                            else:
                                print("发送数据不成功，请重新发送")
                                break
                        elif affirm_msg == "2":
                            print("不续传")
                            break
                        else:
                            print("输入的命令不存在")
                            continue
                elif status_code == "402":
                    print("文件不存在")   # 文件不存在
                    send_md5 = upload.Breakpoint().transfer(filename, 0, total_size, self.client)  # 进行文件的传输返回此次发送数据的md5
                    recv_md5 = self.client.recv(1024).decode()  # 服务端接收到此次发送数据的md5
                    print("\nsend md5", send_md5)
                    print("recv md5", recv_md5)
                    if send_md5 == recv_md5: print("发送数据成功")
                    else : print("发送数据不成功，请重新发送")
                else:
                    print("用户磁盘空间不够")
            else:print("发送的文件不存在")
        else: print("401 error,命令不正确，一次只能上传一个文件")

    def get(self, cmd):
        lst = cmd.split()
        if len(lst) == 2:
            filename = lst[1]
            fileName = filename.split("\\")[-1]
            self.default_file = os.path.join(settings.DEFAULT_PATH, fileName)
            if os.path.isfile(self.default_file):  # 用户下载的文件在默认地址下是否存在
                while True:
                    affirm_msg = input("创建的文件已经存在，请确认是否需要续传：1：续传 2：不续传：")
                    if affirm_msg == "1":
                        self.get_file(cmd)
                    elif affirm_msg == "2":
                        break
                    else:
                        print("命令不正确")
            else:
                self.get_file(cmd, exist="no")
        else: print("401 error,命令不正确，一次只能下载一个文件")

    def get_file(self, cmd, exist="yes"):
        """
        因为get方法从客户端下载文件，文件存在续传和文件不存在直接下载写法一样，故提取
        :param cmd:
        :param exist: 判断客户端文件是否存在
        :return:
        """
        self.client.send(cmd.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == "206":
            print("需要下载的文件在客户端存在，在服务端也存在，开始续传" if exist == "yes"
                  else "需要下载的文件在服务端存在，在客户端不存在，开始下载")
            has_recvd_size = os.stat(self.default_file).st_size if exist == "yes" else 0
            self.client.send(str(has_recvd_size).encode())
            total_size = self.client.recv(1024).decode()
            self.client.send("000".encode())  # 系统交互，防止粘包
            recvd_size = 0
            m = hashlib.md5()
            with open(self.default_file, "ab") as fa:
                remain_size = int(total_size) - has_recvd_size
                while recvd_size != remain_size:  # 循环接收来自服务端的文件数据
                    data = self.client.recv(1024)
                    m.update(data)
                    recvd_size += len(data)
                    fa.write(data)
                    all_recvd_size = has_recvd_size + recvd_size
                    upload.Breakpoint().progress_bar(all_recvd_size, int(total_size))
                self.client.send("000".encode())  # 粘包
                send_md5 = self.client.recv(1024).decode()  # 服务端发送数据的md5
                if has_recvd_size == int(total_size):
                    print("文件大小一致，无需下载")
                    self.interact()    # 如果按这种逻辑（先判断客户端文件是否存在，在判断该文件的大小是否一致）写，
                    # 只能调用interact()选项才能返回
                if send_md5 == m.hexdigest():
                    print("接收文件成功")
                else:
                    print("接收文件不成功")
        else:
            print("需要下载的文件不存在，无法续传")

    def mkdir(self, cmd):
        self.client.send(cmd.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == "403":
            print("创建的目录存在")
        elif status_code == "401":
            print("输入的命令不存在")

    def pwd(self, cmd):
        self.client.send(cmd.encode())
        cur_path = self.client.recv(1024).decode()
        print(cur_path)

    def cd(self, cmd):
        """
        :param cmd:  eg cd dirname / cd .. /
        :return:
        """
        self.client.send(cmd.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == "402":
            print("创建的目录不存在")
        elif status_code == "400":
            print("命令不正确，格式 cd .. / cd dirname")
        elif status_code == "403":
            print("没有上层目录了")
        else:
            pass

    def ls(self, cmd):
        self.client.send(cmd.encode())
        dirs = self.client.recv(1024).decode()
        print(dirs)




if __name__ == "__main__":
    host,port = "192.168.1.40", 9998
    myClient = MySocketClient(host, port)
    myClient.start()

