# Auth Service

一个独立部署的认证服务，基于 `FastAPI + PostgreSQL + JWT` 实现。

## 目录结构

```text
auth-service/
├── api/
├── scripts/
├── requirements.txt
├── main.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .workflow/
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
export VOICE_APP_POSTGRES_HOST=localhost
export VOICE_APP_POSTGRES_PORT=5432
export VOICE_APP_POSTGRES_USER=yibao_user
export VOICE_APP_POSTGRES_PASSWORD=123456
export VOICE_APP_POSTGRES_DB=yibao_auth
```

JWT 配置：

```bash
export VOICE_APP_JWT_SECRET_KEY=dev-secret-change-me
export VOICE_APP_JWT_ALGORITHM=HS256
export VOICE_APP_JWT_EXPIRE_MINUTES=60
```

服务端口：

```bash
export VOICE_APP_AUTH_SERVICE_PORT=8004
```

## 启动服务

在服务根目录执行：

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8004
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
docker compose up --build
```

默认暴露：

- `auth-service`: `8004`
- `postgres`: `5432`

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
