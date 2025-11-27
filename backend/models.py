from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化SQLAlchemy
db = SQLAlchemy()

class Model(db.Model):
    """模型数据模型（Ollama模型，支持OpenAI接口标准）"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    api_endpoint = db.Column(db.String(255), nullable=False)  # OpenAI兼容的API端点
    api_key = db.Column(db.String(255), nullable=True)  # API密钥（如果需要）
    model_name = db.Column(db.String(100), nullable=False)  # Ollama模型名称
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Model {self.name} ({self.model_name})>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'api_endpoint': self.api_endpoint,
            'model_name': self.model_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Agent(db.Model):
    """智能体数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    status = db.Column(db.String(20), default='inactive')  # inactive, running, paused, stopped
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与Model的关系
    model = db.relationship('Model', backref=db.backref('agents', lazy=True))
    
    def __repr__(self):
        return f'<Agent {self.name} ({self.status})>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_id': self.model_id,
            'model_name': self.model.name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AgentLog(db.Model):
    """智能体日志数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # info, warning, error, debug
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立与Agent的关系
    agent = db.relationship('Agent', backref=db.backref('logs', lazy=True))
    
    def __repr__(self):
        return f'<AgentLog {self.level}: {self.message[:50]}>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

class Conversation(db.Model):
    """对话数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    conversation_id = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与Agent的关系
    agent = db.relationship('Agent', backref=db.backref('conversations', lazy=True))
    
    def __repr__(self):
        return f'<Conversation {self.conversation_id} (Agent: {self.agent.name})>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'conversation_id': self.conversation_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Message(db.Model):
    """消息数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立与Conversation的关系
    conversation = db.relationship('Conversation', backref=db.backref('messages', lazy=True))
    
    def __repr__(self):
        return f'<Message {self.role}: {self.content[:50]}>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class Role(db.Model):
    """角色数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与User的关系
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'users': [user.to_dict() for user in self.users]
        }

class User(db.Model):
    """用户数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
