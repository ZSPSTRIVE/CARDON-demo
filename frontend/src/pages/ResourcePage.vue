<template>
  <div class="resource-container">
    <div class="header-section">
      <h1>资源碳排放分析</h1>
      <p class="subtitle">深入分析不同能源资源的碳排放特征与趋势</p>
    </div>
    
    <div class="controls-section">
      <div class="control-group">
        <label>分析周期：</label>
        <select v-model="selectedPeriod" @change="loadResourceData">
          <option value="monthly">月度分析</option>
          <option value="quarterly">季度分析</option>
          <option value="yearly">年度分析</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>对比基准：</label>
        <select v-model="selectedBaseline" @change="loadResourceData">
          <option value="2020">2020年</option>
          <option value="2021">2021年</option>
          <option value="2022">2022年</option>
          <option value="2023">2023年</option>
        </select>
      </div>
      
      <button class="analyze-btn" @click="loadResourceData">
        <i class="fas fa-chart-line"></i> 开始分析
      </button>
    </div>
    
    <div class="charts-section">
      <div class="chart-row">
        <div class="chart-card">
          <h3>资源碳排放构成</h3>
          <div id="resource-pie-chart" class="chart"></div>
        </div>
        
        <div class="chart-card">
          <h3>碳排放强度对比</h3>
          <div id="intensity-bar-chart" class="chart"></div>
        </div>
      </div>
      
      <div class="chart-row">
        <div class="chart-card full-width">
          <h3>资源使用趋势分析</h3>
          <div id="trend-line-chart" class="chart"></div>
        </div>
      </div>
    </div>
    
    <div class="metrics-section">
      <h2>关键指标分析</h2>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">🔥</div>
          <div class="metric-content">
            <h4>最高排放资源</h4>
            <div class="metric-value">{{ metrics.highestEmission.resource }}</div>
            <div class="metric-detail">{{ metrics.highestEmission.value }} 万吨</div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">🌱</div>
          <div class="metric-content">
            <h4>最清洁资源</h4>
            <div class="metric-value">{{ metrics.cleanestResource.resource }}</div>
            <div class="metric-detail">{{ metrics.cleanestResource.value }} 万吨</div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">📈</div>
          <div class="metric-content">
            <h4>增长最快</h4>
            <div class="metric-value">{{ metrics.fastestGrowth.resource }}</div>
            <div class="metric-detail">{{ metrics.fastestGrowth.rate }}%</div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">📉</div>
          <div class="metric-content">
            <h4>下降最快</h4>
            <div class="metric-value">{{ metrics.fastestDecline.resource }}</div>
            <div class="metric-detail">{{ metrics.fastestDecline.rate }}%</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>深度分析报告</h2>
      <div class="analysis-content">
        <div class="analysis-item">
          <h4>资源结构分析</h4>
          <p>{{ analysis.resourceStructure }}</p>
        </div>
        
        <div class="analysis-item">
          <h4>排放效率评估</h4>
          <p>{{ analysis.emissionEfficiency }}</p>
        </div>
        
        <div class="analysis-item">
          <h4>清洁能源发展</h4>
          <p>{{ analysis.cleanEnergyDevelopment }}</p>
        </div>
        
        <div class="analysis-item">
          <h4>政策影响分析</h4>
          <p>{{ analysis.policyImpact }}</p>
        </div>
      </div>
    </div>
    
    <div class="recommendations-section">
      <h2>优化建议</h2>
      <div class="recommendations-grid">
        <div class="recommendation-card">
          <div class="rec-icon">⚡</div>
          <h4>能源结构优化</h4>
          <p>{{ recommendations.energyStructure }}</p>
        </div>
        
        <div class="recommendation-card">
          <div class="rec-icon">🔧</div>
          <h4>技术升级</h4>
          <p>{{ recommendations.technologyUpgrade }}</p>
        </div>
        
        <div class="recommendation-card">
          <div class="rec-icon">📊</div>
          <h4>监测管理</h4>
          <p>{{ recommendations.monitoringManagement }}</p>
        </div>
        
        <div class="recommendation-card">
          <div class="rec-icon">🌍</div>
          <h4>绿色发展</h4>
          <p>{{ recommendations.greenDevelopment }}</p>
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
const selectedPeriod = ref('monthly')
const selectedBaseline = ref('2022')

const metrics = reactive({
  highestEmission: { resource: '', value: 0 },
  cleanestResource: { resource: '', value: 0 },
  fastestGrowth: { resource: '', rate: 0 },
  fastestDecline: { resource: '', rate: 0 }
})

