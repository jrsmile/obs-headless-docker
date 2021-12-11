#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
logging.basicConfig(level=logging.INFO)

sys.path.append('../')
import json
from obswebsocket import obsws,requests  # noqa: E402
from typing import Optional
from fastapi import FastAPI, Request
app = FastAPI()

host = "localhost"
port = 4444
password = "secret"

@app.post("/sls/on_event")
async def on_event(on_event: str, role_name: str, srt_url: str, remote_ip: str, remote_port: str):
    try:
        ws = obsws(host, port, password)
        ws.connect()
        if on_event=="on_connect" and role_name == "publisher":
            ws.call(requests.SetCurrentScene("Stream"))
        elif on_event=="on_close" and role_name == "publisher":
            ws.call(requests.SetCurrentScene("Fallback"))
        else:
            print(f'Unknown on_event: {on_event} or role: {role_name}')
        ws.disconnect()
    except:
        print('could not connect to obs')
    return {"OK": remote_ip}

@app.post("/sls/stat")
async def on_stat(request: Request):
    rbody = await request.body()
    try:
        jobj = json.loads(rbody)
        print(json.dumps(jobj, indent=4, sort_keys=True))
    except:
        print("could not convert stats to json object")
    #print(rbody)
    return {"Message": "OK"}

# [,{"port": "1935","role": "publisher","pub_domain_app": "input/live","stream_name": "obs","url": "input/live/obs","remote_ip": "127.0.0.1","remote_port": "40348","start_time": "2021-12-11 08:29:02","kbitrate":"2632"},{"port": "1935","role": "player","pub_domain_app": "input/live","stream_name": "desktop","url": "output/live/desktop","remote_ip": "127.0.0.1","remote_port": "43256","start_time": "2021-12-11 08:28:59","kbitrate":"851"},{"port": "1935","role": "publisher","pub_domain_app": "input/live","stream_name": "desktop","url": "input/live/desktop","remote_ip": "95.88.201.37","remote_port": "60371","start_time": "2021-12-11 08:28:46","kbitrate":"829"},{"port": "1935","role": "listener","pub_domain_app": "","stream_name": "","url": "","remote_ip": "","remote_port": "","start_time": "2021-12-11 08:28:50","kbitrate": "0"}]