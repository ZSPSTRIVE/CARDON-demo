<template>
	<div style="max-width:360px;margin:48px auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
		<h2>登录</h2>
		<form @submit.prevent="onSubmit">
			<div style="margin:12px 0;">
				<label>用户名</label>
				<input v-model="username" style="width:100%;padding:8px;" />
			</div>
			<div style="margin:12px 0;">
				<label>密码</label>
				<input type="password" v-model="password" style="width:100%;padding:8px;" />
			</div>
			<button style="padding:8px 16px;">登录</button>
		</form>
		<p v-if="error" style="color:#dc2626;">{{ error }}</p>
	</div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

async function onSubmit() {
	try {
		const { data } = await axios.post('/api/auth/login', { username: username.value, password: password.value })
		localStorage.setItem('token', data.token)
		// 设置全局axios默认headers
		axios.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
		// 刷新页面确保所有组件都使用新的token
		window.location.href = '/'
	} catch (e: any) {
		error.value = '登录失败，请检查用户名或密码'
	}
}
</script> 