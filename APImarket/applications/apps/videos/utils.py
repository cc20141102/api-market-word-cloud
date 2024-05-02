import base64
import json
import re
from urllib import parse
from urllib.parse import urlparse

import requests

from app_conf import douyin_default, ks_default
from applications.apps.douyin.utils import Utils, get_data
from applications.apps.douyin.views import AwemeDetailView, reset_douyin_cookie


async def video_parse_main(share_text: str):
    """
    短视频解析入口
    :param share_text:
    :return:
    """
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    matches = re.findall(pattern, share_text)
    if matches:
        url = matches[0]
        if 'douyin.com' in url:
            return await douyin(url=url)
        elif 'bilibili.com' in url:
            return await bilibili(url)
        elif 'kuaishou.com' in url:
            return await kuaishou(url=url)
        elif 'xiaohongshu.com' in url or 'xhslink.com' in url:
            return await xhs(url=url)
        elif 'ixigua.com' in url:
            return await xigua(url=url)
        elif 'toutiao.com' in url:
            return await toutiao(url=url)
        else:
            return None
    return None


async def douyin(url: str):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": douyin_default or ""
    }
    # 获取请求的真实链接：重定向后的链接,如果没有重定向，则可以直接访问
    request_url = requests.get(url=url, headers=headers)
    if not request_url.status_code == 200:
        return False
    url = request_url.url
    # 获取request_url中path部分
    request_url_path = urlparse(url).path
    # 判断是否个人主页，如果是图集或者单个视频，则统一用请求视频链接
    if "note" in request_url_path or "video" in request_url_path:
        # 获取视频或图集ID
        video_id = re.findall(r"\d+", request_url_path)
        if video_id:
            video_id = video_id[0]
            url = AwemeDetailView.request_domain + Utils().getXbogus(f'aweme_id={video_id}&device_platform=webapp&aid=6383')
        else:
            return False
        print(url)
        from applications.apps.douyin.views import headers as douyin_headers
        douyin_headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        response = await get_data(url, douyin_headers)
        print(response)
        if not response['status_code'] and not response['status_code'] == 0:
            return False

    else:
        return False
    data = {
        "title": response['aweme_detail']['preview_title'],
        "audio": response['aweme_detail']['music']['play_url']['url_list'],
        "thumbnail": response['aweme_detail']['video']['cover']['url_list'][0],
        "pics": [item['url_list'][0]for item in response['aweme_detail']['images']] if response['aweme_detail']['images'] else [],
        "videos": response['aweme_detail']['video']['play_addr']['url_list'],
        "type": "video" if not response['aweme_detail']['images'] else "images",
        "source": "douyin",
        "author": response['aweme_detail']['author']['nickname'],
        "author_id": response['aweme_detail']['author']['sec_uid']
    }
    return data


