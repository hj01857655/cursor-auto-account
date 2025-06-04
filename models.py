from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 用户模型
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    last_login = Column(BigInteger, nullable=True)
    domain = Column(String(255), default='zoowayss.top')
    temp_email_address = Column(String(255), default='zoowayss@mailto.plus',nullable=True)

    # 关联用户的账号
    accounts = relationship("Account", back_populates="user")
    # 
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'domain': self.domain,
            'temp_email_address': self.temp_email_address
        }

    @staticmethod
    def hash_password(password):
        import hashlib
        # 简单哈希密码，生产环境应使用更安全的方法如bcrypt
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self.password_hash == User.hash_password(password)

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
    is_deleted = Column(Integer, default=0)  # 0: 未删除, 1: 已删除
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 关联到用户

    # 新增字段
    accessToken = Column(String(255), nullable=True)  # 访问令牌
    usage = Column(Integer, default=0)  # 使用量
    days = Column(Integer, default=0)  # 天数
    usage_limit = Column(String(50), default=None)  # 使用限制
    account_type = Column(String(20), default='free')  # 账号类型: free, pro, etc.
    status = Column(String(20), default='active')  # 状态: active, inactive, banned, etc.
    workos_session_token = Column(String(1000), nullable=True)  # WorkosCursorSessionToken

    # 关联用户
    user = relationship("User", back_populates="accounts")

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'create_time': self.create_time,
            'expire_time': self.expire_time,
            'is_used': self.is_used,
            'is_deleted': self.is_deleted,
            'expire_time_fmt': datetime.fromtimestamp(self.expire_time).strftime('%Y-%m-%d %H:%M:%S'),
            # 新增字段
            'accessToken': self.accessToken,
            'usage': self.usage,
            'days': self.days,
            'usage_limit': self.usage_limit,
            'account_type': self.account_type,
            'status': self.status,
            'workos_session_token': self.workos_session_token
        }

        # 安全地添加user_id，如果有这个属性
        try:
            data['user_id'] = self.user_id
        except:
            data['user_id'] = None

        return data