#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT,stream=sys.stdout,level=logging.INFO)

sys.path.append('../')
import json
import itertools
from collections import deque
from statistics import mean
from obswebsocket import obsws,requests  # noqa: E402
from typing import Optional
from fastapi import FastAPI, Request
app = FastAPI()

host = "localhost"
port = 4444
password = "secret"

d = deque(maxlen=300)
for i in range(300):
    d.append(1000)

@app.post("/sls/on_event")
async def on_event(on_event: str, role_name: str, srt_url: str, remote_ip: str, remote_port: str):
    try:
        ws = obsws(host, port, password)
        ws.connect()
        if on_event=="on_connect" and role_name == "publisher" and srt_url == "input/live/desktop":
            logging.info(f"New Publisher connected to {srt_url}, switching to Livestream in 5 Seconds...")
            ws.call(requests.SetCurrentScene("Stream"))
        elif on_event=="on_close" and role_name == "publisher" and srt_url == "input/live/desktop":
            logging.info(f"Publisher disconnected from {srt_url}, switching to Fallback in 5 Seconds...")
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
                d.appendleft(int(jobj[s]['kbitrate']))
                avg_bit = int(mean(d))
                cur_bit = int(mean(itertools.islice(d,0,10)))
                logging.info("### Current Bitrate is: {}, average Bitrate is: {} Fallback treshold: {} ###".format(cur_bit, avg_bit,avg_bit *0.5))
                ws = obsws(host, port, password)
                ws.connect()
                scene = ws.call(requests.GetCurrentScene())
                sceneName = scene.getName()
                if cur_bit < avg_bit * 0.5:
                    if sceneName != "Low":
                        ws.call(requests.SetCurrentScene("Low"))
                        logging.warning("Current bitrate to low, switching to Fallback Stream")
                elif cur_bit >= avg_bit *0.5:
                    if sceneName != "Stream":
                        ws.call(requests.SetCurrentScene("Stream"))
                        logging.warning("Current bitrate high enough, switching to Live Stream")
                ws.disconnect()
    except Exception as e:
        logging.error('Failed JSON Parsing: '+ str(e))
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