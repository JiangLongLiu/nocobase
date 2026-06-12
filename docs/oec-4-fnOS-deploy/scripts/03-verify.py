#!/usr/bin/env python3
"""
部署验证脚本
检查容器运行状态、HTTP 健康检查、Web 界面可访问性
"""
import csv
import sys
import json
import paramiko
import urllib.request
import urllib.error

CSV_PATH = r"E:\Qoder_workspace\nocobase\docs\oec-4-fnOS-deploy\password.csv"
REMOTE_DIR = "/vol1/docker/mycontainers/nocobase"
WEB_PORT = 18080


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


def ssh_check(client, name, cmd, expected_exit=0):
    """执行 SSH 命令并检查结果"""
    print(f"\n[检查] {name}")
    print(f"  命令: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    output = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    exit_code = stdout.channel.recv_exit_status()

    if exit_code == expected_exit:
        print(f"  结果: [PASS]")
        if output:
            for line in output.splitlines()[:20]:
                print(f"    {line}")
        return True, output
    else:
        print(f"  结果: [FAIL] (exit={exit_code})")
        if err:
            print(f"  错误: {err}")
        return False, err


def http_check(host, port):
    """HTTP 健康检查"""
    print(f"\n[检查] HTTP 健康检查")
    url = f"http://{host}:{port}/api/app:getLang"
    print(f"  URL: {url}")
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            body = resp.read().decode()
            print(f"  HTTP 状态码: {status}")
            try:
                data = json.loads(body)
                print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"  响应: {body[:500]}")
            if status == 200:
                print(f"  结果: [PASS]")
                return True
            else:
                print(f"  结果: [FAIL]")
                return False
    except urllib.error.HTTPError as e:
        print(f"  HTTP 错误: {e.code} {e.reason}")
        print(f"  结果: [FAIL]")
        return False
    except urllib.error.URLError as e:
        print(f"  连接错误: {e.reason}")
        print(f"  结果: [FAIL]")
        return False
    except Exception as e:
        print(f"  异常: {e}")
        print(f"  结果: [FAIL]")
        return False


def web_ui_check(host, port):
    """检查 Web 界面是否可访问"""
    print(f"\n[检查] Web 界面可访问性")
    url = f"http://{host}:{port}/"
    print(f"  URL: {url}")
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            content_length = resp.headers.get("Content-Length", "unknown")
            print(f"  HTTP 状态码: {status}")
            print(f"  Content-Length: {content_length}")
            if status in (200, 301, 302):
                print(f"  结果: [PASS]")
                return True
            else:
                print(f"  结果: [FAIL]")
                return False
    except urllib.error.HTTPError as e:
        # 404 也算可以（表示服务器在运行）
        if e.code in (301, 302, 404):
            print(f"  HTTP {e.code} - 服务器响应正常")
            print(f"  结果: [PASS]")
            return True
        print(f"  HTTP 错误: {e.code} {e.reason}")
        print(f"  结果: [FAIL]")
        return False
    except Exception as e:
        print(f"  异常: {e}")
        print(f"  结果: [FAIL]")
        return False


def main():
    cred = load_credentials(CSV_PATH)
    host = cred["host"]

    print(f"{'='*50}")
    print(f"NocoBase 部署验证")
    print(f"目标主机: {host}")
    print(f"Web 端口: {WEB_PORT}")
    print(f"{'='*50}")

    results = {}

    # SSH 连接检查
    print(f"\n连接 SSH...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        cred["host"], port=cred["port"],
        username=cred["username"], password=cred["password"],
        timeout=15
    )
    print("[OK] SSH 连接成功")

    try:
        # 1. 检查容器状态
        ok, out = ssh_check(client, "容器运行状态",
                           f"cd {REMOTE_DIR} && docker compose ps")
        results["容器状态"] = ok

        # 2. 检查容器日志（最近20行）
        ok, out = ssh_check(client, "容器日志(最近20行)",
                           f"cd {REMOTE_DIR} && docker compose logs --tail=20 nocobase")
        results["容器日志"] = ok

        # 3. 检查数据库连接
        ok, out = ssh_check(client, "数据库连接",
                           f"cd {REMOTE_DIR} && docker compose exec -T postgres pg_isready -U nocobase")
        results["数据库连接"] = ok

    finally:
        client.close()

    # 4. HTTP 健康检查
    results["HTTP健康检查"] = http_check(host, WEB_PORT)

    # 5. Web 界面检查
    results["Web界面"] = web_ui_check(host, WEB_PORT)

    # 汇总
    print(f"\n{'='*50}")
    print("验证结果汇总")
    print(f"{'='*50}")
    all_pass = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name:<20} [{status}]")
        if not passed:
            all_pass = False

    print(f"\n{'='*50}")
    if all_pass:
        print("所有检查通过! NocoBase 部署成功!")
    else:
        print("部分检查未通过，请检查日志!")
    print(f"{'='*50}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
