# Auth Service gRPC API

服务名：

```text
auth.v1.AuthService
```

公共约定：

- 成功响应包含 `status: "success"`
- 成功响应都会带 `request_id`
- 认证方式为在 `Me` 请求体里传 `token`
- 失败通过 gRPC status code 返回，不再使用 HTTP 状态码

## Healthz

RPC：

```text
Healthz(HealthzRequest) returns (HealthzResponse)
```

成功响应字段：

- `status`
- `request_id`
- `service`
- `port`
- `message`

## Register

RPC：

```text
Register(RegisterRequest) returns (AuthResponse)
```

请求字段：

- `username`: 1 到 64 个字符
- `password`: 6 到 128 个字符

成功响应字段：

- `status`
- `request_id`
- `user_id`

失败时常见 gRPC code：

- `ALREADY_EXISTS`: 用户名已存在
- `INVALID_ARGUMENT`: 请求字段校验失败

## Login

RPC：

```text
Login(LoginRequest) returns (AuthResponse)
```

请求字段：

- `username`
- `password`

成功响应字段：

- `status`
- `request_id`
- `token`
- `user_id`
- `username`

失败时常见 gRPC code：

- `UNAUTHENTICATED`: 用户名或密码错误
- `INVALID_ARGUMENT`: 请求字段校验失败

## Me

RPC：

```text
Me(MeRequest) returns (MeResponse)
```

请求字段：

- `token`

成功响应字段：

- `status`
- `request_id`
- `user_id`
- `username`

失败时常见 gRPC code：

- `UNAUTHENTICATED`: token 缺失、非法或载荷不完整
- `INVALID_ARGUMENT`: token 字段为空
