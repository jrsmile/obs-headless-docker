#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
logging.basicConfig(level=logging.INFO)

sys.path.append('../')
import json
from collections import deque
from statistics import mean
from obswebsocket import obsws,requests  # noqa: E402
from typing import Optional
from fastapi import FastAPI, Request
app = FastAPI()

host = "localhost"
port = 4444
password = "secret"
avg_bitrate = 2000

d = deque(maxlen=10)
for i in range(10):
    d.append(avg_bitrate)

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
            logging.warning(f'Unknown on_event: {on_event} or role: {role_name}')
        ws.disconnect()
    except:
        logging.error('could not connect to obs')
    return {"OK": remote_ip}

@app.post("/sls/stat")
async def on_stat(request: Request):
    rbody = await request.body()
    try:
        jobj = json.loads(rbody)
        logging.debug(json.dumps(jobj, indent=4, sort_keys=True))
        for s in range(len(jobj)):
            if jobj[s]['pub_domain_app'] == "input/live" and jobj[s]['role'] == "publisher" and jobj[s]['stream_name'] == "desktop":
                global d
                d.append(int(jobj[s]['kbitrate']))
                avg_bit = mean(d)
                print("### Current Bitrate is: {}, average Bitrate is: {} ###".format(jobj[s]['kbitrate'], avg_bit))
                ws = obsws(host, port, password)
                ws.connect()
                if avg_bit <= avg_bitrate:
                    ws.call(requests.SetCurrentScene("Fallback"))
                    print("Current bitrate to low, switching to Fallback Stream")
                elif avg_bit > avg_bitrate:
                    ws.call(requests.SetCurrentScene("Stream"))
                    print("Current bitrate high enough, switching to Live Stream")
                ws.disconnect()
    except Exception as e:
        print('Failed JSON Parsing: '+ str(e))
    #print(rbody)
    return {"Message": "OK"}


#"kbitrate": "6151",
#"port": "1935",
#"pub_domain_app": "input/live",
#"remote_ip": "95.88.201.37",
#"remote_port": "61257",
#"role": "publisher",
#"start_time": "2021-12-11 10:23:47",
#"stream_name": "desktop",
#"url": "input/live/desktop"