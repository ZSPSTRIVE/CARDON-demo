<template>
	<div class="app-shell" :style="{ ['--sidebar-w']: sidebarWidth }">
		<header class="app-header"><TopBar /></header>
		<aside class="app-sidebar">
			<Sidebar :collapsed="isCollapsed && !isHovering" @enter="onHover(true)" @leave="onHover(false)" />
		</aside>
		<main class="app-main">
			<Breadcrumb @toggle="toggleCollapse" />
			<slot />
		</main>
	</div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import TopBar from '../components/TopBar.vue'
import Sidebar from '../components/Sidebar.vue'
import Breadcrumb from '../components/Breadcrumb.vue'

const isCollapsed = ref(false)
const isHovering = ref(false)
const sidebarWidth = computed(() => (isCollapsed.value && !isHovering.value) ? '56px' : '220px')
function toggleCollapse(){ isCollapsed.value = !isCollapsed.value }
function onHover(v:boolean){ isHovering.value = v }
</script>
<style scoped>
.app-shell{min-height:100vh;display:grid;grid-template-rows:56px 1fr;grid-template-columns:var(--sidebar-w, 220px) 1fr;gap:16px;padding:16px;box-sizing:border-box;transition:grid-template-columns .2s ease}
.app-header{grid-column:1/3}
.app-sidebar{overflow:visible}
.app-main{overflow:auto}
</style> 