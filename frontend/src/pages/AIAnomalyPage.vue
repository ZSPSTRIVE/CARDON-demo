<template>
	<AppShell>
		<div class="panel" style="padding:12px;">
			<div class="card-title">异常检测</div>
			<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
				<select v-model="industry">
					<option value="manufacturing">制造业</option>
					<option value="energy">能源</option>
					<option value="transportation">交通</option>
					<option value="agriculture">农业</option>
					<option value="construction">建筑</option>
					<option value="services">服务业</option>
					<option value="mining">采矿业</option>
					<option value="chemical">化工业</option>
				</select>
				<input type="number" v-model.number="timeRange" min="7" max="365" style="width:120px;" />
				<button class="button" @click="load">检测</button>
			</div>
			<div style="height:400px;" class="panel"><EChart :option="option" /></div>
			<div style="margin-top:12px;">
				<div class="card-title">异常列表</div>
				<ul style="line-height:1.8;max-height:220px;overflow:auto;">
					<li v-for="(a,idx) in anomalies" :key="idx" style="color:#fca5a5">
						{{ a.date }} | 分数: {{ a.anomaly_score }} | 严重性: {{ a.severity }} | 原因: {{ (a.reasons||[]).join('、') }}
					</li>
				</ul>
			</div>
		</div>
	</AppShell>
</template>
<script setup lang="ts">
import AppShell from '../layouts/AppShell.vue'
import EChart from '../shared/EChart.vue'
import { ref } from 'vue'
import { aiAnomalies } from '../api/ai'

const industry = ref('energy')
const timeRange = ref(90)
const option = ref<any>({})
const anomalies = ref<any[]>([])

async function load(){
	const { data } = await aiAnomalies({ industry: industry.value, timeRange: timeRange.value })
	anomalies.value = data.anomalies || []
	// 简单可视化：按索引展示异常点
	const dates = anomalies.value.map((x:any)=> x.date)
	const scores = anomalies.value.map((x:any)=> Number(x.anomaly_score))
	option.value = {
		tooltip:{},
		xAxis:{ type:'category', data: dates },
		yAxis:{ type:'value', name:'score' },
		series:[{ type:'bar', data: scores, itemStyle:{ color:'#ef4444' } }]
	}
}

load()
</script> 