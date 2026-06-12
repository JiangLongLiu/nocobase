#!/usr/bin/env python3
"""
端口可用性检测脚本
通过 SSH 连接远程主机，检测指定端口是否被占用
"""
import csv
import sys
import paramiko

CSV_PATH = r"E:\Qoder_workspace\nocobase\docs\oec-4-fnOS-deploy\password.csv"
PORTS_TO_CHECK = [80, 443, 3000, 5432, 8080, 8443, 13000, 15432, 18080, 28080, 23000, 23432]

def load_credentials(csv_path):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return {
                "host": row["IP地址"].strip(),
                "username": row["用户名"].strip(),
                "password": row["密码"].strip(),
                "port": int(row["SSH端口"].strip()),
            }

def check_ports(cred, ports):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(cred["host"], port=cred["port"], username=cred["username"], password=cred["password"], timeout=15)

    # 获取所有监听端口
    stdin, stdout, stderr = client.exec_command("ss -tlnp")
    ss_output = stdout.read().decode()

    occupied = set()
    for line in ss_output.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 4:
            addr = parts[3]
            # 提取端口号
            if ":" in addr:
                p = int(addr.rsplit(":", 1)[-1])
                occupied.add(p)

    print(f"\n{'='*50}")
    print(f"主机: {cred['host']}")
    print(f"{'='*50}")
    print(f"\n{'端口':<10} {'状态':<10}")
    print(f"{'-'*20}")
    available = []
    for p in ports:
        status = "已占用" if p in occupied else "可用"
        print(f"{p:<10} {status}")
        if p not in occupied:
            available.append(p)

    print(f"\n可用端口: {available}")

    # 推荐端口方案
    print(f"\n{'='*50}")
    print("推荐端口分配方案:")
    print(f"{'='*50}")
    # NocoBase Web: 优先 18080, 备选 28080
    # PostgreSQL: 优先 25432, 备选 15432
    web_port = next((p for p in [18080, 28080, 13000] if p in available), None)
    pg_port = next((p for p in [25432, 15432, 5432] if p in available), None)
    print(f"  NocoBase Web 端口: {web_port or '无可用端口!'}")
    print(f"  PostgreSQL 端口:    {pg_port or '无可用端口!'}")

    # 列出所有已监听端口
    print(f"\n已监听端口列表:")
    for p in sorted(occupied):
        print(f"  {p}")

    client.close()
    return web_port, pg_port

if __name__ == "__main__":
    cred = load_credentials(CSV_PATH)
    web_port, pg_port = check_ports(cred, PORTS_TO_CHECK)
    if not web_port or not pg_port:
        print("\n[ERROR] 没有足够的可用端口，请手动指定!")
        sys.exit(1)
    print(f"\n[OK] 使用 Web={web_port}, PostgreSQL={pg_port}")
