import { createRouter, createWebHistory } from 'vue-router'

const Dashboard = () => import('./pages/Dashboard.vue')
const HeatmapPage = () => import('./pages/HeatmapPage.vue')
const IndustryPage = () => import('./pages/IndustryPage.vue')
const ResourcePage = () => import('./pages/ResourcePage.vue')
const TablePage = () => import('./pages/TablePage.vue')
const ImportPage = () => import('./pages/ImportPage.vue')
const Login = () => import('./pages/Login.vue')

// AI pages
const AIPredictPage = () => import('./pages/AIPredictPage.vue')
const AIAnomalyPage = () => import('./pages/AIAnomalyPage.vue')
const AICarbonCyclePage = () => import('./pages/AICarbonCyclePage.vue')

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{ path: '/', component: Dashboard, meta: { title: '总览' } },
		{ path: '/heatmap', component: HeatmapPage, meta: { title: '热力分布' } },
		{ path: '/industry', component: IndustryPage, meta: { title: '行业分析' } },
		{ path: '/resource', component: ResourcePage, meta: { title: '资源分析' } },
		{ path: '/table', component: TablePage, meta: { title: '数据明细' } },
		{ path: '/import', component: ImportPage, meta: { title: '数据导入' } },
		{ path: '/ai/predict', component: AIPredictPage, meta: { title: 'AI预测' } },
		{ path: '/ai/anomaly', component: AIAnomalyPage, meta: { title: '异常检测' } },
		{ path: '/ai/carbon', component: AICarbonCyclePage, meta: { title: '碳循环' } },
		{ path: '/login', component: Login, meta: { title: '登录' } }
	]
})

export default router 