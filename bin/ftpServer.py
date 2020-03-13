#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : hgh

import sys
import os
from core import socket_server

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)



if __name__ == "__main__":
    HOST, PORT = "192.168.40.1", 9901
    server = socket_server.socketserver.ThreadingTCPServer((HOST, PORT), socket_server.MyTCPServer)
    server.serve_forever()
