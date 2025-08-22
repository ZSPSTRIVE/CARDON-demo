<template>
	<div class="kpi" :style="{ borderColor: colorBorder, background: bgGradient }">
		<div style="display:flex;align-items:center;gap:10px;">
			<div class="kpi-icon" :style="{ background: colorBg }">{{ icon }}</div>
			<div>
				<div class="label">{{ label }}</div>
				<div class="value">{{ value }}</div>
			</div>
		</div>
		<div class="delta" :class="delta>=0?'up':'down'">{{ delta>=0? '▲ '+deltaText : '▼ '+deltaText }}</div>
	</div>
</template>
<script setup lang="ts">
const props = defineProps<{ label:string; value:string|number; delta:number; deltaText:string; icon?:string; color?:string }>()
const color = props.color || '#7c5cff'
const colorBorder = `rgba(124,92,255,0.35)`
const colorBg = `linear-gradient(180deg, ${color}, rgba(124,92,255,0.2))`
const bgGradient = `linear-gradient(180deg, rgba(124,92,255,0.18), rgba(124,92,255,0.05))`
</script>
<style scoped>
.kpi{border:1px solid;border-radius:12px;padding:12px}
.kpi-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff}
</style> 