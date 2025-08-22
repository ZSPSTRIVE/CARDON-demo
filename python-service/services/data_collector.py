import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from loguru import logger
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

import sys
import os
# 添加父目录到Python路径，确保可以导入models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import DataCollectionRequest, SourceType, IndustryType


# ------------------- 数据采集器 -------------------
class DataCollector:
    """数据采集服务"""
    
    def __init__(self):
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def collect_data(self, request: DataCollectionRequest):
        """执行数据采集"""
        task_id = f"collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.active_tasks[task_id] = {
                "status": "running",
                "progress": 0,
                "start_time": datetime.now(),
                "request": request.model_dump()
            }
            
            logger.info(f"开始数据采集任务: {task_id}")
            
            # 根据数据源类型执行相应采集
            if request.source_type == SourceType.WEB_SCRAPING:
                result = await self._collect_web_data(request)
            elif request.source_type == SourceType.ENERGY_LOGS:
                result = await self._collect_energy_logs(request)
            elif request.source_type == SourceType.REMOTE_SENSING:
                result = await self._collect_remote_sensing_data(request)
            else:
                result = await self._collect_public_data(request)
            
            # 保存采集结果
            file_path = await self._save_collected_data(result, request, task_id)
            
            # 更新任务状态
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["progress"] = 100
            self.active_tasks[task_id]["result"] = {
                "data_count": len(result),
                "file_path": file_path,
                "collection_time": datetime.now().isoformat()
            }
            
            # 移动到已完成任务
            self.completed_tasks[task_id] = self.active_tasks.pop(task_id)
            
            logger.info(f"数据采集任务完成: {task_id}, 数据量: {len(result)}")
            
        except Exception as e:
            logger.error(f"数据采集任务失败: {task_id}, 错误: {e}")
            
            # 更新任务状态
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
            
            # 移动到失败任务
            self.failed_tasks[task_id] = self.active_tasks.pop(task_id)
    
    async def _collect_web_data(self, request: DataCollectionRequest) -> List[Dict[str, Any]]:
        """网络数据爬取（真实 OWID 碳排放数据 URL）"""
        logger.info("开始采集网络数据")
        await asyncio.sleep(2)
        
        web_data = []
        base_time = datetime.now()
        for i in range(50):
            timestamp = base_time - timedelta(hours=i)
            web_data.append({
                "timestamp": timestamp.isoformat(),
                "source_url": "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv",
                "data_type": "web_scraping",
                "value": np.random.normal(100, 20),  # 模拟数值
                "unit": "吨",
                "industry": request.industry.value if request.industry else "unknown"
            })
        
        return web_data
    
    async def _collect_energy_logs(self, request: DataCollectionRequest) -> List[Dict[str, Any]]:
        logger.info("开始采集能源日志数据")
        await asyncio.sleep(2)
        
        energy_data = []
        base_time = datetime.now()
        for i in range(100):
            timestamp = base_time - timedelta(hours=i)
            energy_data.append({
                "timestamp": timestamp.isoformat(),
                "energy_consumption": np.random.normal(1000, 200),
                "emission_factor": np.random.normal(0.5, 0.1),
                "industry": request.industry.value if request.industry else "unknown",
                "region": request.region or "unknown"
            })
        return energy_data
    
    async def _collect_remote_sensing_data(self, request: DataCollectionRequest) -> List[Dict[str, Any]]:
        logger.info("开始采集遥感数据")
        await asyncio.sleep(3)
        
        remote_data = []
        base_time = datetime.now()
        for i in range(50):
            timestamp = base_time - timedelta(days=i)
            remote_data.append({
                "timestamp": timestamp.isoformat(),
                "ndvi": np.random.normal(0.6, 0.2),
                "land_surface_temperature": np.random.normal(25, 10),
                "carbon_flux": np.random.normal(0, 5),
                "region": request.region or "unknown",
                "spatial_resolution": "1km"
            })
        return remote_data
    
    async def _collect_public_data(self, request: DataCollectionRequest) -> List[Dict[str, Any]]:
        logger.info("开始采集公开数据")
        await asyncio.sleep(2)
        
        public_data = []
        base_time = datetime.now()
        for i in range(80):
            timestamp = base_time - timedelta(days=i)
            public_data.append({
                "timestamp": timestamp.isoformat(),
                "gdp": np.random.normal(100000, 20000),
                "population": np.random.normal(1000000, 200000),
                "emission_intensity": np.random.normal(0.8, 0.3),
                "region": request.region or "unknown",
                "data_source": "government_open_data"
            })
        return public_data
    
    async def _save_collected_data(self, data: List[Dict[str, Any]], request: DataCollectionRequest,
                                   task_id: str) -> str:
        os.makedirs("data", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"collected_data_{request.source_type.value}_{timestamp}_{task_id}.json"
        file_path = os.path.join("data", filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "collection_time": datetime.now().isoformat(),
                    "source_type": request.source_type.value,
                    "industry": request.industry.value if request.industry else None,
                    "region": request.region,
                    "data_count": len(data)
                },
                "data": data
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {file_path}")
        return file_path
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        return list(self.active_tasks.values())
    
    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        return list(self.completed_tasks.values())
    
    def get_failed_tasks(self) -> List[Dict[str, Any]]:
        return list(self.failed_tasks.values()) 


# ------------------- 测试运行 -------------------
if __name__ == "__main__":
    async def main():
        collector = DataCollector()
        request = DataCollectionRequest(
            model_type="linear_regression",
            model_performance=0.95,
            source_type=SourceType.WEB_SCRAPING,
            industry=IndustryType.POWER,
            region="Beijing"
        )
        await collector.collect_data(request)
        print("已完成任务:", collector.get_completed_tasks())


    asyncio.run(main())
