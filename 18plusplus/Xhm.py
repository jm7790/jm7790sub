# -*- coding: utf-8 -*-
# by @嗷呜
# Modified to fix MIME type error
import json
import sys
from base64 import b64decode, b64encode
from urllib.parse import urlparse

import requests
from pyquery import PyQuery as pq
from requests import Session
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        try:self.proxies = json.loads(extend)
        except:self.proxies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'dnt': '1',
            'sec-ch-ua-mobile': '?0',
            'origin': '',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=1, i',
        }
        self.host = self.gethost()
        self.session = Session()
        self.headers.update({'origin': self.host,'referer': f'{self.host}/'})
        self.session.proxies.update(self.proxies)
        self.session.headers.update(self.headers)
        pass

    def getName(self):
        return "Xhamster"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "4K": "/4k",
            "国产": "two_click_/categories/chinese",
            "最新": "/newest",
            "最佳": "/best",
            "频道": "/channels",
            "类别": "/categories",
            "明星": "/pornstars"
        }
        classes = []
        filters = {}
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
            if k != '4K': filters[cateManual[k]] = [{'key': 'type', 'name': '类型', 'value': [{'n': '4K', 'v': '/4k'}]}]
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        data = self.getpq()
        return {'list': self.getlist(data(".thumb-list--sidebar .thumb-list__item"))}

    def categoryContent(self, tid, pg, filter, extend):
        vdata = []
        result = {}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        if tid in ['/4k', '/newest', '/best'] or 'two_click_' in tid:
            if 'two_click_' in tid: tid = tid.split('click_')[-1]
            data = self.getpq(f'{tid}{extend.get("type", "")}/{pg}')
            vdata = self.getlist(data(".thumb-list--sidebar .thumb-list__item"))
        elif tid == '/channels':
            data = self.getpq(f'{tid}/{pg}')
            jsdata = self.getjsdata(data)
            if jsdata and 'channels' in jsdata:
                for i in jsdata['channels']:
                    vdata.append({
                        'vod_id': f"two_click_" + i.get('channelURL'),
                        'vod_name': i.get('channelName'),
                        'vod_pic': self.proxy(i.get('siteLogoURL')),
                        'vod_year': f'videos:{i.get("videoCount")}',
                        'vod_tag': 'folder',
                        'vod_remarks': f'subscribers:{i["subscriptionModel"].get("subscribers")}',
                        'style': {'ratio': 1.33, 'type': 'rect'}
                    })
        elif tid == '/categories':
            result['pagecount'] = pg
            data = self.getpq(tid)
            self.cdata = self.getjsdata(data)
            if self.cdata and 'layoutPage' in self.cdata:
                for i in self.cdata['layoutPage']['store']['popular']['assignable']:
                    vdata.append({
                        'vod_id': "one_click_" + i.get('id'),
                        'vod_name': i.get('name'),
                        'vod_pic': '',
                        'vod_tag': 'folder',
                        'style': {'ratio': 1.33, 'type': 'rect'}
                    })
        elif tid == '/pornstars':
            data = self.getpq(f'{tid}/{pg}')
            pdata = self.getjsdata(data)
            if pdata and 'pagesPornstarsComponent' in pdata:
                for i in pdata['pagesPornstarsComponent']['pornstarListProps']['pornstars']:
                    vdata.append({
                        'vod_id': f"two_click_" + i.get('pageURL'),
                        'vod_name': i.get('name'),
                        'vod_pic': self.proxy(i.get('imageThumbUrl')),
                        'vod_remarks': i.get('translatedCountryName'),
                        'vod_tag': 'folder',
                        'style': {'ratio': 1.33, 'type': 'rect'}
                    })
        elif 'one_click' in tid:
            result['pagecount'] = pg
            tid = tid.split('click_')[-1]
            if hasattr(self, 'cdata') and self.cdata:
                for i in self.cdata['layoutPage']['store']['popular']['assignable']:
                    if i.get('id') == tid:
                        for j in i['items']:
                            vdata.append({
                                'vod_id': f"two_click_" + j.get('url'),
                                'vod_name': j.get('name'),
                                'vod_pic': self.proxy(j.get('thumb')),
                                'vod_tag': 'folder',
                                'style': {'ratio': 1.33, 'type': 'rect'}
                            })
        result['list'] = vdata
        return result

    def detailContent(self, ids):
        data = self.getpq(ids[0])
        djs = self.getjsdata(data)
        vn = data('meta[property="og:title"]').attr('content')
        dtext = data('#video-tags-list-container')
        href = dtext('a').attr('href')
        title = dtext('span[class*="body-bold-"]').eq(0).text()
        pdtitle = ''
        if href:
            pdtitle = '[a=cr:' + json.dumps({'id': 'two_click_' + href, 'name': title}) + '/]' + title + '[/a]'
        vod = {
            'vod_name': vn,
            'vod_director': pdtitle,
            'vod_remarks': data('.rb-new__info').text(),
            'vod_play_from': 'Xhamster',
            'vod_play_url': ''
        }
        try:
            plist = []
            if djs and 'xplayerSettings' in djs:
                d = djs['xplayerSettings']['sources']
                f = d.get('standard')

                def custom_sort_key(url):
                    quality = url.split('$')[0]
                    number = ''.join(filter(str.isdigit, quality))
                    number = int(number) if number else 0
                    return -number, quality

                if f:
                    for key, value in f.items():
                        if isinstance(value, list):
                            for info in value:
                                id = self.e64(f'{0}@@@@{info.get("url") or info.get("fallback")}')
                                plist.append(f"{info.get('label') or info.get('quality')}${id}")
                plist.sort(key=custom_sort_key)
                if d.get('hls'):
                    for format_type, info in d['hls'].items():
                        if url := info.get('url'):
                            encoded = self.e64(f'{0}@@@@{url}')
                            plist.append(f"{format_type}${encoded}")
            else:
                # 尝试备用方式解析（简单的正则或页面结构，如果JS数据提取失败）
                # 这里保持原逻辑，如果提取失败则报错
                pass

        except Exception as e:
            plist = [f"{vn}${self.e64(f'{1}@@@@{ids[0]}')}"]
            print(f"获取视频信息失败: {str(e)}")
        
        if not plist: # 兜底逻辑
             plist = [f"{vn}${self.e64(f'{1}@@@@{ids[0]}')}"]

        vod['vod_play_url'] = '#'.join(plist)
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        data = self.getpq(f'/search/{key}?page={pg}')
        return {'list': self.getlist(data(".thumb-list--sidebar .thumb-list__item")), 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        ids = self.d64(id).split('@@@@')
        if '.m3u8' in ids[1]: ids[1] = self.proxy(ids[1], 'm3u8')
        return {'parse': int(ids[0]), 'url': ids[1], 'header': self.headers}

    def localProxy(self, param):
        url = self.d64(param['url'])
        if param.get('type') == 'm3u8':
            return self.m3Proxy(url)
        else:
            return self.tsProxy(url)

    def gethost(self):
        try:
            response = requests.get('https://xhamster.com',proxies=self.proxies,headers=self.headers,allow_redirects=False)
            if 'Location' in response.headers:
                return response.headers['Location']
            return "https://xhamster.com"
        except Exception as e:
            print(f"获取主页失败: {str(e)}")
            return "https://zn.xhamster.com"

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def getlist(self, data):
        vlist = []
        for i in data.items():
            vlist.append({
                'vod_id': i('.role-pop').attr('href'),
                'vod_name': i('.video-thumb-info a').text(),
                'vod_pic': self.proxy(i('.role-pop img').attr('src')),
                'vod_year': i('.video-thumb-info .video-thumb-views').text().split(' ')[0],
                'vod_remarks': i('.role-pop div[data-role="video-duration"]').text(),
                'style': {'ratio': 1.33, 'type': 'rect'}
            })
        return vlist

    def getpq(self, path=''):
        h = '' if path.startswith('http') else self.host
        try:
            response = self.session.get(f'{h}{path}').text
            return pq(response)
        except Exception as e:
            print(f"{str(e)}")
            return pq("")

    def getjsdata(self, data):
        try:
            vhtml = data("script[id='initials-script']").text()
            if not vhtml:
                return {}
            jst = json.loads(vhtml.split('initials=')[-1][:-1])
            return jst
        except:
            return {}

    def m3Proxy(self, url):
        # 修正：将 application/vnd.apple.mpegur 改为 application/vnd.apple.mpegurl
        try:
            ydata = requests.get(url, headers=self.headers, proxies=self.proxies, allow_redirects=False)
            data = ydata.content.decode('utf-8')
            if ydata.headers.get('Location'):
                url = ydata.headers['Location']
                data = requests.get(url, headers=self.headers, proxies=self.proxies).content.decode('utf-8')
            lines = data.strip().split('\n')
            last_r = url[:url.rfind('/')]
            parsed_url = urlparse(url)
            durl = parsed_url.scheme + "://" + parsed_url.netloc
            for index, string in enumerate(lines):
                if '#EXT' not in string and string.strip():
                    if 'http' not in string:
                        domain = last_r if string.count('/') < 2 else durl
                        string = domain + ('' if string.startswith('/') else '/') + string
                    
                    ext = string.split('.')[-1].split('?')[0]
                    if len(ext) > 4 or '/' in ext: 
                         ext = 'ts'
                    lines[index] = self.proxy(string, ext)
            data = '\n'.join(lines)
            return [200, "application/vnd.apple.mpegurl", data]
        except Exception as e:
             print(f"m3Proxy Error: {e}")
             return [500, "text/plain", str(e)]

    def tsProxy(self, url):
        try:
            data = requests.get(url, headers=self.headers, proxies=self.proxies, stream=True)
            # 增加默认 Content-Type，防止服务器不返回导致播放失败
            ct = data.headers.get('Content-Type', 'video/mp2t')
            return [200, ct, data.content]
        except Exception as e:
            return [500, "text/plain", str(e)]

    def proxy(self, data, type='img'):
        if data and len(self.proxies):return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        else:return data