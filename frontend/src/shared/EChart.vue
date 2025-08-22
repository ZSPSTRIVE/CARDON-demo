<template>
	<div ref="el" style="width:100%;height:100%;"></div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { ref, onMounted, onBeforeUnmount, watch, type Ref } from 'vue'

const props = defineProps<{ option: any }>()
const el: Ref<HTMLDivElement | null> = ref(null)
let chart: echarts.ECharts | null = null

onMounted(() => {
	if (el.value) {
		chart = echarts.init(el.value)
		if (props.option) chart.setOption(props.option)
		window.addEventListener('resize', resize)
	}
})

onBeforeUnmount(() => {
	window.removeEventListener('resize', resize)
	chart?.dispose()
})

watch(() => props.option, (opt) => {
	if (chart && opt) chart.setOption(opt, true)
}, { deep: true })

function resize() {
	chart?.resize()
}
</script> 