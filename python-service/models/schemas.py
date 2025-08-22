from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum

class SourceType(str, Enum):
    """数据源类型"""
    WEB_SCRAPING = "web_scraping"
    ENERGY_LOGS = "energy_logs"
    REMOTE_SENSING = "remote_sensing"
    PUBLIC_DATA = "public_data"
    MODIS = "modis"

class IndustryType(str, Enum):
    """行业类型"""
    MANUFACTURING = "manufacturing"
    ENERGY = "energy"
    TRANSPORTATION = "transportation"
    AGRICULTURE = "agriculture"
    CONSTRUCTION = "construction"
    SERVICES = "services"
    MINING = "mining"
    CHEMICAL = "chemical"

class ResourceType(str, Enum):
    """资源类型"""
    COAL = "coal"
    OIL = "oil"
    GAS = "gas"
    ELECTRICITY = "electricity"
    RENEWABLE = "renewable"
    NUCLEAR = "nuclear"

class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# 数据采集相关模型
class DataCollectionRequest(BaseModel):
    """数据采集请求"""
    source_type: SourceType = Field(..., description="数据源类型")
    industry: Optional[IndustryType] = Field(None, description="行业类型")
    region: Optional[str] = Field(None, description="地区")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    urls: Optional[List[str]] = Field(None, description="爬取URL列表")
    api_keys: Optional[Dict[str, str]] = Field(None, description="API密钥")
    custom_filters: Optional[Dict[str, Any]] = Field(None, description="自定义过滤条件")

class DataCollectionResponse(BaseModel):
    """数据采集响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    task_id: str = Field(..., description="任务ID")
    estimated_time: str = Field(..., description="预计完成时间")
    data_count: Optional[int] = Field(None, description="采集数据量")
    file_path: Optional[str] = Field(None, description="数据文件路径")

# AI预测相关模型
class PredictionRequest(BaseModel):
    """预测请求"""
    industry: IndustryType = Field(..., description="行业类型")
    resource_type: ResourceType = Field(..., description="资源类型")
    time_period: int = Field(..., description="预测时间周期(月)", ge=1, le=60)
    features: Optional[Dict[str, Any]] = Field(None, description="特征参数")
    model_type: Optional[str] = Field("lstm", description="模型类型")
    confidence_level: Optional[float] = Field(0.95, description="置信水平", ge=0.5, le=0.99)

    model_config = {
        'protected_namespaces': ()  # 清空保护前缀
    }

class PredictionResponse(BaseModel):
    """预测响应"""
    success: bool = Field(..., description="是否成功")
    predictions: List[Dict[str, Any]] = Field(..., description="预测结果")
    confidence: float = Field(..., description="预测置信度")
    carbon_neutral_year: Optional[int] = Field(None, description="碳中和年份")
    trend_analysis: Dict[str, Any] = Field(..., description="趋势分析")
    model_performance: Optional[Dict[str, float]] = Field(None, description="模型性能指标")

    model_config = {
        'protected_namespaces': ()  # 清空保护前缀
    }

# 异常检测相关模型
class AnomalyRequest(BaseModel):
    """异常检测请求"""
    industry: IndustryType = Field(..., description="行业类型")
    time_range: int = Field(..., description="检测时间范围(天)", ge=7, le=365)
    threshold: Optional[float] = Field(0.95, description="异常检测阈值", ge=0.5, le=0.99)
    include_historical: Optional[bool] = Field(True, description="是否包含历史异常")
    alert_level: Optional[RiskLevel] = Field(RiskLevel.MEDIUM, description="告警等级")

class AnomalyResponse(BaseModel):
    """异常检测响应"""
    success: bool = Field(..., description="是否成功")
    anomalies: List[Dict[str, Any]] = Field(..., description="检测到的异常")
    risk_level: RiskLevel = Field(..., description="整体风险等级")
    recommendations: List[str] = Field(..., description="建议措施")
    statistical_summary: Optional[Dict[str, Any]] = Field(None, description="统计摘要")

# 碳循环分析相关模型
class CarbonCycleRequest(BaseModel):
    """碳循环分析请求"""
    region: str = Field(..., description="分析地区")
    time_period: int = Field(..., description="分析时间周期(年)", ge=1, le=10)
    include_remote_sensing: Optional[bool] = Field(True, description="是否包含遥感数据")
    spatial_resolution: Optional[str] = Field("1km", description="空间分辨率")
    vegetation_types: Optional[List[str]] = Field(None, description="植被类型")

class CarbonCycleResponse(BaseModel):
    """碳循环分析响应"""
    success: bool = Field(..., description="是否成功")
    carbon_sink: Dict[str, float] = Field(..., description="碳汇数据")
    carbon_source: Dict[str, float] = Field(..., description="碳源数据")
    net_emission: float = Field(..., description="净排放量")
    sequestration_potential: Dict[str, Any] = Field(..., description="固碳潜力")
    map_data: Optional[Dict[str, Any]] = Field(None, description="地图数据")
    temporal_trends: Optional[List[Dict[str, Any]]] = Field(None, description="时间趋势")

# 通用响应模型
class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="是否成功")
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., description="进度百分比", ge=0, le=100)
    start_time: datetime = Field(..., description="开始时间")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