async def bilibili(url:str):
    # 网络请求
    headers = {
        "referer": "https://search.bilibili.com/all?vt=63863998&keyword=%E8%8A%99%E8%95%96%E8%AF%B4&from_source=webtop_search&spm_id_from=333.1007&search_source=3",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": "buvid3=798D045B-044E-B159-D119-CE6F1D65290A26986infoc; b_nut=1676455526; CURRENT_FNVAL=4048; _uuid=D226F248-F6B10-104F9-787F-B381CD10F584D27359infoc; rpdid=|(Y|RJYkRuk0J'uY~YRlllk~; i-wanna-go-back=-1; b_ut=5; nostalgia_conf=-1; buvid4=9CB54975-CAAF-278A-801D-08D9FFA2746827622-023021518-lDPmqXPdj3j/FRGnEFCvXw==; buvid_fp_plain=undefined; header_theme_version=CLOSE; bp_video_offset_235693265=765160041876553700; DedeUserID=3493144259726260; DedeUserID__ckMd5=c6c4e098704df79c; CURRENT_QUALITY=120; home_feed_column=5; fingerprint=fcea116eb68fb1e1b7de3cdf436a86b4; PVID=1; bp_video_offset_3493144259726260=753287450881687600; buvid_fp=fcea116eb68fb1e1b7de3cdf436a86b4; b_lsid=9AAF8E7D_186F347EEB3; SESSDATA=214104d3,1694670823,e9fac*32; bili_jct=d2c3246d6115136ba6617d1597355664; sid=6rql2o0o; innersign=1"
    }

    response = requests.get(url, headers)
    # 判断请求结果
    if not response.status_code == 200:
        return False
    pattern = r'<script>window.__playinfo__=(.*?)</script>'
    script_list = re.findall(pattern, response.text, re.DOTALL)

    if not script_list:
        return False

    response_data = json.loads(script_list[0])
    # 作品信息
    info_pattern = r'<script>window.__INITIAL_STATE__=(.*?);\(function\(\)\{var s;'
    # 标题
    info_text = re.findall(info_pattern, response.text)[0]

    info_text = json.loads(info_text)
    title = info_text['videoData']["title"]
    # 作者
    author = info_text["upData"]["name"]
    author_id = info_text["upData"]["mid"]
    # 缩略图
    thumbnail = info_text["videoData"]['pic']
    # 视频
    video_list = response_data["data"]["dash"]["video"]
    videos = [item["baseUrl"] for item in video_list]
    # 音频
    audio_list = response_data["data"]["dash"]["audio"]
    audios = [item["baseUrl"] for item in audio_list]
    # 图集
    pics = []

    data = {
        "title": title,
        "audio": audios,
        "thumbnail": thumbnail,
        "pics": [],
        "videos": videos,
        "type": "video" if videos else ("images" if pics else ("audio" if audios else "")),
        "source": "bilibili",
        "author": author,
        "author_id": author_id
    }
    return data


async def kuaishou(url:str):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": ks_default
    }
    # 获取请求的真实链接：重定向后的链接,如果没有重定向，则可以直接访问
    request_url = requests.get(url=url, headers=headers)
    if not request_url.status_code == 200:
        return False
    url = request_url.url
    response = requests.get(url=url, headers=headers)
    if not response.status_code == 200:
        return False
    pattern = r'<script>window.__APOLLO_STATE__=(.*?)"clients":{}}'  # 匹配所有的 HTML 标签
    script_list = re.findall(pattern, response.text, re.DOTALL)
    if not script_list:
        return False
    script_list[0] = script_list[0] + '"clients":{}}'
    data = json.loads(parse.unquote(script_list[0]))
    # 获取视频ID
    request_url_path = urlparse(url).path
    substring = "/short-video/"
    video_id = request_url_path.split(substring, 1)[-1]

    # 获取视频数据的key
    video_obj_Key = 'VisionVideoDetailPhoto:' + video_id
    video_obj = data['defaultClient'][video_obj_Key]
    title = video_obj['caption']
    thumbnail = video_obj['coverUrl']
    videos = [video_obj['photoUrl']]
    audio = [video_obj['photoH265Url']]
    pics = []
    data = {
        "title": title,
        "audio": audio,
        "thumbnail": thumbnail,
        "pics": pics,
        "videos": videos,
        "type": "video" if videos else ("images" if pics else ("audio" if audio else "")),
        "source": "kuaishou",
    }

    return data


