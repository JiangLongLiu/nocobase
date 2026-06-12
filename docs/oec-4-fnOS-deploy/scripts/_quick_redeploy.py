"""快速上传配置并重建容器"""
import paramiko

HOST = "192.168.123.54"
LOCAL_COMPOSE = r"e:\Qoder_workspace\nocobase\docs\oec-4-fnOS-deploy\config\docker-compose.yml"
LOCAL_ENV = r"e:\Qoder_workspace\nocobase\docs\oec-4-fnOS-deploy\config\.env"
REMOTE_DIR = "/vol1/docker/mycontainers/nocobase"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", "1234567890", timeout=15)

# Upload files
s = c.open_sftp()
s.put(LOCAL_COMPOSE, f"{REMOTE_DIR}/docker-compose.yml")
print("uploaded docker-compose.yml")
s.put(LOCAL_ENV, f"{REMOTE_DIR}/.env")
print("uploaded .env")
s.close()

# Recreate containers
i, o, e = c.exec_command(f"cd {REMOTE_DIR} && docker compose down && docker compose up -d 2>&1", timeout=120)
print(o.read().decode())

c.close()
print("Done!")
