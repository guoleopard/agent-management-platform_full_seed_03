from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from models import db, Agent, AgentLog, Model, Conversation, Message
import os
import requests
import uuid
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
# 优先使用环境变量中的MySQL配置，否则使用SQLite
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
if DB_TYPE == 'mysql':
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'agent_management')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()

# 初始化Flask-RESTX API
api = Api(
    app,
    version='1.0',
    title='Agent Management Platform API',
    description='智能体管理平台API文档',
    doc='/docs',  # Swagger UI文档路径
    prefix='/api'  # API前缀
)

# 创建命名空间
model_ns = api.namespace('models', description='模型管理API')
agent_ns = api.namespace('agents', description='智能体管理API')
chat_ns = api.namespace('chat', description='智能体会话API')
log_ns = api.namespace('logs', description='日志管理API')

# 定义数据模型
model_model = api.model('Model', {
    'id': fields.Integer(readonly=True, description='模型ID'),
    'name': fields.String(required=True, description='模型名称'),
    'description': fields.String(description='模型描述'),
    'api_endpoint': fields.String(required=True, description='API端点'),
    'model_name': fields.String(required=True, description='模型名称'),
    'status': fields.String(description='模型状态', enum=['active', 'inactive']),
    'created_at': fields.String(readonly=True, description='创建时间'),
    'updated_at': fields.String(readonly=True, description='更新时间')
})

agent_model = api.model('Agent', {
    'id': fields.Integer(readonly=True, description='智能体ID'),
    'name': fields.String(required=True, description='智能体名称'),
    'description': fields.String(description='智能体描述'),
    'model_id': fields.Integer(required=True, description='模型ID'),
    'model_name': fields.String(readonly=True, description='模型名称'),
    'status': fields.String(description='智能体状态', enum=['inactive', 'running', 'paused', 'stopped']),
    'created_at': fields.String(readonly=True, description='创建时间'),
    'updated_at': fields.String(readonly=True, description='更新时间')
})

chat_model = api.model('Chat', {
    'message': fields.String(required=True, description='用户消息'),
    'conversation_id': fields.String(description='对话ID')
})

chat_response_model = api.model('ChatResponse', {
    'message': fields.String(description='响应消息'),
    'conversation_id': fields.String(description='对话ID'),
    'response': fields.String(description='智能体响应')
})

conversation_model = api.model('Conversation', {
    'id': fields.Integer(readonly=True, description='对话ID'),
    'agent_id': fields.Integer(description='智能体ID'),
    'conversation_id': fields.String(description='对话ID'),
    'created_at': fields.String(readonly=True, description='创建时间'),
    'updated_at': fields.String(readonly=True, description='更新时间')
})

message_model = api.model('Message', {
    'id': fields.Integer(readonly=True, description='消息ID'),
    'conversation_id': fields.Integer(description='对话ID'),
    'role': fields.String(description='角色', enum=['user', 'assistant']),
    'content': fields.String(description='消息内容'),
    'timestamp': fields.String(readonly=True, description='时间戳')
})

log_model = api.model('AgentLog', {
    'id': fields.Integer(readonly=True, description='日志ID'),
    'agent_id': fields.Integer(description='智能体ID'),
    'level': fields.String(description='日志级别', enum=['info', 'warning', 'error', 'debug']),
    'message': fields.String(description='日志消息'),
    'timestamp': fields.String(readonly=True, description='时间戳')
})

# 首页路由
@app.route('/')
def index():
    """首页"""
    return jsonify({'message': 'Agent Management Platform API', 'docs': '/api/docs'})

# --------------------------
# 模型管理API
# --------------------------