const analysis = reactive({
  resourceStructure: '',
  emissionEfficiency: '',
  cleanEnergyDevelopment: '',
  policyImpact: ''
})

const recommendations = reactive({
  energyStructure: '',
  technologyUpgrade: '',
  monitoringManagement: '',
  greenDevelopment: ''
})

let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

// 生命周期钩子
onMounted(() => {
  initCharts()
  loadResourceData()
})

// 初始化图表
function initCharts() {
  // 饼图
  const pieDom = document.getElementById('resource-pie-chart')
  if (pieDom) {
    pieChart = echarts.init(pieDom)
  }
  
  // 柱状图
  const barDom = document.getElementById('intensity-bar-chart')
  if (barDom) {
    barChart = echarts.init(barDom)
  }
  
  // 折线图
  const lineDom = document.getElementById('trend-line-chart')
  if (lineDom) {
    lineChart = echarts.init(lineDom)
  }
  
  // 响应式调整
  window.addEventListener('resize', () => {
    pieChart?.resize()
    barChart?.resize()
    lineChart?.resize()
  })
}

// 加载资源数据
async function loadResourceData() {
  try {
    const params = {
      period: selectedPeriod.value,
      baseline: selectedBaseline.value
    }
    
    const response = await http.get('/emissions/resource-analysis', { params })
    
    if (response.data) {
      renderCharts(response.data)
      updateMetrics(response.data)
      generateAnalysis(response.data)
      generateRecommendations(response.data)
    }
  } catch (error) {
    console.error('加载资源数据失败:', error)
  }
}

// 渲染图表
function renderCharts(data: any) {
  renderPieChart(data.resources)
  renderBarChart(data.resources)
  renderLineChart(data.trends)
}

