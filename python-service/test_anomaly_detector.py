#!/usr/bin/env python3
"""
测试异常检测功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.anomaly_detector import AnomalyDetector
from models.schemas import IndustryType

async def test_anomaly_detection():
    """测试异常检测功能"""
    print("🧪 开始测试异常检测功能...")
    
    try:
        # 创建异常检测器实例
        detector = AnomalyDetector()
        
        # 初始化模型
        await detector.initialize_models()
        print("✅ 模型初始化成功")
        
        # 测试异常检测
        print("🔍 测试异常检测...")
        result = await detector.detect_anomalies(IndustryType.ENERGY, 30)
        
        print("📊 检测结果:")
        print(f"   - 异常数量: {len(result.get('anomalies', []))}")
        print(f"   - 风险等级: {result.get('risk_level', 'unknown')}")
        print(f"   - 建议数量: {len(result.get('recommendations', []))}")
        
        if 'anomalies' in result and result['anomalies']:
            print("   - 第一个异常:")
            first_anomaly = result['anomalies'][0]
            print(f"     日期: {first_anomaly.get('date', 'N/A')}")
            print(f"     分数: {first_anomaly.get('anomaly_score', 'N/A')}")
            print(f"     原因: {first_anomaly.get('reasons', [])}")
        
        print("🎉 异常检测测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    
    # 运行测试
    success = asyncio.run(test_anomaly_detection())
    
    if success:
        print("\n✅ 所有测试通过！异常检测功能正常工作")
    else:
        print("\n❌ 测试失败，请检查错误信息") 