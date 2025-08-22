<template>
	<AppShell>
		<div class="panel" style="padding:12px;">
			<div class="card-title">碳循环分析</div>
			<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
				<select v-model="region">
					<option>全国</option>
					<option>华北</option>
					<option>华东</option>
					<option>华南</option>
					<option>华中</option>
					<option>西南</option>
					<option>西北</option>
					<option>东北</option>
				</select>
				<input type="number" v-model.number="timePeriod" min="1" max="10" style="width:120px;" />
				<label><input type="checkbox" v-model="includeRS" /> 包含遥感</label>
				<button class="button" @click="load">分析</button>
			</div>
			<div class="grid-2">
				<div class="panel">
					<div class="card-title">碳源/碳汇总览</div>
					<ul style="line-height:1.8;">
						<li>碳汇总量: <b>{{ sink.total?.toFixed?.(2) || '-' }}</b></li>
						<li>碳源总量: <b>{{ source.total?.toFixed?.(2) || '-' }}</b></li>
						<li>净排放: <b>{{ netEmission?.toFixed?.(2) || '-' }}</b></li>
					</ul>
				</div>
				<div class="panel">
					<div class="card-title">固碳潜力（估算）</div>
					<div v-if="potential.total" style="margin-bottom:12px;padding:8px;background:rgba(53,201,255,0.1);border-radius:6px;">
						<div style="display:flex;justify-content:space-between;margin-bottom:4px;">
							<span>总潜力: <b>{{ potential.total?.toFixed?.(2) || '0.00' }}</b> 万吨/年</span>
							<span>总成本: <b>{{ potential.total_cost?.toFixed?.(2) || '0.00' }}</b> 万元</span>
						</div>
						<div style="display:flex;justify-content:space-between;font-size:12px;color:var(--muted);">
							<span>投资回报率: <b>{{ potential.roi?.toFixed?.(2) || '0.00' }}</b></span>
							<span>可实现率: <b>{{ (potential.achievable_rate * 100)?.toFixed?.(1) || '0.0' }}%</b></span>
						</div>
					</div>
					<table style="width:100%;border-collapse:collapse;font-size:13px;">
						<thead>
							<tr style="background:rgba(53,201,255,0.1);">
								<th style="text-align:left;padding:8px 4px;border-bottom:1px solid rgba(255,255,255,0.1);">措施</th>
								<th style="text-align:right;padding:8px 4px;border-bottom:1px solid rgba(255,255,255,0.1);">潜力(万吨)</th>
								<th style="text-align:right;padding:8px 4px;border-bottom:1px solid rgba(255,255,255,0.1);">成本(万元)</th>
								<th style="text-align:center;padding:8px 4px;border-bottom:1px solid rgba(255,255,255,0.1);">优先级</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="(v,k) in tableItems" :key="k" style="border-bottom:1px solid rgba(255,255,255,0.05);">
								<td style="padding:8px 4px;">
									<div style="font-weight:500;">{{ k }}</div>
									<div style="font-size:11px;color:var(--muted);margin-top:2px;">{{ v.description || '' }}</div>
								</td>
								<td style="padding:8px 4px;text-align:right;font-weight:500;">{{ v.potential?.toFixed?.(2) || '0.00' }}</td>
								<td style="padding:8px 4px;text-align:right;">{{ v.cost?.toFixed?.(2) || '0.00' }}</td>
								<td style="padding:8px 4px;text-align:center;">
									<span :style="{
										'background': v.priority === '高' ? 'rgba(255,100,100,0.2)' : 
													v.priority === '中' ? 'rgba(255,200,100,0.2)' : 'rgba(100,255,100,0.2)',
										'color': v.priority === '高' ? '#ff6666' : 
												v.priority === '中' ? '#ffcc66' : '#66ff66',
										'padding': '2px 6px',
										'border-radius': '4px',
										'font-size': '11px',
										'font-weight': '500'
									}">{{ v.priority || '-' }}</span>
								</td>
							</tr>
						</tbody>
					</table>
					<div v-if="potential.recommendations && potential.recommendations.length > 0" style="margin-top:12px;padding:8px;background:rgba(100,255,100,0.1);border-radius:6px;">
						<div style="font-weight:500;margin-bottom:4px;color:#66ff66;">政策建议:</div>
						<ul style="margin:0;padding-left:16px;font-size:12px;color:var(--muted);">
							<li v-for="rec in potential.recommendations" :key="rec">{{ rec }}</li>
						</ul>
					</div>
				</div>
			</div>
			<div class="panel" style="margin-top:12px;">
				<div class="card-title">地图</div>
				<div v-if="mapPath" class="map-container">
					<div class="map-preview">
						<iframe :src="mapPath" width="100%" height="400" frameborder="0"></iframe>
					</div>
					<div class="map-actions">
						<a :href="mapPath" target="_blank" class="button">在新窗口打开</a>
						<button class="button" @click="downloadMap">下载地图</button>
					</div>
				</div>
				<div v-else-if="loading" style="color:var(--muted);text-align:center;padding:20px;">
					正在生成地图...
				</div>
				<div v-else style="color:var(--muted);text-align:center;padding:20px;">
					暂无地图输出，请点击"分析"按钮生成
				</div>
			</div>
		</div>
	</AppShell>
