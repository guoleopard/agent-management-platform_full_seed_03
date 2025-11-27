<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElCard } from 'element-plus'

// 配置axios基础URL
axios.defaults.baseURL = 'http://localhost:5003/api'

// 数据模型
const models = ref([])
const agentForm = ref({
  name: '',
  description: '',
  model_id: '',
  status: 'inactive'
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入智能体名称', trigger: 'blur' }
  ],
  model_id: [
    { required: true, message: '请选择模型', trigger: 'change' }
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

// 创建智能体
const createAgent = async () => {
  try {
    await axios.post('/agents', agentForm.value)
    ElMessage.success('智能体创建成功')
    // 重置表单
    agentForm.value = {
      name: '',
      description: '',
      model_id: '',
      status: 'inactive'
    }
  } catch (error) {
    ElMessage.error('创建智能体失败：' + error.message)
  }
}

// 页面挂载时获取模型列表
onMounted(() => {
  getModels()
})
</script>

<template>
  <div class="agent-create-container">
    <div class="header">
      <h1>创建智能体</h1>
    </div>
    
    <el-card style="max-width: 600px; margin: 0 auto">
      <el-form :model="agentForm" :rules="rules" ref="agentFormRef" label-width="120px">
        <el-form-item label="智能体名称" prop="name">
          <el-input v-model="agentForm.name" placeholder="请输入智能体名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="agentForm.description" placeholder="请输入智能体描述" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="选择模型" prop="model_id">
          <el-select v-model="agentForm.model_id" placeholder="请选择模型">
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="agentForm.status" placeholder="请选择状态">
            <el-option label=" inactive" value="inactive" />
            <el-option label="运行中" value="running" />
            <el-option label="暂停" value="paused" />
            <el-option label="已停止" value="stopped" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="createAgent" style="width: 100%">创建智能体</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.agent-create-container {
  padding: 20px;
  height: 100%;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}
</style>