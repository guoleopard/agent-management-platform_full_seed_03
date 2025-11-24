from flask import Flask, request, jsonify
from models import db, Agent, AgentLog
import os

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """首页"""
    return jsonify({'message': 'Agent Management Platform API'})

# --------------------------
# 智能体管理API
# --------------------------

@app.route('/agents', methods=['POST'])
def create_agent():
    """注册新智能体"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        # 检查智能体是否已存在
        existing_agent = Agent.query.filter_by(name=data['name']).first()
        if existing_agent:
            return jsonify({'error': 'Agent already exists'}), 409
        
        # 创建新智能体
        agent = Agent(
            name=data['name'],
            description=data.get('description', ''),
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
        
        return jsonify({'message': 'Agent created successfully', 'agent': agent.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents', methods=['GET'])
def get_agents():
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
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/<int:agent_id>', methods=['GET'])
def get_agent(agent_id):
    """获取单个智能体信息"""
    try:
        agent = Agent.query.get_or_404(agent_id)
        return jsonify({'agent': agent.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
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
                return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400
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
        
        return jsonify({'message': 'Agent updated successfully', 'agent': agent.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
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
        
        return jsonify({'message': 'Agent deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/<int:agent_id>/status', methods=['POST'])
def update_agent_status(agent_id):
    """更新智能体运行状态"""
    try:
        agent = Agent.query.get_or_404(agent_id)
        data = request.get_json()
        
        # 验证状态值
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
            
        valid_statuses = ['inactive', 'running', 'paused', 'stopped']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400
        
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
        
        return jsonify({'message': f'Agent status updated to {agent.status}', 'agent': agent.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------------------
# 日志管理API
# --------------------------

@app.route('/agents/<int:agent_id>/logs', methods=['GET'])
def get_agent_logs(agent_id):
    """获取智能体日志"""
    try:
        # 验证智能体是否存在
        agent = Agent.query.get_or_404(agent_id)
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询日志
        logs = AgentLog.query.filter_by(agent_id=agent_id).order_by(AgentLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构造响应数据
        response = {
            'logs': [log.to_dict() for log in logs.items],
            'page': logs.page,
            'per_page': logs.per_page,
            'total': logs.total,
            'pages': logs.pages
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_all_logs():
    """获取所有智能体日志"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询日志
        logs = AgentLog.query.order_by(AgentLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构造响应数据
        response = {
            'logs': [log.to_dict() for log in logs.items],
            'page': logs.page,
            'per_page': logs.per_page,
            'total': logs.total,
            'pages': logs.pages
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
