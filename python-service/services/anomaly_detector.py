import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

import sys
import os
# 添加父目录到Python路径，确保可以导入models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import AnomalyRequest, IndustryType, RiskLevel

class AutoEncoder(nn.Module):
    """自编码器异常检测模型"""
    
    def __init__(self, input_size, encoding_dim):
        super(AutoEncoder, self).__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_size, encoding_dim * 2),
            nn.ReLU(),
            nn.Linear(encoding_dim * 2, encoding_dim),
            nn.ReLU()
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, encoding_dim * 2),
            nn.ReLU(),
            nn.Linear(encoding_dim * 2, input_size),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class AnomalyDetector:
    """异常检测服务"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.isolation_forests = {}
        self.is_initialized = False
        self.model_dir = "models"
        
        # 确保模型目录存在
        os.makedirs(self.model_dir, exist_ok=True)
    
    async def initialize_models(self):
        """初始化异常检测模型"""
        try:
            logger.info("开始初始化异常检测模型...")
            
            # 为每个行业创建模型
            for industry in IndustryType:
                model_key = industry.value
                
                # 创建或加载模型
                model_path = os.path.join(self.model_dir, f"autoencoder_{model_key}.pth")
                scaler_path = os.path.join(self.model_dir, f"anomaly_scaler_{model_key}.pkl")
                if_path = os.path.join(self.model_dir, f"isolation_forest_{model_key}.pkl")
                
                if (os.path.exists(model_path) and os.path.exists(scaler_path) and 
                    os.path.exists(if_path)):
                    # 加载已有模型
                    self.models[model_key] = torch.load(model_path)
                    self.scalers[model_key] = joblib.load(scaler_path)
                    self.isolation_forests[model_key] = joblib.load(if_path)
                    logger.info(f"加载异常检测模型: {model_key}")
                else:
                    # 创建新模型
                    self.models[model_key] = AutoEncoder(
                        input_size=8,  # 特征数量
                        encoding_dim=4
                    )
                    
                    # 创建标准化器
                    self.scalers[model_key] = StandardScaler()
                    
                    # 创建隔离森林
                    self.isolation_forests[model_key] = IsolationForest(
                        contamination=0.1,
                        random_state=42
                    )
                    
                    logger.info(f"创建新异常检测模型: {model_key}")
            
            self.is_initialized = True
            logger.info("异常检测模型初始化完成")
            
        except Exception as e:
            logger.error(f"异常检测模型初始化失败: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """检查模型是否准备就绪"""
        return self.is_initialized and len(self.models) > 0
    
    async def detect_anomalies(self, industry: IndustryType, time_range: int, 
                              threshold: float = 0.95) -> Dict[str, Any]:
        """检测异常"""
        try:
            if not self.is_ready():
                raise RuntimeError("异常检测模型尚未初始化")
            
            model_key = industry.value
            
            if model_key not in self.models:
                raise ValueError(f"未找到模型: {model_key}")
            
            # 生成模拟数据用于异常检测
            data = self._generate_simulation_data(industry, time_range)
            
            # 检测异常
            anomalies = self._detect_anomalies_in_data(data, model_key, threshold)
            
            # 评估风险等级
            risk_level = self._assess_risk_level(anomalies)
            
            # 生成建议
            recommendations = self._generate_recommendations(anomalies, risk_level)
            
            # 统计摘要
            statistical_summary = self._generate_statistical_summary(anomalies, data)
            
            return {
                "anomalies": anomalies,
                "risk_level": risk_level,
                "recommendations": recommendations,
                "statistical_summary": statistical_summary
            }
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            raise
    
    def _generate_simulation_data(self, industry: IndustryType, time_range: int) -> pd.DataFrame:
        """生成模拟数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_range)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 根据行业生成不同的数据模式
        base_values = self._get_industry_base_values(industry)
        
        data = []
        for i, date in enumerate(dates):
            # 基础值 + 趋势 + 季节性 + 随机噪声
            trend = base_values["emission"] * (1 + 0.001 * i)  # 缓慢上升趋势
            seasonal = base_values["emission"] * 0.2 * np.sin(2 * np.pi * i / 365)  # 年度季节性
            noise = np.random.normal(0, base_values["emission"] * 0.1)  # 10%的随机噪声
            
            # 偶尔添加异常值
            if np.random.random() < 0.05:  # 5%的概率出现异常
                anomaly_factor = np.random.choice([0.1, 2.0, 5.0])  # 异常倍数
                emission = base_values["emission"] * anomaly_factor
            else:
                emission = max(0, trend + seasonal + noise)
            
            data.append({
                'date': date,
                'emission': emission,
                'energy_consumption': np.random.normal(base_values["energy"], base_values["energy"] * 0.1),
                'temperature': np.random.normal(base_values["temperature"], 5),
                'humidity': np.random.normal(base_values["humidity"], 10),
                'pressure': np.random.normal(base_values["pressure"], 5),
                'wind_speed': np.random.normal(base_values["wind_speed"], 2),
                'gdp': np.random.normal(base_values["gdp"], base_values["gdp"] * 0.05),
                'policy_factor': np.random.normal(1.0, 0.1)
            })
        
        return pd.DataFrame(data)
    
    def _get_industry_base_values(self, industry: IndustryType) -> Dict[str, float]:
        """获取行业基础值"""
        base_values = {
            IndustryType.ENERGY: {
                "emission": 1000,
                "energy": 5000,
                "temperature": 25,
                "humidity": 60,
                "pressure": 1013,
                "wind_speed": 3,
                "gdp": 100000
            },
            IndustryType.MANUFACTURING: {
                "emission": 800,
                "energy": 4000,
                "temperature": 22,
                "humidity": 50,
                "pressure": 1013,
                "wind_speed": 2,
                "gdp": 80000
            },
            IndustryType.TRANSPORTATION: {
                "emission": 600,
                "energy": 3000,
                "temperature": 20,
                "humidity": 55,
                "pressure": 1013,
                "wind_speed": 5,
                "gdp": 60000
            },
            IndustryType.AGRICULTURE: {
                "emission": 400,
                "energy": 2000,
                "temperature": 18,
                "humidity": 70,
                "pressure": 1013,
                "wind_speed": 4,
                "gdp": 40000
            },
            IndustryType.CONSTRUCTION: {
                "emission": 500,
                "energy": 2500,
                "temperature": 24,
                "humidity": 45,
                "pressure": 1013,
                "wind_speed": 3,
                "gdp": 50000
            },
            IndustryType.SERVICES: {
                "emission": 300,
                "energy": 1500,
                "temperature": 21,
                "humidity": 55,
                "pressure": 1013,
                "wind_speed": 2,
                "gdp": 30000
            },
            IndustryType.MINING: {
                "emission": 700,
                "energy": 3500,
                "temperature": 26,
                "humidity": 40,
                "pressure": 1013,
                "wind_speed": 4,
                "gdp": 70000
            },
            IndustryType.CHEMICAL: {
                "emission": 900,
                "energy": 4500,
                "temperature": 23,
                "humidity": 50,
                "pressure": 1013,
                "wind_speed": 2,
                "gdp": 90000
            }
        }
        
        return base_values.get(industry, base_values[IndustryType.MANUFACTURING])
    
    def _detect_anomalies_in_data(self, data: pd.DataFrame, model_key: str, threshold: float) -> List[Dict[str, Any]]:
        """在数据中检测异常"""
        anomalies = []
        
        # 选择特征列
        feature_columns = ['emission', 'energy_consumption', 'temperature', 'humidity', 
                          'pressure', 'wind_speed', 'gdp', 'policy_factor']
        
        X = data[feature_columns].values
        
        # 方法1: 使用隔离森林
        if_anomalies = self.isolation_forests[model_key].fit_predict(X)
        
        # 方法2: 使用自编码器重构误差
        autoencoder_anomalies = self._detect_with_autoencoder(X, model_key, threshold)
        
        # 方法3: 统计方法（Z-score）
        statistical_anomalies = self._detect_with_statistics(X, threshold)
        
        # 综合多种方法的结果
        for i, (date, row) in enumerate(data.iterrows()):
            is_anomaly = False
            anomaly_score = 0
            anomaly_reasons = []
            
            # 检查隔离森林结果
            if if_anomalies[i] == -1:
                is_anomaly = True
                anomaly_score += 0.4
                anomaly_reasons.append("机器学习模型检测到异常模式")
            
            # 检查自编码器结果
            if autoencoder_anomalies[i]:
                is_anomaly = True
                anomaly_score += 0.4
                anomaly_reasons.append("自编码器重构误差异常")
            
            # 检查统计结果
            if statistical_anomalies[i]:
                is_anomaly = True
                anomaly_score += 0.2
                anomaly_reasons.append("统计指标超出正常范围")
            
            if is_anomaly:
                # 确保date是日期对象，如果是索引则从row中获取
                if hasattr(date, 'isoformat'):
                    date_str = date.isoformat()
                elif isinstance(date, (int, float)):
                    # 如果是数字索引，从row中获取实际的日期
                    date_str = str(row.get('date', date))
                else:
                    date_str = str(date)
                
                anomalies.append({
                    "date": date_str,
                    "anomaly_score": round(anomaly_score, 3),
                    "reasons": anomaly_reasons,
                    "emission": row["emission"],
                    "energy_consumption": row["energy_consumption"],
                    "temperature": row["temperature"],
                    "severity": self._calculate_severity(anomaly_score)
                })
        
        return anomalies
    
    def _detect_with_autoencoder(self, X: np.ndarray, model_key: str, threshold: float) -> List[bool]:
        """使用自编码器检测异常"""
        try:
            model = self.models[model_key]
            model.eval()
            
            # 数据标准化
            X_scaled = self.scalers[model_key].fit_transform(X)
            X_tensor = torch.FloatTensor(X_scaled)
            
            # 重构
            with torch.no_grad():
                reconstructed = model(X_tensor)
            
            # 计算重构误差
            mse = torch.mean((X_tensor - reconstructed) ** 2, dim=1)
            
            # 计算异常阈值
            error_threshold = torch.quantile(mse, threshold)
            
            # 标记异常
            anomalies = (mse > error_threshold).numpy()
            
            return anomalies.tolist()
            
        except Exception as e:
            logger.warning(f"自编码器异常检测失败: {e}")
            return [False] * len(X)
    
    def _detect_with_statistics(self, X: np.ndarray, threshold: float) -> List[bool]:
        """使用统计方法检测异常"""
        anomalies = []
        
        for i in range(X.shape[1]):
            column = X[:, i]
            mean = np.mean(column)
            std = np.std(column)
            
            if std == 0:
                continue
            
            # 计算Z-score
            z_scores = np.abs((column - mean) / std)
            
            # 标记异常（Z-score > 2.5）
            column_anomalies = z_scores > 2.5
            
            if i == 0:  # 第一列
                anomalies = column_anomalies
            else:
                anomalies = anomalies | column_anomalies
        
        return anomalies.tolist()
    
    def _calculate_severity(self, anomaly_score: float) -> str:
        """计算异常严重程度"""
        if anomaly_score >= 0.8:
            return "critical"
        elif anomaly_score >= 0.6:
            return "high"
        elif anomaly_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _assess_risk_level(self, anomalies: List[Dict[str, Any]]) -> RiskLevel:
        """评估整体风险等级"""
        if not anomalies:
            return RiskLevel.LOW
        
        # 计算平均异常分数
        avg_score = np.mean([a["anomaly_score"] for a in anomalies])
        
        # 计算严重异常的数量
        critical_count = sum(1 for a in anomalies if a["severity"] == "critical")
        high_count = sum(1 for a in anomalies if a["severity"] == "high")
        
        # 风险等级判断
        if critical_count > 0 or avg_score > 0.8:
            return RiskLevel.CRITICAL
        elif high_count > 2 or avg_score > 0.6:
            return RiskLevel.HIGH
        elif high_count > 0 or avg_score > 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(self, anomalies: List[Dict[str, Any]], risk_level: RiskLevel) -> List[str]:
        """生成建议措施"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "立即启动应急响应预案",
                "暂停相关生产活动",
                "组织专家团队进行现场调查",
                "加强实时监控频率"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "增加数据采集频率",
                "检查设备运行状态",
                "分析异常数据模式",
                "制定预防措施"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "关注异常数据趋势",
                "定期检查系统状态",
                "优化数据采集流程"
            ])
        else:
            recommendations.extend([
                "继续正常监控",
                "定期维护检测系统"
            ])
        
        # 根据具体异常类型添加特定建议
        emission_anomalies = [a for a in anomalies if a.get("emission", 0) > 1000]
        if emission_anomalies:
            recommendations.append("检查排放控制设备运行状态")
        
        energy_anomalies = [a for a in anomalies if a.get("energy_consumption", 0) > 5000]
        if energy_anomalies:
            recommendations.append("优化能源使用效率")
        
        return recommendations
    
    def _generate_statistical_summary(self, anomalies: List[Dict[str, Any]], data: pd.DataFrame) -> Dict[str, Any]:
        """生成统计摘要"""
        if not anomalies:
            return {"message": "未检测到异常"}
        
        # 异常统计
        severity_counts = {}
        for anomaly in anomalies:
            severity = anomaly["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # 时间分布
        anomaly_dates = []
        for anomaly in anomalies:
            date_str = anomaly["date"]
            try:
                if isinstance(date_str, str):
                    # 尝试解析ISO格式日期
                    if 'T' in date_str or '-' in date_str:
                        parsed_date = datetime.fromisoformat(date_str)
                    else:
                        # 如果不是标准格式，使用当前时间
                        parsed_date = datetime.now()
                elif hasattr(date_str, 'isoformat'):
                    parsed_date = date_str
                elif isinstance(date_str, (int, float)):
                    # 如果是数字，使用当前时间
                    parsed_date = datetime.now()
                else:
                    parsed_date = datetime.now()
                anomaly_dates.append(parsed_date)
            except (ValueError, TypeError):
                # 如果解析失败，使用当前时间
                anomaly_dates.append(datetime.now())
        
        if not anomaly_dates:
            anomaly_dates = [datetime.now()]
        
        # 按月份统计
        monthly_counts = {}
        for date in anomaly_dates:
            month_key = date.strftime("%Y-%m")
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        return {
            "total_anomalies": len(anomalies),
            "severity_distribution": severity_counts,
            "monthly_distribution": monthly_counts,
            "anomaly_rate": len(anomalies) / len(data) * 100,
            "date_range": {
                "start": min(anomaly_dates).isoformat(),
                "end": max(anomaly_dates).isoformat()
            }
        } 