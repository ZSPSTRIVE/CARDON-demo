import http from './http'

export async function aiHealth() {
	return http.get('/ai/health')
}

export async function aiPredict(params: { industry: string; resourceType: string; timePeriod: number }) {
	return http.post('/ai/predict', null, { params })
}

export async function aiAnomalies(params: { industry: string; timeRange: number }) {
	return http.post('/ai/anomalies', null, { params })
}

export async function aiCarbonCycle(params: { region: string; timePeriod: number }) {
	return http.post('/ai/carbon-cycle', null, { params })
}

export async function aiCollect(params: { sourceType: string; industry?: string; region?: string }) {
	return http.post('/ai/collect', null, { params })
}

export async function aiTaskStatus() {
	return http.get('/ai/tasks/status')
} 