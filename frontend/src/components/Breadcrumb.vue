<template>
	<div class="breadcrumb">
		<button class="hamburger" @click="$emit('toggle')">
			<span></span><span></span><span></span>
		</button>
		<span class="title">{{ title || '总览' }}</span>
	</div>
</template>
<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
const title = route.meta?.title as string | undefined
</script>
<style scoped>
.breadcrumb{height:36px;display:flex;align-items:center;color:#b6c7df;gap:8px}
.hamburger{width:28px;height:22px;display:flex;flex-direction:column;justify-content:space-between;background:transparent;border:none;cursor:pointer;padding:0}
.hamburger span{display:block;height:3px;background:currentColor;border-radius:2px}
.title{font-weight:600}
</style> 