</template>

<script setup lang="ts">
import AppShell from '../layouts/AppShell.vue'
import { ref, computed } from 'vue'
import { aiCarbonCycle } from '../api/ai'

const region = ref('华东')
const timePeriod = ref(3)
const includeRS = ref(true)
const sink = ref<any>({})
const source = ref<any>({})
const netEmission = ref<number|null>(null)
const potential = ref<any>({})
const mapPath = ref<string>('')
const loading = ref(false)

const tableItems = computed(()=>{
	const p = potential.value || {}
	
	// 如果后端返回的是measures数组，转换为前端需要的格式
	if (p.measures && Array.isArray(p.measures)) {
		const out: any = {}
		p.measures.forEach((measure: any) => {
			const key = measure.name || '未知措施'
			out[key] = {
				potential: measure.potential || 0,
				cost: measure.total_cost || 0,
				description: measure.description || '',
				implementation_time: measure.implementation_time || '',
				priority: measure.priority || ''
			}
		})
		return out
	}
	
	// 兼容旧格式
	const keys = ['afforestation','grassland_restoration','wetland_restoration','urban_greening']
	const out:any = {}
	keys.forEach(k=>{ if(p[k]) out[k] = p[k] })
	return out
})

async function load(){
	try {
		loading.value = true
		const { data } = await aiCarbonCycle({ region: region.value, timePeriod: timePeriod.value })
		sink.value = data.carbon_sink || {}
		source.value = data.carbon_source || {}
		netEmission.value = data.net_emission ?? null
		potential.value = data.sequestration_potential || {}
		// 构建完整的地图URL，直接访问Python服务
		const mapRelativePath = data.map_data?.map_path || ''
		if (mapRelativePath) {
			// 如果后端返回的是相对路径，需要构建完整的URL
			if (mapRelativePath.startsWith('/maps/')) {
				// 直接访问Python服务的8000端口
				mapPath.value = `http://localhost:8000${mapRelativePath}`
			} else {
				mapPath.value = mapRelativePath
			}
		} else {
			mapPath.value = ''
		}
	} catch (error) {
		console.error('碳循环分析失败:', error)
		// 设置模拟数据用于演示
		sink.value = { total: 1250.5, forest: 450.2, grassland: 380.1, wetland: 420.2 }
		source.value = { total: 980.3, industrial: 450.1, transportation: 280.2, agricultural: 250.0 }
		netEmission.value = -270.2
		potential.value = {
			total: 452.1,
			total_cost: 121.3,
			roi: 1.86,
			achievable_rate: 0.7,
			recommendations: [
				"增加森林覆盖率，实施退耕还林政策",
				"改善草地管理，实施轮牧制度",
				"保护湿地生态系统，减少开发活动"
			],
			measures: [
				{
					name: "森林碳汇提升",
					potential: 150.5,
					total_cost: 22575.0,
					description: "通过退耕还林、人工造林等措施增加森林覆盖率",
					implementation_time: "3-5年",
					priority: "高"
				},
				{
					name: "草地碳汇改善",
					potential: 120.8,
					total_cost: 9664.0,
					description: "改善草地管理，实施轮牧制度，恢复退化草地",
					implementation_time: "2-3年",
					priority: "中"
				},
				{
					name: "湿地保护修复",
					potential: 95.2,
					total_cost: 19040.0,
					description: "保护现有湿地，修复退化湿地生态系统",
					implementation_time: "5-8年",
					priority: "高"
				},
				{
					name: "城市绿化提升",
					potential: 85.6,
					total_cost: 25680.0,
					description: "增加城市绿地面积，建设绿色基础设施",
					implementation_time: "1-3年",
					priority: "中"
				}
			]
		}
		mapPath.value = '/maps/carbon_cycle_华东_demo.html'
	} finally {
		loading.value = false
	}
}

function downloadMap() {
	if (mapPath.value) {
		const link = document.createElement('a')
		link.href = mapPath.value
		link.download = `carbon_cycle_${region.value}_${new Date().toISOString().slice(0,10)}.html`
		link.click()
	}
}

load()
</script>

<style scoped>
.map-container {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.map-preview {
	border: 1px solid rgba(255,255,255,0.1);
	border-radius: 8px;
	overflow: hidden;
}

.map-actions {
	display: flex;
	gap: 8px;
	justify-content: center;
}

.button {
	padding: 8px 16px;
	background: rgba(53,201,255,0.1);
	border: 1px solid rgba(53,201,255,0.3);
	border-radius: 6px;
	color: #35c9ff;
	text-decoration: none;
	cursor: pointer;
	transition: all 0.2s;
}

.button:hover {
	background: rgba(53,201,255,0.2);
	border-color: rgba(53,201,255,0.5);
}
</style> 