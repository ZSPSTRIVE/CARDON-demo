<template>
	<svg class="icon" aria-hidden="true" :style="{ width: size+'px', height: size+'px' }">
		<use :xlink:href="'#' + name"></use>
	</svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ name: string; size?: number }>(), { size: 18 })
</script>
<style scoped>
.icon{fill: currentColor}
</style> 