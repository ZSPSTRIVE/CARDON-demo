#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的碳循环功能测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    """主测试函数"""
    print("🚀 碳循环功能简单测试")
    print("=" * 40)
    
    try:
        # 1. 测试导入
        print("1. 测试模块导入...")
        from services.carbon_cycle import CarbonCycleModel
        print("   ✅ 导入成功")
        
        # 2. 测试模型创建
        print("2. 测试模型创建...")
        model = CarbonCycleModel()
        print("   ✅ 模型创建成功")
        
        # 3. 测试初始化
        print("3. 测试模型初始化...")
        model.initialize_models()
        if model.is_ready():
            print("   ✅ 模型初始化成功")
        else:
            print("   ❌ 模型初始化失败")
            return False
        
        # 4. 测试分析功能
        print("4. 测试碳循环分析...")
        result = model.analyze_carbon_cycle(
            region="华东",
            time_period=7,
            include_remote_sensing=True
        )
        
        if result.get("success"):
            print("   ✅ 分析成功")
            print(f"   碳汇总量: {result['carbon_sink']['total']:.2f}")
            print(f"   碳源总量: {result['carbon_source']['total']:.2f}")
            print(f"   净排放: {result['net_emission']:.2f}")
            
            if result.get("map_data"):
                map_path = result["map_data"].get("map_path", "")
                print(f"   地图路径: {map_path}")
        else:
            print(f"   ❌ 分析失败: {result.get('error')}")
            return False
        
        # 5. 测试地图生成
        print("5. 测试地图生成...")
        if result.get("map_data") and result["map_data"].get("map_path"):
            print("   ✅ 地图生成成功")
        else:
            print("   ⚠️ 地图生成可能有问题")
        
        print("\n🎉 所有测试通过！碳循环功能正常")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 