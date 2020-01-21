import json
from base.tools import Encoding
from base.tools import get


def subtext2vmesslinks(sub_text):
    """解析订阅数据得到vmess链接，并去除没有vmess://开头的数据
    :param sub_text: 订阅文本
    :return: vmess链接列表
    """
    vmesslinks = Encoding.b64decode(sub_text).strip('\n').split('\n')
    return [x for x in vmesslinks if x[:8] == 'vmess://']


def vmesslinks2subtext(vmesslinks):
    """通过vmess链接列表生成订阅数据
    :param vmesslinks: vmess链接列表
    :return: 订阅数据
    """
    return Encoding.b64encode('\n'.join([x.strip('=') for x in vmesslinks]))


def vmesslinks2vemssobjs(vmesslinks):
    """解析vmess链接列表，并将json文本转化成字典对象
    :param vmesslinks: vmess链接列表
    :return: vmess字典对象
    """
    return [json.loads(Encoding.b64decode(x[8:])) for x in vmesslinks]


def sublink2vmessobjs(sublink):
    """
    sublink --> subtext --> vmesslinks --> vmessobjs
    """
    subtext = get(sublink)
    if subtext == None:
        return None
    vmesslinks = subtext2vmesslinks(subtext)
    return vmesslinks2vemssobjs(vmesslinks)


def vemssobj2node(vmessobj, subid=''):
    return {
        "configVersion": vmessobj['v'],
        "address": vmessobj['add'],
        "port": vmessobj['port'],
        "id": vmessobj['id'],
        "alterId": vmessobj['aid'],
        "security": "auto",
        "network": vmessobj['net'],
        "remarks": vmessobj['ps'],
        "headerType": vmessobj['type'],
        "requestHost": vmessobj['host'],
        "path": vmessobj['path'],
        "streamSecurity": vmessobj['tls'],
        "allowInsecure": "",
        "configType": 1,
        "testResult": "",
        "subid": subid
    }


def node2vmesslink(node):
    obj = {
        'add': node['address'],
        'aid': node['alterId'],
        'host': node['requestHost'],
        'id': node['id'],
        'net': node['network'],
        'path': node['path'],
        'port': node['port'],
        'ps': node['remarks'],
        'tls': node['streamSecurity'],
        'type': node['headerType'],
        'v': node['configVersion']
    }
    objstr = json.dumps(obj)
    return 'vmess://' + Encoding.b64encode_with_eq(objstr)
