import time
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    last_login = Column(BigInteger, nullable=True)
    
    # 关联用户的账号
    accounts = relationship("Account", back_populates="user")
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'last_login': self.last_login
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
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 关联到用户
    
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
            'expire_time_fmt': datetime.fromtimestamp(self.expire_time).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 安全地添加user_id，如果有这个属性
        try:
            data['user_id'] = self.user_id
        except:
            data['user_id'] = None
            
        return data 