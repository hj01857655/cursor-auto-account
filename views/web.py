from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request
import jwt
from models import User, Account
import auth
from auth import token_required

# 创建蓝图
web_bp = Blueprint('web', __name__)

# 前端页面 - 登录页面
@web_bp.route('/login', methods=['GET'])
def login_page():
    # 检查是否已登录
    token = request.cookies.get('token')
    if token:
        try:
            # 使用auth模块的SECRET_KEY
            # 验证token
            payload = jwt.decode(token, auth.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = User.query.get(user_id)
            if user:
                return redirect(url_for('web.index'))
        except:
            pass  # Token无效或过期，继续显示登录页
    
    return render_template('login.html')

# 前端页面 - 查看账号列表
@web_bp.route('/', methods=['GET'])
def index():
    # 检查是否已登录
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('web.login_page'))
    
    try:
        # 验证token
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return redirect(url_for('web.login_page'))
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 根据用户权限获取账号列表
        if current_user.id == 1:  # 管理员可以看到所有账号
            total_accounts = Account.query.count()
            accounts = Account.query.order_by(Account.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        else:  # 普通用户只能看到自己的账号
            total_accounts = Account.query.filter(Account.user_id == current_user.id).count()
            accounts = Account.query.filter(Account.user_id == current_user.id).order_by(Account.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        total_pages = max(1, (total_accounts + per_page - 1) // per_page) if total_accounts > 0 else 1
        
        return render_template(
            'index.html', 
            accounts=[account.to_dict() for account in accounts.items] if hasattr(accounts, 'items') else [], 
            now=datetime.now(),
            current_page=page,
            total_pages=total_pages,
            per_page=per_page,
            total_accounts=total_accounts,
            current_user=current_user,
            is_admin=(current_user.id == 1)
        )
        
    except Exception as e:
        print(f"索引页错误: {e}")
        return redirect(url_for('web.login_page'))