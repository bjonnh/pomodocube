#!/usr/bin/python

import zmq
import sys

url = 'tcp://127.0.0.1:5555'
if len(sys.argv)>1:
    ctx = zmq.Context()
    push = ctx.socket(zmq.REQ)
    push.connect(url)

    push.send_string(sys.argv[1])

