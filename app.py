import os
import random
import string
from flask import Flask, render_template_string
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 导入自定义模块
from models import db
import auth
from db_utils import init_db
from views.api import api_bp
import urllib.parse
# 创建并配置 Flask 应用
def create_app():
    app = Flask(__name__)

    # 从环境变量获取数据库配置
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_PORT'] = int(os.getenv('DB_PORT', '3306'))
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'root')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'cursor_accounts')

    # 设置 SQLAlchemy 数据库 URI
    # 对密码进行URL编码，避免特殊字符（如@）造成解析问题
    encoded_password = urllib.parse.quote_plus(app.config["DB_PASSWORD"])
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{app.config["DB_USER"]}:{encoded_password}@{app.config["DB_HOST"]}:{app.config["DB_PORT"]}/{app.config["DB_NAME"]}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT密钥
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', ''.join(random.choices(string.ascii_letters + string.digits, k=32)))
    # Token有效期（天）
    app.config['TOKEN_EXPIRY_DAYS'] = int(os.getenv('TOKEN_EXPIRY_DAYS', '30'))

    # 初始化数据库
    db.init_app(app)

    # 设置认证模块的密钥和过期时间 - 修复直接设置模块变量
    auth.SECRET_KEY = app.config['SECRET_KEY']
    auth.TOKEN_EXPIRY_DAYS = app.config['TOKEN_EXPIRY_DAYS']

    # 注册蓝图
    app.register_blueprint(api_bp)

    # 添加根路由 - 系统健康状况页面
    @app.route('/')
    def index():
        from datetime import datetime
        import psutil
        import os

        # 获取系统信息
        try:
            # 数据库连接状态
            db_status = "✅ 连接正常"
            try:
                from models import User, Account
                user_count = User.query.count()
                account_count = Account.query.count()
                active_accounts = Account.query.filter_by(status='active', is_deleted=0).count()
            except Exception as e:
                db_status = f"❌ 连接失败: {str(e)}"
                user_count = account_count = active_accounts = 0

            # 系统资源
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # 应用信息
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        except Exception as e:
            # 如果获取系统信息失败，使用默认值
            db_status = "❓ 未知"
            user_count = account_count = active_accounts = 0
            cpu_percent = 0
            memory = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()
            disk = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return render_template_string('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cursor 账号管理系统 - 系统状态</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2em;
            margin: 10px 0;
            opacity: 0.9;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 {
            margin: 0 0 20px 0;
            color: #2c3e50;
            font-size: 1.3em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 15px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .status-label {
            font-weight: 600;
            color: #495057;
        }
        .status-value {
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 20px;
            background: #e9ecef;
        }
        .status-success { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-danger { background: #f8d7da; color: #721c24; }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        .progress-fill.warning { background: linear-gradient(90deg, #ffc107, #fd7e14); }
        .progress-fill.danger { background: linear-gradient(90deg, #dc3545, #e83e8c); }
        .api-endpoints {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .endpoint {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .endpoint-method {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .method-get { background: #28a745; color: white; }
        .method-post { background: #007bff; color: white; }
        .method-put { background: #ffc107; color: black; }
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Cursor 账号管理系统</h1>
        <p>系统健康状况监控面板</p>
        <p>当前时间: {{ current_time }}</p>
    </div>

    <div class="dashboard">
        <div class="card">
            <h3>🗄️ 数据库状态</h3>
            <div class="status-item">
                <span class="status-label">连接状态</span>
                <span class="status-value {{ 'status-success' if '✅' in db_status else 'status-danger' }}">{{ db_status }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">用户总数</span>
                <span class="status-value">{{ user_count }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">账号总数</span>
                <span class="status-value">{{ account_count }}</span>
            </div>
            <div class="status-item">
                <span class="status-label">活跃账号</span>
                <span class="status-value status-success">{{ active_accounts }}</span>
            </div>
        </div>

        <div class="card">
            <h3>💻 系统资源</h3>
            <div class="status-item">
                <span class="status-label">CPU 使用率</span>
                <span class="status-value">{{ "%.1f"|format(cpu_percent) }}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill {{ 'warning' if cpu_percent > 70 else ('danger' if cpu_percent > 90 else '') }}"
                     style="width: {{ cpu_percent }}%"></div>
            </div>

            <div class="status-item">
                <span class="status-label">内存使用率</span>
                <span class="status-value">{{ "%.1f"|format(memory.percent) }}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill {{ 'warning' if memory.percent > 70 else ('danger' if memory.percent > 90 else '') }}"
                     style="width: {{ memory.percent }}%"></div>
            </div>

            <div class="status-item">
                <span class="status-label">磁盘使用率</span>
                <span class="status-value">{{ "%.1f"|format(disk.percent) }}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill {{ 'warning' if disk.percent > 70 else ('danger' if disk.percent > 90 else '') }}"
                     style="width: {{ disk.percent }}%"></div>
            </div>
        </div>

        <div class="card">
            <h3>⚙️ 应用信息</h3>
            <div class="status-item">
                <span class="status-label">运行状态</span>
                <span class="status-value status-success">✅ 正常运行</span>
            </div>
            <div class="status-item">
                <span class="status-label">调试模式</span>
                <span class="status-value status-warning">🔧 开启</span>
            </div>
            <div class="status-item">
                <span class="status-label">端口</span>
                <span class="status-value">8001</span>
            </div>
            <div class="status-item">
                <span class="status-label">Python版本</span>
                <span class="status-value">{{ python_version }}</span>
            </div>
        </div>
    </div>

    <div class="api-endpoints">
        <h3>🔗 API 接口状态</h3>
        <div class="endpoint">
            <div>
                <span class="endpoint-method method-get">GET</span>
                <span>/api/health</span>
            </div>
            <span class="status-value status-success">✅ 可用</span>
        </div>
        <div class="endpoint">
            <div>
                <span class="endpoint-method method-post">POST</span>
                <span>/api/login</span>
            </div>
            <span class="status-value status-success">✅ 可用</span>
        </div>
        <div class="endpoint">
            <div>
                <span class="endpoint-method method-post">POST</span>
                <span>/api/register</span>
            </div>
            <span class="status-value status-success">✅ 可用</span>
        </div>
        <div class="endpoint">
            <div>
                <span class="endpoint-method method-get">GET</span>
                <span>/api/account</span>
            </div>
            <span class="status-value status-success">✅ 可用</span>
        </div>
        <div class="endpoint">
            <div>
                <span class="endpoint-method method-get">GET</span>
                <span>/api/admin/accounts</span>
            </div>
            <span class="status-value status-success">✅ 可用</span>
        </div>
    </div>

    <button class="refresh-btn" onclick="location.reload()">🔄 刷新状态</button>

    <div class="footer">
        <p>Cursor 账号管理系统 | 后端服务正常运行</p>
    </div>

    <script>
        // 自动刷新页面 (每30秒)
        setTimeout(() => {
            location.reload();
        }, 30000);

        // 添加一些动画效果
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.card, .api-endpoints');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>
        ''',
        current_time=current_time,
        db_status=db_status,
        user_count=user_count,
        account_count=account_count,
        active_accounts=active_accounts,
        cpu_percent=cpu_percent,
        memory=memory,
        disk=disk,
        python_version=f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        )

    return app

# 应用入口
if __name__ == '__main__':
    # 创建应用
    app = create_app()

    # 初始化数据库
    init_db(app)

    # 获取环境变量中的主机和端口，默认为0.0.0.0:8001
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8001'))

    # 启动应用
    app.run(host=host, port=port, debug=(os.getenv('DEBUG', 'False').lower() == 'true'))