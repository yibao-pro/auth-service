# Auth Service

一个独立部署的认证服务，基于 `FastAPI + PostgreSQL + JWT` 实现。

## 目录结构

```text
auth-service/
├── api/
│   └── app.py
├── src/
│   ├── auth_jwt.py
│   ├── db.py
│   ├── errors.py
│   ├── logging.py
│   ├── repo.py
│   ├── routes.py
│   ├── schemas.py
│   ├── service.py
│   └── settings.py
├── test/
├── requirements.txt
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

服务默认直接连接独立的认证数据库，不依赖 `yibao-pro` 的 `.env`：

```bash
export VOICE_APP_POSTGRES_HOST=localhost
export VOICE_APP_POSTGRES_PORT=5432
export VOICE_APP_POSTGRES_USER=yibao_user
export VOICE_APP_POSTGRES_PASSWORD=123456
export VOICE_APP_POSTGRES_DB=yibao-auth
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
