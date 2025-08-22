#!/usr/bin/env python3
"""
测试导入是否正常工作的脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """测试所有必要的导入"""
    try:
        print("开始测试导入...")
        
        # 测试models.schemas导入
        print("1. 测试 models.schemas 导入...")
        from models.schemas import (
            DataCollectionRequest, SourceType, IndustryType,
            PredictionRequest, ResourceType,
            AnomalyRequest, RiskLevel,
            CarbonCycleRequest, CarbonCycleResponse
        )
        print("   ✓ models.schemas 导入成功")
        
        # 测试services导入
        print("2. 测试 services 导入...")
        from services.data_collector import DataCollector
        from services.ai_predictor import AIPredictor
        from services.anomaly_detector import AnomalyDetector
        from services.carbon_cycle import CarbonCycleModel
        print("   ✓ services 导入成功")
        
        # 测试实例化
        print("3. 测试类实例化...")
        data_collector = DataCollector()
        ai_predictor = AIPredictor()
        anomaly_detector = AnomalyDetector()
        carbon_cycle_model = CarbonCycleModel()
        print("   ✓ 类实例化成功")
        
        print("\n🎉 所有导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print(f"   当前Python路径: {sys.path}")
        print(f"   当前工作目录: {os.getcwd()}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ 系统准备就绪，可以启动服务")
    else:
        print("\n❌ 系统存在问题，请检查导入路径")
        sys.exit(1) 