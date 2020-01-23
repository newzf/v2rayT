import time
import itertools
from prettytable import PrettyTable
from cmd import Cmd

from base.service import Service
from base.v2ctl import V2ctl


class Cli(Cmd):
    prompt = 'v2rayT> '
    intro = 'Welcome to v2rayT!'

    def __init__(self, root_path):
        Cmd.__init__(self)
        self.root_path = root_path
        self.service = Service(root_path)
        self.v2ctl = V2ctl(root_path)
        

    def show_baseset(self, options):
        obj = self.service.get_baseset()
        titles = ['监听端口', '协议', 'udp转发', '启用流量监听', '多路复用', '允许局域网连接', '绕过局域网和大陆', '路由策略']
        datas = [
            [obj['port'], obj['protocol'], obj['udp'], obj['sniffing'], obj['mux'], obj['allowLANConn'], obj['local'],
             obj['domainStrategy']]]
        show_table(titles, datas)

    def alter_baseset(self, options):
        optionsdict = options2dict(options, {'p': 'port', 'u': 'udp', 's': 'sniffing', 'm': 'mux', 'l': 'lanconn',
                                             'r': 'roundlocal', })
        if 'port' in optionsdict.keys():
            self.service.set_local_port(optionsdict['port'])
        if 'udp' in optionsdict.keys():
            b = optionsdict['udp']
            if b.lower() == 'true':
                self.service.set_udp(True)
            elif b.lower() == 'false':
                self.service.set_udp(False)
        if 'sniffing' in optionsdict.keys():
            b = optionsdict['sniffing']
            if b.lower() == 'true':
                self.service.set_sniffing(True)
            elif b.lower() == 'false':
                self.service.set_sniffing(False)
        if 'mux' in optionsdict.keys():
            b = optionsdict['mux']
            if b.lower() == 'true':
                self.service.set_mux(True)
            elif b.lower() == 'false':
                self.service.set_mux(False)
        if 'lanconn' in optionsdict.keys():
            b = optionsdict['lanconn']
            if b.lower() == 'true':
                self.service.set_LANConn(True)
            elif b.lower() == 'false':
                self.service.set_LANConn(False)
        if 'roundlocal' in optionsdict.keys():
            b = optionsdict['roundlocal']
            if b.lower() == 'true':
                self.service.set_round_local(True)
            elif b.lower() == 'false':
                self.service.set_round_local(False)
        if 'asis' in optionsdict.keys():
            self.service.set_domainStrategy(1)
        if 'ipifnonmatch' in optionsdict.keys():
            self.service.set_domainStrategy(2)
        if 'ipondemand' in optionsdict.keys():
            self.service.set_domainStrategy(3)

        self.show_baseset(None)

    def do_baseset(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'show':
                self.show_baseset(options)
            elif l[0] == 'alter':
                self.alter_baseset(options)
        try:
            pass
        except BaseException as e:
            print(e)
            print('使用 help beseset 查看用法')

    def show_node(self, options):
        key = 'all'
        optionsdict = options2dict(options, {'s': 'select'})
        if 'select' in optionsdict.keys():
            key = optionsdict['select']
        if 'all' in optionsdict.keys():
            titles = ['别名', '地址', '端口', '用户ID', 'aid', '加密方式', '传输协议', '伪装类型', '伪装域名', 'path', '安全传输']
            keys = ['remarks', 'address', "port", 'id', 'alterId', 'security', 'network', 'headerType',
                    'requestHost', 'path', 'streamSecurity']
        else:
            titles = ['别名', '地址', '端口', '加密方式', '传输协议', '安全传输']
            keys = ['remarks', 'address', "port", 'security', 'network', 'streamSecurity']
        datas, index = self.service.get_node(key)
        show_table(titles, datas, keys, index)
        print('当前选定节点索引: ', self.service.get_selected_node_index())

    def add_node(self, options):
        optionsdict = options2dict(options, {
            'a': 'address',
            'p': 'port',
            'i': 'id',
            'n': 'network',
            'r': 'remarks',
            's': 'security',
            't': 'type',
            'h': 'host'
        })
        if 'vmess' in optionsdict.keys():
            vmess = self.service.add_node_by_vmesslinks([optionsdict['vmess']])
            print('添加列表:')
            for x in vmess:
                print(x)
            if len(vmess) > 0:
                print('[节点添加成功]')
        elif 'file' in optionsdict.keys():
            vmess = self.service.add_node_by_vmesslinks_file(optionsdict['file'])
            print('添加列表:')
            print('---------------------------------------------------------------')
            for x in vmess:
                print(x)
            print('---------------------------------------------------------------')
            if len(vmess) > 0:
                print('[节点添加成功]')
        elif 'sub' in optionsdict.keys():
            key = optionsdict['sub'] if optionsdict['sub'] != '' else 'all'
            if 'proxy' in optionsdict.keys():
                self.service.update_node_by_sub(key, optionsdict['proxy'])
            else:
                self.service.update_node_by_sub(key)
            print('[从订阅更新节点成功]')
        elif 'address' in optionsdict.keys() and 'port' in optionsdict.keys() and 'id' in optionsdict.keys() and 'aid' in optionsdict.keys() and 'network' in optionsdict.keys():
            addr = optionsdict['address']
            port = optionsdict['port']
            id = optionsdict['id']
            aid = optionsdict['aid']
            net = optionsdict['network']
            remarks = optionsdict['remarks'] if 'remarks' in optionsdict.keys() else ''
            security = optionsdict['security'] if 'security' in optionsdict.keys() else 'auto'
            type = optionsdict['type'] if 'type' in optionsdict.keys() else 'none'
            host = optionsdict['host'] if 'host' in optionsdict.keys() else ''
            path = optionsdict['path'] if 'path' in optionsdict.keys() else ''
            tls = optionsdict['tls'] if 'tls' in optionsdict.keys() else ''
            node = self.service.add_node(addr, port, id, aid, net, remarks, security, type, host, path, tls)
            print('添加节点:')
            print(node)
            print('[成功]')

    def del_node(self, options):
        if len(options) == 1:
            key = options[0]
            i = self.service.del_node(key)
            print('[成功删除', i, '个节点]')

    def export_node(self, options):
        key = 'all'
        if len(options) == 1:
            key = options[0]
        titles = ['别名', 'vmess链接']
        keys = ['remarks', 'link']
        datas, _ = self.service.get_vmesslinks(key)
        print('------------------------------------------------')
        for d in datas:
            print(d['link'])
        print('------------------------------------------------')

    def tcping_node(self, options):
        import sys,os
        key = 'all'
        count = 3
        if len(options) >= 1:
            key = options[0]
        optionsdict = options2dict(options, {'c': 'count'})
        if 'count' in optionsdict.keys():
            count = int(optionsdict['count'])
        titles = ['别名', '地址', '端口', 'tcping']
        keys = ['remarks', 'address', "port", 'testResult']
        for datas, index in self.service.tcping_node(key, count):
            show_table(titles, datas, keys, index)

    def do_node(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'show':
                self.show_node(options)
            elif l[0] == 'add':
                self.add_node(options)
            elif l[0] == 'del':
                self.del_node(options)
            elif l[0] == 'export':
                self.export_node(options)
            elif l[0] == 'tcping':
                self.tcping_node(options)

    def add_sub(self, options):
        if len(options) == 0:
            return
        url = options[0]
        optionsdict = options2dict(options[1:], {'r': 'remark'})
        if 'remark' in optionsdict.keys():
            self.service.add_sub(url, optionsdict['remark'])
            print('[订阅添加成功]')
        else:
            self.service.add_sub(url)
            print('[订阅添加成功]')

    def show_sub(self, options):
        titles = ['别名', 'url']
        keys = ['remarks', 'url']
        datas, _ = self.service.get_sub()
        show_table(titles, datas, keys)

    def del_sub(self, options):
        if len(options) == 1:
            key = options[0]
            i = self.service.del_sub(key)
            print('[成功删除', i, '个订阅]')

    def do_sub(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'add':
                self.add_sub(options)
            elif l[0] == 'show':
                self.show_sub(options)
            elif l[0] == 'del':
                self.del_sub(options)

    def add_dns(self, options):
        if len(options) == 0:
            return
        dns = options[0]
        self.service.add_dns(dns)
        print('[DNS添加成功]')

    def show_dns(self, options):
        obj, _ = self.service.get_dns()
        datas = obj
        table = PrettyTable()
        table.add_column('索引', list(range(len(datas))))
        table.add_column('dns', datas)
        print(table)

    def del_dns(self, options):
        if len(options) == 1:
            key = options[0]
            i = self.service.del_dns(key)
            print('[删除成功', i, '条]')

    def do_dns(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'add':
                self.add_dns(options)
            elif l[0] == 'show':
                self.show_dns(options)
            elif l[0] == 'del':
                self.del_dns(options)

    def add_router(self, options):
        mode = 0
        d = ''
        optionsdict = options2dict(options, {'i': 'ip', 'd': 'domain'})
        if 'direct' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 1
                d = optionsdict['ip']
            elif 'domain' in optionsdict.keys():
                mode = 2
                d = optionsdict['domain']
        elif 'proxy' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 3
                d = optionsdict['ip']
            elif 'domain' in optionsdict.keys():
                mode = 4
                d = optionsdict['domain']
        elif 'block' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 5
                d = optionsdict['ip']
            elif 'domain' in optionsdict.keys():
                mode = 6
                d = optionsdict['domain']
        if mode > 0 and d != '':
            self.service.add_router(d, mode)

    def show_router(self, options):
        optionsdict = options2dict(options, {'i': 'ip', 'd': 'domain', 's': 'select'})
        mode = 0
        key = optionsdict['select'] if 'select' in optionsdict.keys() else 'all'
        if 'direct' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 1
            elif 'domain' in optionsdict.keys():
                mode = 2
        elif 'proxy' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 3
            elif 'domain' in optionsdict.keys():
                mode = 4
        elif 'block' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 5
            elif 'domain' in optionsdict.keys():
                mode = 6
        if mode > 0:
            datas, index = self.service.get_router(key, mode)
            index = list(range(len(datas))) if index is None else index[:len(datas)]
            table = PrettyTable()
            table.add_column('索引', index)
            table.add_column('数据', datas)
            print(table)

    def del_router(self, options):
        if len(options) == 0:
            return
        key = options[0]
        optionsdict = options2dict(options[1:], {'i': 'ip', 'd': 'domain'})
        mode = 0
        if 'direct' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 1
            elif 'domain' in optionsdict.keys():
                mode = 2
        elif 'proxy' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 3
            elif 'domain' in optionsdict.keys():
                mode = 4
        elif 'block' in optionsdict.keys():
            if 'ip' in optionsdict.keys():
                mode = 5
            elif 'domain' in optionsdict.keys():
                mode = 6
        if mode > 0:
            i = self.service.del_router(key, mode)
            print('[删除成功', i, '条]')

    def do_router(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'add':
                self.add_router(options)
            elif l[0] == 'show':
                self.show_router(options)
            elif l[0] == 'del':
                self.del_router(options)


    def show_log(self, options):
        titles = ['日志地址', '日志等级']
        datas = [self.service.get_logset()]
        show_table(titles, datas)

    def alter_log(self, options):
        optionsdict = options2dict(options, {'p':'path', 'l':'level'})
        if 'path' in optionsdict.keys():
            self.service.set_logPath(optionsdict['path'])
            self.show_log(None)
        if 'level' in optionsdict.keys():
            if optionsdict['level'] in ['debug','info','warning','error','none']:
                self.service.set_logPath(optionsdict['level'])
                self.show_log(None)

    def do_log(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'show':
                self.show_log(options)
            elif l[0] == 'alter':
                self.alter_log(options)


    def start_service(self, options):
        if options is not None and len(options) == 1:
            self.service.set_node_index(options[0])
        if self.v2ctl.is_running():
            self.v2ctl.stop()
        self.v2ctl.start()
        time.sleep(2.0)
        if self.v2ctl.is_running():
            print('v2ray启动成功, 监听端口: {}, 选定节点: {}'.format(self.service.get_baseset()['port'],
                                                         self.service.get_selected_node_index()))
        else:
            print('v2ray启动失败,请在logs文件夹查看临时日志文件v2.log')

    def stop_service(self, options):
        self.v2ctl.stop()

    def restart_service(self, options):
        if options is not None and len(options) == 1:
            self.service.set_node_index(options[0])
        self.v2ctl.restart()
        time.sleep(2.0)
        if self.v2ctl.is_running():
            print('v2ray启动成功, 监听端口: {}, 选定节点: {}'.format(self.service.get_baseset()['port'],
                                                         self.service.get_selected_node_index()))
        else:
            print('v2ray启动失败,请在logs文件夹查看临时日志文件v2.log')

    def status_service(self, options):
        print(self.v2ctl.statue())

    def do_service(self, line):
        l = self.args2list(line)
        if len(l) != 0:
            options = l[1:]
            if l[0] == 'start':
                self.start_service(options)
            elif l[0] == 'stop':
                self.stop_service(options)
            elif l[0] == 'restart':
                self.restart_service(options)
            elif l[0] == 'status':
                self.status_service(options)


    def help_baseset(self):
        print('')
        print('baseset {commands} [options] ...')
        print('')
        print('Commands:')
        print('  show                                 {}'.format('查看基本设置'))
        print('  alter [options]                      {}'.format('修改基本设置'))
        print('')
        print('alter Options')
        print('  -p,--port {{port}}                   {}'.format('设置监听端口'))
        print('  -u,--udp {{true|false}}              {}'.format('是否启用udp'))
        print('  -s,--sniffing {{true|false}}         {}'.format('是否启用流量监听'))
        print('  -l,--lanconn {{true|false}}          {}'.format('是否启用局域网连接'))
        print('  -m,--mux {{true|false}}              {}'.format('是否启用局域网连接'))
        print('  -r,--roundlocal {{true|false}}     {}'.format('是否启用绕过局域网及大陆'))
        print('  --asis                             {}'.format('设置路由策略为AsIs'))
        print('  --ipifnonmatch                     {}'.format('设置路由策略为IPIfNonMatch'))
        print('  --ipondemand                       {}'.format('设置路由策略为IPOnDemand'))
        print('  ')

    def help_node(self):
        print('')
        print('node {commands} [options] ...')
        print('')
        print('Commands:')
        print('  add [options]                {}'.format('添加节点'))
        print('  show [options]               {}'.format('查看节点信息'))
        print('  del {{索引参数}}                {}'.format('根据索引参数删除节点'))
        print('  export {{索引参数}}             {}'.format('导出为vmess链接'))
        print('  tcping {{索引参数}}             {}'.format('tcping指定索引节点'))
        print('')
        print('add Options')
        print('  --vmess {{vmess链接}}          {}'.format('导入vmess://数据'))
        print('  --file {{文件名}}               {}'.format('从文件批量导入vmess://数据,文件必须与v2rayT.py处于同级目录'))
        print('  --sub [订阅索引参数]            {}'.format('从订阅更新节点,没有索引参数就默认为全部'))
        print('  --proxy {{本地sock5端口}}       {}'.format('和--sub一起用,通过代理更新订阅'))
        print('  ')
        print('  下面11个属于直接通过参数添加')
        print('  -a,--address {地址}')
        print('  -p,--port {端口}')
        print('  -i,--id {用户id}')
        print('  --aid {额外ID}')
        print('  -n,--network {传输协议}')
        print('  -r,--remarks {别名}')
        print('  -s,--security {加密方式}')
        print('  -t,--type {伪装类型}')
        print('  -h,--host {伪装域名}')
        print('  --path {path}')
        print('  --tls {底层安全传输}')
        print('  其中 前五个[-a,-p,-i,--aid,-n]必须要有')
        print('')
        print('show Options')
        print('  -s,--select {索引参数}  %s' % '根据索引参数选取')
        print('      示例: -s 0-2,6,7   选取索引为0,1,2,6,7的数据')
        print('  --all                 {}'.format('显示全部字段'))
        print('')
        print('tcping Options')
        print('  -c,--count {tcping次数}  %s' % '默认3次')
        print('')

    def help_sub(self):
        print('')
        print('sub {commands} [options] ...')
        print('')
        print('Commands:')
        print('  add {{sublink}} [options]          {}'.format('添加订阅'))
        print('  show                             {}'.format('查看订阅信息'))
        print('  del {{索引参数}}                    {}'.format('根据索引参数删除订阅'))
        print('')
        print('add Options')
        print('  -r,--remark {{别名}}           {}'.format('自定义别名'))
        print('')

    def help_dns(self):
        print('')
        print('dns {commands} ...')
        print('')
        print('Commands:')
        print('  add {{dns}}                   {}'.format('添加dns'))
        print('  show                        {}'.format('查看dns列表'))
        print('  del {{索引参数}}                {}'.format('根据索引参数删除dns'))
        print('')

    def help_router(self):
        print('')
        print('router {commands} [options] ...')
        print('')
        print('Commands:')
        print('  add {{base options}} {{options}}              {}'.format('添加路由'))
        print('  show {{base options}} [options]             {}'.format('查看路由'))
        print('  del {{索引参数}} {{base options}} {{options}}   {}'.format('删除路由'))
        print('')
        print('')
        print('base Options')
        print('  --direct                                {}'.format('选定直接访问路由表'))
        print('  --proxy                                 {}'.format('选定代理访问路由表'))
        print('  --block                                 {}'.format('选定禁止访问路由表'))
        print('')
        print('add Options')
        print('  -i,--ip {{ip}}                           {}'.format('添加到ip表'))
        print('  -d,--domain {{域名}}                     {}'.format('添加到域名表'))
        print('')
        print('show Options')
        print('  -i,--ip                                {}'.format('查看ip表'))
        print('  -d,--domain                            {}'.format('查看域名表'))
        print('  -s,--select {{索引参数}}                  {}'.format('根据索引参数选取'))
        print('')
        print('del Options')
        print('  -i,--ip                                {}'.format('按索引参数删除ip表数据'))
        print('  -d,--domain                            {}'.format('按索引参数删除域名表数据'))
        print('')

    def help_log(self):
        print('')
        print('log {commands} [options] ...')
        print('')
        print('Commands:')
        print('  show                                    {}'.format('查看v2ray-core日志设置'))
        print('  alter [options]                         {}'.format('修改v2ray-core日志设置'))
        print('')
        print('alter Options')
        print('  -p,--path {{文件夹绝对地址}}                               {}'.format('选定直接访问路由表'))
        print('  -l,--level  {{debug|info|warning|error|none}}            {}'.format('选定代理访问路由表'))
        print('')

    def help_service(self):
        print('')
        print('service {commands} [options] ...')
        print('')
        print('Commands:')
        print('  start [节点索引]                         {}'.format('启动v2ray'))
        print('  stop                                    {}'.format('停止v2ray'))
        print('  restart [节点索引]                       {}'.format('重启v2ray'))
        print('  status                                  {}'.format('查看v2ray状态'))
        print('')

    def help_exit(self):
        print('')
        print('exit      退出')
        print('')

    def help_version(self):
        print('')
        print('version   查看版本')
        print('')

    def complete_baseset(self, text, line, begidx, endidx):
        data = ['show', 'alter ']
        return self.comtools(line, text, data)

    def complete_node(self, text, line, begidx, endidx):
        data = ['add', 'show', 'del', 'export', 'tcping']
        return self.comtools(line, text, data)

    def complete_sub(self, text, line, begidx, endidx):
        data = ['add', 'show', 'del']
        return self.comtools(line, text, data)

    def complete_dns(self, text, line, begidx, endidx):
        data = ['add', 'show', 'del']
        return self.comtools(line, text, data)

    def complete_router(self, text, line, begidx, endidx):
        data = ['add', 'show', 'del']
        return self.comtools(line, text, data)

    def complete_log(self, text, line, begidx, endidx):
        data = ['show', 'alter']
        return self.comtools(line, text, data)

    def complete_service(self, text, line, begidx, endidx):
        data = ['start', 'stop', 'restart', 'status']
        return self.comtools(line, text, data)

    def do_version(self, *args):
        print('+-------------------------------------+')
        print("+            v2rayT v{}              +".format('0.1'))
        print('+-------------------------------------+')

    def do_exit(self, args):
        return True

    @staticmethod
    def args2list(args):
        return [x for x in args.strip(' ').split(' ') if x != '']

    def comtools(self, line, text, completions):
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions if s.startswith(mline)]

    def emptyline(self):
        print('print input command')

    def default(self, line):
        print('what a input ?')


def options2dict(l, keys=None):
    """
    操作选项转换成字典
    """
    d = dict()
    key = ''
    for x in l:
        if x[0] == '-':
            key = x.strip('-')
            if keys is not None and key in keys.keys():
                key = keys[key]
            d[key] = ''
        else:
            d[key] = x
    return d


def show_table(titles, datas, keys=None, index=None, is_print=True):
    """
    打印表格
    """
    table = PrettyTable(list(itertools.chain(('索引',), titles)))
    if index is None or len(index) == 0:
        index = [i for i in range(len(datas))]

    if keys is None:
        for i in range(len(datas)):
            x = datas[i]
            table.add_row(list(itertools.chain((index[i],), x)))
        if is_print:
            print(table)
        else:
            return table
    elif len(titles) == len(keys):
        for i in range(len(datas)):
            x = datas[i]
            d = [x[key] for key in keys]
            table.add_row(list(itertools.chain((index[i],), d)))
        if is_print:
            print(table)
        else:
            return table

