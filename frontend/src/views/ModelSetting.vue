<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElTable, ElTableColumn, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption } from 'element-plus'

// 配置axios基础URL
axios.defaults.baseURL = 'http://localhost:5000/api'

// 数据模型
const models = ref([])
const dialogVisible = ref(false)
const editingModel = ref(null)
const modelForm = ref({
  name: '',
  description: '',
  api_endpoint: '',
  model_name: '',
  status: 'active'
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  api_endpoint: [
    { required: true, message: '请输入API端点', trigger: 'blur' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ]
}

// 获取模型列表
const getModels = async () => {
  try {
    const response = await axios.get('/models')
    models.value = response.data.models
  } catch (error) {
    ElMessage.error('获取模型列表失败：' + error.message)
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  editingModel.value = null
  modelForm.value = {
    name: '',
    description: '',
    api_endpoint: '',
    model_name: '',
    status: 'active'
  }
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (model) => {
  editingModel.value = model
  modelForm.value = {
    name: model.name,
    description: model.description,
    api_endpoint: model.api_endpoint,
    model_name: model.model_name,
    status: model.status
  }
  dialogVisible.value = true
}

// 保存模型
const saveModel = async () => {
  try {
    if (editingModel.value) {
      // 编辑模型
      await axios.put(`/models/${editingModel.value.id}`, modelForm.value)
      ElMessage.success('模型更新成功')
    } else {
      // 创建模型
      await axios.post('/models', modelForm.value)
      ElMessage.success('模型创建成功')
    }
    dialogVisible.value = false
    getModels()
  } catch (error) {
    ElMessage.error('保存模型失败：' + error.message)
  }
}

// 删除模型
const deleteModel = async (modelId) => {
  try {
    await axios.delete(`/models/${modelId}`)
    ElMessage.success('模型删除成功')
    getModels()
  } catch (error) {
    ElMessage.error('删除模型失败：' + error.message)
  }
}

// 页面挂载时获取模型列表
onMounted(() => {
  getModels()
})
</script>

<template>
  <div class="model-setting-container">
    <div class="header">
      <h1>Ollama模型设置</h1>
      <el-button type="primary" @click="openCreateDialog">创建模型</el-button>
    </div>
    
    <el-table :data="models" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="模型名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="api_endpoint" label="API端点" />
      <el-table-column prop="model_name" label="Ollama模型名称" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
            {{ scope.row.status === 'active' ? '活跃' : ' inactive' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="200" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="primary" size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteModel(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 模型创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingModel ? '编辑模型' : '创建模型'" width="500px">
      <el-form :model="modelForm" :rules="rules" ref="modelFormRef" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="modelForm.description" placeholder="请输入描述" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="API端点" prop="api_endpoint">
          <el-input v-model="modelForm.api_endpoint" placeholder="请输入API端点" />
        </el-form-item>
        <el-form-item label="Ollama模型名称" prop="model_name">
          <el-input v-model="modelForm.model_name" placeholder="请输入Ollama模型名称" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="modelForm.status" placeholder="请选择状态">
            <el-option label="活跃" value="active" />
            <el-option label=" inactive" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveModel">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.model-setting-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dialog-footer {
  text-align: right;
}
</style>