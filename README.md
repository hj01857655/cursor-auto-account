# Cursor 账号管理系统

本项目是站在巨人的肩膀上开发。 [源项目地址](https://github.com/chengazhen/cursor-auto-free) [参考项目](https://github.com/yeongpin/cursor-free-vip)

项目刚上线，还有很多bug 慢慢填吧

这是一个用于管理 Cursor 账号的 Web 服务，支持自动注册、存储账号信息、查看和修改账号状态。

拿到账号密码，到自己的浏览器登录，[到这里](https://tempmail.plus/en/#!) 获取验证码

[预览站点](https://cursor-account.zoowayss.top)

资源有限，请勿滥用账号

![img.png](./.assets/image.png)

## 如何使用

点击获取账号，这部分过程会很慢，请耐心等待，请勿多次点击获取账号，服务器资源有限请谅解。获取完会弹窗，复制即可
拿到账号密码，到自己的浏览器登录，[到这里](https://tempmail.plus/en/#!) 获取验证码

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

### 修改账号状态

```
PUT /api/account/{id}/status
Content-Type: application/json

{
  "is_used": 0
}
```

## 部署注意事项

1. **环境要求**:
   - 需要 Chrome 浏览器（用于自动注册账号）
   - MySQL 数据库
   - Docker 和 Docker Compose（推荐部署方式）

2. **数据库配置**:
   - 默认使用环境变量配置数据库连接
   - 可在 docker-compose.yml 中修改数据库配置

## 免责声明

1. 本项目仅供学习和技术研究使用，不得用于商业目的
2. 使用本项目产生的任何法律责任由使用者自行承担
3. 本项目不保证所创建账号的长期可用性，Cursor官方政策变更可能导致功能失效
4. 请遵守Cursor的服务条款，合理使用生成的账号
5. 项目维护者不对使用本工具导致的任何问题负责

## 许可证

MIT 