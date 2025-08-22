#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碳循环服务启动脚本
"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 确保必要的目录存在
os.makedirs("maps", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

if __name__ == "__main__":
    print("🚀 启动碳循环服务...")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"🗺️ 地图目录: {os.path.abspath('maps')}")
    print(f"📊 数据目录: {os.path.abspath('data')}")
    print(f"📝 日志目录: {os.path.abspath('logs')}")
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 