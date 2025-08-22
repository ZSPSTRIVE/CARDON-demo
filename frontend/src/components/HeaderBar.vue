<template>
	<div class="header">
		<div>
			<div class="title">碳排放可视化中枢</div>
			<div class="sub">Industry x Resource Emission Intelligence</div>
		</div>
		<div class="right">
			<div>{{ nowText }}</div>
			<button class="button" @click="toggleFull">全屏</button>
			<router-link to="/login" class="button">登录</router-link>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
const nowText = ref('')
let timer: any
function tick(){
	const d = new Date()
	nowText.value = d.toLocaleString()
}
function toggleFull(){
	const el = document.documentElement
	if (!document.fullscreenElement) el.requestFullscreen?.()
	else document.exitFullscreen?.()
}
onMounted(()=>{ tick(); timer = setInterval(tick, 1000) })
onBeforeUnmount(()=> clearInterval(timer))
</script> 