// 渲染饼图
function renderPieChart(resources: any[]) {
  if (!pieChart) return
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: resources.map(r => r.type)
    },
    series: [
      {
        name: '碳排放量',
        type: 'pie',
        radius: '50%',
        data: resources.map(r => ({
          value: r.currentUsage,
          name: r.type
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  pieChart.setOption(option)
}

// 渲染柱状图
function renderBarChart(resources: any[]) {
  if (!barChart) return
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: resources.map(r => r.type),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '碳排放强度 (吨/万元)'
    },
    series: [
      {
        name: '碳排放强度',
        type: 'bar',
        data: resources.map(r => r.carbonIntensity),
        itemStyle: {
          color: function(params: any) {
            const colors = ['#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
            return colors[params.dataIndex % colors.length]
          }
        }
      }
    ]
  }
  
  barChart.setOption(option)
}

// 渲染折线图
function renderLineChart(trends: any[]) {
  if (!lineChart) return
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['煤炭', '石油', '天然气', '电力', '可再生能源', '核能']
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trends.map(t => t.period)
    },
    yAxis: {
      type: 'value',
      name: '碳排放量 (万吨)'
    },
    series: [
      {
        name: '煤炭',
        type: 'line',
        data: trends.map(t => t.coal),
        smooth: true
      },
      {
        name: '石油',
        type: 'line',
        data: trends.map(t => t.oil),
        smooth: true
      },
      {
        name: '天然气',
        type: 'line',
        data: trends.map(t => t.gas),
        smooth: true
      },
      {
        name: '电力',
        type: 'line',
        data: trends.map(t => t.electricity),
        smooth: true
      },
      {
        name: '可再生能源',
        type: 'line',
        data: trends.map(t => t.renewable),
        smooth: true
      },
      {
        name: '核能',
        type: 'line',
        data: trends.map(t => t.nuclear),
        smooth: true
      }
    ]
  }
  
  lineChart.setOption(option)
}

// 更新指标
function updateMetrics(data: any) {
  const resources = data.resources
  
  // 最高排放资源
  const highest = resources.reduce((prev: any, current: any) => 
    prev.currentUsage > current.currentUsage ? prev : current
  )
  metrics.highestEmission = {
    resource: highest.type,
    value: Math.round(highest.currentUsage / 10000 * 100) / 100
  }
  
  // 最清洁资源
  const cleanest = resources.reduce((prev: any, current: any) => 
    prev.carbonIntensity < current.carbonIntensity ? prev : current
  )
  metrics.cleanestResource = {
    resource: cleanest.type,
    value: Math.round(cleanest.carbonIntensity)
  }
  
  // 增长最快
  const fastestGrowth = resources.reduce((prev: any, current: any) => 
    (current.growthRate || 0) > (prev.growthRate || 0) ? current : prev
  )
  metrics.fastestGrowth = {
    resource: fastestGrowth.type,
    rate: Math.round((fastestGrowth.growthRate || 0) * 100)
  }
  
  // 下降最快
  const fastestDecline = resources.reduce((prev: any, current: any) => 
    (current.declineRate || 0) > (prev.declineRate || 0) ? current : prev
  )
  metrics.fastestDecline = {
    resource: fastestDecline.type,
    rate: Math.round((fastestDecline.declineRate || 0) * 100)
  }
}

// 生成分析报告
function generateAnalysis(data: any) {
  const resources = data.resources
  
  // 资源结构分析
  const totalUsage = resources.reduce((sum: number, r: any) => sum + r.currentUsage, 0)
  const fossilFuelPercentage = resources
    .filter((r: any) => ['coal', 'oil', 'gas'].includes(r.type))
    .reduce((sum: number, r: any) => sum + r.currentUsage, 0) / totalUsage * 100
  
  analysis.resourceStructure = `化石能源占比${Math.round(fossilFuelPercentage)}%，清洁能源占比${Math.round(100 - fossilFuelPercentage)}%。当前能源结构仍以传统能源为主，清洁能源发展空间巨大。`
  
  // 排放效率评估
  const avgEfficiency = resources.reduce((sum: number, r: any) => sum + r.efficiency, 0) / resources.length
  analysis.emissionEfficiency = `平均能源效率为${Math.round(avgEfficiency)}%，其中${resources.find((r: any) => r.efficiency === Math.max(...resources.map((r: any) => r.efficiency)))?.type}效率最高。建议推广高效技术，提升整体能效水平。`
  
  // 清洁能源发展
  const renewableGrowth = resources.find((r: any) => r.type === 'renewable')?.growthRate || 0
  analysis.cleanEnergyDevelopment = `可再生能源增长率为${Math.round(renewableGrowth * 100)}%，发展势头良好。建议继续加大投资力度，完善配套设施建设。`
  
  // 政策影响分析
  analysis.policyImpact = '碳达峰碳中和政策对能源结构转型产生显著影响，传统能源使用量呈下降趋势，清洁能源占比持续提升。政策执行效果明显。'
}

// 生成建议
function generateRecommendations(data: any) {
  const resources = data.resources
  const highEmissionResources = resources.filter((r: any) => r.carbonIntensity > 500)
  
  if (highEmissionResources.length > 0) {
    recommendations.energyStructure = `重点控制${highEmissionResources.map((r: any) => r.type).join('、')}等高排放资源使用，逐步提高清洁能源占比，优化能源结构。`
  } else {
    recommendations.energyStructure = '当前能源结构相对合理，建议继续保持清洁能源发展势头，进一步降低化石能源依赖。'
  }
  
  recommendations.technologyUpgrade = '推广先进燃烧技术、碳捕获与封存技术，提升传统能源使用效率，降低单位产出碳排放。'
  
  recommendations.monitoringManagement = '建立完善的碳排放监测体系，实时监控各资源使用情况，为精准施策提供数据支撑。'
  
  recommendations.greenDevelopment = '大力发展风能、太阳能、生物质能等可再生能源，建设绿色能源体系，实现可持续发展。'
}
</script>

<style scoped>
.resource-container {
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

.analyze-btn {
  padding: 10px 20px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s;
}

.analyze-btn:hover {
  background: #229954;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-row.full-width {
  grid-template-columns: 1fr;
}

.chart-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-card h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  text-align: center;
}

.chart {
  width: 100%;
  height: 300px;
}

.full-width .chart {
  height: 400px;
}

.metrics-section {
  margin-bottom: 30px;
}

.metrics-section h2 {
  color: #2c3e50;
  margin-bottom: 25px;
  text-align: center;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.metric-icon {
  font-size: 2.5em;
}

.metric-content h4 {
  color: #7f8c8d;
  margin-bottom: 10px;
  font-size: 0.9em;
  text-transform: uppercase;
}

.metric-value {
  font-size: 1.8em;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.metric-detail {
  color: #95a5a6;
  font-size: 0.9em;
}

.analysis-section {
  background: white;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
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

.recommendations-section {
  margin-bottom: 30px;
}

.recommendations-section h2 {
  color: #2c3e50;
  margin-bottom: 25px;
  text-align: center;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s;
}

.recommendation-card:hover {
  transform: translateY(-5px);
}

.rec-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.recommendation-card h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.2em;
}

.recommendation-card p {
  color: #7f8c8d;
  line-height: 1.6;
  text-align: justify;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-group select {
    min-width: auto;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .metric-card {
    flex-direction: column;
    text-align: center;
  }
}
</style> 