async def xhs(url:str):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": "xhsTrackerId=11d22b07-29a4-409c-a16b-c1ae80804a9e; xhsTrackerId.sig=jTITBQ2MZx8Y2W16OlOsJAvADOWnkc8DxJddwQQysUA; a1=1880994c95c2d929pmrrbucna8wlvdo8l3f3zzpml30000149141; webId=85a5b68fea11ae9453621ef38efa774d; gid=yYY8jj4SD81KyYY8jj4SjquU2SJfjJjU6FFDi617SI0YEqq81hflYu888y4jy4y8JS400fDi; gid.sign=jMjW4wsS0U65QqupInCGGvU4nAM=; smidV2=20230511182812b12e70f5b77815a098e7dc07049829370054efb1ec8649b40; xsecappid=xhs-pc-web; abRequestId=85a5b68fea11ae9453621ef38efa774d; web_session=0400697bd634e980161cccd0ec364b6c26a56a; webBuild=3.4.1; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=62f314a8-253e-4e75-9aca-cf371b9e17db"
    }
    # 获取请求的真实链接：重定向后的链接,如果没有重定向，则可以直接访问
    request_url = requests.get(url=url, headers=headers)
    if not request_url.status_code == 200:
        return False
    url = parse.unquote(request_url.url)
    response = requests.get(url=url, headers=headers)
    pattern = r'<script>window.__INITIAL_STATE__=(.*?)</script>'  # 匹配所有的 HTML 标签
    script_list = re.findall(pattern, response.text, re.DOTALL)
    if not script_list:
        return False
    # print(script_list[0].replace("undefined", 'null'))
    data = json.loads(script_list[0].replace("undefined", 'null'))
    note_id = data['note']['firstNoteId']
    # print(json.dumps(data['note']['noteDetailMap'][note_id]))
    title = data['note']['noteDetailMap'][note_id]['note']['title'] or data['note']['noteDetailMap'][note_id]['note'][
        'desc']
    author = data['note']['noteDetailMap'][note_id]['note']['user']['nickname']
    author_id = data['note']['noteDetailMap'][note_id]['note']['user']['userId']
    audio = []
    thumbnail = "https://ci.xiaohongshu.com/" + data['note']['noteDetailMap'][note_id]['note']['imageList'][0][
        'traceId'] + "?imageView2/2/w/0/format/jpg/v3"
    videos = ["https://sns-video-hw.xhscdn.com/" + data['note']['noteDetailMap'][note_id]['note']['video']['consumer'][
        'originVideoKey']] if data['note']['noteDetailMap'][note_id]['note']['type'] == 'video' else []
    pics = ["https://ci.xiaohongshu.com/" + item['traceId'] + "?imageView2/2/w/0/format/jpg/v3" for item in
            data['note']['noteDetailMap'][note_id]['note']['imageList']]
    data = {
        "title": title,
        "thumbnail": thumbnail,
        "pics": pics,
        "videos": videos,
        "type": "video" if videos else ("images" if pics else ("audio" if audio else "")),
        "source": "xhs",
        "author": author,
        "author_id": author_id
    }
    return data


async def xigua(url:str):
    headers = {
        "cookie": "ixigua-a-s=1; support_webp=true; support_avif=false; csrf_session_id=35f57a473d7cfda427632c9f991b2330; __ac_nonce=0647590ce00420738211; __ac_signature=_02B4Z6wo00f01m3mdpQAAIDAKvBIOIuNSx5txnIAAP8b5A3jWMl5oHIfG2wCdjWLqNDzdAZMt9M1ojOoUQJbDcfcsY61TZoxFkoavGAyvyA2Nyci4PKzqYCQ16KeLLh10dCmvixRN92dvsM908; msToken=mAZhyDyYFgAhdanzKg4mCvch09GAfXKmMZVm0PojP3yj-hUqVyJ2lU7RtrVufRrWRw-VJxhScy5QJksdbbuJC6LsTUzu-dpQr4x0AmsIiQt1RbARsUgy; tt_scid=saqMtnW2TjHR.RkiTpxuFpB0.KsoslnuVlWRn-rmSP5zAHx0OeZIGNa7NK07qyhdc994; ttwid=1|-nU0rlQ2BWtJaoTTvJLIs9HY4QovRM2x1evYZEj2hL8|1685427699|66ec5570ade07832cfab3be451cb2f07931f3654ec397fa3f90016da9e3cf6be",
        "Referer": "https://www.ixigua.com",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    }
    # 获取请求的真实链接：重定向后的链接,如果没有重定向，则可以直接访问
    request_url = requests.get(url=url)
    if not request_url.status_code == 200:
        return False
    response = requests.get(url=request_url.url, headers=headers)
    pattern = r'window._SSR_HYDRATED_DATA=(.*?)</script>'  # 匹配所有的 HTML 标签
    script_list = re.findall(pattern, response.text.encode('raw_unicode_escape').decode(), re.DOTALL)
    if not script_list:
        return False
    from urllib import parse
    data = script_list[0].replace("undefined", 'null')
    data = json.loads(data)
    try:
        title = data['anyVideo']['gidInformation']['packerData']['video']['title']
    except:
        return False
    author = data['anyVideo']['gidInformation']['packerData']['video']['user_info']['name']
    author_id = data['anyVideo']['gidInformation']['packerData']['video']['user_info']['user_id']
    try:
        thumbnail = data['anyVideo']['gidInformation']['packerData']['video']['poster_url']
    except:
        thumbnail = ""
    try:
        videos = [base64.b64decode(item["main_url"]).decode() for item in
                  data['anyVideo']['gidInformation']['packerData']['video']['videoResource']['normal']['video_list']]
    except:
        # 获取第一个键值对
        data_dict = data['anyVideo']['gidInformation']['packerData']['video']['videoResource']['normal']['video_list']
        video_values = list(data_dict.values())
        videos = [base64.b64decode(video_values[-1]["main_url"]).decode()]
    pics = []
    try:
        audio = [base64.b64decode(item["main_url"]).decode() for item in
                 data['anyVideo']['gidInformation']['packerData']['video']['videoResource']['dash']['dynamic_video'][
                     'dynamic_audio_list']]
    except:
        audio = []
    data = {
        "title": title,
        "audio": audio,
        "thumbnail": thumbnail,
        "pics": pics,
        "videos": videos,
        "type": "video" if videos else ("images" if pics else ("audio" if audio else "")),
        "source": "xigua",
        "author": author,
        "author_id": author_id
    }
    return data


