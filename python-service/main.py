from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from loguru import logger
import os
import sys
from pathlib import Path
from datetime import datetime

# 确保可以以项目根为基准导入 models 和 services
CURRENT_FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_FILE_DIR  # 本地 python-service 目录
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.data_collector import DataCollector
from services.ai_predictor import AIPredictor
from services.anomaly_detector import AnomalyDetector
from services.carbon_cycle import CarbonCycleModel
from models.schemas import (
    PredictionRequest, PredictionResponse, 
    AnomalyRequest, AnomalyResponse,
    CarbonCycleRequest, CarbonCycleResponse,
    DataCollectionRequest, DataCollectionResponse
)

# 配置日志
os.makedirs("logs", exist_ok=True)
logger.add("logs/carbon_service.log", rotation="1 day", retention="30 days")
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

# 初始化服务
data_collector = DataCollector()
ai_predictor = AIPredictor()
anomaly_detector = AnomalyDetector()
carbon_cycle_model = CarbonCycleModel()

# Lifespan 上下文管理器替代 startup/shutdown
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("碳排放AI分析服务启动中...")
    try:
        # 初始化模型（异步）
        await ai_predictor.initialize_models()
        await anomaly_detector.initialize_models()
        await carbon_cycle_model.initialize_models()
        logger.info("AI模型初始化完成")
    except Exception as e:
        logger.error(f"AI模型初始化失败: {e}")
    yield
    logger.info("应用关闭，Lifespan清理完成")

# 创建 FastAPI 应用
app = FastAPI(
    title="碳排放AI分析服务",
    description="提供数据采集、AI预测、异常检测、碳循环模型分析等服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# 路由接口
# ------------------------------
@app.get("/")
async def root():
    """服务健康检查"""
    return {
        "service": "碳排放AI分析服务",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """详细的健康检查"""
    return {
        "status": "healthy",
        "services": {
            "data_collector": "ready",
            "ai_predictor": "ready" if ai_predictor.is_ready() else "not_ready",
            "anomaly_detector": "ready" if anomaly_detector.is_ready() else "not_ready",
            "carbon_cycle_model": "ready" if carbon_cycle_model.is_ready() else "not_ready"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/collect/data", response_model=DataCollectionResponse)
async def collect_data(request: DataCollectionRequest, background_tasks: BackgroundTasks):
    """数据采集接口"""
    try:
        logger.info(f"开始数据采集: {request.source_type}")
        background_tasks.add_task(data_collector.collect_data, request)
        return DataCollectionResponse(
            success=True,
            message="数据采集任务已启动",
            task_id=f"collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            estimated_time="5-10分钟"
        )
    except Exception as e:
        logger.error(f"数据采集失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/emissions", response_model=PredictionResponse)
async def predict_emissions(request: PredictionRequest):
    """碳排放预测接口"""
    try:
        logger.info(f"开始碳排放预测: {request.industry} - {request.resource_type}")
        prediction_result = await ai_predictor.predict_emissions(
            industry=request.industry,
            resource_type=request.resource_type,
            time_period=request.time_period,
            features=request.features
        )
        return PredictionResponse(
            success=True,
            predictions=prediction_result["predictions"],
            confidence=prediction_result["confidence"],
            carbon_neutral_year=prediction_result.get("carbon_neutral_year"),
            trend_analysis=prediction_result["trend_analysis"],
            model_performance=prediction_result.get("model_performance")
        )
    except Exception as e:
        logger.error(f"碳排放预测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect/anomalies", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest):
    """异常检测接口"""
    try:
        logger.info(f"开始异常检测: {request.industry}")
        anomaly_result = await anomaly_detector.detect_anomalies(
            industry=request.industry,
            time_range=request.time_range,
            threshold=request.threshold
        )
        return AnomalyResponse(
            success=True,
            anomalies=anomaly_result["anomalies"],
            risk_level=anomaly_result["risk_level"],
            recommendations=anomaly_result["recommendations"],
            statistical_summary=anomaly_result.get("statistical_summary")
        )
    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/carbon-cycle", response_model=CarbonCycleResponse)
async def analyze_carbon_cycle(request: CarbonCycleRequest):
    """碳循环分析接口"""
    try:
        logger.info(f"开始碳循环分析: {request.region}")
        cycle_result = await carbon_cycle_model.analyze_carbon_cycle(
            region=request.region,
            time_period=request.time_period,
            include_remote_sensing=request.include_remote_sensing
        )
        return CarbonCycleResponse(
            success=True,
            carbon_sink=cycle_result["carbon_sink"],
            carbon_source=cycle_result["carbon_source"],
            net_emission=cycle_result["net_emission"],
            sequestration_potential=cycle_result["sequestration_potential"],
            map_data=cycle_result.get("map_data"),
            temporal_trends=cycle_result.get("temporal_trends")
        )
    except Exception as e:
        logger.error(f"碳循环分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/template/{template_type}")
async def download_template(template_type: str):
    """下载数据模板"""
    template_files = {
        "emissions": "templates/emissions_template.csv",
        "remote_sensing": "templates/remote_sensing_template.csv",
        "energy_logs": "templates/energy_logs_template.csv"
    }
    if template_type not in template_files:
        raise HTTPException(status_code=400, detail="无效的模板类型")
    file_path = template_files[template_type]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="模板文件不存在")
    return FileResponse(file_path, filename=f"{template_type}_template.csv", media_type="text/csv")

@app.get("/api/status/tasks")
async def get_task_status():
    """获取后台任务状态"""
    return {
        "active_tasks": data_collector.get_active_tasks(),
        "completed_tasks": data_collector.get_completed_tasks(),
        "failed_tasks": data_collector.get_failed_tasks()
    }

# ------------------------------
# 启动服务
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
