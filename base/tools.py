import base64
import json
import requests
import subprocess

def get(url, proxy_port=None):
    session = requests.session()
    if proxy_port is not None:
        session.proxies = {'http': 'socks5://127.0.0.1:{}'.format(proxy_port),
                           'https': 'socks5://127.0.0.1:{}'.format(proxy_port)}
    return session.get(url).text


def run_cmd(cmd):
    result_str = ''
    process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_f = process.stdout
    error_f = process.stderr
    errors = error_f.read()
    if errors: pass
    result_str = result_f.read().strip()
    if result_f:
        result_f.close()
    if error_f:
        error_f.close()
    return result_str




class FileIo():
    @staticmethod
    def readjson(path):
        """
        读取json文件
        """
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def savejson(path, obj):
        """
        保存obj到json文件
        """
        with open(path, "w+", encoding='utf-8') as f:
            return json.dump(obj, f, indent=2, ensure_ascii=False)


class Encoding():
    @staticmethod
    def b64decode(s, encoding='utf-8'):
        """
        base64解码
        """
        if len(s) % 4 != 0:
            s += '=' * (len(s) % 4)
        temp = base64.urlsafe_b64decode(s.encode('utf-8'))
        return temp.decode(encoding)

    @staticmethod
    def b64encode_with_eq(s, encoding='utf-8'):
        """
        带等号base64编码
        """
        temp = base64.urlsafe_b64encode(s.encode('utf-8'))
        return temp.decode(encoding)

    @staticmethod
    def b64encode(s):
        """
        去等号base64编码
        """
        return Encoding.b64encode_with_eq(s).rstrip('=')


class Dealdata():
    @staticmethod
    def is_int(s):
        """
        是否为整数
        """
        try:
            int(s)
            return True
        except ValueError:
            pass
        return False

    @staticmethod
    def praseindex(key):
        """
        类似切片，返回索引列表，如：
        praseindex('1-2,7-8,9') --> [1,2,7,8,9]
        """
        key = key.strip(',')
        if key.find(',') >= 0:
            r = []
            for x in key.split(','):
                try:
                    for i in Dealdata.praseindex(x):
                        r.append(i)
                except TypeError as e:
                    return None
            return sorted(set(r))
        elif key.find('-') >= 0:
            l = key.split('-')
            if len(l) == 2 and Dealdata.is_int(l[0]) and Dealdata.is_int(l[1]):
                a, b = int(l[0]), int(l[1])
                if a > b:
                    a, b = b, a
                return [i for i in range(a, b + 1)]
        elif Dealdata.is_int(key):
            return int(key),

    @staticmethod
    def cut_data(l, key='all'):
        """
        拆分数据
        """

        if key == 'all':
            return l, []
        indexs = Dealdata.praseindex(key)
        if indexs is None:
            return [], l
        select_data = []
        not_select_data = []
        for i in range(len(l)):
            if i in indexs:
                select_data.append(l[i])
            else:
                not_select_data.append(l[i])
        return select_data, not_select_data
