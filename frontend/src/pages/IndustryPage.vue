<template>
	<div class="bigscreen" style="grid-template-rows:72px 1fr 36px;">
		<HeaderBar />
		<div style="display:grid;grid-template-columns:260px 1fr;gap:var(--grid-gap);">
			<FilterPanel :start="filters.start" :end="filters.end" :industries="filters.industries" :resources="filters.resources" :auto="filters.auto" @update="onUpdate" />
			<div style="display:grid;grid-template-rows:1fr 1fr;gap:var(--grid-gap);">
				<ChartCard title="行业堆叠面积趋势"><EChart :option="areaOption" /></ChartCard>
				<ChartCard title="行业Top概览"><EChart :option="topOption" /></ChartCard>
			</div>
		</div>
		<div class="footer"><span>行业分析</span><span></span></div>
	</div>
</template>
<script setup lang="ts">
import HeaderBar from '../components/HeaderBar.vue'
import FilterPanel from '../components/FilterPanel.vue'
import ChartCard from '../components/ChartCard.vue'
import EChart from '../shared/EChart.vue'
import http from '../api/http'
import { reactive, ref, onMounted } from 'vue'

const filters = reactive({ start:'2022-01-01', end:'2022-12-01', industries:'', resources:'', auto:false })
const areaOption = ref<any>({})
const topOption = ref<any>({})

function onUpdate(next:any){ Object.assign(filters, next); load() }

async function load(){
	const params:any = { start:filters.start, end:filters.end }
	const inds = filters.industries? filters.industries.split(',').map((x:string)=>x.trim()).filter(Boolean):[]
	if(inds.length) params.industries = inds
	const { data } = await http.get('/emissions/line',{ params })
	const dates = (data.total||[]).map((d:any)=>d.date)
	const series:any[] = []
	if(data.byIndustry){
		for(const [k,arr] of Object.entries<any>(data.byIndustry)){
			series.push({ name:k, type:'line', areaStyle:{}, stack:'total', smooth:true, data: arr.map((x:any)=>Number(x.value)) })
		}
	}
	areaOption.value = { tooltip:{ trigger:'axis' }, legend:{}, xAxis:{ type:'category', data:dates }, yAxis:{ type:'value' }, series }
	const top = await http.get('/emissions/bar',{ params:{...params, groupBy:'industry'} })
	topOption.value = { tooltip:{}, xAxis:{ type:'category', data: top.data.map((d:any)=>d.name) }, yAxis:{ type:'value' }, series:[{ type:'bar', data: top.data.map((d:any)=>Number(d.value)) }] }
}

onMounted(()=> load())
</script> 