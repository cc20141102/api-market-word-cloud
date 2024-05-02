import json
import re
from urllib import parse

import requests


async def get_aweme_detail(aweme_id: str, cookie: str = None):
    """
    获取作品详情
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62",
        "Referer": f"https://www.kuaishou.com/short-video/{aweme_id}",
        "Origin": "https://www.kuaishou.com",
        "Host":"www.kuaishou.com",
        "Cookie": cookie
    }
    result = {}
    try:
        response = requests.get(url=f"https://www.kuaishou.com/short-video/{aweme_id}", headers=headers)
    except:
        return {}
    if not response.status_code == 200:
        return {}
    pattern = r'<script>window.__APOLLO_STATE__=(.*?)"clients":{}}'  # 匹配所有的 HTML 标签
    script_list = re.findall(pattern, response.text, re.DOTALL)
    if not script_list:
        return result
    script_list[0] = script_list[0] + '"clients":{}}'
    result = json.loads(parse.unquote(script_list[0]))
    return result

async def ks_web_request(query:dict, cookie:str=None):
    """
    快手web网络请求
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62",
        "Referer": f"https://www.kuaishou.com/",
        "Origin": "https://www.kuaishou.com",
        "Host": "www.kuaishou.com",
        "Cookie": cookie
    }
    result = {}
    try:
        response = requests.post(url="https://www.kuaishou.com/graphql", headers=headers, json=query)
    except:
        return result
    if not response.status_code == 200:
        return result
    return json.loads(response.text)['data']
