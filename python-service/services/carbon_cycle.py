import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
import os
import json
import folium
from shapely.geometry import Point, Polygon
import geopandas as gpd

import sys
import os
# 添加父目录到Python路径，确保可以导入models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import CarbonCycleRequest, CarbonCycleResponse

# 添加folium地图生成功能
import folium
from folium import plugins

class CarbonCycleModel:
    """碳循环分析模型"""
    
    def __init__(self):
        self.is_initialized = False
        self.region_data = {}
        self.vegetation_models = {}
        
        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        os.makedirs("maps", exist_ok=True)
    
    async def initialize_models(self):
        """初始化碳循环模型"""
        try:
            logger.info("开始初始化碳循环分析模型...")
            
            # 初始化地区数据
            self._initialize_region_data()
            
            # 初始化植被模型
            self._initialize_vegetation_models()
            
            self.is_initialized = True
            logger.info("碳循环分析模型初始化完成")
            
        except Exception as e:
            logger.error(f"碳循环分析模型初始化失败: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """检查模型是否准备就绪"""
        return self.is_initialized
    
    def _initialize_region_data(self):
        """初始化地区数据"""
        # 中国主要地区的基础数据
        self.region_data = {
            "全国": {
                "area": 9600000,  # 平方公里
                "population": 1400000000,
                "forest_coverage": 0.23,  # 森林覆盖率
                "grassland_coverage": 0.41,  # 草地覆盖率
                "wetland_coverage": 0.04,  # 湿地覆盖率
                "urban_coverage": 0.03,  # 城市覆盖率
                "baseline_carbon_sink": 1000,  # 基准碳汇量（万吨/年）
                "baseline_carbon_source": 1200,  # 基准碳源量（万吨/年）
                "center": [35.8617, 104.1954],  # 经纬度中心点
            },
            "华北": {
                "area": 1500000,
                "population": 200000000,
                "forest_coverage": 0.15,
                "grassland_coverage": 0.35,
                "wetland_coverage": 0.02,
                "urban_coverage": 0.08,
                "baseline_carbon_sink": 150,
                "baseline_carbon_source": 300,
                "center": [39.9042, 116.4074],
            },
            "华东": {
                "area": 1200000,
                "population": 250000000,
                "forest_coverage": 0.25,
                "grassland_coverage": 0.20,
                "wetland_coverage": 0.08,
                "urban_coverage": 0.12,
                "baseline_carbon_sink": 200,
                "baseline_carbon_source": 400,
                "center": [31.2304, 121.4737],
            },
            "华南": {
                "area": 800000,
                "population": 150000000,
                "forest_coverage": 0.45,
                "grassland_coverage": 0.15,
                "wetland_coverage": 0.06,
                "urban_coverage": 0.10,
                "baseline_carbon_sink": 300,
                "baseline_carbon_source": 200,
                "center": [23.1291, 113.2644],
            },
            "华中": {
                "area": 1000000,
                "population": 180000000,
                "forest_coverage": 0.30,
                "grassland_coverage": 0.25,
                "wetland_coverage": 0.05,
                "urban_coverage": 0.08,
                "baseline_carbon_sink": 180,
                "baseline_carbon_source": 250,
                "center": [30.5928, 114.3055],
            },
            "西南": {
                "area": 1100000,
                "population": 120000000,
                "forest_coverage": 0.40,
                "grassland_coverage": 0.30,
                "wetland_coverage": 0.03,
                "urban_coverage": 0.05,
                "baseline_carbon_sink": 250,
                "baseline_carbon_source": 180,
                "center": [30.5728, 104.0668],
            },
            "西北": {
                "area": 1300000,
                "population": 80000000,
                "forest_coverage": 0.10,
                "grassland_coverage": 0.50,
                "wetland_coverage": 0.02,
                "urban_coverage": 0.03,
                "baseline_carbon_sink": 100,
                "baseline_carbon_source": 150,
                "center": [36.0611, 103.8343],
            },
            "东北": {
                "area": 900000,
                "population": 100000000,
                "forest_coverage": 0.35,
                "grassland_coverage": 0.25,
                "wetland_coverage": 0.08,
                "urban_coverage": 0.06,
                "baseline_carbon_sink": 220,
                "baseline_carbon_source": 280,
                "center": [45.7417, 126.9620],
            }
        }
    
    def _initialize_vegetation_models(self):
        """初始化植被模型"""
        self.vegetation_models = {
            "forest": {
                "carbon_sequestration_rate": 2.5,  # 吨碳/公顷/年
                "growth_factor": 1.2,
                "seasonal_variation": 0.3
            },
            "grassland": {
                "carbon_sequestration_rate": 0.8,
                "growth_factor": 1.1,
                "seasonal_variation": 0.4
            },
            "wetland": {
                "carbon_sequestration_rate": 3.0,
                "growth_factor": 1.0,
                "seasonal_variation": 0.2
            },
            "urban": {
                "carbon_sequestration_rate": 0.1,
                "growth_factor": 0.9,
                "seasonal_variation": 0.1
            }
        }
    
    async def analyze_carbon_cycle(self, region: str, time_period: int = 365) -> Dict[str, Any]:
        """分析碳循环"""
        try:
            if not self.is_ready():
                raise RuntimeError("碳循环模型尚未初始化")
            
            if region not in self.region_data:
                raise ValueError(f"未找到地区: {region}")
            
            region_info = self.region_data[region]
            
            # 生成时间序列数据
            time_series = self._generate_time_series(time_period)
            
            # 计算碳汇
            carbon_sink_data = self._calculate_carbon_sink(region_info, time_series)
            
            # 计算碳源
            carbon_source_data = self._calculate_carbon_source(region_info, time_series)
            
            # 计算净碳平衡
            net_carbon_balance = []
            for i in range(len(time_series)):
                sink = carbon_sink_data[i]["total_sink"]
                source = carbon_source_data[i]["total_source"]
                net_balance = sink - source
                net_carbon_balance.append({
                    "date": time_series[i],
                    "net_balance": net_balance,
                    "sink": sink,
                    "source": source,
                    "balance_status": "positive" if net_balance > 0 else "negative"
                })
            
            # 计算碳汇潜力
            sequestration_potential = self._calculate_sequestration_potential(region_info)
            
            # 生成地图数据
            map_data = self._generate_map_data(region, carbon_sink_data, carbon_source_data, net_carbon_balance)
            
            # 分析时间趋势
            temporal_trends = self._analyze_temporal_trends(net_carbon_balance)
            
            # 导出分析报告
            report_path = await self.export_analysis_report(region, {
                "carbon_sink": carbon_sink_data,
                "carbon_source": carbon_source_data,
                "net_balance": net_carbon_balance,
                "sequestration_potential": sequestration_potential,
                "temporal_trends": temporal_trends
            })
            
            # 计算汇总数据
            total_sink = sum(d["total_sink"] for d in carbon_sink_data)
            total_source = sum(d["total_source"] for d in carbon_source_data)
            net_emission = total_source - total_sink
            
            return {
                "carbon_sink": {
                    "total": total_sink,
                    "forest": sum(d["forest_sink"] for d in carbon_sink_data),
                    "grassland": sum(d["grassland_sink"] for d in carbon_sink_data),
                    "wetland": sum(d["wetland_sink"] for d in carbon_sink_data)
                },
                "carbon_source": {
                    "total": total_source,
                    "industrial": sum(d["industrial_source"] for d in carbon_source_data),
                    "transportation": sum(d["transportation_source"] for d in carbon_source_data),
                    "agricultural": sum(d["agricultural_source"] for d in carbon_source_data)
                },
                "net_emission": net_emission,
                "sequestration_potential": sequestration_potential,
                "map_data": map_data,
                "temporal_trends": temporal_trends
            }
            
        except Exception as e:
            logger.error(f"碳循环分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "region": region,
                "time_period": time_period
            }
    
    def _generate_time_series(self, time_period: int) -> List[str]:
        """生成时间序列"""
        dates = []
        start_date = datetime.now() - timedelta(days=time_period)
        
        for i in range(time_period):
            date = start_date + timedelta(days=i)
            dates.append(date.isoformat())
        
        return dates
    
    def _calculate_carbon_sink(self, region_info: Dict[str, Any], time_series: List[str]) -> List[Dict[str, Any]]:
        """计算碳汇"""
        carbon_sink_data = []
        
        for i, date_str in enumerate(time_series):
            date = datetime.fromisoformat(date_str)
            month = date.month
            
            # 基础碳汇
            forest_sink = (region_info["forest_coverage"] * region_info["area"] * 100 * 
                          self.vegetation_models["forest"]["carbon_sequestration_rate"] / 10000)
            
            grassland_sink = (region_info["grassland_coverage"] * region_info["area"] * 100 * 
                             self.vegetation_models["grassland"]["carbon_sequestration_rate"] / 10000)
            
            wetland_sink = (region_info["wetland_coverage"] * region_info["area"] * 100 * 
                           self.vegetation_models["wetland"]["carbon_sequestration_rate"] / 10000)
            
            # 季节性调整
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * (month - 6) / 12)
            
            # 增长因子
            growth_factor = 1 + 0.01 * (i / len(time_series))
            
            # 随机波动
            noise = np.random.normal(1, 0.05)
            
            total_sink = (forest_sink + grassland_sink + wetland_sink) * seasonal_factor * growth_factor * noise
            
            carbon_sink_data.append({
                "date": date_str,
                "forest_sink": forest_sink * seasonal_factor * growth_factor * noise,
                "grassland_sink": grassland_sink * seasonal_factor * growth_factor * noise,
                "wetland_sink": wetland_sink * seasonal_factor * growth_factor * noise,
                "total_sink": total_sink,
                "seasonal_factor": seasonal_factor,
                "growth_factor": growth_factor
            })
        
        return carbon_sink_data
    
    def _calculate_carbon_source(self, region_info: Dict[str, Any], time_series: List[str]) -> List[Dict[str, Any]]:
        """计算碳源"""
        carbon_source_data = []
        
        for i, date_str in enumerate(time_series):
            date = datetime.fromisoformat(date_str)
            month = date.month
            
            # 基础碳源
            baseline_source = region_info["baseline_carbon_source"]
            
            # 季节性调整（冬季供暖等）
            seasonal_factor = 1 + 0.4 * np.cos(2 * np.pi * (month - 1) / 12)
            
            # 人口增长因子
            population_factor = 1 + 0.005 * (i / len(time_series))
            
            # 政策减排因子
            policy_factor = 1 - 0.002 * (i / len(time_series))
            
            # 随机波动
            noise = np.random.normal(1, 0.1)
            
            total_source = baseline_source * seasonal_factor * population_factor * policy_factor * noise
            
            carbon_source_data.append({
                "date": date_str,
                "baseline_source": baseline_source,
                "seasonal_factor": seasonal_factor,
                "population_factor": population_factor,
                "policy_factor": policy_factor,
                "total_source": total_source
            })
        
        return carbon_source_data
    
    def _calculate_sequestration_potential(self, region_info: Dict[str, Any]) -> Dict[str, Any]:
        """计算碳汇潜力"""
        current_forest = region_info["forest_coverage"]
        current_grassland = region_info["grassland_coverage"]
        
        # 理论最大覆盖率
        max_forest = 0.35
        max_grassland = 0.50
        
        # 计算潜力
        forest_potential = (max_forest - current_forest) * region_info["area"] * 100 * 2.5 / 10000
        grassland_potential = (max_grassland - current_grassland) * region_info["area"] * 100 * 0.8 / 10000
        
        total_potential = forest_potential + grassland_potential
        
        return {
            "forest_potential": forest_potential,
            "grassland_potential": grassland_potential,
            "total_potential": total_potential,
            "current_forest_coverage": current_forest,
            "current_grassland_coverage": current_grassland,
            "max_forest_coverage": max_forest,
            "max_grassland_coverage": max_grassland
        }
    
    def _generate_map_data(self, region: str, carbon_sink_data: List[Dict[str, Any]], 
                          carbon_source_data: List[Dict[str, Any]], 
                          net_balance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成地图数据"""
        try:
            # 获取地区中心点
            center = self._get_region_center(region)
            
            # 创建地图
            m = folium.Map(location=center, zoom_start=6, tiles='OpenStreetMap')
            
            # 添加地区边界
            region_geojson = self._get_region_geojson(region)
            if region_geojson:
                folium.GeoJson(
                    region_geojson,
                    name=region,
                    style_function=lambda x: {
                        'fillColor': '#3388ff',
                        'color': '#3388ff',
                        'weight': 2,
                        'fillOpacity': 0.1
                    }
                ).add_to(m)
            
            # 添加碳汇点
            for i, sink_data in enumerate(carbon_sink_data[-10:]):  # 最近10天
                if i % 2 == 0:  # 每隔一天添加一个点
                    folium.CircleMarker(
                        location=[center[0] + np.random.normal(0, 0.5), 
                                center[1] + np.random.normal(0, 0.5)],
                        radius=10,
                        popup=f"碳汇: {sink_data['total_sink']:.2f}万吨",
                        color='green',
                        fill=True,
                        fillColor='green',
                        fillOpacity=0.7
                    ).add_to(m)
            
            # 添加碳源点
            for i, source_data in enumerate(carbon_source_data[-10:]):
                if i % 2 == 0:
                    folium.CircleMarker(
                        location=[center[0] + np.random.normal(0, 0.5), 
                                center[1] + np.random.normal(0, 0.5)],
                        radius=8,
                        popup=f"碳源: {source_data['total_source']:.2f}万吨",
                        color='red',
                        fill=True,
                        fillColor='red',
                        fillOpacity=0.7
                    ).add_to(m)
            
            # 添加图例
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 150px; height: 90px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><b>碳循环图例</b></p>
            <p><span style="color:green;">●</span> 碳汇点</p>
            <p><span style="color:red;">●</span> 碳源点</p>
            <p><span style="color:blue;">■</span> 地区边界</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # 保存地图
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            map_filename = f"carbon_cycle_{region}_{timestamp}.html"
            map_path = os.path.join("maps", map_filename)
            
            m.save(map_path)
            logger.info(f"地图已保存: {map_path}")
            
            return {
                "map_path": map_path,
                "map_filename": map_filename,
                "center": center,
                "zoom_level": 6,
                "layers_count": 3
            }
            
        except Exception as e:
            logger.error(f"地图生成失败: {e}")
            return {
                "error": str(e),
                "center": [35.8617, 104.1954],
                "zoom_level": 6
            }
    
    def _get_region_center(self, region: str) -> List[float]:
        """获取地区中心点"""
        if region in self.region_data:
            return self.region_data[region].get("center", [35.8617, 104.1954])
        return [35.8617, 104.1954]  # 默认中国中心
    
    def _get_region_geojson(self, region: str) -> Optional[Dict[str, Any]]:
        """获取地区GeoJSON数据"""
        # 简化的地区边界数据
        region_boundaries = {
            "全国": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [73.0, 18.0], [135.0, 18.0], [135.0, 54.0], [73.0, 54.0], [73.0, 18.0]
                    ]]
                },
                "properties": {"name": "全国"}
            },
            "华北": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [110.0, 35.0], [120.0, 35.0], [120.0, 45.0], [110.0, 45.0], [110.0, 35.0]
                    ]]
                },
                "properties": {"name": "华北"}
            }
        }
        
        return region_boundaries.get(region)
    
    def _analyze_temporal_trends(self, net_balance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析时间趋势"""
        if not net_balance_data:
            return {"trend": "unknown", "description": "无数据"}
        
        balances = [d["net_balance"] for d in net_balance_data]
        
        if len(balances) < 2:
            return {"trend": "stable", "description": "数据不足"}
        
        # 计算趋势
        x = np.arange(len(balances))
        slope, intercept = np.polyfit(x, balances, 1)
        
        # 趋势分类
        if slope > 0.1:
            trend = "improving"
            description = "碳平衡状况正在改善"
        elif slope < -0.1:
            trend = "worsening"
            description = "碳平衡状况正在恶化"
        else:
            trend = "stable"
            description = "碳平衡状况相对稳定"
        
        # 计算统计信息
        mean_balance = np.mean(balances)
        std_balance = np.std(balances)
        positive_days = sum(1 for b in balances if b > 0)
        negative_days = sum(1 for b in balances if b < 0)
        
        return {
            "trend": trend,
            "description": description,
            "slope": slope,
            "mean_balance": mean_balance,
            "std_balance": std_balance,
            "positive_days": positive_days,
            "negative_days": negative_days,
            "total_days": len(balances),
            "improvement_rate": positive_days / len(balances) if len(balances) > 0 else 0
        }
    
    async def export_analysis_report(self, region: str, analysis_data: Dict[str, Any]) -> str:
        """导出分析报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"carbon_cycle_report_{region}_{timestamp}.json"
            report_path = os.path.join("data", report_filename)
            
            # 准备报告数据
            report = {
                "region": region,
                "analysis_date": datetime.now().isoformat(),
                "summary": {
                    "total_days": len(analysis_data.get("net_balance", [])),
                    "average_sink": np.mean([d["total_sink"] for d in analysis_data.get("carbon_sink", [])]) if analysis_data.get("carbon_sink") else 0,
                    "average_source": np.mean([d["total_source"] for d in analysis_data.get("carbon_source", [])]) if analysis_data.get("carbon_source") else 0,
                    "net_balance_trend": analysis_data.get("temporal_trends", {}).get("trend", "unknown")
                },
                "detailed_data": analysis_data
            }
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析报告已导出: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"报告导出失败: {e}")
            return ""


# ----------------------
# 脚本运行入口
# ----------------------
if __name__ == "__main__":
    import asyncio

    async def main():
        model = CarbonCycleModel()
        await model.initialize_models()
        if model.is_ready():
            region = "华东"
            result = await model.analyze_carbon_cycle(region=region, time_period=5)
            report_path = result["report_path"]
            print(f"分析报告生成成功: {report_path}")
            print(f"地图路径: {result['map_data']['map_path']}")
        else:
            print("模型初始化失败，无法运行分析")

    asyncio.run(main())
