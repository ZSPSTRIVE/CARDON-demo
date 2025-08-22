# 碳排放可视化系统（AI增强版）

本项目是一个完整的碳排放数据可视化与分析系统，基于 Spring Boot 2.7（Java 17）后端与 Vue 3 + Vite + ECharts 前端，使用 MySQL 8 持久化与 Docker 容器化部署，认证采用 JWT。系统不仅支持碳排放的可视化分析，还引入**数据采集层、数据处理层、模型分析层**，实现碳排放全流程管理与AI预测。

## 🚀 新增AI功能特性

### 数据采集层
- **网络数据爬取**: 自动爬取能源消耗、排放数据
- **能源消耗日志采集**: 实时监控设备能源使用情况
- **遥感卫星数据接口**: 集成MODIS等卫星数据
- **公开数据下载**: 政府公开数据自动采集

### AI模型分析层
- **LSTM预测模型**: 基于深度学习的碳排放趋势预测
- **AutoEncoder异常检测**: 智能识别数据异常和风险点
- **碳循环模型**: 地区碳汇/碳源平衡分析
- **碳中和年份预测**: 基于历史数据的碳中和路径规划

## 🏗️ 技术架构

### 后端架构
- **Spring Boot 2.7**: 主应用框架
- **Spring Security + JWT**: 安全认证
- **Spring Data JPA**: 数据持久化
- **MySQL 8**: 主数据库
- **Python AI服务**: FastAPI + PyTorch + 机器学习

### AI/ML技术栈
- **PyTorch**: 深度学习框架
- **LSTM**: 时间序列预测
- **AutoEncoder**: 异常检测
- **scikit-learn**: 传统机器学习
- **rasterio**: 地理空间数据处理

## 📁 项目结构

```
碳排放项目/
├── backend/                    # Spring Boot 后端
├── frontend/                   # Vue 3 前端
├── python-service/            # Python AI服务
│   ├── services/             # AI服务模块
│   ├── models/               # 数据模型
│   └── templates/            # 数据模板
└── docker-compose.yml        # 容器编排配置
```

## 🚀 快速开始

### 一键启动（推荐）
```bash
docker compose up -d --build
```

### 分步启动（开发模式）
```bash
# 1. 启动Python AI服务
cd python-service
pip install -r requirements.txt
python start.py

# 2. 启动Spring Boot后端
cd backend
mvn spring-boot:run

# 3. 启动Vue前端
cd frontend
npm install
npm run dev
```

## 🔐 访问信息

- **前端界面**: http://localhost:80
- **后端API**: http://localhost:8080
- **AI服务**: http://localhost:8000
- **默认账号**: admin / admin123

## 📊 核心功能

### AI智能分析
- **排放预测**: 基于LSTM的未来排放量预测
- **异常检测**: 智能识别数据异常和风险点
- **碳循环分析**: 地区碳汇/碳源平衡评估
- **碳中和路径**: 实现碳中和的时间路径规划

### 数据管理
- **多源数据采集**: 网络爬虫、API接口、文件导入
- **数据清洗**: 自动数据质量检查与清洗
- **模板下载**: 标准数据格式模板

## 🔧 API接口

### AI分析接口
- `POST /api/ai/predict` - 排放预测
- `POST /api/ai/anomalies` - 异常检测
- `POST /api/ai/carbon-cycle` - 碳循环分析
- `POST /api/ai/collect` - 启动数据采集

## 📈 使用场景

### 政府机构
- **政策制定**: 基于数据的减排政策制定
- **目标监控**: 碳排放目标的实时监控

### 企业用户
- **排放管理**: 企业碳排放的全面管理
- **合规监控**: 排放法规的合规性监控

## 🛠️ 开发指南

### 添加新的AI模型
1. 在 `python-service/services/` 下创建新的服务类
2. 在 `main.py` 中注册新的API端点
3. 在 `AIService.java` 中添加对应的调用方法

### 自定义数据源
1. 在 `data_collector.py` 中添加新的采集方法
2. 在 `schemas.py` 中定义新的数据模型
3. 更新数据模板文件

## 🔍 故障排除

### 常见问题
1. **Python服务启动失败**: 检查依赖包安装和端口占用
2. **AI模型加载失败**: 检查模型文件路径和权限
3. **数据库连接失败**: 检查MySQL服务状态和配置

### 日志查看
```bash
docker compose logs python-service
docker compose logs backend
docker compose logs frontend
