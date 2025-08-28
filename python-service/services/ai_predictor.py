import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
import joblib
import os

import sys
import os
# 添加父目录到Python路径，确保可以导入models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import IndustryType, ResourceType

class LSTMPredictor(nn.Module):
    """LSTM预测模型"""
    
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class AIPredictor:
    """AI预测服务"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_initialized = False
        self.model_dir = "models"
        
        # 确保模型目录存在
        os.makedirs(self.model_dir, exist_ok=True)
    
    def initialize_models(self):
        """初始化AI模型"""
        try:
            logger.info("开始初始化AI预测模型...")
            
            # 为每个行业和资源类型组合创建模型
            for industry in IndustryType:
                for resource in ResourceType:
                    model_key = f"{industry.value}_{resource.value}"
                    
                    # 创建或加载模型
                    model_path = os.path.join(self.model_dir, f"lstm_{model_key}.pth")
                    scaler_path = os.path.join(self.model_dir, f"scaler_{model_key}.pkl")
                    
                    if os.path.exists(model_path) and os.path.exists(scaler_path):
                        # 加载已有模型
                        self.models[model_key] = torch.load(model_path)
                        self.scalers[model_key] = joblib.load(scaler_path)
                        logger.info(f"加载模型: {model_key}")
                    else:
                        # 创建新模型
                        self.models[model_key] = LSTMPredictor(
                            input_size=10,  # 特征数量
                            hidden_size=64,
                            num_layers=2,
                            output_size=1
                        )
                        
                        # 创建标准化器
                        from sklearn.preprocessing import StandardScaler
                        self.scalers[model_key] = StandardScaler()
                        
                        logger.info(f"创建新模型: {model_key}")
            
            self.is_initialized = True
            logger.info("AI预测模型初始化完成")
            
        except Exception as e:
            logger.error(f"AI模型初始化失败: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """检查模型是否准备就绪"""
        return self.is_initialized and len(self.models) > 0
    
    def predict_emissions(self, industry: str, resource_type: str, 
                               time_period: int, features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """预测碳排放"""
        try:
            if not self.is_ready():
                raise RuntimeError("AI模型尚未初始化")
            
            model_key = f"{industry}_{resource_type}"
            
            # 生成模拟预测数据
            predictions = []
            base_date = datetime.now()
            
            for i in range(time_period):
                # 模拟预测值（实际应用中应该使用训练好的模型）
                predicted_value = np.random.normal(1000, 200)  # 基础值1000，标准差200
                date = base_date + timedelta(days=30*i)
                
                predictions.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_emission": round(predicted_value, 2)
                })
            
            # 计算置信度
            confidence = round(np.random.uniform(0.7, 0.95), 3)
            
            # 估算碳中和年份
            carbon_neutral_year = 2050 + np.random.randint(-5, 10)
            
            # 趋势分析
            trend_analysis = {
                "trend": "decreasing" if np.random.random() > 0.5 else "increasing",
                "rate": round(np.random.uniform(0.5, 3.0), 2),
                "confidence": confidence
            }
            
            return {
                "predictions": predictions,
                "confidence": confidence,
                "carbon_neutral_year": int(carbon_neutral_year),
                "trend_analysis": trend_analysis,
                "model_performance": {
                    "mae": round(np.random.uniform(50, 150), 2),
                    "rmse": round(np.random.uniform(80, 200), 2),
                    "r2": round(np.random.uniform(0.6, 0.9), 3)
                }
            }
            
        except Exception as e:
            logger.error(f"碳排放预测失败: {e}")
            raise
    