async def toutiao(url:str):
    headers = {
        "cookie": 'ttcid=07170d3840d94f48bc444ea28edb78aa28; _ga=GA1.1.1593405489.1677485323; csrftoken=6335cc8a6291f226a1c3ea8464f94ef1; _tea_utm_cache_24={"utm_source":"copy_link","utm_medium":"toutiao_android","utm_campaign":"client_share"}; tt_webid=7200966524499314237; s_v_web_id=verify_li5qsk57_m9l4NLJV_wQEK_49h6_925i_GXkIPtlRMBTh; local_city_cache=合肥; msToken=6dj4lwFXadDUHYGXM0lf-HSidEmJ4dcsffGNY--1K9GXe6uiwfQ8O6FUAMbFIhp_5vrz3BvHBPenvkNAIfzdFip-fuv5xEdSM2acUT7-CPY=; ariaDefaultTheme=undefined; _ga_QEHZPBE5HH=GS1.1.1685432683.4.1.1685432817.0.0.0; ttwid=1|-nU0rlQ2BWtJaoTTvJLIs9HY4QovRM2x1evYZEj2hL8|1685432817|03ee35f249e2f15df5348963cd40b8d0635b6690ee21e48d00c42a1e119d05c4; tt_scid=LzGRxZohDBn2CBEE4N.RRB.kAYqc8S0cfiFpInGKxhT1eXKNDYC27cbEb03oIaHM00bb'.encode(
            "utf-8").decode('latin-1'),
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    }
    # 获取请求的真实链接：重定向后的链接,如果没有重定向，则可以直接访问
    request_url = requests.get(url=url)

    if not request_url.status_code == 200:
        return False
    response = requests.get(url=request_url.url, headers=headers)
    # print(response.text)
    pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'  # 匹配所有的 HTML 标签
    script_list = re.findall(pattern, response.text, re.DOTALL)
    if not script_list:
        return False
    from urllib.parse import unquote
    data = json.loads(unquote(script_list[0]))

    try:
        title = data['data']['initialVideo']['title']
    except:
        title = ''

    author = data['data']['initialVideo']['userInfo']['name']
    author_id = data['data']['initialVideo']['userInfo']['userId']
    try:
        thumbnail = "http" + data['data']['initialVideo']['coverUrl']
    except:
        thumbnail = ""
    try:
        videos = [item["main_url"] for item in
                  data['data']['initialVideo']['videoPlayInfo']['video_list']]
    except:
        videos = []

    try:
        audio = [item["main_url"] for item in
                 data['data']['initialVideo']['videoPlayInfo']['dynamic_video']['dynamic_audio_list']]
    except:
        audio = []
    pics = []
    data = {
        "title": title,
        "audio": audio,
        "thumbnail": thumbnail,
        "videos": videos,
        "pics": [],
        "type": "video" if videos else ("images" if pics else ("audio" if audio else "")),
        "source": "toutiao",
        "author": author,
        "author_id": author_id
    }

    return data