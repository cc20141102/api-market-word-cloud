import requests


def sign(uri, data=None, a1="", web_session=""):
    # 填写自己的 flask 签名服务端口地址
    res = requests.post("http://112.124.25.137:5006",
                        json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
    signs = res.json()
    # print(signs)
    return {
        "x-s": signs["x-s"],
        "x-t": signs["x-t"]
    }