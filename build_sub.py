#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把自建 VPS 的订阅「落成静态文件」，推到 GitHub Pages 做固定入口。
换 IP 后只需：改 SERVER_IP -> python build_sub.py -> git commit/push
"""
import base64, io, json, os, sys, urllib.request
import yaml

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else '64.204.25.118'  # 换 IP 可传参：python build_sub.py 1.2.3.4
UUID      = 'c346d926-910c-47ca-977d-f33611e69b48'
BASE      = f'http://{SERVER_IP}:13315/{UUID}'
OUT       = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
os.makedirs(OUT, exist_ok=True)

def get(path, timeout=20):
    return urllib.request.urlopen(f'{BASE}/{path}', timeout=timeout).read().decode('utf-8', 'ignore')

def build_clash():
    """从 /proxies 取节点，内联成自包含的 Clash 配置（不依赖 VPS 的 proxy-provider）"""
    nodes = yaml.safe_load(get('proxies'))['proxies']
    for n in nodes:
        n['name'] = 'US-' + n['name'].split(' ')[-1]
        if n['type'] in ('hysteria2', 'tuic', 'trojan', 'anytls'):
            n['skip-cert-verify'] = True
    names = [n['name'] for n in nodes]
    cfg = {
        'mixed-port': 7890, 'allow-lan': False, 'mode': 'rule', 'log-level': 'info',
        'ipv6': False, 'unified-delay': True, 'tcp-concurrent': True,
        'proxies': nodes,
        'proxy-groups': [
            {'name': '🚀 节点选择', 'type': 'select', 'proxies': ['♻️ 自动选择'] + names + ['DIRECT']},
            {'name': '♻️ 自动选择', 'type': 'url-test', 'url': 'https://www.gstatic.com/generate_204',
             'interval': 300, 'tolerance': 50, 'proxies': names},
        ],
        'rules': [
            f'IP-CIDR,{SERVER_IP}/32,DIRECT,no-resolve',
            'DOMAIN-SUFFIX,local,DIRECT',
            'IP-CIDR,127.0.0.0/8,DIRECT,no-resolve',
            'IP-CIDR,10.0.0.0/8,DIRECT,no-resolve',
            'IP-CIDR,172.16.0.0/12,DIRECT,no-resolve',
            'IP-CIDR,192.168.0.0/16,DIRECT,no-resolve',
            'GEOSITE,cn,DIRECT', 'GEOIP,CN,DIRECT',
            'MATCH,🚀 节点选择',
        ],
    }
    head = (f'# 自建 VPS 静态订阅（{SERVER_IP}）\n'
            f'# 由 build_sub.py 生成，节点已内联，不依赖服务器上的 proxy-provider\n')
    return head + yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False, width=4096), len(nodes)


def _fix_insecure(b64_text):
    """把小火箭/v2rayN 列表里的自签证书节点改成 insecure=1（去掉 hpkp 严格校验）。
    原因：服务器是自签证书，Shadowrocket 对 hpkp 支持不好，会显示不出延迟/连不上。"""
    raw = b64_text.strip()
    try:
        dec = base64.b64decode(raw + '=' * (-len(raw) % 4)).decode('utf-8', 'ignore')
    except Exception:
        return b64_text
    out = []
    for line in dec.splitlines():
        line = line.strip()
        if not line:
            continue
        scheme = line.split('://')[0].lower()
        if scheme in ('hysteria2', 'hysteria', 'tuic', 'anytls', 'trojan'):
            base, sep, frag = line.partition('#')
            head, _, query = base.partition('?')
            params = [x for x in query.split('&') if x and not x.startswith(('hpkp=', 'insecure='))]
            params.append('insecure=1')
            line = head + '?' + '&'.join(params) + (sep + frag if sep else '')
        out.append(line)
    return base64.b64encode('\n'.join(out).encode()).decode()

def write(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(f'  {name:20s} {len(text):>6d} B')

def main():
    print(f'源：{BASE}')
    clash, n = build_clash()
    write('clash.yaml', clash)
    write('shadowrocket.txt', _fix_insecure(get('shadowrocket')))   # base64 节点列表（自签证书 → insecure=1）
    write('v2rayn.txt', _fix_insecure(get('v2rayn')))
    write('sing-box.json', get('sing-box'))
    write('proxies.yaml', get('proxies'))
    write('index.html', f"""<!doctype html><meta charset="utf-8">
<title>sub</title><pre>
Clash        : ./clash.yaml
Shadowrocket : ./shadowrocket.txt
V2rayN       : ./v2rayn.txt
sing-box     : ./sing-box.json
节点数        : {n}   server: {SERVER_IP}
更新于        : {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}
</pre>""")
    print(f'完成：{n} 个节点')

if __name__ == '__main__':
    main()
