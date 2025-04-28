# Cursor 账号管理系统

这是一个用于管理 Cursor 账号的 Web 服务，支持自动注册、存储账号信息、查看和修改账号状态。

## 功能特点

- 自动注册 Cursor 账号并存储到 MySQL 数据库
- 提供 RESTful API 用于获取账号
- 提供 Web 页面用于查看和管理所有账号
- 支持点击复制账号信息
- 支持修改账号使用状态
- Docker 容器化部署

## 快速开始

### 使用 Docker Compose 部署（推荐）

1. 克隆仓库
```bash
git clone https://github.com/yourusername/cursor-auto-account.git
cd cursor-auto-account
```

2. 修改 Caddyfile 中的域名（如果需要）
```
# 修改 Caddyfile 中的域名
vim Caddyfile
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问服务
   - 网页界面: http://localhost:8080
   - API接口: http://localhost:8080/api/account

### 手动部署

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 修改数据库配置（如果需要）
```python
# 在 app.py 中修改以下配置
DB_HOST = '47.109.39.201'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'f4N:1!GRbb]UtdGeP:rP'
DB_NAME = 'cursor_accounts'
```

3. 运行服务
```bash
python app.py
```

## API 文档

### 获取账号

```
GET /api/account
```

响应示例:
```json
{
  "status": "success",
  "message": "找到可用账号",
  "account": {
    "id": 1,
    "email": "example@zoowayss.top",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "create_time": 1678901234,
    "expire_time": 1681579634,
    "is_used": 1,
    "expire_time_fmt": "2023-04-15 12:00:34"
  }
}
```

### 添加账号

```
POST /api/account
Content-Type: application/json

{
  "email": "example@zoowayss.top",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "is_used": 0
}
```

### 修改账号状态

```
PUT /api/account/{id}/status
Content-Type: application/json

{
  "is_used": 0
}
```

## 部署注意事项

1. **安全性**：
   - 确保数据库凭据安全
   - 配置防火墙限制数据库端口访问
   - 使用 HTTPS 保护 Web 服务

2. **资源要求**：
   - Chrome 浏览器（用于账号注册）
   - MySQL 数据库
   - 至少 1GB 内存

3. **数据备份**：
   - 定期备份 MySQL 数据

## 许可证

MIT 