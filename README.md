# Auth Service

一个独立部署的认证服务，基于 `FastAPI + PostgreSQL + JWT` 实现。

## 目录结构

```text
auth-service/
├── api/
├── .github/workflows/
├── scripts/
├── requirements.txt
├── main.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── src/
├── database/
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

服务默认不依赖 `yibao-pro`，并且优先通过 `DATABASE_URL` 连接数据库：

```bash
export DATABASE_URL=postgresql://yibao_user:123456@localhost:5432/yibao_auth
```

如果不提供 `DATABASE_URL`，才会回退到以下拆分参数：

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=yibao_user
export POSTGRES_PASSWORD=123456
export POSTGRES_DB=yibao_auth
```

JWT 配置：

```bash
export JWT_SECRET_KEY=dev-secret-change-me
export JWT_ALGORITHM=HS256
export JWT_EXPIRE_MINUTES=60
```

服务端口：

```bash
export AUTH_SERVICE_PORT=8004
```

## 启动服务

在服务根目录执行：

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8004
```

或使用启动脚本：

```bash
./scripts/start_auth_service.sh
```

## Docker

不把 PostgreSQL 装进 `auth-service` 镜像。

- `auth-service` 是一个容器
- `postgres` 是另一个容器
- `docker-compose` 负责网络和环境变量注入
- `auth-service` 通过 `DATABASE_URL` 连接 `postgres`

使用方式：

```bash
cp .env.example .env
docker compose up -d --build
```

默认暴露：

- `auth-service`: `8004`
- `postgres`: `5432`

## 镜像

GitHub Actions 会构建并推送镜像到：

```text
ghcr.io/yibao-pro/auth-service:latest
```

手动拉取示例：

```bash
docker pull ghcr.io/yibao-pro/auth-service:latest
```

单独运行容器时，服务默认监听容器内 `8004` 端口：

```bash
docker run -d \
  --name auth-service \
  --env-file .env \
  -p 8004:8004 \
  ghcr.io/yibao-pro/auth-service:latest
```

如果部署环境希望服务监听 `8030`，可以覆盖端口环境变量：

```bash
docker run -d \
  --name auth-service \
  --env-file .env \
  -e AUTH_SERVICE_PORT=8030 \
  -p 8030:8030 \
  ghcr.io/yibao-pro/auth-service:latest
```

## GitHub Actions

仓库使用 GitHub Actions 工作流 [docker-image.yml](./.github/workflows/docker-image.yml)：

- `docker-image`：构建并推送 `ghcr.io/yibao-pro/auth-service:latest`
- `deploy`：通过 SSH 登录服务器，先启动 candidate 容器做健康检查，再替换正式容器

部署任务依赖以下 GitHub Secrets：

- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_SSH_KEY`

服务器部署脚本约定：

- 部署目录：`/data/yibao-agent-platform/auth-service`
- 环境文件：`/data/yibao-agent-platform/auth-service/.env`
- 正式容器名：`yibao-auth-service`
- 候选容器名：`yibao-auth-service-candidate`
- 生产端口：`8030`

## 接口

- `GET /healthz`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

## 说明

当前服务目录已经不再依赖 `./yibao-pro` 的运行时代码或它的环境变量文件。

数据库初始化 SQL 位于：

- `database/create_database.sql`
- `database/auth_postgres.sql`

其中 `auth_postgres.sql` 是从旧项目拆出来的最小认证表结构，目前只包含 `users` 表。
