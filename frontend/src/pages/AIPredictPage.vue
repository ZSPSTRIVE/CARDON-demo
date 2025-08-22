<template>
	<AppShell>
		<div class="panel" style="padding:12px;">
			<div class="card-title">排放预测</div>
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
				<select v-model="resourceType">
					<option value="coal">煤炭</option>
					<option value="oil">石油</option>
					<option value="gas">天然气</option>
					<option value="electricity">电力</option>
					<option value="renewable">可再生</option>
					<option value="nuclear">核能</option>
				</select>
				<input type="number" v-model.number="timePeriod" min="1" max="60" style="width:100px;" />
				<button class="button" @click="load">预测</button>
			</div>
			<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px;color:var(--muted)">
				<div>置信度: <b>{{ confidence }}</b></div>
				<div>碳中和年份: <b>{{ carbonNeutralYear || '-' }}</b></div>
			</div>
			<div style="height:420px;" class="panel"><EChart :option="option" /></div>
		</div>
	</AppShell>
</template>
<script setup lang="ts">
import AppShell from '../layouts/AppShell.vue'
import EChart from '../shared/EChart.vue'
import { ref } from 'vue'
import { aiPredict } from '../api/ai'

const industry = ref('manufacturing')
const resourceType = ref('coal')
const timePeriod = ref(12)
const confidence = ref('')
const carbonNeutralYear = ref<number|null>(null)
const option = ref<any>({})

async function load(){
	const { data } = await aiPredict({ industry: industry.value, resourceType: resourceType.value, timePeriod: timePeriod.value })
	confidence.value = (data.confidence ?? '').toString()
	carbonNeutralYear.value = data.carbon_neutral_year ?? null
	const dates = (data.predictions||[]).map((x:any)=> x.date)
	const values = (data.predictions||[]).map((x:any)=> Number(x.predicted_emission))
	option.value = {
		tooltip:{ trigger:'axis' },
		xAxis:{ type:'category', data: dates },
		yAxis:{ type:'value' },
		series:[{ name:'预测排放', type:'line', smooth:true, areaStyle:{}, data: values }]
	}
}

load()
</script> 