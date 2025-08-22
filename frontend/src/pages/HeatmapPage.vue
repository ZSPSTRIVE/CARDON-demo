<template>
  <div class="heatmap-container">
      <div class="header-section">
        <h1>碳排放热力分布图</h1>
        <p class="subtitle">基于地理位置的碳排放强度可视化分析</p>
      </div>
      
      <div class="controls-section">
        <div class="control-group">
          <label>时间范围：</label>
          <select v-model="selectedTimeRange" @change="loadHeatmapData">
            <option value="30">最近30天</option>
            <option value="90">最近90天</option>
            <option value="180">最近180天</option>
            <option value="365">最近一年</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>行业类型：</label>
          <select v-model="selectedIndustry" @change="loadHeatmapData">
            <option value="all">全部行业</option>
            <option value="manufacturing">制造业</option>
            <option value="energy">能源业</option>
            <option value="transportation">交通运输</option>
            <option value="agriculture">农业</option>
            <option value="construction">建筑业</option>
            <option value="services">服务业</option>
            <option value="mining">采矿业</option>
            <option value="chemical">化工业</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>资源类型：</label>
          <select v-model="selectedResource" @change="loadHeatmapData">
            <option value="all">全部资源</option>
            <option value="coal">煤炭</option>
            <option value="oil">石油</option>
            <option value="gas">天然气</option>
            <option value="electricity">电力</option>
            <option value="renewable">可再生能源</option>
            <option value="nuclear">核能</option>
          </select>
        </div>
        
        <button class="refresh-btn" @click="loadHeatmapData">
          <i class="fas fa-sync-alt"></i> 刷新数据
        </button>
      </div>
      
      <div class="map-section">
        <div class="map-container">
          <div id="heatmap-chart" class="heatmap-chart"></div>
        </div>
        
        <div class="legend-section">
          <h3>图例说明</h3>
          <div class="legend-items">
            <div class="legend-item">
              <div class="legend-color high"></div>
              <span>高排放 (>1000吨)</span>
            </div>
            <div class="legend-item">
              <div class="legend-color medium"></div>
              <span>中排放 (500-1000吨)</span>
            </div>
            <div class="legend-item">
              <div class="legend-color low"></div>
              <span>低排放 (<500吨)</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <h3>覆盖地区</h3>
            <div class="stat-value">{{ stats.coveredRegions }}</div>
            <div class="stat-label">个省市</div>
          </div>
          
          <div class="stat-card">
            <h3>总排放量</h3>
            <div class="stat-value">{{ stats.totalEmissions }}</div>
            <div class="stat-label">万吨</div>
          </div>
          
          <div class="stat-card">
            <h3>平均强度</h3>
            <div class="stat-value">{{ stats.averageIntensity }}</div>
            <div class="stat-label">吨/平方公里</div>
          </div>
          
          <div class="stat-card">
            <h3>热点数量</h3>
            <div class="stat-value">{{ stats.hotspotCount }}</div>
            <div class="stat-label">个</div>
          </div>
        </div>
      </div>
      
      <div class="analysis-section">
        <h2>热力分析报告</h2>
        <div class="analysis-content">
          <div class="analysis-item">
            <h4>排放热点分析</h4>
            <p>{{ analysis.hotspotAnalysis }}</p>
          </div>
          
          <div class="analysis-item">
            <h4>区域对比</h4>
            <p>{{ analysis.regionalComparison }}</p>
          </div>
          
          <div class="analysis-item">
            <h4>趋势变化</h4>
            <p>{{ analysis.trendAnalysis }}</p>
          </div>
          
          <div class="analysis-item">
            <h4>政策建议</h4>
            <p>{{ analysis.policyRecommendations }}</p>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import http from '../api/http'
import { ref, onMounted, reactive } from 'vue'
import * as echarts from 'echarts'

// 响应式数据
const selectedTimeRange = ref('90')
const selectedIndustry = ref('all')
const selectedResource = ref('all')

const stats = reactive({
  coveredRegions: 0,
  totalEmissions: 0,
  averageIntensity: 0,
  hotspotCount: 0
})

const analysis = reactive({
  hotspotAnalysis: '',
  regionalComparison: '',
  trendAnalysis: '',
  policyRecommendations: ''
})

let heatmapChart: echarts.ECharts | null = null

// 生命周期钩子
onMounted(() => {
  initChart()
  loadHeatmapData()
})

// 初始化图表
function initChart() {
  const chartDom = document.getElementById('heatmap-chart')
  if (chartDom) {
    heatmapChart = echarts.init(chartDom)
    window.addEventListener('resize', () => {
      heatmapChart?.resize()
    })
  }
}

// 加载热力图数据
async function loadHeatmapData() {
  try {
    const params = {
      timeRange: selectedTimeRange.value,
      industry: selectedIndustry.value,
      resource: selectedResource.value
    }
    
    const response = await http.get('/emissions/heatmap', { params })
    
    if (response.data) {
      renderHeatmap(response.data)
      updateStats(response.data)
      generateAnalysis(response.data)
    }
  } catch (error) {
    console.error('加载热力图数据失败:', error)
  }
}

