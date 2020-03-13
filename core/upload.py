#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : hgh

import hashlib
import sys


class Breakpoint(object):
    # 本模块确认用户上传或下载的文件是否存在，如果存在是否需要断点续传
    def transfer(self, filename, has_send_size, total_size, conn):
        """
        进行续传
        :param filename:
        :param has_send_size: 已经发送的文件大小
        :param total_size: 需要传输文件总大小
        :param conn: 客户端和服务端进行数据交换的接口
        :return:
        """
        with open(filename, 'rb') as fr:
            fr.seek(has_send_size)     # 定位到续传的位置
            print("has_send", has_send_size, "total", total_size)
            m = hashlib.md5()
            if has_send_size == total_size:
                self.progress_bar(has_send_size, total_size)
            for line in fr:
                conn.send(line)
                m.update(line)
                has_send_size += len(line)
                # self.progress_bar(has_send_size,total_size)
        return m.hexdigest()

    def progress_bar(self, has_send_size, total_size):
        bar_width = 50     # 进度条长度
        process = has_send_size / total_size
        send_bar = int(process * bar_width + 0.5)     # 发送的数据占到的进度条长度，四舍五入取整
        sys.stdout.write("#" * send_bar + "=" * (bar_width - send_bar) + "\r")  # 注意点：只能这么写才能达到要求
        sys.stdout.write("\r%.2f%%: %s%s" % (process * 100, "#" * send_bar, "=" * (bar_width - send_bar)))  # 注意点：在pycharm中要加\r\n
                                                                       # 用sublime只要\r否则换行
        sys.stdout.flush()

