import os
import uuid

from base import vmess
from base.tools import Dealdata


class Inbound():
    def __init__(self,
                 port=1080,
                 protocol='socks',
                 udp=True,
                 sniffing=True,
                 allowLANConn=False,
                 data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {
                "port": port,
                "protocol": protocol,
                "udp": udp,
                "sniffing": sniffing,
                "allowLANConn": allowLANConn
            }

    def set_port(self, port):
        self.data['port'] = port

    def open_udp(self):
        self.data['udp'] = True

    def close_udp(self):
        self.data['udp'] = False

    def open_sniffing(self):
        self.data['sniffing'] = True

    def close_sniffing(self):
        self.data['sniffing'] = False

    def open_LANConn(self):
        self.data['allowLANConn'] = True

    def close_LANConn(self):
        self.data['allowLANConn'] = False

    def get_data(self):
        return self.data

    def gen_config_obj(self):
        configObj = [{
            "tag": "proxy",
            "port": self.data['port'],
            "listen": "0.0.0.0" if self.data['allowLANConn'] else "127.0.0.1",
            "protocol": self.data['protocol'],
            "sniffing": {
                "enabled": self.data['sniffing'],
                "destOverride": ["http", "tls"]
            },
            "settings": {
                "auth": "noauth",
                "udp": self.data['udp'],
                "ip": None,
                "address": None,
                "clients": None
            },
            "streamSettings": None
        }]
        return configObj


class Loglevel:
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    NONE = 'none'


class Log():
    def __init__(self, logPath='', loglevel=Loglevel.WARNING, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {"logPath": logPath, "loglevel": loglevel}

    def set_logPath(self, logPath):
        self.data['logPath'] = logPath

    def set_loglevel(self, loglevel=Loglevel.WARNING):
        if loglevel != None:
            self.data['loglevel'] = loglevel

    def get_set(self):
        return self.data['logPath'],self.data['loglevel']

    def gen_config_obj(self):
        if self.data['logPath'] == '':
            configObj = {
                "access": '',
                "error": '',
                "loglevel": self.data['loglevel']
            }
        else:
            configObj = {
                "access": self.data['logPath'] + os.sep + 'access.log',
                "error": self.data['logPath'] + os.sep + 'error.log',
                "loglevel": self.data['loglevel']
            }
        return configObj


class Outbound():
    def __init__(self, index=0, vmess=[], mux=True, sub=[], kcp=None, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {
                "mux": mux,
                "index": index,
                "vmess": vmess,
                "sub": sub,
                "kcp": kcp if kcp is not None else {
                    "mtu": 1350,
                    "tti": 50,
                    "uplinkCapacity": 12,
                    "downlinkCapacity": 100,
                    "congestion": False,
                    "readBufferSize": 2,
                    "writeBufferSize": 2
                }
            }
    def select_index(self, i):
        if not Dealdata.is_int(i) or int(i) < 0:
            return
        if int(i) < len(self.data['vmess']):
            self.data['index'] = int(i)

    def open_mux(self):
        self.data['mux'] = True

    def close_mux(self):
        self.data['mux'] = False

    def add_node_by_vmesslinks(self, vmesslinks):
        objs = vmess.vmesslinks2vemssobjs(vmesslinks)
        for obj in objs:
            node = vmess.vemssobj2node(obj)
            self.data['vmess'].append(node)

    def add_node(self, addr, port, id, aid, net, remarks='', security='auto', type='none', host='', path='', tls=''):
        node = {
            "configVersion": 2,
            "address": addr,
            "port": port,
            "id": id,
            "alterId": aid,
            "security": security,
            "network": net,
            "remarks": remarks,
            "headerType": type,
            "requestHost": host,
            "path": path,
            "streamSecurity": tls,
            "allowInsecure": "",
            "configType": 1,
            "testResult": "",
            "subid": ""
        }
        self.data['vmess'].append(node)
        return node

    def add_sub(self, url, remarks="remarks"):
        sublist = self.data['sub']
        sublist.append({
            "id": str(uuid.uuid1()),
            "remarks": remarks,
            "url": url
        })

    def update_node_by_sub(self, subkey='all'):
        sublist = self.data['sub']
        selectdata, _ = Dealdata.cut_data(sublist, subkey)
        subids = []
        newnodes = []
        for sub in selectdata:
            vmessobjs = vmess.sublink2vmessobjs(sub['url'])
            if vmessobjs != None:
                subids.append(sub['id'])
                for obj in vmessobjs:
                    newnodes.append(vmess.vemssobj2node(obj, sub['id']))
        for node in self.data['vmess']:
            if node['subid'] not in subids:
                newnodes.append(node)
        self.data['vmess'] = newnodes

    def del_node(self, key):
        olddata = self.data['vmess']
        _, newdata = Dealdata.cut_data(olddata, key)
        self.data['vmess'] = newdata
        return len(olddata) - len(newdata)

    def del_sub(self, key):
        olddata = self.data['sub']
        _, newdata = Dealdata.cut_data(olddata, key)
        self.data['sub'] = newdata
        return len(olddata) - len(newdata)

    def set_tls(self, node):
        if node['streamSecurity'] != 'tls':
            return None
        return {"allowInsecure": True, "serverName": node['requestHost']}

    def set_tcp(self, node):
        if node['network'] != 'tcp':
            return None
        return None

    def set_kcp(self, node):
        if node['network'] != 'kcp':
            return None
        kcpset = self.data['kcp']
        return {
            "mtu": kcpset['mtu'],
            "tti": kcpset['tti'],
            "uplinkCapacity": kcpset['uplinkCapacity'],
            "downlinkCapacity": kcpset['downlinkCapacity'],
            "congestion": kcpset['congestion'],
            "readBufferSize": kcpset['readBufferSize'],
            "writeBufferSize": kcpset['writeBufferSize'],
            "header": {
                "type": "none"
            }
        }

    def set_ws(self, node):
        if node['network'] != 'ws':
            return None
        return {
            "connectionReuse": True,
            "path": node['path'],
            "headers": {
                "Host": node['requestHost']
            }
        }

    def set_http(self, node):
        if node['network'] != 'h2':
            return None
        return {"path": node['path'], "host": [node['requestHost']]}

    def set_quic(self, node):
        """
        暂不支持quic
        """
        if node['network'] != 'quic':
            return None
        return None

    def gen_config_obj(self):
        nodes = self.data['vmess']
        if len(nodes) == 0:
            return [{
            "tag": "direct",
            "protocol": "freedom",
            "settings": {
                "vnext": None,
                "servers": None,
                "response": None
            },
            "streamSettings": None,
            "mux": None
        }, {
            "tag": "block",
            "protocol": "blackhole",
            "settings": {
                "vnext": None,
                "servers": None,
                "response": {
                    "type": "http"
                }
            },
            "streamSettings": None,
            "mux": None
        }]
        node = nodes[self.data['index']]
        configObj = [{
            "tag": "proxy",
            "protocol": "vmess",
            "settings": {
                "vnext": [{
                    "address":
                        node['address'],
                    "port":
                        int(node['port']),
                    "users": [{
                        "id": node['id'],
                        "alterId": int(node['alterId']),
                        "email": "t@t.tt",
                        "security": node['security']
                    }]
                }],
                "servers":
                    None,
                "response":
                    None
            },
            "streamSettings": {
                "network": node['network'],
                "security": node['streamSecurity'],
                "tlsSettings": self.set_tls(node),
                "tcpSettings": self.set_tcp(node),
                "kcpSettings": self.set_kcp(node),
                "wsSettings": self.set_ws(node),
                "httpSettings": self.set_http(node),
                "quicSettings": self.set_quic(node)
            },
            "mux": {
                "enabled": self.data['mux']
            }
        }, {
            "tag": "direct",
            "protocol": "freedom",
            "settings": {
                "vnext": None,
                "servers": None,
                "response": None
            },
            "streamSettings": None,
            "mux": None
        }, {
            "tag": "block",
            "protocol": "blackhole",
            "settings": {
                "vnext": None,
                "servers": None,
                "response": {
                    "type": "http"
                }
            },
            "streamSettings": None,
            "mux": None
        }]
        return configObj


class DNS():
    def __init__(self, data=[]):
        self.data = data

    def add_DNS(self, dns):
        self.data.append(dns)

    def del_DNS(self, key):
        _, newdata = Dealdata.cut_data(self.data, key)
        l = len(self.data) - len(newdata)
        self.data = newdata
        return l

    def gen_config_obj(self):
        configObj = {
            "servers": self.data
        }
        return configObj


class Router():
    def __init__(self, domainStrategy='IPIfNonMatch', local=False, proxy={'domain': [], 'ip': []},
                 direct={'domain': [], 'ip': []},
                 block={'domain': [], 'ip': []}, data=None):
        if data is None:
            self.data = {
                "domainStrategy": domainStrategy,
                "local": local,
                "proxy": proxy,
                "direct": direct,
                "block": block
            }
        else:
            self.data = data

    def set_domainStrategy_AsIs(self):
        self.data['domainStrategy'] = 'AsIs'

    def set_domainStrategy_IPIfNonMatch(self):
        self.data['domainStrategy'] = 'IPIfNonMatch'

    def set_domainStrategy_IPOnDemand(self):
        self.data['domainStrategy'] = 'IPOnDemand'

    def open_local(self):
        self.data['local'] = True

    def close_local(self):
        self.data['local'] = False

    def add_proxy_domain(self, domain):
        r = self.data['proxy']['domain']
        r.append(domain)

    def add_proxy_ip(self, ip):
        r = self.data['proxy']['ip']
        r.append(ip)

    def add_direct_domain(self, domain):
        r = self.data['direct']['domain']
        r.append(domain)

    def add_direct_ip(self, ip):
        r = self.data['direct']['ip']
        r.append(ip)

    def add_block_domain(self, domain):
        r = self.data['block']['domain']
        r.append(domain)

    def add_block_ip(self, ip):
        r = self.data['block']['ip']
        r.append(ip)

    def del_proxy_domain(self, key):
        r = self.data['proxy']['domain']
        _, new_data = Dealdata.cut_data(r, key)
        self.data['proxy']['domain'] = new_data
        return new_data, len(r) - len(new_data)

    def del_proxy_ip(self, key):
        r = self.data['proxy']['ip']
        _, new_data = Dealdata.cut_data(r, key)
        self.data['proxy']['ip'] = new_data
        return len(r) - len(new_data)

    def del_direct_domain(self, key):
        r = self.data['direct']['domain']
        _, new_data = Dealdata.cut_data(r, key)
        self.data['direct']['domain'] = new_data
        return len(r) - len(new_data)

    def del_direct_ip(self, key):
        r = self.data['direct']['ip']
        _, new_data = Dealdata.cut_data(r, key)
        self.data['direct']['indexs'] = new_data
        return len(r) - len(new_data)

    def del_block_domain(self, key):
        r = self.data['block']['domain']
        _, new_data = Dealdata.cut_data(r, key)
        self.data['block']['domain'] = new_data
        return len(r) - len(new_data)

    def del_block_ip(self, key):
        r = self.data['block']['ip']
        _, new_data = Dealdata.cut_data(r, key)
        self.data['block']['ip'] = new_data
        return len(r) - len(new_data)

    def gen_config_obj(self):
        configObj = {
            "domainStrategy": self.data['domainStrategy'],
            "rules": []
        }

        if len(self.data['proxy']['domain']) > 0:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "proxy",
                "ip": None,
                "domain": self.data['proxy']['domain']
            })
        if len(self.data['proxy']['ip']) > 0:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "proxy",
                "ip": self.data['proxy']['ip'],
                "domain": None
            })
        if len(self.data['direct']['ip']) > 0:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "direct",
                "ip": self.data['direct']['ip'],
                "domain": None
            })

        if len(self.data['direct']['domain']) > 0:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "direct",
                "ip": None,
                "domain": self.data['direct']['domain']
            })

        if len(self.data['block']['ip']) > 0:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "block",
                "ip": self.data['block']['ip'],
                "domain": None
            })

        if len(self.data['block']['domain']) > 0:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "block",
                "ip": None,
                "domain": self.data['block']['domain']
            })


        if self.data['local']:
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "direct",
                "ip": [
                    "geoip:private"
                ],
                "domain": None
            })
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "direct",
                "ip": [
                    "geoip:cn"
                ],
                "domain": None
            })
            configObj['rules'].append({
                "type": "field",
                "port": None,
                "inboundTag": None,
                "outboundTag": "direct",
                "ip": None,
                "domain": [
                    "geosite:cn"
                ]
            })
        return configObj
