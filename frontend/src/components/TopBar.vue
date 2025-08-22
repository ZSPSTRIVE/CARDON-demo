<template>
	<header class="topbar">
		<div class="brand">
			<div class="logo">中国碳排放数据可视化</div>
		</div>
		<div class="actions">
			<button class="icon-btn" title="主题" @click="toggleTheme"><Icon icon="ph:sun" /></button>
			<button class="icon-btn" title="通知"><Icon icon="ph:bell" /></button>
			<button class="icon-btn" title="消息"><Icon icon="ph:chat-circle" /></button>
			<router-link to="/login" class="icon-btn" title="用户"><Icon icon="ph:user" /></router-link>
		</div>
	</header>
</template>
<script setup lang="ts">
import { Icon } from '@iconify/vue'
function toggleTheme(){
	document.documentElement.classList.toggle('light')
}
</script>
<style scoped>
.topbar{height:56px;display:flex;align-items:center;justify-content:space-between;background:rgba(15,26,43,0.8);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0 12px}
.logo{background:#ef4444;color:#fff;padding:8px 12px;border-radius:6px;font-weight:700;letter-spacing:1px}
a.icon-btn, .icon-btn{display:flex;align-items:center;justify-content:center;width:36px;height:36px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#eaf2ff;border-radius:8px;cursor:pointer}
.icon-btn:hover{background:rgba(255,255,255,0.12)}
</style> 