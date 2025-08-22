<template>
	<div class="panel">
		<div class="card-title">筛选条件</div>
		<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
			<div>
				<label>开始</label>
				<input type="date" v-model="local.start" />
			</div>
			<div>
				<label>结束</label>
				<input type="date" v-model="local.end" />
			</div>
			<div style="grid-column: span 2;">
				<label>行业 (逗号分隔)</label>
				<input v-model="local.industries" placeholder="能源,制造,交通" />
			</div>
			<div style="grid-column: span 2;">
				<label>资源 (逗号分隔)</label>
				<input v-model="local.resources" placeholder="煤炭,电力,汽油" />
			</div>
		</div>
		<div style="display:flex;align-items:center;gap:12px;margin-top:12px;">
			<label><input type="checkbox" v-model="local.auto" /> 自动刷新</label>
			<button class="button" @click="apply">应用</button>
		</div>
	</div>
</template>
<script setup lang="ts">
import { reactive, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps<{ 
	start:string; end:string; industries:string; resources:string; auto:boolean 
}>()
const emit = defineEmits(['update'])

const local = reactive({ ...props })
let timer:any

function apply(){ emit('update', { ...local }) }

watch(()=>local.auto, (v)=>{
	clearInterval(timer)
	if(v){ timer = setInterval(()=> apply(), 15000) }
})

onMounted(()=>{ if(local.auto){ timer = setInterval(()=> apply(), 15000) } })
onBeforeUnmount(()=> clearInterval(timer))
</script> 