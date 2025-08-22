<template>
	<div class="bigscreen" style="grid-template-rows:72px 1fr 36px;">
		<HeaderBar />
		<div class="panel" style="max-width:800px;margin:0 auto;width:100%;">
			<div class="card-title">CSV 数据导入</div>
			<p style="color:var(--muted)">模板字段：date, industry, resource, region, emission</p>
			<input type="file" accept=".csv" @change="onFile" />
			<button class="button" style="margin-left:12px" :disabled="!file" @click="upload">上传</button>
			<div v-if="loading" style="margin-top:12px;color:var(--muted)">上传中...</div>
			<div v-if="result" style="margin-top:12px;">
				<div>成功：{{ result.success }}，失败：{{ result.failed }}</div>
				<ul style="max-height:200px;overflow:auto;color:#fca5a5">
					<li v-for="(e,i) in result.errors" :key="i">{{ e }}</li>
				</ul>
			</div>
		</div>
		<div class="footer"><span>数据导入</span><span>需要管理员权限</span></div>
	</div>
</template>
<script setup lang="ts">
import HeaderBar from '../components/HeaderBar.vue'
import http from '../api/http'
import { ref } from 'vue'

const file = ref<File|null>(null)
const loading = ref(false)
const result = ref<any>(null)

function onFile(e:any){ file.value = e.target.files?.[0] || null }

async function upload(){
	if(!file.value) return
	loading.value = true
	const form = new FormData()
	form.append('file', file.value)
	try{
		const { data } = await http.post('/emissions/import', form, { headers:{ 'Content-Type':'multipart/form-data' } })
		result.value = data
	}catch(err:any){
		result.value = { success:0, failed:0, errors:[err?.response?.data?.message || '上传失败'] }
	}finally{
		loading.value = false
	}
}
</script> 