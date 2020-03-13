#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : hgh

from core import socket_client
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)



if __name__ == "__main__":
    host, port = "192.168.40.1", 9901
    myClient = socket_client.MySocketClient(host, port)
    myClient.start()