@model_ns.route('/')
class ModelList(Resource):
    @model_ns.doc('list_models')
    @model_ns.marshal_list_with(model_model)
    def get(self):
        """获取模型列表"""
        try:
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 查询模型
            models = Model.query.paginate(page=page, per_page=per_page, error_out=False)
            
            # 构造响应数据
            response = {
                'models': [model.to_dict() for model in models.items],
                'page': models.page,
                'per_page': models.per_page,
                'total': models.total,
                'pages': models.pages
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @model_ns.doc('create_model')
    @model_ns.expect(model_model)
    @model_ns.marshal_with(model_model, code=201)
    def post(self):
        """创建新模型"""
        try:
            data = request.get_json()
            
            # 验证必填字段
            if not data or 'name' not in data or 'api_endpoint' not in data or 'model_name' not in data:
                return {'error': 'Name, api_endpoint and model_name are required'}, 400
            
            # 检查模型是否已存在
            existing_model = Model.query.filter_by(name=data['name']).first()
            if existing_model:
                return {'error': 'Model already exists'}, 409
            
            # 创建新模型
            model = Model(
                name=data['name'],
                description=data.get('description', ''),
                api_endpoint=data['api_endpoint'],
                api_key=data.get('api_key', None),
                model_name=data['model_name'],
                status=data.get('status', 'active')
            )
            
            db.session.add(model)
            db.session.commit()
            
            return {'message': 'Model created successfully', 'model': model.to_dict()}, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

@model_ns.route('/<int:model_id>')
@model_ns.param('model_id', '模型ID')
class ModelResource(Resource):
    @model_ns.doc('get_model')
    @model_ns.marshal_with(model_model)
    def get(self, model_id):
        """获取单个模型信息"""
        try:
            model = Model.query.get_or_404(model_id)
            return {'model': model.to_dict()}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @model_ns.doc('update_model')
    @model_ns.expect(model_model)
    @model_ns.marshal_with(model_model)
    def put(self, model_id):
        """更新模型信息"""
        try:
            model = Model.query.get_or_404(model_id)
            data = request.get_json()
            
            # 更新模型信息
            if 'name' in data:
                model.name = data['name']
            if 'description' in data:
                model.description = data['description']
            if 'api_endpoint' in data:
                model.api_endpoint = data['api_endpoint']
            if 'api_key' in data:
                model.api_key = data['api_key']
            if 'model_name' in data:
                model.model_name = data['model_name']
            if 'status' in data:
                # 验证状态值
                valid_statuses = ['active', 'inactive']
                if data['status'] not in valid_statuses:
                    return {'error': f'Invalid status. Must be one of {valid_statuses}'}, 400
                model.status = data['status']
            
            db.session.commit()
            
            return {'message': 'Model updated successfully', 'model': model.to_dict()}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @model_ns.doc('delete_model')
    def delete(self, model_id):
        """删除模型"""
        try:
            model = Model.query.get_or_404(model_id)
            model_name = model.name
            
            # 检查是否有智能体使用该模型
            if len(model.agents) > 0:
                return {'error': f'Model "{model_name}" is being used by {len(model.agents)} agents. Cannot delete.'}, 400
            
            # 删除模型
            db.session.delete(model)
            db.session.commit()
            
            return {'message': 'Model deleted successfully'}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

# --------------------------
# 智能体管理API
# --------------------------

@agent_ns.route('/')
class AgentList(Resource):
    @agent_ns.doc('list_agents')
    @agent_ns.marshal_list_with(agent_model)
    def get(self):
        """获取智能体列表（支持分页）"""
        try:
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 查询智能体
            agents = Agent.query.paginate(page=page, per_page=per_page, error_out=False)
            
            # 构造响应数据
            response = {
                'agents': [agent.to_dict() for agent in agents.items],
                'page': agents.page,
                'per_page': agents.per_page,
                'total': agents.total,
                'pages': agents.pages
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @agent_ns.doc('create_agent')
    @agent_ns.expect(agent_model)
    @agent_ns.marshal_with(agent_model, code=201)
    def post(self):
        """注册新智能体"""
        try:
            data = request.get_json()
            
            # 验证必填字段
            if not data or 'name' not in data or 'model_id' not in data:
                return {'error': 'Name and model_id are required'}, 400
            
            # 检查智能体是否已存在
            existing_agent = Agent.query.filter_by(name=data['name']).first()
            if existing_agent:
                return {'error': 'Agent already exists'}, 409
            
            # 检查模型是否存在
            model = Model.query.get(data['model_id'])
            if not model:
                return {'error': 'Model not found'}, 404
            
            # 创建新智能体
            agent = Agent(
                name=data['name'],
                description=data.get('description', ''),
                model_id=data['model_id'],
                status=data.get('status', 'inactive')
            )
            
            db.session.add(agent)
            db.session.commit()
            
            # 添加创建日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" created successfully'
            )
            db.session.add(log)
            db.session.commit()
            
            return {'message': 'Agent created successfully', 'agent': agent.to_dict()}, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

@agent_ns.route('/<int:agent_id>')
@agent_ns.param('agent_id', '智能体ID')
class AgentResource(Resource):
    @agent_ns.doc('get_agent')
    @agent_ns.marshal_with(agent_model)
    def get(self, agent_id):
        """获取单个智能体信息"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            return {'agent': agent.to_dict()}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @agent_ns.doc('update_agent')
    @agent_ns.expect(agent_model)
    @agent_ns.marshal_with(agent_model)
    def put(self, agent_id):
        """更新智能体信息"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            data = request.get_json()
            
            # 更新智能体信息
            if 'name' in data:
                agent.name = data['name']
            if 'description' in data:
                agent.description = data['description']
            if 'status' in data:
                # 验证状态值
                valid_statuses = ['inactive', 'running', 'paused', 'stopped']
                if data['status'] not in valid_statuses:
                    return {'error': f'Invalid status. Must be one of {valid_statuses}'}, 400
                agent.status = data['status']
            
            db.session.commit()
            
            # 添加更新日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" updated successfully'
            )
            db.session.add(log)
            db.session.commit()
            
            return {'message': 'Agent updated successfully', 'agent': agent.to_dict()}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @agent_ns.doc('delete_agent')
    def delete(self, agent_id):
        """删除智能体"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            agent_name = agent.name
            
            # 删除智能体
            db.session.delete(agent)
            db.session.commit()
            
            # 添加删除日志
            log = AgentLog(
                agent_id=agent_id,
                level='info',
                message=f'Agent "{agent_name}" deleted successfully'
            )
            db.session.add(log)
            db.session.commit()
            
            return {'message': 'Agent deleted successfully'}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@agent_ns.route('/<int:agent_id>/status')
@agent_ns.param('agent_id', '智能体ID')
class AgentStatusResource(Resource):
    @agent_ns.doc('update_agent_status')
    def post(self, agent_id):
        """更新智能体运行状态"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            data = request.get_json()
            
            # 验证状态值
            if 'status' not in data:
                return {'error': 'Status is required'}, 400
                
            valid_statuses = ['inactive', 'running', 'paused', 'stopped']
            if data['status'] not in valid_statuses:
                return {'error': f'Invalid status. Must be one of {valid_statuses}'}, 400
            
            # 更新状态
            old_status = agent.status
            agent.status = data['status']
            db.session.commit()
            
            # 添加状态变更日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" status changed from "{old_status}" to "{agent.status}"' 
            )
            db.session.add(log)
            db.session.commit()
            
            return {'message': f'Agent status updated to {agent.status}', 'agent': agent.to_dict()}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

