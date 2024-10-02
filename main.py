# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
# FOR PERSONAL USE ONLY.
#
# Create Date: 2024/10/02
# Last Update on: 2024/10/03
#---------------------------------------------------------------------------------

import os

from utils import Const, JsonDataProcessor

import sys
import time

def display_static_messages():
    print("Message 1: Other information")
    print("Message 2: Other information")
    
    for i in range(100):
        sys.stdout.write(f'\rCurrent number: {i}')  # 数字在同一行不断更新
        sys.stdout.flush()  # 刷新显示
        time.sleep(0.1)

display_static_messages()

