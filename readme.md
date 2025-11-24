# Agent Management Platform

## 项目简介
本项目是一套轻量级的 **智能体管理平台** 示例，旨在帮助 AI 大模型测试人员了解如何构建一个基本的智能体（Agent）管理系统。平台提供以下核心功能：
- **智能体注册**：通过 REST API 注册新的智能体，记录名称、描述、状态等元数据。
- **智能体列表**：展示已注册智能体的概览，支持分页查询。
- **状态管理**：启动、暂停、停止智能体的运行状态。
- **日志查看**：简易的日志接口，帮助调试智能体的行为。

## 适用场景
- 大模型测试环境中，需要统一管理多个对话机器人或任务执行器。
- 教育或培训任务，示例如何使用 Flask（或 FastAPI）+ SQLite 实现基本的 CRUD 操作。

## 技术栈
- **后端**：Python + Flask
- **数据库**：SQLite（轻量）
- **ORM**：Flask-SQLAlchemy
- **依赖管理**：requirements.txt

## 结构说明
```
agent-management-platform
├── app.py               # 主应用入口，定义 API 路由
├── models.py            # 数据模型（SQLAlchemy）
├── db.sqlite3          # 本地 SQLite 数据库文件（自动生成）
├── requirements.txt    # 项目依赖
└── README.md            # 项目说明文档
```

## 安装与运行

### 1. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python app.py
```

应用将在 http://localhost:5000 启动

## API 文档

### 智能体管理

#### 1. 注册智能体
- **POST** `/agents`
- 请求体：
  ```json
  {
    "name": "agent-001",
    "description": "测试智能体",
    "status": "inactive"
  }
  ```
- 响应：
  ```json
  {
    "message": "Agent created successfully",
    "agent": {
      "id": 1,
      "name": "agent-001",
      "description": "测试智能体",
      "status": "inactive",
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T12:00:00"
    }
  }
  ```

#### 2. 获取智能体列表
- **GET** `/agents`
- 参数：
  - `page`: 页码（默认：1）
  - `per_page`: 每页数量（默认：10）
- 响应：
  ```json
  {
    "agents": [
      {
        "id": 1,
        "name": "agent-001",
        "description": "测试智能体",
        "status": "inactive",
        "created_at": "2023-09-01T12:00:00",
        "updated_at": "2023-09-01T12:00:00"
      }
    ],
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1
  }
  ```

#### 3. 获取单个智能体
- **GET** `/agents/<int:agent_id>`
- 响应：
  ```json
  {
    "agent": {
      "id": 1,
      "name": "agent-001",
      "description": "测试智能体",
      "status": "inactive",
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T12:00:00"
    }
  }
  ```

#### 4. 更新智能体
- **PUT** `/agents/<int:agent_id>`
- 请求体：
  ```json
  {
    "name": "agent-001-updated",
    "description": "更新后的测试智能体",
    "status": "running"
  }
  ```
- 响应：
  ```json
  {
    "message": "Agent updated successfully",
    "agent": {
      "id": 1,
      "name": "agent-001-updated",
      "description": "更新后的测试智能体",
      "status": "running",
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T13:00:00"
    }
  }
  ```

#### 5. 删除智能体
- **DELETE** `/agents/<int:agent_id>`
- 响应：
  ```json
  {
    "message": "Agent deleted successfully"
  }
  ```

#### 6. 更新智能体状态
- **POST** `/agents/<int:agent_id>/status`
- 请求体：
  ```json
  {
    "status": "running"
  }
  ```
- 响应：
  ```json
  {
    "message": "Agent status updated to running",
    "agent": {
      "id": 1,
      "name": "agent-001",
      "description": "测试智能体",
      "status": "running",
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T14:00:00"
    }
  }
  ```

### 日志管理

#### 1. 获取智能体日志
- **GET** `/agents/<int:agent_id>/logs`
- 参数：
  - `page`: 页码（默认：1）
  - `per_page`: 每页数量（默认：20）
- 响应：
  ```json
  {
    "logs": [
      {
        "id": 1,
        "agent_id": 1,
        "level": "info",
        "message": "Agent "agent-001" created successfully",
        "timestamp": "2023-09-01T12:00:00"
      }
    ],
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
  ```

#### 2. 获取所有日志
- **GET** `/logs`
- 参数：
  - `page`: 页码（默认：1）
  - `per_page`: 每页数量（默认：20）
- 响应：
  ```json
  {
    "logs": [
      {
        "id": 1,
        "agent_id": 1,
        "level": "info",
        "message": "Agent "agent-001" created successfully",
        "timestamp": "2023-09-01T12:00:00"
      }
    ],
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
  ```

## 状态说明
智能体支持以下状态：
- `inactive`: 未激活
- `running`: 运行中
- `paused`: 已暂停
- `stopped`: 已停止

## 日志级别
日志支持以下级别：
- `info`: 信息
- `warning`: 警告
- `error`: 错误
- `debug`: 调试
