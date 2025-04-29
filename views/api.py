import logging
import time
import traceback
from flask import Blueprint, jsonify, request
from models import db, User, Account
from auth import token_required, admin_required, generate_token
from account_service import create_account_for_user

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 设置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 用户注册
@api_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': '请提供用户名和密码'
            }), 400
            
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': '用户名已存在'
            }), 400
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            password_hash=User.hash_password(data['password']),
            email=data.get('email'),
            created_at=int(time.time())
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # 生成token
        token = generate_token(new_user.id)
        
        return jsonify({
            'status': 'success',
            'message': '注册成功',
            'user': new_user.to_dict(),
            'token': token
        })
        
    except Exception as e:
        logger.error(f"注册失败: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 用户登录
@api_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': '请提供用户名和密码'
            }), 400
            
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.verify_password(data['password']):
            return jsonify({
                'status': 'error',
                'message': '用户名或密码错误'
            }), 401
            
        # 更新最后登录时间
        user.last_login = int(time.time())
        db.session.commit()
        
        # 生成token
        token = generate_token(user.id)
        
        return jsonify({
            'status': 'success',
            'message': '登录成功',
            'user': user.to_dict(),
            'token': token
        })
        
    except Exception as e:
        logger.error(f"登录失败: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 获取用户信息
@api_bp.route('/user', methods=['GET'])
@token_required
def get_user_info():
    user = request.current_user
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    })

# 退出登录
@api_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # 无需数据库操作，客户端清除token即可
    return jsonify({
        'status': 'success',
        'message': '已成功退出登录'
    })

# 获取一个可用账号 (已登录用户)
@api_bp.route('/account', methods=['GET'])
@token_required
def get_account(current_user):
    try:
        
        result = create_account_for_user(current_user)
        if result.get('status') == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 获取用户的所有账号
@api_bp.route('/accounts', methods=['GET'])
@token_required
def get_user_accounts():
    try:
        user_id = request.current_user.id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询用户的账号 - 只查询明确归属于该用户的账号
        query = Account.query.filter_by(user_id=user_id).order_by(Account.create_time.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        accounts = [account.to_dict() for account in pagination.items]
        
        return jsonify({
            'status': 'success',
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'accounts': accounts
        })
    
    except Exception as e:
        logger.error(f"获取用户账号失败: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 修改账号使用状态
@api_bp.route('/account/<int:account_id>/status', methods=['PUT'])
@token_required
def update_account_status(current_user, account_id):
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
        
        # 检查用户权限
        user = current_user
        
        # 严格检查账号所有权 - 只有明确归属于当前用户或管理员的账号才能修改
        # 不再自动归属无主账号
        if not hasattr(account, 'user_id') or account.user_id is None:
            if user.id == 1:  # 管理员可以处理无主账号
                try:
                    account.user_id = user.id  # 管理员可以认领无主账号
                except:
                    pass  # 如果列不存在，忽略错误
            else:
                return jsonify({
                    'status': 'error',
                    'message': '无权修改此账号'
                }), 403
        elif account.user_id != user.id and user.id != 1:
            return jsonify({
                'status': 'error',
                'message': '无权修改此账号'
                }), 403
            
        # 更新状态
        account.is_used = data['is_used']
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '账号状态已更新',
            'account': account.to_dict()
        })
    
    except Exception as e:
        logger.error(f"更新账号状态失败: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 管理员获取所有账号
@api_bp.route('/admin/accounts', methods=['GET'])
@admin_required
def admin_get_accounts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 计算总页数
        total_accounts = Account.query.count()
        total_pages = (total_accounts + per_page - 1) // per_page
        
        # 获取当前页的账号数据，按照create_time倒序排列
        accounts = Account.query.order_by(Account.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'status': 'success',
            'page': page,
            'per_page': per_page,
            'total': total_accounts,
            'total_pages': total_pages,
            'accounts': [account.to_dict() for account in accounts.items]
        })
    
    except Exception as e:
        logger.error(f"管理员获取所有账号失败: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 管理员获取所有用户
@api_bp.route('/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询用户
        query = User.query.order_by(User.id)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'status': 'success',
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'users': users
        })
    
    except Exception as e:
        logger.error(f"管理员获取所有用户失败: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 健康检查
@api_bp.route('/health', methods=['GET'])
def health_check():
    from datetime import datetime
    return jsonify({'status': 'ok', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}), 200

@api_bp.route('/user/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    try:
        # 记录调试信息
        logger.info(f"更新用户请求 - 当前用户ID: {current_user.id}")
        
        # 检查权限
        if current_user.id != user_id and not current_user.is_admin:
            logger.warning(f"权限不足 - 当前用户ID: {current_user.id}, 目标用户ID: {user_id}")
            return jsonify({
                'status': 'error',
                'message': '无权修改其他用户信息'
            }), 403

        # 获取请求数据
        data = request.json
        if not data:
            logger.warning("缺少更新数据")
            return jsonify({
                'status': 'error',
                'message': '缺少更新数据'
            }), 400

        # 查找用户
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"用户不存在 - 用户ID: {user_id}")
            return jsonify({
                'status': 'error',
                'message': '用户不存在'
            }), 404

        # 更新用户信息
        if 'username' in data:
            user.username = data['username']
        if 'domain' in data:
            user.domain = data['domain']
        if 'temp_email_address' in data:
            user.temp_email_address = data['temp_email_address']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = User.hash_password(data['password'])

        db.session.commit()
        logger.info(f"用户信息更新成功 - 用户ID: {user_id}")

        return jsonify({
            'status': 'success',
            'message': '用户信息更新成功',
            'user': user.to_dict()
        })

    except Exception as e:
        logger.error(f"更新用户信息失败: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 