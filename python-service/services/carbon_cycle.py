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
from services.data_collector import DataCollector

# 添加folium地图生成功能
import folium
from folium import plugins

class CarbonCycleModel:
    """碳循环分析模型"""

    def __init__(self):
        self.is_initialized = False
        self.region_data = {}
        self.vegetation_models = {}
        self.data_collector = DataCollector()  # 集成数据采集器

        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        os.makedirs("maps", exist_ok=True)

    def initialize_models(self):
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
            },
            "industrial": {
                "emission_rate": 1.5 # 吨碳/平方公里/年
            },
            "transportation": {
                "emission_rate": 0.5 # 吨碳/平方公里/年
            },
            "agricultural": {
                "emission_rate": 0.2 # 吨碳/平方公里/年
            }
        }
    
    def analyze_carbon_cycle(self, region: str, time_period: int, include_remote_sensing: bool = True) -> Dict[str, Any]:
        """分析碳循环"""
        try:
            if not self.is_initialized:
                return {
                    "success": False,
                    "error": "模型未初始化",
                    "region": region,
                    "time_period": time_period
                }
            
            if region not in self.region_data:
                return {
                    "success": False,
                    "error": f"不支持的地区: {region}",
                    "region": region,
                    "time_period": time_period
                }
            
            region_info = self.region_data[region]
            logger.info(f"开始分析地区 {region} 的碳循环，时间周期: {time_period} 天")
            
            # 生成时间序列
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
            temporal_trends_data = self._analyze_temporal_trends(net_carbon_balance)
            # 将时间趋势数据包装成列表格式以符合API响应结构
            temporal_trends = [temporal_trends_data] if temporal_trends_data else []
            
            # 导出分析报告
            report_path = self.export_analysis_report(region, {
                "carbon_sink": carbon_sink_data,
                "carbon_source": carbon_source_data,
                "net_balance": net_carbon_balance,
                "sequestration_potential": sequestration_potential,
                "temporal_trends": temporal_trends_data
            })
            
            # 计算汇总数据
            total_sink = sum(d["total_sink"] for d in carbon_sink_data)
            total_source = sum(d["total_source"] for d in carbon_source_data)
            net_emission = total_source - total_sink
            
            # 构建响应数据，确保与前端期望的结构一致
            response = {
                "success": True,
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
                "temporal_trends": temporal_trends,
                "report_path": report_path,
                # 添加前端需要的字段
                "sink": carbon_sink_data,
                "source": carbon_source_data,
                "potential": sequestration_potential,
                "mapPath": map_data.get("map_path", "") if map_data else ""
            }
            
            logger.info(f"碳循环分析完成: {region}, 碳汇: {total_sink:.2f}, 碳源: {total_source:.2f}, 净排放: {net_emission:.2f}")
            return response
            
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
        
        # 确保时间周期至少为1天
        if time_period < 1:
            time_period = 1
        
        for i in range(time_period):
            date = start_date + timedelta(days=i)
            dates.append(date.isoformat())
        
        return dates

    def _calculate_carbon_sink(self, region_info: Dict[str, Any], time_series: List[str]) -> List[Dict[str, Any]]:
        """计算碳汇"""
        carbon_sink_data = []
        
        for i, date_str in enumerate(time_series):
            try:
                date = datetime.fromisoformat(date_str)
                month = date.month
            except (ValueError, TypeError):
                # 如果日期解析失败，使用当前时间
                date = datetime.now()
                month = date.month
            
            # 基础碳汇（万吨/年）
            forest_sink = (region_info["forest_coverage"] * region_info["area"] * 100 * 
                          self.vegetation_models["forest"]["carbon_sequestration_rate"] / 10000)
            
            grassland_sink = (region_info["grassland_coverage"] * region_info["area"] * 100 * 
                             self.vegetation_models["grassland"]["carbon_sequestration_rate"] / 10000)
            
            wetland_sink = (region_info["wetland_coverage"] * region_info["area"] * 100 * 
                           self.vegetation_models["wetland"]["carbon_sequestration_rate"] / 10000)
            
            # 添加季节性变化（春夏季节碳汇能力更强）
            seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (month - 3) / 12)
            
            # 添加随机波动
            random_factor = 1.0 + np.random.normal(0, 0.1)
            
            # 计算总碳汇
            total_sink = (forest_sink + grassland_sink + wetland_sink) * seasonal_factor * random_factor
            
            carbon_sink_data.append({
                "date": date_str,
                "total_sink": total_sink,
                "forest_sink": forest_sink * seasonal_factor * random_factor,
                "grassland_sink": grassland_sink * seasonal_factor * random_factor,
                "wetland_sink": wetland_sink * seasonal_factor * random_factor,
                "seasonal_factor": seasonal_factor,
                "random_factor": random_factor
            })
        
        return carbon_sink_data

    def _calculate_carbon_source(self, region_info: Dict[str, Any], time_series: List[str]) -> List[Dict[str, Any]]:
        """计算碳源"""
        carbon_source_data = []
        
        for i, date_str in enumerate(time_series):
            try:
                date = datetime.fromisoformat(date_str)
                month = date.month
            except (ValueError, TypeError):
                # 如果日期解析失败，使用当前时间
                date = datetime.now()
                month = date.month
            
            # 基础碳源（万吨/年）
            industrial_source = (region_info["urban_coverage"] * region_info["area"] * 100 * 
                               self.vegetation_models["industrial"]["emission_rate"] / 10000)
            
            transportation_source = (region_info["urban_coverage"] * region_info["area"] * 50 * 
                                   self.vegetation_models["transportation"]["emission_rate"] / 10000)
            
            agricultural_source = (region_info["grassland_coverage"] * region_info["area"] * 30 * 
                                 self.vegetation_models["agricultural"]["emission_rate"] / 10000)
            
            # 添加季节性变化
            seasonal_factor = 1.0 + 0.2 * np.sin(2 * np.pi * (month - 1) / 12)
            
            # 添加随机波动
            random_factor = 1.0 + np.random.normal(0, 0.1)
            
            # 计算总碳源
            total_source = (industrial_source + transportation_source + agricultural_source) * seasonal_factor * random_factor
            
            carbon_source_data.append({
                "date": date_str,
                "total_source": total_source,
                "industrial_source": industrial_source * seasonal_factor * random_factor,
                "transportation_source": transportation_source * seasonal_factor * random_factor,
                "agricultural_source": agricultural_source * seasonal_factor * random_factor,
                "seasonal_factor": seasonal_factor,
                "random_factor": random_factor
            })
        
        return carbon_source_data
    
    def _calculate_sequestration_potential(self, region_info: Dict[str, Any]) -> Dict[str, Any]:
        """计算碳汇潜力"""
        try:
            # 基础潜力计算（万吨/年）
            forest_potential = region_info["forest_coverage"] * region_info["area"] * 100 * 0.5  # 50%提升空间
            grassland_potential = region_info["grassland_coverage"] * region_info["area"] * 100 * 0.3  # 30%提升空间
            wetland_potential = region_info["wetland_coverage"] * region_info["area"] * 100 * 0.4  # 40%提升空间
            urban_green_potential = region_info["urban_coverage"] * region_info["area"] * 100 * 0.2  # 20%提升空间
            
            # 总潜力
            total_potential = forest_potential + grassland_potential + wetland_potential + urban_green_potential
            
            # 详细措施和成本估算
            measures = [
                {
                    "name": "森林碳汇提升",
                    "potential": round(forest_potential, 2),
                    "cost_per_ton": 150,  # 元/吨碳
                    "total_cost": round(forest_potential * 150, 2),
                    "description": "通过退耕还林、人工造林等措施增加森林覆盖率",
                    "implementation_time": "3-5年",
                    "priority": "高"
                },
                {
                    "name": "草地碳汇改善",
                    "potential": round(grassland_potential, 2),
                    "cost_per_ton": 80,
                    "total_cost": round(grassland_potential * 80, 2),
                    "description": "改善草地管理，实施轮牧制度，恢复退化草地",
                    "implementation_time": "2-3年",
                    "priority": "中"
                },
                {
                    "name": "湿地保护修复",
                    "potential": round(wetland_potential, 2),
                    "cost_per_ton": 200,
                    "total_cost": round(wetland_potential * 200, 2),
                    "description": "保护现有湿地，修复退化湿地生态系统",
                    "implementation_time": "5-8年",
                    "priority": "高"
                },
                {
                    "name": "城市绿化提升",
                    "potential": round(urban_green_potential, 2),
                    "cost_per_ton": 300,
                    "total_cost": round(urban_green_potential * 300, 2),
                    "description": "增加城市绿地面积，建设绿色基础设施",
                    "implementation_time": "1-3年",
                    "priority": "中"
                }
            ]
            
            # 政策建议
            recommendations = []
            if forest_potential > 1000:
                recommendations.append("增加森林覆盖率，实施退耕还林政策")
            if grassland_potential > 500:
                recommendations.append("改善草地管理，实施轮牧制度")
            if wetland_potential > 200:
                recommendations.append("保护湿地生态系统，减少开发活动")
            if urban_green_potential > 100:
                recommendations.append("加强城市绿化建设，推广绿色建筑")
            
            # 成本效益分析
            total_cost = sum(m["total_cost"] for m in measures)
            cost_effectiveness = total_cost / total_potential if total_potential > 0 else 0
            
            return {
                "total": round(total_potential, 2),
                "forest": round(forest_potential, 2),
                "grassland": round(grassland_potential, 2),
                "wetland": round(wetland_potential, 2),
                "urban_green": round(urban_green_potential, 2),
                "measures": measures,
                "recommendations": recommendations,
                "achievable_rate": 0.7,  # 70%可实现率
                "time_horizon": "5-10年",
                "total_cost": round(total_cost, 2),
                "cost_effectiveness": round(cost_effectiveness, 2),
                "roi": round(total_potential * 50 / total_cost, 2) if total_cost > 0 else 0  # 假设碳汇价值50元/吨
            }
            
        except Exception as e:
            logger.error(f"碳汇潜力计算失败: {e}")
            return {
                "total": 0,
                "forest": 0,
                "grassland": 0,
                "wetland": 0,
                "urban_green": 0,
                "measures": [],
                "recommendations": ["数据不足，无法计算"],
                "achievable_rate": 0,
                "time_horizon": "未知",
                "total_cost": 0,
                "cost_effectiveness": 0,
                "roi": 0
            }

    def _generate_map_data(self, region: str, carbon_sink_data: List[Dict[str, Any]], 
                          carbon_source_data: List[Dict[str, Any]], 
                          net_balance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成地图数据"""
        try:
            center = self._get_region_center(region)
            
            # 创建地图
            m = folium.Map(
                location=center,
                zoom_start=6,
                tiles='OpenStreetMap',
                control_scale=True
            )
            
            # 添加地区边界
            region_geojson = self._get_region_geojson(region)
            if region_geojson:
                folium.GeoJson(
                    region_geojson,
                    name=f"{region}边界",
                    style_function=lambda x: {
                        'fillColor': '#35c9ff',
                        'color': '#35c9ff',
                        'weight': 2,
                        'fillOpacity': 0.1
                    }
                ).add_to(m)
            
            # 计算平均碳汇和碳源用于地图显示
            avg_sink = np.mean([d["total_sink"] for d in carbon_sink_data]) if carbon_sink_data else 0
            avg_source = np.mean([d["total_source"] for d in carbon_source_data]) if carbon_source_data else 0
            
            # 添加碳汇区域标记
            sink_locations = self._generate_sink_locations(center, region)
            for i, location in enumerate(sink_locations):
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>碳汇区域 {i+1}</h4>
                    <p><strong>平均碳汇:</strong> {avg_sink:.2f}万吨/天</p>
                    <p><strong>森林碳汇:</strong> {carbon_sink_data[-1]['forest_sink']:.2f}万吨</p>
                    <p><strong>草地碳汇:</strong> {carbon_sink_data[-1]['grassland_sink']:.2f}万吨</p>
                    <p><strong>湿地碳汇:</strong> {carbon_sink_data[-1]['wetland_sink']:.2f}万吨</p>
                </div>
                """ if carbon_sink_data else "碳汇区域"
                
                folium.CircleMarker(
                    location=location,
                    radius=15,
                    popup=folium.Popup(popup_content, max_width=250),
                    color='green',
                    fill=True,
                    fillColor='green',
                    fillOpacity=0.8,
                    weight=2
                ).add_to(m)
            
            # 添加碳源区域标记
            source_locations = self._generate_source_locations(center, region)
            for i, location in enumerate(source_locations):
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>碳源区域 {i+1}</h4>
                    <p><strong>平均碳源:</strong> {avg_source:.2f}万吨/天</p>
                    <p><strong>工业排放:</strong> {carbon_source_data[-1]['industrial_source']:.2f}万吨</p>
                    <p><strong>交通排放:</strong> {carbon_source_data[-1]['transportation_source']:.2f}万吨</p>
                    <p><strong>农业排放:</strong> {carbon_source_data[-1]['agricultural_source']:.2f}万吨</p>
                </div>
                """ if carbon_source_data else "碳源区域"
                
                folium.CircleMarker(
                    location=location,
                    radius=12,
                    popup=folium.Popup(popup_content, max_width=250),
                    color='red',
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.8,
                    weight=2
                ).add_to(m)
            
            # 添加净碳平衡标记
            if net_balance_data:
                latest_balance = net_balance_data[-1]
                balance_color = 'green' if latest_balance['net_balance'] > 0 else 'red'
                balance_icon = 'check-circle' if latest_balance['net_balance'] > 0 else 'times-circle'
                
                balance_popup = f"""
                <div style="width: 200px;">
                    <h4>净碳平衡</h4>
                    <p><strong>日期:</strong> {latest_balance['date']}</p>
                    <p><strong>净平衡:</strong> {latest_balance['net_balance']:.2f}万吨</p>
                    <p><strong>状态:</strong> {'碳汇>碳源' if latest_balance['net_balance'] > 0 else '碳源>碳汇'}</p>
                    <p><strong>碳汇总量:</strong> {latest_balance['sink']:.2f}万吨</p>
                    <p><strong>碳源总量:</strong> {latest_balance['source']:.2f}万吨</p>
                </div>
                """
                
                folium.Marker(
                    location=[center[0] + 0.5, center[1] + 0.5],
                    popup=folium.Popup(balance_popup, max_width=250),
                    icon=folium.Icon(color=balance_color, icon=balance_icon, prefix='fa')
                ).add_to(m)
            
            # 添加详细的图例
            legend_html = f'''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 220px; height: 220px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:12px; padding: 10px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 10px 0; color: #333;">{region}碳循环图例</h4>
            <p style="margin: 2px 0;"><span style="color:green; font-size: 16px;">●</span> 碳汇区域 (平均: {avg_sink:.1f}万吨/天)</p>
            <p style="margin: 2px 0;"><span style="color:red; font-size: 16px;">●</span> 碳源区域 (平均: {avg_source:.1f}万吨/天)</p>
            <p style="margin: 2px 0;"><span style="color:blue; font-size: 16px;">■</span> 地区边界</p>
            <p style="margin: 2px 0;"><span style="color:green; font-size: 16px;">✓</span> 碳汇>碳源</p>
            <p style="margin: 2px 0;"><span style="color:red; font-size: 16px;">✗</span> 碳源>碳汇</p>
            <p style="margin: 5px 0; font-size: 10px; color: #666;">点击标记查看详细信息</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # 添加图层控制
            folium.LayerControl().add_to(m)
            
            # 保存地图 - 使用绝对路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            map_filename = f"carbon_cycle_{region}_{timestamp}.html"
            
            # 确保maps目录存在
            maps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")
            os.makedirs(maps_dir, exist_ok=True)
            
            map_path = os.path.join(maps_dir, map_filename)
            
            # 保存地图文件
            m.save(map_path)
            
            # 验证文件是否成功保存
            if os.path.exists(map_path):
                file_size = os.path.getsize(map_path)
                logger.info(f"地图已保存: {map_path} (大小: {file_size} 字节)")
                
                # 生成相对路径用于前端访问
                relative_path = f"/maps/{map_filename}"
                logger.info(f"相对路径: {relative_path}")
                
                # 验证HTML文件内容
                with open(map_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 1000:  # 确保文件有足够的内容
                        logger.info(f"地图HTML文件生成成功，内容长度: {len(content)} 字符")
                    else:
                        logger.warning(f"地图HTML文件内容可能不完整，长度: {len(content)} 字符")
                
            else:
                logger.error(f"地图文件保存失败: {map_path}")
                relative_path = ""
                file_size = 0
            
            return {
                "map_path": relative_path,
                "map_filename": map_filename,
                "absolute_path": map_path,
                "center": center,
                "zoom_level": 6,
                "layers_count": 4,
                "file_size": file_size,
                "sink_count": len(sink_locations),
                "source_count": len(source_locations),
                "avg_sink": round(avg_sink, 2),
                "avg_source": round(avg_source, 2)
            }
            
        except Exception as e:
            logger.error(f"地图生成失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
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
            },
            "华东": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [115.0, 25.0], [125.0, 25.0], [125.0, 35.0], [115.0, 35.0], [115.0, 25.0]
                    ]]
                },
                "properties": {"name": "华东"}
            },
            "华南": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [105.0, 18.0], [115.0, 18.0], [115.0, 28.0], [105.0, 28.0], [105.0, 18.0]
                    ]]
                },
                "properties": {"name": "华南"}
            }
        }
        
        return region_boundaries.get(region)
    
    def _generate_sink_locations(self, center: List[float], region: str) -> List[List[float]]:
        """生成碳汇位置"""
        locations = []
        base_lat, base_lng = center
        
        # 根据地区生成不同数量的碳汇位置
        num_locations = {
            "全国": 8,
            "华北": 3,
            "华东": 4,
            "华南": 3,
            "华中": 3,
            "西南": 4,
            "西北": 2,
            "东北": 3
        }.get(region, 3)
        
        for i in range(num_locations):
            # 在中心点周围生成位置
            lat_offset = np.random.uniform(-1.0, 1.0)
            lng_offset = np.random.uniform(-1.0, 1.0)
            
            locations.append([base_lat + lat_offset, base_lng + lng_offset])
        
        return locations
    
    def _generate_source_locations(self, center: List[float], region: str) -> List[List[float]]:
        """生成碳源位置"""
        locations = []
        base_lat, base_lng = center
        
        # 根据地区生成不同数量的碳源位置
        num_locations = {
            "全国": 6,
            "华北": 2,
            "华东": 3,
            "华南": 2,
            "华中": 2,
            "西南": 2,
            "西北": 1,
            "东北": 2
        }.get(region, 2)
        
        for i in range(num_locations):
            # 在中心点周围生成位置，与碳汇位置错开
            lat_offset = np.random.uniform(-0.8, 0.8) + 0.5 * (i % 2)
            lng_offset = np.random.uniform(-0.8, 0.8) + 0.5 * ((i + 1) % 2)
            
            locations.append([base_lat + lat_offset, base_lng + lng_offset])
        
        return locations
    
    def _analyze_temporal_trends(self, net_balance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析时间趋势"""
        try:
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
                "slope": float(slope),  # 确保是Python原生类型
                "mean_balance": float(mean_balance),
                "std_balance": float(std_balance),
                "positive_days": int(positive_days),
                "negative_days": int(negative_days),
                "total_days": int(len(balances)),
                "improvement_rate": float(positive_days / len(balances)) if len(balances) > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"时间趋势分析失败: {e}")
            return {
                "trend": "unknown",
                "description": f"分析失败: {str(e)}",
                "slope": 0.0,
                "mean_balance": 0.0,
                "std_balance": 0.0,
                "positive_days": 0,
                "negative_days": 0,
                "total_days": 0,
                "improvement_rate": 0.0
            }

    def export_analysis_report(self, region: str, analysis_data: Dict[str, Any]) -> str:
        """导出分析报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"carbon_cycle_report_{region}_{timestamp}.json"
            
            # 确保data目录存在
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            os.makedirs(data_dir, exist_ok=True)
            
            report_path = os.path.join(data_dir, report_filename)
            
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
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
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
        model.initialize_models()
        if model.is_ready():
            region = "华东"
            result = model.analyze_carbon_cycle(region=region, time_period=5)
            report_path = result["report_path"]
            print(f"分析报告生成成功: {report_path}")
            print(f"地图路径: {result['map_data']['map_path']}")
        else:
            print("模型初始化失败，无法运行分析")

    asyncio.run(main()) 