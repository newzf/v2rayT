# v2rayT

v2rayT是一款v2ray 终端版客户端，使用Python编写，基于v2ray项目，仅支持vmess协议，支持订阅，路由，vmess分享，项目地址：https://github.com/hsernos/v2rayT

### 主要特性
----
- **支持协议:** vmess:// 协议
- **支持导入**: 支持本地文件及url导入
- **支持编辑**: 导入配置后可以手动更改配置信息
- **手动配置**: 支持在导入或未导入情况下手动配置主要参数
- **支持模式**: 支持路由，纯自定义，需要熟悉v2ray路由写法
- **支持订阅**: <span style="color: red">支持v2ray订阅</span>
- **支持跨平台**: 仅需更换v2ray-core下的文件，win平台无法使用Tab键补齐，mac系统未测试

### 下载安装
- 直接clone源码到本地就行了

### v2ray简介
   V2Ray 是 Project V 下的一个工具。Project V 包含一系列工具，帮助你打造专属的定制网络体系。而 V2Ray 属于最核心的一个。
简单地说，V2Ray 是一个与 Shadowsocks 类似的代理软件，但比Shadowsocks更具优势

V2Ray 用户手册：[https://www.v2ray.com](https://www.v2ray.com)

V2Ray 项目地址：[https://github.com/v2ray/v2ray-core](https://github.com/v2ray/v2ray-core)

### 功能预览

### 相关文件
	v2ray-core文件:v2rayT/v2ray-core
	项目启动文件: v2rayT/v2rayT.py
	项目配置文件: v2rayT/v2rayT.json

### 待实现功能:
	软件日志
	ping
	速度测试

### 相关问题
	1. 遇到问题先在v2ray-core目录下手动启动，排除端口被占用的问题

### 软件使用问题
	1. 相关设置的配置秉着不怀疑的原则进行设计，比如说添加一个订阅，任意字符串都行，不进行url类型检测或是否可连接限制，一切靠自觉
	2. 有问题请提issue

### 感谢
	参考: v2rayN配置文件、V2rayU的README文档格式
