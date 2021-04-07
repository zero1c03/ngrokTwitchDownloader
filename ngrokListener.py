from flask import Flask
from flask import json
from flask import Response
from flask import request
from concurrent.futures import ThreadPoolExecutor as Pool
from queue import Queue
import time, datetime, threading, subprocess, logging, sys, os, configparser, streamlink

app = Flask(__name__)
inet_addr = "127.0.0.1"

mainDir = sys.path[0]
Config = configparser.ConfigParser()
setting = {}
recording = []

@app.route("/api/online/<string:name>", methods=['POST'])
def postMethod(name):
    if name not in recording:
        thread = threading.Thread(target=startRecording, args=(name.lower(),))
        thread.start()
        return name + " start download"
    else:
        return name + " is downloading"

def startRecording(name):
    try:
        name = name.lower()
        streams = streamlink.streams("https://www.twitch.tv/" + name)
        stream = streams["best"]
        fd = stream.open()
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime("%Y.%m.%d_%H.%M.%S")
        file = os.path.join(setting['save_directory'], name, "{st}_{name}.mp4".format(path=setting['save_directory'], name=name,
                                                            st=st))
        os.makedirs(os.path.join(setting['save_directory'], name), exist_ok=True)
        with open(file, 'wb') as f:
            recording.append(name)
            while True:
                try:
                    data = fd.read(1024)
                    f.write(data)
                except:
                    break
    finally:
        if name in recording:
            recording.remove(name)


def readConfig():
    global setting
    Config.read(mainDir + "/config.conf")
    setting = {
        'save_directory': Config.get('paths', 'save_directory'),
        }
    if not os.path.exists("{path}".format(path=setting['save_directory'])):
        os.makedirs("{path}".format(path=setting['save_directory']))


if __name__ == '__main__':
    readConfig()
    #app.debug = True
    print("inet_addr: " + inet_addr)
    app.run(
        host=inet_addr,
        port=8090
    )
