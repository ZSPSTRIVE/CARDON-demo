<template>
	<div class="panel chart-card">
		<div class="card-title">
			<span>{{ title }}</span>
		</div>
		<div class="chart-body">
			<slot />
		</div>
	</div>
</template>
<script setup lang="ts">
defineProps<{ title:string }>()
</script> 