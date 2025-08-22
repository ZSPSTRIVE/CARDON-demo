#!/usr/bin/env python3
"""
碳排放AI分析服务启动脚本
"""

import os
import sys
import uvicorn
from loguru import logger

def main():
    """主函数"""
    # 配置日志
    logger.add(
        "logs/startup.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    logger.info("正在启动碳排放AI分析服务...")
    
    # 检查必要的目录
    required_dirs = ["logs", "data", "models", "maps", "templates"]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.info(f"确保目录存在: {dir_name}")
    
    # 检查依赖
    try:
        import torch
        import pandas
        import numpy
        import fastapi
        logger.info("所有依赖包检查通过")
    except ImportError as e:
        logger.error(f"依赖包缺失: {e}")
        logger.error("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 启动服务
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 