# --------------------------
# 智能体会话API
# --------------------------

@chat_ns.route('/agents/<int:agent_id>/chat')
@chat_ns.param('agent_id', '智能体ID')
class ChatResource(Resource):
    @chat_ns.doc('chat_with_agent')
    @chat_ns.expect(chat_model)
    @chat_ns.marshal_with(chat_response_model)
    def post(self, agent_id):
        """与智能体进行对话"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            data = request.get_json()
            
            # 验证必填字段
            if not data or 'message' not in data:
                return {'error': 'Message is required'}, 400
            
            # 获取对话ID，如果没有则创建新对话
            conversation_id = data.get('conversation_id')
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                # 创建新对话
                conversation = Conversation(
                    agent_id=agent.id,
                    conversation_id=conversation_id
                )
                db.session.add(conversation)
                db.session.commit()
            else:
                # 查找现有对话
                conversation = Conversation.query.filter_by(
                    agent_id=agent.id,
                    conversation_id=conversation_id
                ).first()
                if not conversation:
                    return {'error': 'Conversation not found'}, 404
            
            # 保存用户消息
            user_message = Message(
                conversation_id=conversation.id,
                role='user',
                content=data['message']
            )
            db.session.add(user_message)
            db.session.commit()
            
            # 调用模型API获取响应
            model = agent.model
            if model.status != 'active':
                return {'error': 'Model is inactive'}, 400
            
            # 构造OpenAI兼容的请求
            openai_request = {
                'model': model.model_name,
                'messages': [
                    {'role': msg.role, 'content': msg.content}
                    for msg in conversation.messages
                ]
            }
            
            # 添加API密钥（如果有）
            headers = {'Content-Type': 'application/json'}
            if model.api_key:
                headers['Authorization'] = f'Bearer {model.api_key}'
            
            # 发送请求到模型API
            response = requests.post(model.api_endpoint, json=openai_request, headers=headers)
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            assistant_message_content = response_data['choices'][0]['message']['content']
            
            # 保存助手消息
            assistant_message = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=assistant_message_content
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            # 添加对话日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Conversation {conversation_id}: User message received and responded'
            )
            db.session.add(log)
            db.session.commit()
            
            # 构造响应
            return {
                'message': 'Chat completed successfully',
                'conversation_id': conversation_id,
                'response': assistant_message_content
            }, 200
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Model API error: {str(e)}'}, 500
        except Exception as e:
            return {'error': str(e)}, 500

@chat_ns.route('/agents/<int:agent_id>/conversations')
@chat_ns.param('agent_id', '智能体ID')
class ConversationListResource(Resource):
    @chat_ns.doc('get_agent_conversations')
    @chat_ns.marshal_list_with(conversation_model)
    def get(self, agent_id):
        """获取智能体的对话列表"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 查询对话
            conversations = Conversation.query.filter_by(agent_id=agent.id)
            conversations = conversations.order_by(Conversation.updated_at.desc())
            conversations = conversations.paginate(page=page, per_page=per_page, error_out=False)
            
            # 构造响应数据
            response = {
                'conversations': [conversation.to_dict() for conversation in conversations.items],
                'page': conversations.page,
                'per_page': conversations.per_page,
                'total': conversations.total,
                'pages': conversations.pages
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@chat_ns.route('/conversations/<string:conversation_id>/messages')
@chat_ns.param('conversation_id', '对话ID')
class MessageListResource(Resource):
    @chat_ns.doc('get_conversation_messages')
    @chat_ns.marshal_list_with(message_model)
    def get(self, conversation_id):
        """获取对话的消息列表"""
        try:
            # 查找对话
            conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
            if not conversation:
                return {'error': 'Conversation not found'}, 404
            
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # 查询消息
            messages = Message.query.filter_by(conversation_id=conversation.id)
            messages = messages.order_by(Message.timestamp.asc())
            messages = messages.paginate(page=page, per_page=per_page, error_out=False)
            
            # 构造响应数据
            response = {
                'messages': [message.to_dict() for message in messages.items],
                'page': messages.page,
                'per_page': messages.per_page,
                'total': messages.total,
                'pages': messages.pages
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

# --------------------------
# 日志管理API
# --------------------------

@log_ns.route('/agents/<int:agent_id>/logs')
@log_ns.param('agent_id', '智能体ID')
class AgentLogListResource(Resource):
    @log_ns.doc('get_agent_logs')
    @log_ns.marshal_list_with(log_model)
    def get(self, agent_id):
        """获取智能体日志列表（支持分页）"""
        try:
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            level = request.args.get('level')
            
            # 查询日志
            logs = AgentLog.query.filter_by(agent_id=agent_id)
            
            # 根据级别过滤
            if level:
                logs = logs.filter_by(level=level)
            
            # 分页查询
            logs = logs.order_by(AgentLog.timestamp.desc())
            logs = logs.paginate(page=page, per_page=per_page, error_out=False)
            
            # 构造响应数据
            response = {
                'logs': [log.to_dict() for log in logs.items],
                'page': logs.page,
                'per_page': logs.per_page,
                'total': logs.total,
                'pages': logs.pages
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@log_ns.route('/')
class LogListResource(Resource):
    @log_ns.doc('get_all_logs')
    @log_ns.marshal_list_with(log_model)
    def get(self):
        """获取所有智能体日志列表（支持分页）"""
        try:
            # 获取分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            level = request.args.get('level')
            
            # 查询日志
            logs = AgentLog.query
            
            # 根据级别过滤
            if level:
                logs = logs.filter_by(level=level)
            
            # 分页查询
            logs = logs.order_by(AgentLog.timestamp.desc())
            logs = logs.paginate(page=page, per_page=per_page, error_out=False)
            
            # 构造响应数据
            response = {
                'logs': [log.to_dict() for log in logs.items],
                'page': logs.page,
                'per_page': logs.per_page,
                'total': logs.total,
                'pages': logs.pages
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
