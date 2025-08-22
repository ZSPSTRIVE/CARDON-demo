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
					<table style="width:100%;border-collapse:collapse;">
						<thead><tr><th style="text-align:left">措施</th><th style="text-align:right">潜力</th><th style="text-align:right">成本</th></tr></thead>
						<tbody>
							<tr v-for="(v,k) in tableItems" :key="k">
								<td style="padding:6px 4px;">{{ k }}</td>
								<td style="padding:6px 4px;text-align:right;">{{ v.potential?.toFixed?.(2) }}</td>
								<td style="padding:6px 4px;text-align:right;">{{ v.cost?.toFixed?.(2) }}</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
			<div class="panel" style="margin-top:12px;">
				<div class="card-title">地图</div>
				<div v-if="mapPath"><a :href="mapPath" target="_blank">打开地图: {{ mapPath }}</a></div>
				<div v-else style="color:var(--muted)">暂无地图输出</div>
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

const tableItems = computed(()=>{
	const p = potential.value || {}
	const keys = ['afforestation','grassland_restoration','wetland_restoration','urban_greening']
	const out:any = {}
	keys.forEach(k=>{ if(p[k]) out[k] = p[k] })
	return out
})

async function load(){
	const { data } = await aiCarbonCycle({ region: region.value, timePeriod: timePeriod.value })
	sink.value = data.carbon_sink || {}
	source.value = data.carbon_source || {}
	netEmission.value = data.net_emission ?? null
	potential.value = data.sequestration_potential || {}
	mapPath.value = data.map_data?.map_path || ''
}

load()
</script> 