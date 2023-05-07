from ws4py.client.threadedclient import WebSocketClient
import base64
import hashlib
import json
import time
import uuid

base_url = "ws://wsapi.xfyun.cn/v1/aiui"
app_id = "e3dffe15"
api_key = "ffa7ef4a09911bad0155964f470b5a45"
end_tag = "--end--"
Q = []


class WsapiClientAudio(WebSocketClient):
    def opened(self):
        pass

    def closed(self, code, reason=None):
        if code == 1000:
            print("链接正常关闭")
        else:
            print("链接关闭异常！错误码：" + str(code) + "原因：" + str(reason))

    def received_message(self, m):
        with open("../log.txt", "a") as f:
            f.write(str(m) + "\r")
        s = json.loads(str(m))
        if s['action'] == "started":
            file_object = open("ppp.wav", 'rb')
            try:
                while True:
                    chunk = file_object.read(1280)
                    if not chunk:
                        break
                    self.send(chunk)
                    time.sleep(0.04)
            finally:
                file_object.close()
            self.send(bytes(end_tag.encode("utf-8")))
            print("发送结束标识")

        elif s['action'] == "result":
            data = s['data']
            if data['sub'] == "iat":
                Q.append(data["text"])
                print(data["text"])
            elif data['sub'] == "nlp":
                intent = data['intent']
                if intent['rc'] == 0:
                    Q.append(intent['answer']['text'])
                    print(intent['answer']['text'])
                else:
                    Q.append("我不知道你在说什么")
            elif data['sub'] == "tts":
                # TODO 播报pcm音频
                print("tts: " + base64.b64decode(data['content']).decode())


class WsapiClientText(WsapiClientAudio):

    def __init__(self, url, protocols=None, extensions=None, heartbeat_freq=None,
                 ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(url, protocols, extensions, heartbeat_freq, ssl_options, headers, exclude_headers)
        self.question = None

    def received_message(self, m):
        s = json.loads(str(m))
        if s['action'] == "started":
            self.send(self.question.encode("utf-8"))
            self.send(bytes(end_tag.encode("utf-8")))
            print("发送结束标识")
        elif s['action'] == "result":
            data = s['data']
            if data['sub'] == "iat":
                Q.append(data["text"])
                print(data["text"])
            elif data['sub'] == "nlp":
                intent = data['intent']
                if intent['rc'] == 0:
                    Q.append(intent['answer']['text'])
                    print(intent['answer']['text'])
                else:
                    Q.append("我不知道你在说什么")
            elif data['sub'] == "tts":
                # TODO 播报pcm音频
                print("tts: " + base64.b64decode(data['content']).decode())


def get_auth_id():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return hashlib.md5(":".join([mac[e:e + 2] for e in range(0, 11, 2)]).encode("utf-8")).hexdigest()


def XFServerAudio():
    try:
        curTime = int(time.time())
        auth_id = get_auth_id()
        param_iat = """{{
            "auth_id": "{0}",
            "result_level": "plain",
            "interact_mode": "oneshot",
            "data_type": "audio",
            "aue": "raw",
            "scene": "main_box",
            "sample_rate": "16000",
            "ver_type": "monitor",
            "close_delay": "200",
            "context": "{{\\\"sdk_support\\\":[\\\"iat\\\",\\\"nlp\\\",\\\"tts\\\"]}}"
        }}"""
        param = param_iat.format(auth_id).encode(encoding="utf-8")
        paramBase64 = base64.b64encode(param).decode()
        checkSumPre = api_key + str(curTime) + paramBase64
        checksum = hashlib.md5(checkSumPre.encode("utf-8")).hexdigest()
        connParam = "?appid=" + app_id + "&checksum=" + checksum + "&param=" + paramBase64 + \
                    "&curtime=" + str(curTime) + "&signtype=md5"
        ws = WsapiClientAudio(base_url + connParam, protocols=['chat'], headers=[("Origin", "https://wsapi.xfyun.cn")])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        pass
    print(Q)
    return Q


def XFServerText(text: str):
    try:
        curTime = int(time.time())
        auth_id = get_auth_id()
        param_iat = """{{
            "auth_id": "{0}",
            "result_level": "plain",
            "interact_mode": "oneshot",
            "data_type": "text",
            "scene": "main_box",
            "ver_type": "monitor",
            "close_delay": "200",
            "context": "{{\\\"sdk_support\\\":[\\\"iat\\\",\\\"nlp\\\",\\\"tts\\\"]}}"
        }}"""
        param = param_iat.format(auth_id).encode(encoding="utf-8")
        paramBase64 = base64.b64encode(param).decode()
        checkSumPre = api_key + str(curTime) + paramBase64
        checksum = hashlib.md5(checkSumPre.encode("utf-8")).hexdigest()
        connParam = "?appid=" + app_id + "&checksum=" + checksum + "&param=" + paramBase64 + \
                    "&curtime=" + str(curTime) + "&signtype=md5"
        ws = WsapiClientText(base_url + connParam, protocols=['chat'], headers=[("Origin", "https://wsapi.xfyun.cn")])
        ws.question = text
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        pass
    print(Q)
    return Q
