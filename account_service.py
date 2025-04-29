import time
from sqlalchemy import text
import register as account_register
from models import db, Account

# 为用户创建账号
def create_account_for_user(current_user):
    try:
        # 生成随机名字和账号信息
        email_generator = account_register.EmailGenerator(domain=current_user.domain)
        account_info = email_generator.get_account_info()
        
        # 从返回的字典中获取信息
        email = account_info["email"]
        password = account_info["password"]
        first_name = account_info["first_name"]
        last_name = account_info["last_name"]
        
        # 检查邮箱是否已存在
        existing_account = Account.query.filter_by(email=email).first()
        if existing_account:
            return {'status': 'error', 'message': '该邮箱已被使用，请重试'}
        
        # 注册账号
        registration = account_register.Register(first_name, last_name, email, password,current_user.temp_email_address)
        success = registration.register()
        
        if not success:
            return {'status': 'error', 'message': '注册失败，请稍后再试'}
        
        # 计算过期时间 (15天后)
        create_time = int(time.time())
        expire_time = create_time + (15 * 24 * 60 * 60)
        
        # 创建账号对象
        account = Account(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            create_time=create_time,
            expire_time=expire_time,
            user_id=current_user.id,
            is_used=0  # 标记为已使用
        )
        
        db.session.add(account)
        db.session.commit()
        return {
            'status': 'success',
            'message': '新账号已创建',
            'account': account.to_dict()
        }
    
    except Exception as e:
        return {'status': 'error', 'message': str(e)} 