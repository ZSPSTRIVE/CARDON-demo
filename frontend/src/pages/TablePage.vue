<template>
  <div class="table-container">
    <div class="header-section">
      <h1>碳排放数据明细</h1>
      <p class="subtitle">详细的碳排放记录查询与管理</p>
    </div>
    
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>时间范围：</label>
          <div class="date-inputs">
            <input type="date" v-model="filters.startDate" @change="applyFilters">
            <span>至</span>
            <input type="date" v-model="filters.endDate" @change="applyFilters">
          </div>
        </div>
        
        <div class="filter-group">
          <label>行业类型：</label>
          <select v-model="filters.industry" @change="applyFilters">
            <option value="">全部行业</option>
            <option value="manufacturing">制造业</option>
            <option value="energy">能源业</option>
            <option value="transportation">交通运输</option>
            <option value="agriculture">农业</option>
            <option value="construction">建筑业</option>
            <option value="services">服务业</option>
            <option value="mining">采矿业</option>
            <option value="chemical">化工业</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>资源类型：</label>
          <select v-model="filters.resource" @change="applyFilters">
            <option value="">全部资源</option>
            <option value="coal">煤炭</option>
            <option value="oil">石油</option>
            <option value="gas">天然气</option>
            <option value="electricity">电力</option>
            <option value="renewable">可再生能源</option>
            <option value="nuclear">核能</option>
          </select>
        </div>
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label>排放范围：</label>
          <div class="range-inputs">
            <input type="number" v-model="filters.minEmission" placeholder="最小值" @change="applyFilters">
            <span>至</span>
            <input type="number" v-model="filters.maxEmission" placeholder="最大值" @change="applyFilters">
          </div>
        </div>
        
        <div class="filter-group">
          <label>状态：</label>
          <select v-model="filters.status" @change="applyFilters">
            <option value="">全部状态</option>
            <option value="normal">正常</option>
            <option value="anomaly">异常</option>
            <option value="warning">警告</option>
          </select>
        </div>
        
        <div class="filter-actions">
          <button class="reset-btn" @click="resetFilters">
            <i class="fas fa-undo"></i> 重置
          </button>
          <button class="export-btn" @click="exportData">
            <i class="fas fa-download"></i> 导出
          </button>
        </div>
      </div>
    </div>
    
    <div class="table-section">
      <div class="table-header">
        <div class="table-info">
          <span>共 {{ pagination.total }} 条记录</span>
          <span>当前显示 {{ pagination.start + 1 }}-{{ Math.min(pagination.start + pagination.pageSize, pagination.total) }} 条</span>
        </div>
        
        <div class="table-controls">
          <select v-model="pagination.pageSize" @change="changePageSize">
            <option value="10">10条/页</option>
            <option value="20">20条/页</option>
            <option value="50">50条/页</option>
            <option value="100">100条/页</option>
          </select>
        </div>
      </div>
      
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th @click="sortBy('id')">
                ID
                <i class="fas fa-sort" v-if="sortField !== 'id'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th @click="sortBy('date')">
                日期
                <i class="fas fa-sort" v-if="sortField !== 'date'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th @click="sortBy('industry')">
                行业
                <i class="fas fa-sort" v-if="sortField !== 'industry'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th @click="sortBy('resource')">
                资源
                <i class="fas fa-sort" v-if="sortField !== 'resource'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th @click="sortBy('emissions')">
                排放量(吨)
                <i class="fas fa-sort" v-if="sortField !== 'emissions'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th @click="sortBy('location')">
                位置
                <i class="fas fa-sort" v-if="sortField !== 'location'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th @click="sortBy('status')">
                状态
                <i class="fas fa-sort" v-if="sortField !== 'status'"></i>
                <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                <i class="fas fa-sort-down" v-else></i>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in tableData" :key="record.id" :class="getRowClass(record)">
              <td>{{ record.id }}</td>
              <td>{{ formatDate(record.date) }}</td>
              <td>
                <span class="industry-tag" :class="getIndustryClass(record.industry)">
                  {{ getIndustryName(record.industry) }}
                </span>
              </td>
              <td>
                <span class="resource-tag" :class="getResourceClass(record.resource)">
                  {{ getResourceName(record.resource) }}
                </span>
              </td>
              <td class="emission-value">{{ formatNumber(record.emissions) }}</td>
              <td>{{ record.location }}</td>
              <td>
                <span class="status-badge" :class="getStatusClass(record.status)">
                  {{ getStatusName(record.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn view-btn" @click="viewRecord(record)" title="查看详情">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="action-btn edit-btn" @click="editRecord(record)" title="编辑">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="action-btn delete-btn" @click="deleteRecord(record)" title="删除">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination">
        <button 
          class="page-btn" 
          :disabled="pagination.currentPage === 1"
          @click="goToPage(1)"
        >
          <i class="fas fa-angle-double-left"></i>
        </button>
        
        <button 
          class="page-btn" 
          :disabled="pagination.currentPage === 1"
          @click="goToPage(pagination.currentPage - 1)"
        >
          <i class="fas fa-angle-left"></i>
        </button>
        
        <span class="page-info">
          第 {{ pagination.currentPage }} 页，共 {{ pagination.totalPages }} 页
        </span>
        
        <button 
          class="page-btn" 
          :disabled="pagination.currentPage === pagination.totalPages"
          @click="goToPage(pagination.currentPage + 1)"
        >
          <i class="fas fa-angle-right"></i>
        </button>
        
        <button 
          class="page-btn" 
          :disabled="pagination.currentPage === pagination.totalPages"
          @click="goToPage(pagination.totalPages)"
        >
          <i class="fas fa-angle-double-right"></i>
        </button>
      </div>
    </div>
    
    <!-- 详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>记录详情</h3>
          <button class="close-btn" @click="closeDetailModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>ID:</label>
              <span>{{ selectedRecord.id }}</span>
            </div>
            <div class="detail-item">
              <label>日期:</label>
              <span>{{ formatDate(selectedRecord.date) }}</span>
            </div>
            <div class="detail-item">
              <label>行业:</label>
              <span>{{ getIndustryName(selectedRecord.industry) }}</span>
            </div>
            <div class="detail-item">
              <label>资源:</label>
              <span>{{ getResourceName(selectedRecord.resource) }}</span>
            </div>
            <div class="detail-item">
              <label>排放量:</label>
              <span>{{ formatNumber(selectedRecord.emissions) }} 吨</span>
            </div>
            <div class="detail-item">
              <label>位置:</label>
              <span>{{ selectedRecord.location }}</span>
            </div>
            <div class="detail-item">
              <label>状态:</label>
              <span class="status-badge" :class="getStatusClass(selectedRecord.status)">
                {{ getStatusName(selectedRecord.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import http from '../api/http'
import { ref, reactive, onMounted, computed } from 'vue'

// 响应式数据
const filters = reactive({
  startDate: '',
  endDate: '',
  industry: '',
  resource: '',
  minEmission: '',
  maxEmission: '',
  status: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0,
  start: 0
})

const sortField = ref('id')
const sortOrder = ref('asc')
const tableData = ref<any[]>([])
const showDetailModal = ref(false)
const selectedRecord = ref<any>({})

// 计算属性
const startDate = computed(() => {
  if (!filters.startDate) {
    const date = new Date()
    date.setMonth(date.getMonth() - 1)
    return date.toISOString().split('T')[0]
  }
  return filters.startDate
})

const endDate = computed(() => {
  if (!filters.endDate) {
    return new Date().toISOString().split('T')[0]
  }
  return filters.endDate
})

// 生命周期钩子
onMounted(() => {
  filters.startDate = startDate.value
  filters.endDate = endDate.value
  loadTableData()
})

// 加载表格数据
async function loadTableData() {
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      start: startDate.value,
      end: endDate.value,
      industry: filters.industry,
      resource: filters.resource,
      minEmission: filters.minEmission,
      maxEmission: filters.maxEmission,
      status: filters.status,
      sortField: sortField.value,
      sortOrder: sortOrder.value
    }
    
    const response = await http.get('/emissions/data-details', { params })
    
    if (response.data) {
      tableData.value = response.data.records
      pagination.total = response.data.totalRecords
      pagination.totalPages = response.data.totalPages
      pagination.start = (pagination.currentPage - 1) * pagination.pageSize
    }
  } catch (error) {
    console.error('加载表格数据失败:', error)
  }
}

// 应用过滤器
function applyFilters() {
  pagination.currentPage = 1
  loadTableData()
}

// 重置过滤器
function resetFilters() {
  Object.assign(filters, {
    startDate: startDate.value,
    endDate: endDate.value,
    industry: '',
    resource: '',
    minEmission: '',
    maxEmission: '',
    status: ''
  })
  applyFilters()
}

// 排序
function sortBy(field: string) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  loadTableData()
}

// 分页
function goToPage(page: number) {
  pagination.currentPage = page
  loadTableData()
}

function changePageSize() {
  pagination.currentPage = 1
  loadTableData()
}

// 查看记录详情
function viewRecord(record: any) {
  selectedRecord.value = record
  showDetailModal.value = true
}

// 编辑记录
function editRecord(record: any) {
  // 实现编辑功能
  console.log('编辑记录:', record)
}

// 删除记录
function deleteRecord(record: any) {
  if (confirm(`确定要删除ID为${record.id}的记录吗？`)) {
    // 实现删除功能
    console.log('删除记录:', record)
    loadTableData()
  }
}

// 关闭详情模态框
function closeDetailModal() {
  showDetailModal.value = false
  selectedRecord.value = {}
}

// 导出数据
function exportData() {
  // 实现导出功能
  console.log('导出数据')
}

// 工具函数
function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function formatNumber(num: number) {
  return num.toLocaleString()
}

function getIndustryName(industry: string) {
  const names: { [key: string]: string } = {
    manufacturing: '制造业',
    energy: '能源业',
    transportation: '交通运输',
    agriculture: '农业',
    construction: '建筑业',
    services: '服务业',
    mining: '采矿业',
    chemical: '化工业'
  }
  return names[industry] || industry
}

function getResourceName(resource: string) {
  const names: { [key: string]: string } = {
    coal: '煤炭',
    oil: '石油',
    gas: '天然气',
    electricity: '电力',
    renewable: '可再生能源',
    nuclear: '核能'
  }
  return names[resource] || resource
}

function getStatusName(status: string) {
  const names: { [key: string]: string } = {
    normal: '正常',
    anomaly: '异常',
    warning: '警告'
  }
  return names[status] || status
}

function getIndustryClass(industry: string) {
  return `industry-${industry}`
}

function getResourceClass(resource: string) {
  return `resource-${resource}`
}

function getStatusClass(status: string) {
  return `status-${status}`
}

function getRowClass(record: any) {
  if (record.status === 'anomaly') return 'row-anomaly'
  if (record.status === 'warning') return 'row-warning'
  return ''
}
</script>

<style scoped>
.table-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2.5em;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1em;
}

.filters-section {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 200px;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9em;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
}

.date-inputs,
.range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-inputs input,
.range-inputs input {
  width: 120px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.reset-btn,
.export-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background 0.3s;
}

.reset-btn {
  background: #95a5a6;
  color: white;
}

.reset-btn:hover {
  background: #7f8c8d;
}

.export-btn {
  background: #3498db;
  color: white;
}

.export-btn:hover {
  background: #2980b9;
}

.table-section {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.table-info {
  display: flex;
  gap: 20px;
  color: #7f8c8d;
  font-size: 0.9em;
}

.table-controls select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 15px 10px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
  cursor: pointer;
  user-select: none;
}

.data-table th:hover {
  background: #e9ecef;
}

.data-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.row-anomaly {
  background: #fff5f5;
}

.row-warning {
  background: #fffbf0;
}

.industry-tag,
.resource-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
}

.industry-manufacturing { background: #e3f2fd; color: #1976d2; }
.industry-energy { background: #fff3e0; color: #f57c00; }
.industry-transportation { background: #e8f5e8; color: #388e3c; }
.industry-agriculture { background: #f3e5f5; color: #7b1fa2; }
.industry-construction { background: #e0f2f1; color: #00796b; }
.industry-services { background: #fce4ec; color: #c2185b; }
.industry-mining { background: #fff8e1; color: #fbc02d; }
.industry-chemical { background: #f1f8e9; color: #689f38; }

.resource-coal { background: #ffebee; color: #d32f2f; }
.resource-oil { background: #fff3e0; color: #f57c00; }
.resource-gas { background: #e8f5e8; color: #388e3c; }
.resource-electricity { background: #e3f2fd; color: #1976d2; }
.resource-renewable { background: #e8f5e8; color: #388e3c; }
.resource-nuclear { background: #f3e5f5; color: #7b1fa2; }

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
}

.status-normal { background: #e8f5e8; color: #388e3c; }
.status-anomaly { background: #ffebee; color: #d32f2f; }
.status-warning { background: #fff3e0; color: #f57c00; }

.emission-value {
  font-weight: 600;
  color: #2c3e50;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.view-btn {
  background: #3498db;
  color: white;
}

.view-btn:hover {
  background: #2980b9;
}

.edit-btn {
  background: #f39c12;
  color: white;
}

.edit-btn:hover {
  background: #e67e22;
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.page-btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #3498db;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #7f8c8d;
  font-size: 0.9em;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  color: #7f8c8d;
}

.close-btn:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.detail-item label {
  font-weight: 600;
  color: #2c3e50;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: auto;
  }
  
  .filter-actions {
    margin-left: 0;
    justify-content: center;
  }
  
  .table-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .table-info {
    justify-content: center;
  }
  
  .table-controls {
    align-self: center;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .action-btn {
    width: 28px;
    height: 28px;
  }
}
</style> 