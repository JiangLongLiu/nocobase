#!/usr/bin/env python3
"""
上传配置文件并启动容器
通过 SCP 上传 docker-compose.yml 和 .env 到远程主机，然后执行 docker compose up
"""
import csv
import os
import sys
import time
import paramiko

CSV_PATH = r"E:\Qoder_workspace\nocobase\docs\oec-4-fnOS-deploy\password.csv"
CONFIG_DIR = r"E:\Qoder_workspace\nocobase\docs\oec-4-fnOS-deploy\config"
REMOTE_DIR = "/vol1/docker/mycontainers/nocobase"

# 要上传的文件
FILES_TO_UPLOAD = [
    "docker-compose.yml",
    ".env",
]


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


def create_remote_dir(client, remote_dir):
    """递归创建远程目录"""
    print(f"[1/4] 创建远程目录: {remote_dir}")
    stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_dir}")
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        print(f"  [ERROR] 创建目录失败: {stderr.read().decode()}")
        return False
    print(f"  [OK] 目录已就绪")
    return True


def upload_files(sftp, local_dir, remote_dir, files):
    """上传文件到远程主机"""
    print(f"\n[2/4] 上传配置文件到 {remote_dir}")
    for fname in files:
        local_path = os.path.join(local_dir, fname)
        remote_path = f"{remote_dir}/{fname}"
        if not os.path.exists(local_path):
            print(f"  [WARN] 本地文件不存在: {local_path}")
            continue
        file_size = os.path.getsize(local_path)
        print(f"  上传 {fname} ({file_size} bytes) ...", end=" ")
        sftp.put(local_path, remote_path)
        print("[OK]")
    print(f"  [OK] 所有文件已上传")


def execute_command(client, cmd, timeout=300, show_output=True):
    """执行远程命令并实时输出"""
    print(f"\n  执行: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)

    output_lines = []
    # 逐行读取输出
    for line in iter(stdout.readline, ""):
        line = line.strip()
        if line and show_output:
            print(f"    {line}")
        output_lines.append(line)

    err_output = stderr.read().decode()
    exit_code = stdout.channel.recv_exit_status()

    if err_output and show_output:
        for line in err_output.strip().splitlines():
            print(f"    [stderr] {line}")

    return exit_code, "\n".join(output_lines), err_output


def start_containers(client, remote_dir):
    """拉取镜像并启动容器"""
    print(f"\n[3/4] 拉取镜像...")
    code, out, err = execute_command(
        client,
        f"cd {remote_dir} && docker compose pull",
        timeout=600
    )
    if code != 0:
        print(f"  [ERROR] 镜像拉取失败 (exit={code})")
        return False

    print(f"\n[4/4] 启动容器...")
    code, out, err = execute_command(
        client,
        f"cd {remote_dir} && docker compose up -d",
        timeout=120
    )
    if code != 0:
        print(f"  [ERROR] 容器启动失败 (exit={code})")
        return False

    print(f"\n  [OK] 容器已启动，等待服务就绪...")
    time.sleep(10)

    # 查看容器状态
    code, out, err = execute_command(
        client,
        f"cd {remote_dir} && docker compose ps",
        timeout=30
    )
    return True


def main():
    cred = load_credentials(CSV_PATH)
    print(f"{'='*50}")
    print(f"目标主机: {cred['host']}")
    print(f"远程目录: {REMOTE_DIR}")
    print(f"{'='*50}")

    # 建立 SSH 连接
    print(f"\n连接 SSH {cred['host']}:{cred['port']} ...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        cred["host"], port=cred["port"],
        username=cred["username"], password=cred["password"],
        timeout=15
    )
    print("[OK] SSH 连接成功")

    try:
        # 创建远程目录
        if not create_remote_dir(client, REMOTE_DIR):
            sys.exit(1)

        # 上传文件
        sftp = client.open_sftp()
        upload_files(sftp, CONFIG_DIR, REMOTE_DIR, FILES_TO_UPLOAD)
        sftp.close()

        # 启动容器
        if not start_containers(client, REMOTE_DIR):
            sys.exit(1)

        print(f"\n{'='*50}")
        print("部署完成!")
        print(f"{'='*50}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
