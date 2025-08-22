<template>
	<div class="drawer-wrap" :class="{ floating: collapsed }">
		<div class="overlay" v-if="collapsed" @mouseenter="$emit('enter')" @mouseleave="$emit('leave')"></div>
		<aside class="sidebar" :class="{ collapsed }" @mouseenter="$emit('enter')" @mouseleave="$emit('leave')">
			<div class="logo">{{ collapsed ? '' : '中国碳排放' }}</div>
			<nav>
				<router-link to="/" class="nav-item" exact-active-class="active"><IconFont name="icon-shouye" /><span v-if="!collapsed">总览</span></router-link>
				<router-link to="/heatmap" class="nav-item" exact-active-class="active"><IconFont name="icon-relitu" /><span v-if="!collapsed">热力分布</span></router-link>
				<router-link to="/industry" class="nav-item" exact-active-class="active"><IconFont name="icon-hangye" /><span v-if="!collapsed">行业分析</span></router-link>
				<router-link to="/resource" class="nav-item" exact-active-class="active"><IconFont name="icon-ziyuan" /><span v-if="!collapsed">资源分析</span></router-link>
				<router-link to="/table" class="nav-item" exact-active-class="active"><IconFont name="icon-biaoge" /><span v-if="!collapsed">数据明细</span></router-link>
				<router-link to="/import" class="nav-item" exact-active-class="active"><IconFont name="icon-shangchuan" /><span v-if="!collapsed">数据导入</span></router-link>
				<!-- AI -->
				<router-link to="/ai/predict" class="nav-item" exact-active-class="active"><IconFont name="icon-yuce" /><span v-if="!collapsed">AI预测</span></router-link>
				<router-link to="/ai/anomaly" class="nav-item" exact-active-class="active"><IconFont name="icon-yichang" /><span v-if="!collapsed">异常检测</span></router-link>
				<router-link to="/ai/carbon" class="nav-item" exact-active-class="active"><IconFont name="icon-tanxunhuan" /><span v-if="!collapsed">碳循环</span></router-link>
			</nav>
		</aside>
	</div>
</template>
<script setup lang="ts">
import IconFont from './IconFont.vue'
withDefaults(defineProps<{ collapsed?: boolean }>(), { collapsed: false })
</script>
<style scoped>
.drawer-wrap{position:relative}
.floating .sidebar{position:fixed;left:16px;top:72px;width:220px;z-index:50;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.floating .overlay{position:fixed;inset:0;background:transparent;z-index:40}
.sidebar{width:100%;background:rgba(8,14,26,0.9);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:8px;transition: all .2s ease}
.logo{font-weight:700;letter-spacing:1px;margin-bottom:8px;color:#35c9ff;white-space:nowrap;overflow:hidden}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:8px;color:#bcd7ff;border:1px solid transparent;white-space:nowrap}
.nav-item:hover{background:rgba(53,201,255,0.08);border-color:rgba(53,201,255,0.2)}
.active{background:linear-gradient(180deg,rgba(53,201,255,0.22),rgba(53,201,255,0.1));border-color:rgba(53,201,255,0.35);color:#e8f6ff}
.collapsed .logo{margin:0;text-align:center}
.collapsed .nav-item{justify-content:flex-start}
</style> 