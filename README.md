# Cursor 账号管理系统

本项目是站在巨人的肩膀上开发。 [源项目地址](https://github.com/chengazhen/cursor-auto-free) [参考项目](https://github.com/yeongpin/cursor-free-vip)

项目刚上线，还有很多bug 慢慢填吧

这是一个用于管理 Cursor 账号的 Web 服务，支持自动注册、存储账号信息、查看和修改账号状态。

[预览站点](https://cursor-account.zoowayss.top)

资源有限，请勿滥用账号

![img.png](./.assets/image.png)

## 如何使用

点击获取账号，这部分过程会很慢，请耐心等待，请勿多次点击获取账号，服务器资源有限请谅解。获取完会弹窗，复制即可
![img.png](./.assets/image-1745820621145.png)
拿到账号密码，到自己的浏览器登录，[到这里](https://tempmail.plus/en/#!) 获取验证码

需要改一下名称 , 代码改了一下 现在填  fuckcursor

![image-20250428115252533](./.assets/image-20250428115252533.png)

## 功能特点

- 自动注册 Cursor 账号并存储到 MySQL 数据库
- 提供 RESTful API 用于获取账号
- 提供 Web 页面用于查看和管理所有账号
- 支持点击复制账号信息
- 支持修改账号使用状态
- Docker 容器化部署

## 目前存在的问题

1. 同一个域名，账号注册过多会导致全部账号实效。这里后续会使用用户提供的域名，自己用自己的域名。

   没有域名怎么办  [看这里](https://linux.do/t/topic/26864) ，目前自测 [eu.org](http://eu.org/) 是可以的

   有了域名，还需要配置 cf 邮箱转发

## 快速开始

### 使用 Docker Compose 部署（推荐）

1. 克隆仓库
```bash
git clone https://github.com/yourusername/cursor-auto-account.git
cd cursor-auto-account
```

2. 启动项目
```
uv pip install -r requirements.txt
python app.py
```


4. 访问服务
   - 网页界面: http://localhost:8081

## 免责声明

1. 本项目仅供学习和技术研究使用，不得用于商业目的
2. 使用本项目产生的任何法律责任由使用者自行承担
3. 本项目不保证所创建账号的长期可用性，Cursor官方政策变更可能导致功能失效
4. 请遵守Cursor的服务条款，合理使用生成的账号
5. 项目维护者不对使用本工具导致的任何问题负责
## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=zoowayss/cursor-auto-account&type=Date)](https://www.star-history.com/#zoowayss/cursor-auto-account&Date)
## 许可证

MIT 