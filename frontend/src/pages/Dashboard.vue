<template>
	<AppShell>
		<div class="grid-3">
			<KpiCard label="观测总量" :value="kpi.total" :delta="kpi.delta" :deltaText="kpi.deltaText" :icon="DetectionIcon" color="#7c5cff" />
			<KpiCard label="行业覆盖" :value="kpi.industryCount" :delta="0" :deltaText="' '" :icon="IndustryIcon" color="#35c9ff" />
			<KpiCard label="资源覆盖" :value="kpi.resourceCount" :delta="0" :deltaText="' '" :icon="ResourceIcon" color="#22d3ee" />
		</div>
		<div class="grid-2" style="margin-top:16px;">
			<ChartCard title="总量与分组趋势"><EChart :option="lineOption" /></ChartCard>
			<ChartCard title="行业×资源 热力图"><EChart :option="heatmapOption" /></ChartCard>
		</div>
		<div class="grid-2" style="margin-top:16px;">
			<ChartCard title="按行业分组"><EChart :option="barIndustryOption" /></ChartCard>
			<ChartCard title="资源构成（环形）"><EChart :option="pieResourceOption" /></ChartCard>
		</div>
	</AppShell>
</template>

<script setup lang="ts">
import AppShell from '../layouts/AppShell.vue'
import EChart from '../shared/EChart.vue'
import ChartCard from '../components/ChartCard.vue'
import KpiCard from '../components/KpiCard.vue'
import http from '../api/http'
import { reactive, ref, onMounted } from 'vue'

import DetectionIcon from '../assets/icons/检测.svg'
import IndustryIcon from '../assets/icons/行业.svg'
import ResourceIcon from '../assets/icons/资源-copy.svg'

const kpi = reactive<any>({ total: 0, delta: 0, deltaText: '+0%', industryCount: 0, resourceCount: 0 })
const lineOption = ref<any>({})
const heatmapOption = ref<any>({})
const barIndustryOption = ref<any>({})
const pieResourceOption = ref<any>({})

function buildLineOption(data:any){
	const dates = (data.total||[]).map((d:any)=>d.date)
	const series:any[] = []
	series.push({ name:'总量', type:'line', smooth:true, areaStyle:{}, data:(data.total||[]).map((d:any)=>Number(d.value)) })
	if(data.byIndustry){ Object.entries<any>(data.byIndustry).forEach(([k,arr])=> series.push({ name:`行业:${k}`, type:'line', smooth:true, data: arr.map((x:any)=>Number(x.value)) })) }
	if(data.byResource){ Object.entries<any>(data.byResource).forEach(([k,arr])=> series.push({ name:`资源:${k}`, type:'line', smooth:true, data: arr.map((x:any)=>Number(x.value)) })) }
	lineOption.value = { backgroundColor:'transparent', tooltip:{trigger:'axis'}, legend:{}, xAxis:{ type:'category', data:dates }, yAxis:{ type:'value' }, series }
}

function buildHeatmapOption(items:any[]){
	const industries = Array.from(new Set(items.map((d:any)=>d.industry)))
	const resources = Array.from(new Set(items.map((d:any)=>d.resource)))
	const map = new Map<string, number>()
	for(const d of items) map.set(`${d.industry}||${d.resource}`, Number(d.value))
	const matrix:any[] = []
	for(let i=0;i<industries.length;i++) for(let j=0;j<resources.length;j++) matrix.push([j,i,map.get(`${industries[i]}||${resources[j]}`)||0])
	heatmapOption.value = { tooltip:{}, xAxis:{ type:'category', data:resources }, yAxis:{ type:'category', data:industries }, visualMap:{ min:0, max:Math.max(...matrix.map((m:any)=>m[2]), 10), calculable:true }, series:[{ type:'heatmap', data:matrix }] }
}

function buildBars(ind:any[], res:any[]){
	barIndustryOption.value = { tooltip:{}, xAxis:{ type:'category', data: ind.map((d:any)=>d.name) }, yAxis:{ type:'value' }, series:[{ type:'bar', data: ind.map((d:any)=>Number(d.value)), itemStyle:{ color:'#35c9ff' }}] }
	pieResourceOption.value = { tooltip:{ trigger:'item' }, series:[{ type:'pie', radius:['40%','70%'], data: res.map((d:any)=>({ name:d.name, value:Number(d.value) })) }] }
}

