# Auth Service

一个独立部署的认证服务，基于 `FastAPI + PostgreSQL + JWT` 实现。

## 目录结构

```text
auth-service/
├── .github/workflows/
├── api/
├── database/
├── docs/
├── Dockerfile
├── .env.example
├── docker-compose.yml
├── main.py
├── requirements.txt
├── scripts/
├── src/
└── README.md
```

## 核心能力

- 用户注册
- 用户登录并签发 JWT
- 基于 Bearer Token 获取当前用户
- 独立 PostgreSQL 库连接
- Docker 镜像构建与 GitHub Actions 自动部署

## 环境变量

优先使用 `DATABASE_URL`：

```bash
DATABASE_URL=postgresql://yibao_user:123456@localhost:5432/yibao-auth
```

如果不提供 `DATABASE_URL`，则读取：

```bash
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

JWT 相关：

```bash
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_EXPIRE_MINUTES
```

服务端口：

```bash
AUTH_SERVICE_PORT
```

## 本地启动

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务：

```bash
./scripts/start_auth_service.sh
```

或：

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8004
```

## Docker

本项目不把 PostgreSQL 装进 `auth-service` 镜像。

本地联调方式：

```bash
cp .env.example .env
docker compose up -d --build
```

如果容器需要连接宿主机 PostgreSQL，运行时需带：

```bash
--add-host host.docker.internal:host-gateway
```

镜像地址：

```text
ghcr.io/yibao-pro/auth-service:latest
```

拉取示例：

```bash
docker pull ghcr.io/yibao-pro/auth-service:latest
```

## GitHub Actions

工作流文件：
- [docker-image.yml](./.github/workflows/docker-image.yml)

当前流程：
- `docker-image`：构建并推送 `ghcr.io/yibao-pro/auth-service:latest`
- `deploy`：GitHub runner 先把镜像打包成 artifact，再通过 SCP 传到目标服务器，服务器 `docker load` 后先启动 candidate 容器做健康检查，再替换正式容器

部署所需 GitHub Secrets：
- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_SSH_KEY`

服务器部署约定：
- 部署目录：`/data/yibao-agent-platform/auth-service`
- 环境文件：`/data/yibao-agent-platform/auth-service/.env`
- 正式容器名：`yibao-auth-service`
- 候选容器名：`yibao-auth-service-candidate`
- 生产端口：`8030`

## 新机器部署

下面是新机器从零部署 `auth-service` 的推荐流程。

### 1. 安装 Docker

确认机器上已经安装 Docker，并且当前用户可以直接执行 `docker`：

```bash
docker --version
docker ps
```

如果当前用户没有权限，需要先把用户加入 `docker` 组，或改用 `sudo docker`。

### 2. 创建部署目录

```bash
sudo mkdir -p /data/yibao-agent-platform/auth-service
sudo chown -R $USER:$USER /data/yibao-agent-platform/auth-service
cd /data/yibao-agent-platform/auth-service
```

### 3. 准备服务器本地 `.env`

先复制模板：

```bash
cp .env.example .env
```

然后修改 `.env`。一个可用示例：

```bash
AUTH_SERVICE_PORT=8030
DATABASE_URL=postgresql://yibao_user:123456@host.docker.internal:5432/yibao-auth
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_DB=yibao-auth
POSTGRES_USER=yibao_user
POSTGRES_PASSWORD=123456
POSTGRES_ADMIN_DB=postgres
JWT_SECRET_KEY=replace-with-your-own-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
INIT_DB_ON_START=false
```

说明：
- 如果数据库和服务在同一台宿主机上，容器访问宿主机数据库时可用 `host.docker.internal`
- Linux 下运行容器时，需要配合 `--add-host host.docker.internal:host-gateway`
- `JWT_SECRET_KEY` 必须替换成你自己的随机密钥
- 生产环境建议直接使用 `DATABASE_URL`，避免多套配置来源

### 4. 拉取镜像

```bash
docker pull ghcr.io/yibao-pro/auth-service:latest
```

### 5. 启动正式容器

```bash
docker run -d \
  --name yibao-auth-service \
  --restart unless-stopped \
  --add-host host.docker.internal:host-gateway \
  --env-file /data/yibao-agent-platform/auth-service/.env \
  -e INIT_DB_ON_START=false \
  -e AUTH_SERVICE_PORT=8030 \
  -p 8030:8030 \
  ghcr.io/yibao-pro/auth-service:latest
```

### 6. 健康检查

```bash
curl --noproxy '*' http://127.0.0.1:8030/healthz
```

期望返回：

```json
{
  "status": "success",
  "service": "auth-service"
}
```

### 7. 查看日志

```bash
docker logs yibao-auth-service --tail 100
```

### 8. 更新镜像

后续手动更新可以直接执行：

```bash
docker pull ghcr.io/yibao-pro/auth-service:latest
docker stop yibao-auth-service
docker rm yibao-auth-service
docker run -d \
  --name yibao-auth-service \
  --restart unless-stopped \
  --add-host host.docker.internal:host-gateway \
  --env-file /data/yibao-agent-platform/auth-service/.env \
  -e INIT_DB_ON_START=false \
  -e AUTH_SERVICE_PORT=8030 \
  -p 8030:8030 \
  ghcr.io/yibao-pro/auth-service:latest
```

### 9. 接入 GitHub Actions 自动部署

如果要让仓库里的 GitHub Actions 接管部署，目标机器需要满足这些条件：

- 机器能被 GitHub Actions 通过 SSH 登录
- 机器本地存在 `/data/yibao-agent-platform/auth-service/.env`
- 机器已安装 Docker

当前 workflow 不再依赖服务器直接访问 `ghcr.io`，也不要求服务器本地必须有 `127.0.0.1:7890` 代理。
镜像会先在 GitHub runner 上构建并推送，然后 runner 再把同一镜像打包传到服务器，服务器只负责 `docker load` 和容器切换。

仓库中需要配置这些 GitHub Secrets：

- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_SSH_KEY`

工作流会在服务器上执行这些动作：

- 接收 GitHub runner 传来的镜像包并执行 `docker load`
- 启动 `yibao-auth-service-candidate`
- 请求 `http://127.0.0.1:18030/healthz`
- 通过后替换正式容器 `yibao-auth-service`

### 10. 常见问题

`curl /healthz` 失败：
- 先看 `docker logs yibao-auth-service`
- 再确认 `.env` 里的数据库地址是否可达

容器连不上宿主机 PostgreSQL：
- 检查 `DATABASE_URL` 是否使用了 `host.docker.internal`
- 检查 `docker run` 是否带了 `--add-host host.docker.internal:host-gateway`

部署时如果镜像同步失败：
- 先看 workflow 里的 `Upload image artifact`、`Copy image archive to server`、`docker load` 哪一步失败
- 当前 deploy 已经不依赖服务器本机直接 `docker pull ghcr.io`

## 接口

- `GET /healthz`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

详细接口文档见：
- [docs/api.md](./docs/api.md)

## 数据库

数据库脚本位于：
- `database/create_database.sql`
- `database/auth_postgres.sql`

其中 `auth_postgres.sql` 是当前服务所需的最小认证表结构，只包含 `users` 表。

## 说明

- 当前服务目录不依赖 `./yibao-pro` 的运行时代码
- 服务器真实 `.env` 仅保留在服务器本地，不提交到仓库
