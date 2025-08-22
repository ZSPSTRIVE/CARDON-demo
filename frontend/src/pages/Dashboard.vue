<template>
	<AppShell>
		<div class="grid-3">
			<KpiCard label="观测总量" :value="kpi.total" :delta="kpi.delta" :deltaText="kpi.deltaText" icon="👁" color="#7c5cff" />
			<KpiCard label="行业覆盖" :value="kpi.industryCount" :delta="0" :deltaText="' '" icon="🏭" color="#35c9ff" />
			<KpiCard label="资源覆盖" :value="kpi.resourceCount" :delta="0" :deltaText="' '" icon="⛽" color="#22d3ee" />
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
}

onMounted(()=> loadAll())
</script> 