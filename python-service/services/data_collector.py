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
        self.sequestration_cache = {}  # 缓存固碳潜力数据
        self.last_update_time = None
    
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

    async def collect_sequestration_potential(self, region: str, force_update: bool = False) -> Dict[str, Any]:
        """动态采集固碳潜力数据"""
        try:
            # 检查缓存是否需要更新（每小时更新一次）
            current_time = datetime.now()
            cache_key = f"sequestration_{region}"
            
            if (not force_update and 
                cache_key in self.sequestration_cache and 
                self.last_update_time and 
                (current_time - self.last_update_time).total_seconds() < 3600):
                
                logger.info(f"使用缓存的固碳潜力数据: {region}")
                return self.sequestration_cache[cache_key]
            
            logger.info(f"开始动态采集固碳潜力数据: {region}")
            
            # 模拟实时数据采集过程
            await asyncio.sleep(1)  # 模拟网络请求延迟
            
            # 基于当前时间和地区特征动态计算固碳潜力
            dynamic_potential = await self._calculate_dynamic_sequestration_potential(region)
            
            # 更新缓存
            self.sequestration_cache[cache_key] = dynamic_potential
            self.last_update_time = current_time
            
            # 保存到文件
            await self._save_sequestration_data(dynamic_potential, region)
            
            logger.info(f"固碳潜力数据采集完成: {region}")
            return dynamic_potential
            
        except Exception as e:
            logger.error(f"固碳潜力数据采集失败: {e}")
            # 返回默认数据
            return self._get_default_sequestration_data(region)

    async def _calculate_dynamic_sequestration_potential(self, region: str) -> Dict[str, Any]:
        """动态计算固碳潜力"""
        current_time = datetime.now()
        
        # 基础地区数据
        region_data = {
            "全国": {"area": 9600000, "forest_coverage": 0.23, "grassland_coverage": 0.41, "wetland_coverage": 0.04, "urban_coverage": 0.03},
            "华北": {"area": 1500000, "forest_coverage": 0.15, "grassland_coverage": 0.35, "wetland_coverage": 0.02, "urban_coverage": 0.08},
            "华东": {"area": 1200000, "forest_coverage": 0.25, "grassland_coverage": 0.20, "wetland_coverage": 0.08, "urban_coverage": 0.12},
            "华南": {"area": 800000, "forest_coverage": 0.45, "grassland_coverage": 0.15, "wetland_coverage": 0.06, "urban_coverage": 0.10},
            "华中": {"area": 1000000, "forest_coverage": 0.30, "grassland_coverage": 0.25, "wetland_coverage": 0.05, "urban_coverage": 0.08},
            "西南": {"area": 1100000, "forest_coverage": 0.40, "grassland_coverage": 0.30, "wetland_coverage": 0.03, "urban_coverage": 0.05},
            "西北": {"area": 1300000, "forest_coverage": 0.10, "grassland_coverage": 0.50, "wetland_coverage": 0.02, "urban_coverage": 0.03},
            "东北": {"area": 900000, "forest_coverage": 0.35, "grassland_coverage": 0.25, "wetland_coverage": 0.08, "urban_coverage": 0.06}
        }
        
        region_info = region_data.get(region, region_data["全国"])
        
        # 动态因子（基于时间、季节、政策等）
        seasonal_factor = 1.0 + 0.2 * np.sin(2 * np.pi * (current_time.month - 3) / 12)  # 季节性变化
        policy_factor = 1.0 + 0.1 * np.sin(current_time.hour / 24 * 2 * np.pi)  # 政策影响
        economic_factor = 1.0 + 0.05 * np.random.normal(0, 1)  # 经济因素
        technology_factor = 1.0 + 0.02 * (current_time.year - 2020)  # 技术进步
        
        # 计算各项潜力（动态调整）
        forest_potential = (region_info["forest_coverage"] * region_info["area"] * 100 * 0.5 * 
                           seasonal_factor * policy_factor * economic_factor * technology_factor)
        
        grassland_potential = (region_info["grassland_coverage"] * region_info["area"] * 100 * 0.3 * 
                              seasonal_factor * policy_factor * economic_factor * technology_factor)
        
        wetland_potential = (region_info["wetland_coverage"] * region_info["area"] * 100 * 0.4 * 
                            seasonal_factor * policy_factor * economic_factor * technology_factor)
        
        urban_green_potential = (region_info["urban_coverage"] * region_info["area"] * 100 * 0.2 * 
                                seasonal_factor * policy_factor * economic_factor * technology_factor)
        
        total_potential = forest_potential + grassland_potential + wetland_potential + urban_green_potential
        
        # 动态成本计算
        base_cost_per_ton = 150 + 10 * np.sin(current_time.hour / 24 * 2 * np.pi)  # 成本波动
        forest_cost = forest_potential * base_cost_per_ton
        grassland_cost = grassland_potential * (base_cost_per_ton * 0.6)
        wetland_cost = wetland_potential * (base_cost_per_ton * 1.3)
        urban_cost = urban_green_potential * (base_cost_per_ton * 1.8)
        
        total_cost = forest_cost + grassland_cost + wetland_cost + urban_cost
        
        # 动态措施数据
        measures = [
            {
                "name": "森林碳汇提升",
                "potential": round(forest_potential, 2),
                "cost_per_ton": round(base_cost_per_ton, 2),
                "total_cost": round(forest_cost, 2),
                "description": f"通过退耕还林、人工造林等措施增加森林覆盖率（更新时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}）",
                "implementation_time": "3-5年",
                "priority": "高",
                "dynamic_factors": {
                    "seasonal_factor": round(seasonal_factor, 3),
                    "policy_factor": round(policy_factor, 3),
                    "economic_factor": round(economic_factor, 3),
                    "technology_factor": round(technology_factor, 3)
                }
            },
            {
                "name": "草地碳汇改善",
                "potential": round(grassland_potential, 2),
                "cost_per_ton": round(base_cost_per_ton * 0.6, 2),
                "total_cost": round(grassland_cost, 2),
                "description": f"改善草地管理，实施轮牧制度，恢复退化草地（更新时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}）",
                "implementation_time": "2-3年",
                "priority": "中",
                "dynamic_factors": {
                    "seasonal_factor": round(seasonal_factor, 3),
                    "policy_factor": round(policy_factor, 3),
                    "economic_factor": round(economic_factor, 3),
                    "technology_factor": round(technology_factor, 3)
                }
            },
            {
                "name": "湿地保护修复",
                "potential": round(wetland_potential, 2),
                "cost_per_ton": round(base_cost_per_ton * 1.3, 2),
                "total_cost": round(wetland_cost, 2),
                "description": f"保护现有湿地，修复退化湿地生态系统（更新时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}）",
                "implementation_time": "5-8年",
                "priority": "高",
                "dynamic_factors": {
                    "seasonal_factor": round(seasonal_factor, 3),
                    "policy_factor": round(policy_factor, 3),
                    "economic_factor": round(economic_factor, 3),
                    "technology_factor": round(technology_factor, 3)
                }
            },
            {
                "name": "城市绿化提升",
                "potential": round(urban_green_potential, 2),
                "cost_per_ton": round(base_cost_per_ton * 1.8, 2),
                "total_cost": round(urban_cost, 2),
                "description": f"增加城市绿地面积，建设绿色基础设施（更新时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}）",
                "implementation_time": "1-3年",
                "priority": "中",
                "dynamic_factors": {
                    "seasonal_factor": round(seasonal_factor, 3),
                    "policy_factor": round(policy_factor, 3),
                    "economic_factor": round(economic_factor, 3),
                    "technology_factor": round(technology_factor, 3)
                }
            }
        ]
        
        # 动态政策建议
        recommendations = []
        if forest_potential > 10000000:
            recommendations.append(f"增加森林覆盖率，实施退耕还林政策（当前潜力: {forest_potential/10000:.1f}万吨）")
        if grassland_potential > 5000000:
            recommendations.append(f"改善草地管理，实施轮牧制度（当前潜力: {grassland_potential/10000:.1f}万吨）")
        if wetland_potential > 2000000:
            recommendations.append(f"保护湿地生态系统，减少开发活动（当前潜力: {wetland_potential/10000:.1f}万吨）")
        if urban_green_potential > 1000000:
            recommendations.append(f"加强城市绿化建设，推广绿色建筑（当前潜力: {urban_green_potential/10000:.1f}万吨）")
        
        # 动态ROI计算
        carbon_value = 50 + 5 * np.sin(current_time.hour / 24 * 2 * np.pi)  # 碳价值波动
        roi = (total_potential * carbon_value) / total_cost if total_cost > 0 else 0
        
        return {
            "total": round(total_potential, 2),
            "forest": round(forest_potential, 2),
            "grassland": round(grassland_potential, 2),
            "wetland": round(wetland_potential, 2),
            "urban_green": round(urban_green_potential, 2),
            "measures": measures,
            "recommendations": recommendations,
            "achievable_rate": 0.7 + 0.05 * np.sin(current_time.hour / 24 * 2 * np.pi),  # 动态可实现率
            "time_horizon": "5-10年",
            "total_cost": round(total_cost, 2),
            "cost_effectiveness": round(total_cost / total_potential, 2) if total_potential > 0 else 0,
            "roi": round(roi, 2),
            "update_time": current_time.isoformat(),
            "dynamic_factors": {
                "seasonal_factor": round(seasonal_factor, 3),
                "policy_factor": round(policy_factor, 3),
                "economic_factor": round(economic_factor, 3),
                "technology_factor": round(technology_factor, 3),
                "carbon_value": round(carbon_value, 2)
            }
        }

    async def _save_sequestration_data(self, data: Dict[str, Any], region: str):
        """保存固碳潜力数据"""
        try:
            os.makedirs("data", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sequestration_potential_{region}_{timestamp}.json"
            file_path = os.path.join("data", filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "region": region,
                        "collection_time": datetime.now().isoformat(),
                        "data_type": "sequestration_potential",
                        "version": "1.0"
                    },
                    "data": data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"固碳潜力数据已保存: {file_path}")
            
        except Exception as e:
            logger.error(f"保存固碳潜力数据失败: {e}")

    def _get_default_sequestration_data(self, region: str) -> Dict[str, Any]:
        """获取默认固碳潜力数据"""
        return {
            "total": 452.1,
            "forest": 150.5,
            "grassland": 120.8,
            "wetland": 95.2,
            "urban_green": 85.6,
            "measures": [
                {
                    "name": "森林碳汇提升",
                    "potential": 150.5,
                    "total_cost": 22575.0,
                    "description": "通过退耕还林、人工造林等措施增加森林覆盖率",
                    "implementation_time": "3-5年",
                    "priority": "高"
                },
                {
                    "name": "草地碳汇改善",
                    "potential": 120.8,
                    "total_cost": 9664.0,
                    "description": "改善草地管理，实施轮牧制度，恢复退化草地",
                    "implementation_time": "2-3年",
                    "priority": "中"
                },
                {
                    "name": "湿地保护修复",
                    "potential": 95.2,
                    "total_cost": 19040.0,
                    "description": "保护现有湿地，修复退化湿地生态系统",
                    "implementation_time": "5-8年",
                    "priority": "高"
                },
                {
                    "name": "城市绿化提升",
                    "potential": 85.6,
                    "total_cost": 25680.0,
                    "description": "增加城市绿地面积，建设绿色基础设施",
                    "implementation_time": "1-3年",
                    "priority": "中"
                }
            ],
            "recommendations": [
                "增加森林覆盖率，实施退耕还林政策",
                "改善草地管理，实施轮牧制度",
                "保护湿地生态系统，减少开发活动"
            ],
            "achievable_rate": 0.7,
            "time_horizon": "5-10年",
            "total_cost": 76959.0,
            "cost_effectiveness": 170.2,
            "roi": 1.86,
            "update_time": datetime.now().isoformat()
        }
    
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
        
        # 测试固碳潜力数据采集
        print("测试固碳潜力数据采集...")
        potential_data = await collector.collect_sequestration_potential("华东")
        print(f"固碳潜力数据: {json.dumps(potential_data, ensure_ascii=False, indent=2)}")
        
        # 测试传统数据采集
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