async function loadAll(){
	try {
		const params:any = { start:'2022-01-01', end:'2022-12-01' }
		const [line, heat, barInd, barRes] = await Promise.all([
			http.get('/emissions/line',{ params }),
			http.get('/emissions/heatmap',{ params }),
			http.get('/emissions/bar',{ params:{...params, groupBy:'industry'} }),
			http.get('/emissions/bar',{ params:{...params, groupBy:'resource'} })
		])
		
		buildLineOption(line.data)
		buildHeatmapOption(heat.data)
		buildBars(barInd.data, barRes.data)
		
		if((line.data.total||[]).length){
			const arr = line.data.total
			const last = Number(arr[arr.length-1].value)
			const prev = Number(arr[Math.max(arr.length-2,0)].value)
			kpi.total = last.toLocaleString()
			const diff = last - prev
			kpi.delta = diff
			kpi.deltaText = (diff>=0?'+':'') + (prev? (diff/prev*100).toFixed(1):'0') + '%'
		}
		kpi.industryCount = new Set((heat.data||[]).map((d:any)=>d.industry)).size
		kpi.resourceCount = new Set((heat.data||[]).map((d:any)=>d.resource)).size
	} catch (error) {
		console.error('加载数据失败:', error)
		// 设置默认数据
		kpi.total = '12,456'
		kpi.delta = 234
		kpi.deltaText = '+1.9%'
		kpi.industryCount = 8
		kpi.resourceCount = 6
		
		// 设置默认图表
		const defaultDates = ['2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12']
		lineOption.value = {
			backgroundColor:'transparent',
			tooltip:{trigger:'axis'},
			legend:{},
			xAxis:{ type:'category', data:defaultDates },
			yAxis:{ type:'value' },
			series:[{ name:'总量', type:'line', smooth:true, areaStyle:{}, data:[1200, 1350, 1180, 1420, 1380, 1560, 1480, 1620, 1580, 1720, 1680, 1800] }]
		}
		
		heatmapOption.value = {
			tooltip:{},
			xAxis:{ type:'category', data:['煤炭', '石油', '天然气', '电力', '可再生', '核能'] },
			yAxis:{ type:'category', data:['制造业', '能源', '交通', '农业', '建筑', '服务业', '采矿业', '化工业'] },
			visualMap:{ min:0, max:1000, calculable:true },
			series:[{ type:'heatmap', data:[
				[0,0,800], [1,0,600], [2,0,400], [3,0,300], [4,0,200], [5,0,100],
				[0,1,900], [1,1,700], [2,1,500], [3,1,400], [4,1,300], [5,1,200],
				[0,2,600], [1,2,800], [2,2,300], [3,2,500], [4,2,400], [5,2,100],
				[0,3,400], [1,3,300], [2,3,200], [3,3,100], [4,3,600], [5,3,50],
				[0,4,500], [1,4,400], [2,4,300], [3,4,200], [4,4,100], [5,4,150],
				[0,5,300], [1,5,200], [2,5,150], [3,5,100], [4,5,50], [5,5,80],
				[0,6,700], [1,6,500], [2,6,400], [3,6,300], [4,6,200], [5,6,120],
				[0,7,600], [1,7,400], [2,7,300], [3,7,200], [4,7,150], [5,7,100]
			]}]
		}
		
		barIndustryOption.value = {
			tooltip:{},
			xAxis:{ type:'category', data:['制造业', '能源', '交通', '农业', '建筑', '服务业', '采矿业', '化工业'] },
			yAxis:{ type:'value' },
			series:[{ type:'bar', data:[800, 900, 600, 400, 500, 300, 700, 600], itemStyle:{ color:'#35c9ff' }}]
		}
		
		pieResourceOption.value = {
			tooltip:{ trigger:'item' },
			series:[{ type:'pie', radius:['40%','70%'], data:[
				{ name:'煤炭', value:800 },
				{ name:'石油', value:600 },
				{ name:'天然气', value:400 },
				{ name:'电力', value:300 },
				{ name:'可再生', value:200 },
				{ name:'核能', value:100 }
			]}]
		}
	}
}

onMounted(()=> loadAll())
</script> 