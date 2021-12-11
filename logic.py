#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
logging.basicConfig(level=logging.INFO)

sys.path.append('../')
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
    return {"Message": "OK"}

# "detail":[{"loc":["query","on_event"],"msg":"field required","type":"value_error.missing"},{"loc":["query","role_name"],"msg":"field required","type":"value_error.missing"},{"loc":["query","srt_url"],"msg":"field required","type":"value_error.missing"},{"loc":["query","remote_ip"],"msg":"field required","type":"value_error.missing"},{"loc":["query","remote_port"],"msg":"field required","type":"value_error.missing"}]}