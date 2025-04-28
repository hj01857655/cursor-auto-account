import os
import time
import random
import string
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, BigInteger, text
from sqlalchemy import create_engine
import register as account_register

# 初始化 Flask 应用
app = Flask(__name__)

# 配置数据库连接
DB_HOST = '47.109.39.201'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'f4N:1!GRbb]UtdGeP:rP'
DB_NAME = 'cursor_accounts'

# 设置 SQLAlchemy 数据库 URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 添加Jinja2过滤器 - 时间戳转日期
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    if not timestamp:
        return ""
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

# 定义账号模型
class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    create_time = Column(BigInteger, nullable=False)
    expire_time = Column(BigInteger, nullable=False)
    is_used = Column(Integer, default=0)  # 0: 未使用, 1: 已使用
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'create_time': self.create_time,
            'expire_time': self.expire_time,
            'is_used': self.is_used,
            'expire_time_fmt': datetime.fromtimestamp(self.expire_time).strftime('%Y-%m-%d %H:%M:%S')
        }

# 创建数据库和表
def init_db():
    with app.app_context():
        # 尝试创建数据库
        engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/')
        try:
            with engine.connect() as conn:
                conn.execute(text(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}'))
                conn.commit()
        except Exception as e:
            print(f"创建数据库时出错: {e}")
        
        # 创建表
        db.create_all()

# 生成随机密码
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choice(chars) for _ in range(length))

# 获取一个可用账号
@app.route('/api/account', methods=['GET'])
def get_account():
    try:
        # 查询是否有未使用的账号
        account = Account.query.filter_by(is_used=0).first()
        
        # 如果没有可用账号，生成一个新账号
        if not account:
            # 生成随机名字和账号信息
            email_generator = account_register.EmailGenerator()
            account_info = email_generator.get_account_info()
            
            # 从返回的字典中获取信息
            email = account_info["email"]
            password = account_info["password"]
            first_name = account_info["first_name"]
            last_name = account_info["last_name"]
            
            # 注册账号
            registration = account_register.Register(first_name, last_name, email, password)
            success = registration.register()
            
            if not success:
                return jsonify({'status': 'error', 'message': '注册失败，请稍后再试'}), 500
            
            # 计算过期时间 (30天后)
            create_time = int(time.time())
            expire_time = create_time + (15 * 24 * 60 * 60)
            
            # 保存到数据库
            account = Account(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                create_time=create_time,
                expire_time=expire_time,
                is_used=0  # 标记为已使用
            )
            db.session.add(account)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': '新账号已创建',
                'account': account.to_dict()
            })
        
        # 标记账号为已使用
        account.is_used = 1
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '找到可用账号',
            'account': account.to_dict()
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 手动添加账号
@app.route('/api/account', methods=['POST'])
def add_account():
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': '请提供有效的邮箱和密码'
            }), 400
        
        # 检查账号是否已存在
        existing_account = Account.query.filter_by(email=data['email']).first()
        if existing_account:
            return jsonify({
                'status': 'error',
                'message': '该邮箱已存在'
            }), 400
        
        # 计算创建时间和过期时间
        create_time = int(time.time())
        expire_time = data.get('expire_time')
        if not expire_time:
            # 默认30天后过期
            expire_time = create_time + (30 * 24 * 60 * 60)
        
        # 创建新账号
        account = Account(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            create_time=create_time,
            expire_time=expire_time,
            is_used=data.get('is_used', 0)
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '账号添加成功',
            'account': account.to_dict()
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 前端页面 - 查看账号列表
@app.route('/', methods=['GET'])
def index():
    accounts = Account.query.all()
    return render_template('index.html', accounts=[account.to_dict() for account in accounts], now=datetime.now())

# 修改账号使用状态
@app.route('/api/account/<int:account_id>/status', methods=['PUT'])
def update_account_status(account_id):
    try:
        # 获取请求数据
        data = request.json
        if data is None or 'is_used' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数'
            }), 400
            
        # 查找账号
        account = Account.query.get(account_id)
        if not account:
            return jsonify({
                'status': 'error',
                'message': f'账号 ID {account_id} 不存在'
            }), 404
            
        # 更新状态
        account.is_used = data['is_used']
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '账号状态已更新',
            'account': account.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 初始化应用
if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    # 初始化数据库
    init_db()
    
    # 启动应用
    app.run(host='0.0.0.0', port=8000, debug=True) 