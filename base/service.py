import os
from base.config import Inbound, Log, Outbound, DNS, Router
from base.tools import Dealdata, FileIo,run_cmd
from base.vmess import node2vmesslink


class Service():

    def __init__(self, root_path):
        self.p = None
        self.root_path = root_path
        path = self.root_path + os.sep + "v2rayT.json"
        if os.path.isfile(path):
            obj = FileIo.readjson(path)
            self.inbound = Inbound(data=obj['inbound'])
            self.log = Log(data=obj['log'])
            self.outbound = Outbound(data=obj['outbound'])
            self.dns = DNS(data=obj['dns'])
            self.router = Router(data=obj['router'])
        else:
            self.inbound = Inbound()
            self.log = Log()
            self.outbound = Outbound()
            self.dns = DNS(['8.8.8.8', '114.114.114.114', 'localhost'])
            self.router = Router()
            self.save()

    def get_baseset(self):
        inbound = data(self.inbound)
        outnund = data(self.outbound)
        router = data(self.router)
        return {
            'port': inbound['port'],
            'protocol': inbound['protocol'],
            'udp': inbound['udp'],
            'sniffing': inbound['sniffing'],
            'allowLANConn': inbound['allowLANConn'],
            'local': router['local'],
            'domainStrategy': router['domainStrategy'],
            'mux': outnund['mux']
        }

    def get_logset(self):
        return self.log.get_logset()

    def get_selected_node_index(self):
        return self.outbound.get_index()

    def tcping_node(self, key='all', count=3):
        d, index = self.get_node(key)
        for i in range(len(d)):
            node = d[i]
            address = node['address']
            port = node['port']
            result = run_cmd('tcping {} -c {} -p {}'.format(address, count, port)).decode()
            if result.find('average = ') > 0:
                result = result[result.find('average = ')+10:]
            node['testResult'] = result
            yield d[:i], index[:i]


    def get_node(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.outbound)['vmess'], key)
        return d, Dealdata.praseindex(key)

    def get_vmesslinks(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.outbound)['vmess'], key)
        vmesslinks = [{'remarks': x['remarks'], 'link': node2vmesslink(x)} for x in d]
        return vmesslinks, Dealdata.praseindex(key)

    def get_sub(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.outbound)['sub'], key)
        return d, Dealdata.praseindex(key)

    def get_dns(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.dns), key)
        return d, Dealdata.praseindex(key)

    def get_router_proxy_domain(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.router)['proxy']['domain'], key)
        return d, Dealdata.praseindex(key)

    def get_router_proxy_ip(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.router)['proxy']['ip'], key)
        return d, Dealdata.praseindex(key)

    def get_router_direct_domain(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.router)['direct']['domain'], key)
        return d, Dealdata.praseindex(key)

    def get_router_direct_ip(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.router)['direct']['ip'], key)
        return d, Dealdata.praseindex(key)

    def get_router_block_domain(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.router)['block']['domain'], key)
        return d, Dealdata.praseindex(key)

    def get_router_block_ip(self, key='all'):
        d, _ = Dealdata.cut_data(data(self.router)['block']['ip'], key)
        return d, Dealdata.praseindex(key)[:len(d)]

    def set_local_port(self, port):
        if Dealdata.is_int(port):
            self.inbound.set_port(int(port))
            self.save()

    def set_node_index(self, index):
        if self.outbound.alter_index(index):
            self.save()

    def set_udp(self, bool=True):
        if bool:
            self.inbound.open_udp()
            self.save()
        else:
            self.inbound.close_udp()
            self.save()

    def set_sniffing(self, bool=True):
        if bool:
            self.inbound.open_sniffing()
            self.save()
        else:
            self.inbound.close_sniffing()
            self.save()

    def set_LANConn(self, bool=True):
        if bool:
            self.inbound.open_LANConn()
            self.save()
        else:
            self.inbound.close_LANConn()
            self.save()

    def set_round_local(self, bool=True):
        if bool:
            self.router.open_local()
            self.save()
        else:
            self.router.close_local()
            self.save()

    def set_mux(self, bool=True):
        if bool:
            self.outbound.open_mux()
            self.save()
        else:
            self.outbound.close_mux()
            self.save()

    def set_domainStrategy(self, mode=2):
        if mode == 1:
            self.router.set_domainStrategy_AsIs()
        elif mode == 2:
            self.router.set_domainStrategy_IPIfNonMatch()
        elif mode == 3:
            self.router.set_domainStrategy_IPOnDemand()
        else:
            return
        self.save()

    def set_logPath(self, logPath=''):
        self.log.set_logPath(logPath)
        self.save()

    def set_loglevel(self, loglevel):
        self.log.set_loglevel(loglevel)
        self.save()

    def add_sub(self, url, remarks='remarks'):
        """
        添加订阅
        """
        self.outbound.add_sub(url, remarks)
        self.save()

    def add_dns(self, dns):
        """
        添加dns
        """
        self.dns.add_DNS(dns)
        self.save()

    def add_node(self, addr, port, id, aid, net, remarks='', security='auto', type='none', host='', path='', tls=''):
        """
        添加节点
        """
        node = self.outbound.add_node(addr, int(port), id, aid, net, remarks, security, type, host, path, tls)
        self.save()
        return node

    def add_node_by_vmesslinks(self, vmesslinks):
        """
        解析vmess添加节点
        """
        vmesslinks = [x.strip('\n') for x in vmesslinks if x[:8] == 'vmess://']
        self.outbound.add_node_by_vmesslinks(vmesslinks)
        self.save()
        return vmesslinks

    def add_node_by_vmesslinks_file(self, filename):
        """
        解析vmess文件添加节点
        """
        path = self.root_path + os.sep + filename
        with open(path, 'r') as f:
            vmesslinks = f.readlines()
        vmesslinks = [x.strip('\n') for x in vmesslinks if x[:8] == 'vmess://']
        self.outbound.add_node_by_vmesslinks(vmesslinks)
        self.save()
        return vmesslinks

    def update_node_by_sub(self, key='all', proxy_port=None):
        """
        更新订阅
        """
        self.outbound.update_node_by_sub(key, proxy_port)
        self.save()

    def add_router(self, value, mode):
        if mode == 1:
            self.router.add_direct_ip(value)
        elif mode == 2:
            self.router.add_direct_domain(value)
        elif mode == 3:
            self.router.add_proxy_ip(value)
        elif mode == 4:
            self.router.add_proxy_domain(value)
        elif mode == 5:
            self.router.add_block_ip(value)
        elif mode == 6:
            self.router.add_block_domain(value)
        self.save()

    def get_router(self, key, mode):
        if mode == 1:
            r = data(self.router)['direct']['ip']
            d, _ = Dealdata.cut_data(r, key)
            return d, Dealdata.praseindex(key)
        elif mode == 2:
            r = data(self.router)['direct']['domain']
            d, _ = Dealdata.cut_data(r, key)
            return d, Dealdata.praseindex(key)
        elif mode == 3:
            r = data(self.router)['proxy']['ip']
            d, _ = Dealdata.cut_data(r, key)
            return d, Dealdata.praseindex(key)
        elif mode == 4:
            r = data(self.router)['proxy']['domain']
            d, _ = Dealdata.cut_data(r, key)
            return d, Dealdata.praseindex(key)
        elif mode == 5:
            r = data(self.router)['block']['ip']
            d, _ = Dealdata.cut_data(r, key)
            return d, Dealdata.praseindex(key)
        elif mode == 6:
            r = data(self.router)['block']['domain']
            d, _ = Dealdata.cut_data(r, key)
            return d, Dealdata.praseindex(key)

    def del_router(self, key, mode):
        i = 0
        if mode == 1:
            i = self.router.del_direct_ip(key)
        elif mode == 2:
            i = self.router.del_direct_domain(key)
        elif mode == 3:
            i = self.router.del_proxy_ip(key)
        elif mode == 4:
            i = self.router.del_proxy_domain(key)
        elif mode == 5:
            i = self.router.del_block_ip(key)
        elif mode == 6:
            i = self.router.del_block_domain(key)
        self.save()
        return i

    def del_node(self, key=''):
        """
        删除节点
        """
        i = self.outbound.del_node(key)
        self.save()
        return i

    def del_sub(self, key=''):
        """
        删除订阅
        """
        i = self.outbound.del_sub(key)
        self.save()
        return i

    def del_dns(self, key):
        """
        删除dns
        """
        i = self.dns.del_DNS(key)
        self.save()
        return i

    def gen_config(self):
        return {
            'log': self.log.gen_config_obj(),
            'inbounds': self.inbound.gen_config_obj(),
            'outbounds': self.outbound.gen_config_obj(),
            'dns': self.dns.gen_config_obj(),
            'routing': self.router.gen_config_obj()
        }

    def save_config(self):
        obj = self.gen_config()
        path = self.root_path + os.sep + "v2ray-core" + os.sep + "config.json"
        FileIo.savejson(path, obj)

    def save(self):
        """
        保存对象到json文件
        """
        path = self.root_path + os.sep + "v2rayT.json"
        FileIo.savejson(path, {
            "inbound": data(self.inbound),
            "log": data(self.log),
            "outbound": data(self.outbound),
            "dns": data(self.dns),
            "router": data(self.router)
        })
        self.save_config()


def data(obj):
    """
    鸭子类型的函数，用于读取config.py中定义的配置类的数据
    """
    return obj.data
