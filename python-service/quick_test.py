#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试碳循环功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入"""
    try:
        print("🔍 测试模块导入...")
        
        # 测试基础模块
        import numpy as np
        import pandas as pd
        import folium
        print("✅ 基础模块导入成功")
        
        # 测试项目模块
        from models.schemas import CarbonCycleRequest, CarbonCycleResponse
        print("✅ 数据模型导入成功")
        
        from services.carbon_cycle import CarbonCycleModel
        print("✅ 碳循环服务导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_model_creation():
    """测试模型创建"""
    try:
        print("\n🔍 测试模型创建...")
        
        from services.carbon_cycle import CarbonCycleModel
        
        # 测试模型创建
        model = CarbonCycleModel()
        print("✅ 模型实例创建成功")
        
        # 测试初始化
        model.initialize_models()
        if model.is_ready():
            print("✅ 模型初始化成功")
            
            # 测试分析功能
            try:
                result = model.analyze_carbon_cycle(
                    region="华东",
                    time_period=7,  # 7天
                    include_remote_sensing=True
                )
                if result.get("success"):
                    print("✅ 碳循环分析功能正常")
                else:
                    print(f"⚠️ 碳循环分析返回错误: {result.get('error')}")
            except Exception as e:
                print(f"⚠️ 碳循环分析异常: {e}")
        else:
            print("❌ 模型初始化失败")
            return False
        
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        return False

def test_data_structures():
    """测试数据结构"""
    try:
        print("\n🔍 测试数据结构...")
        
        from models.schemas import CarbonCycleRequest, CarbonCycleResponse
        
        # 测试请求模型
        request = CarbonCycleRequest(
            region="华东",
            time_period=30,
            include_remote_sensing=True
        )
        print("✅ 请求模型创建成功")
        
        # 测试响应模型
        response = CarbonCycleResponse(
            success=True,
            carbon_sink={"total": 100.0, "forest": 50.0, "grassland": 30.0, "wetland": 20.0},
            carbon_source={"total": 80.0, "industrial": 40.0, "transportation": 25.0, "agricultural": 15.0},
            net_emission=-20.0,
            sequestration_potential={"total": 50.0},
            map_data={"map_path": "/maps/test.html"},
            temporal_trends=[{"trend": "improving"}]
        )
        print("✅ 响应模型创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据结构测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 碳循环功能快速测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("模型创建", test_model_creation),
        ("数据结构", test_data_structures)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！碳循环功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 