// 渲染热力图
function renderHeatmap(data: any[]) {
  if (!heatmapChart) return
  
  // 处理数据
  const industries = Array.from(new Set(data.map(item => item.industry)))
  const resources = Array.from(new Set(data.map(item => item.resource)))
  
  // 创建数据矩阵
  const matrix: number[][] = []
  for (let i = 0; i < industries.length; i++) {
    for (let j = 0; j < resources.length; j++) {
      const item = data.find(d => d.industry === industries[i] && d.resource === resources[j])
      matrix.push([j, i, item ? item.value : 0])
    }
  }
  
  const option = {
    title: {
      text: '碳排放热力分布图',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 18
      }
    },
    tooltip: {
      position: 'top',
      formatter: function(params: any) {
        const industry = industries[params.data[1]]
        const resource = resources[params.data[0]]
        const value = params.data[2]
        return `${industry} × ${resource}<br/>排放量: ${value} 吨`
      }
    },
    grid: {
      height: '70%',
      top: '15%'
    },
    xAxis: {
      type: 'category',
      data: resources,
      splitArea: {
        show: true
      },
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'category',
      data: industries,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: Math.max(...matrix.map(item => item[2]), 1000),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    series: [{
      name: '碳排放量',
      type: 'heatmap',
      data: matrix,
      label: {
        show: true,
        formatter: function(params: any) {
          return params.data[2].toLocaleString()
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  heatmapChart.setOption(option)
}

// 更新统计信息
function updateStats(data: any[]) {
  const totalEmissions = data.reduce((sum, item) => sum + item.value, 0)
  const regions = new Set(data.map(item => item.industry)).size
  const averageIntensity = totalEmissions / regions
  const hotspotCount = data.filter(item => item.value > 800).length
  
  stats.coveredRegions = regions
  stats.totalEmissions = Math.round(totalEmissions / 10000 * 100) / 100 // 转换为万吨
  stats.averageIntensity = Math.round(averageIntensity)
  stats.hotspotCount = hotspotCount
}

// 生成分析报告
function generateAnalysis(data: any[]) {
  const highEmissions = data.filter(item => item.value > 800)
  const lowEmissions = data.filter(item => item.value < 300)
  
  // 热点分析
  if (highEmissions.length > 0) {
    const topIndustry = highEmissions.reduce((prev, current) => 
      prev.value > current.value ? prev : current
    )
    analysis.hotspotAnalysis = `发现${highEmissions.length}个高排放热点，主要集中在${topIndustry.industry}行业，使用${topIndustry.resource}资源时排放量达到${topIndustry.value}吨。`
  } else {
    analysis.hotspotAnalysis = '当前数据范围内未发现明显的高排放热点。'
  }
  
  // 区域对比
  const industryStats = {}
  data.forEach(item => {
    if (!industryStats[item.industry]) {
      industryStats[item.industry] = { total: 0, count: 0 }
    }
    industryStats[item.industry].total += item.value
    industryStats[item.industry].count += 1
  })
  
  const topIndustry = Object.entries(industryStats).reduce((prev, current) => {
    const [name, stats] = current
    const avg = (stats as any).total / (stats as any).count
    return avg > prev.avg ? { name, avg } : prev
  }, { name: '', avg: 0 })
  
  analysis.regionalComparison = `${topIndustry.name}行业的平均排放强度最高，达到${Math.round(topIndustry.avg)}吨，需要重点关注减排措施。`
  
  // 趋势分析
  const avgEmission = data.reduce((sum, item) => sum + item.value, 0) / data.length
  if (avgEmission > 600) {
    analysis.trendAnalysis = '整体排放强度较高，建议加强节能减排政策执行力度。'
  } else if (avgEmission > 300) {
    analysis.trendAnalysis = '排放强度处于中等水平，有进一步优化空间。'
  } else {
    analysis.trendAnalysis = '排放强度较低，继续保持良好的环保表现。'
  }
  
  // 政策建议
  if (highEmissions.length > data.length * 0.3) {
    analysis.policyRecommendations = '建议制定更严格的排放标准，推广清洁能源使用，加强高排放行业的监管。'
  } else if (highEmissions.length > data.length * 0.1) {
    analysis.policyRecommendations = '建议对高排放企业进行重点监控，提供技术升级支持，鼓励采用环保技术。'
  } else {
    analysis.policyRecommendations = '当前排放控制效果良好，建议继续保持现有政策，并探索更先进的减排技术。'
  }
}
</script>

<style scoped>
.heatmap-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2.5em;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1em;
}

.controls-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9em;
}

.control-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  min-width: 150px;
}

.refresh-btn {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s;
}

.refresh-btn:hover {
  background: #2980b9;
}

.map-section {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  margin-bottom: 30px;
}

.map-container {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.heatmap-chart {
  width: 100%;
  height: 500px;
}

.legend-section {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.legend-section h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-color.high {
  background: #d73027;
}

.legend-color.medium {
  background: #fdae61;
}

.legend-color.low {
  background: #313695;
}

.stats-section {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card h3 {
  color: #7f8c8d;
  margin-bottom: 15px;
  font-size: 1em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-size: 2.5em;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #95a5a6;
  font-size: 0.9em;
}

.analysis-section {
  background: white;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.analysis-section h2 {
  color: #2c3e50;
  margin-bottom: 25px;
  text-align: center;
}

.analysis-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.analysis-item h4 {
  color: #34495e;
  margin-bottom: 10px;
  font-size: 1.1em;
}

.analysis-item p {
  color: #7f8c8d;
  line-height: 1.6;
  text-align: justify;
}

@media (max-width: 768px) {
  .map-section {
    grid-template-columns: 1fr;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-group select {
    min-width: auto;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}
</style> 