#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : hgh

import hashlib
import os
import json
from conf import settings

class User_auth(object):
    def auth(self, account_info):
        """
        #此功能是进行用户的登录信息验证，如果登录成功，那么返回用户对应的http状态码及账户信息,否则只返回http状态码
        :param account_info: 用户的账户信息：用户名，密码
        :return:
        """
        name = account_info.split(":")[0]
        pwd = account_info.split(":")[1]
        pwd = self.hash(pwd.encode())   # 将用户名的密码转换成hash值
        user_db_file = settings.DATABASE + r"\%s.db" % name  # 也可以写成 "\\%s.db"  or "/%s.db"
        if os.path.isfile(user_db_file):    # 输入的用户名存在
            with open(user_db_file) as fr:
                user_db_info = json.loads(fr.read())     # or josn.load(fr)
                if pwd == user_db_info['password']:
                    return "200", user_db_info      # 确定，客户请求成功
                else:
                    return "403.11", None     # 密码错误
        else:
            return "400", None     # 用户名不存在，用户认证失败


    def hash(self, pwd):
        """
         用户的密码加密
        :param self:
        :param pwd: 用户密码
        :return:
        """
        m = hashlib.md5()
        m.update(pwd)
        return m.hexdigest()
