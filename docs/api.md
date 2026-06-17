# Auth Service API

Base URL:

```text
/auth
```

公共约定：

- 成功响应包含 `status: "success"`
- 错误响应包含 `status: "error"`
- 响应内都会带 `request_id`
- 认证方式为 `Authorization: Bearer <token>`

## Health Check

`GET /healthz`

说明：
- 服务健康检查

成功响应示例：

```json
{
  "status": "success",
  "request_id": "34a52f04a1af46eba24e06765a8dafab",
  "service": "auth-service",
  "port": 8030,
  "message": "ok"
}
```

## Register

`POST /auth/register`

请求体：

```json
{
  "username": "alice",
  "password": "secret123"
}
```

字段约束：

- `username`: 1 到 64 个字符
- `password`: 6 到 128 个字符

成功响应：

```json
{
  "status": "success",
  "request_id": "f8b61b6b9d8f4f9c9b6454d9c52c3b11",
  "user_id": "3c889fe7-63f7-495d-84ba-778bdfa38dc3",
  "token": null,
  "username": null
}
```

失败状态码：

- `409`: 用户名已存在
- `422`: 请求体校验失败

错误响应示例：

```json
{
  "status": "error",
  "request_id": "8c7c68b5bb2f49d1a38eb0d8e2bdc38b",
  "message": "username already exists"
}
```

## Login

`POST /auth/login`

请求体：

```json
{
  "username": "alice",
  "password": "secret123"
}
```

成功响应：

```json
{
  "status": "success",
  "request_id": "523f5a650d1147d8b4ea9211f47bf442",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "3c889fe7-63f7-495d-84ba-778bdfa38dc3",
  "username": "alice"
}
```

失败状态码：

- `401`: 用户名或密码错误
- `422`: 请求体校验失败

错误响应示例：

```json
{
  "status": "error",
  "request_id": "b8b8c26a2fe14278a2e25e0dcb2ea54f",
  "message": "invalid credentials"
}
```

## Current User

`GET /auth/me`

请求头：

```text
Authorization: Bearer <token>
```

成功响应：

```json
{
  "status": "success",
  "request_id": "5b4b6b0bf2ec4048a8d65c9469141d6d",
  "user_id": "3c889fe7-63f7-495d-84ba-778bdfa38dc3",
  "username": "alice"
}
```

失败状态码：

- `401`: 缺少 token
- `401`: token 非法
- `401`: token 载荷缺失必要字段

典型错误响应：

```json
{
  "detail": "missing token"
}
```

或：

```json
{
  "detail": "invalid token"
}
```

## Validation Error

当请求体不满足约束时，服务返回 `422`：

```json
{
  "status": "error",
  "request_id": "7c99af74db5a42aa94d69d7b0fc1f1f7",
  "message": "password: String should have at least 6 characters",
  "errors": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 6 characters",
      "input": "123",
      "ctx": {
        "min_length": 6
      }
    }
  ]
}
```
