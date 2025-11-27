<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElTable, ElTableColumn, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElTag } from 'element-plus'

// 配置axios基础URL
axios.defaults.baseURL = 'http://localhost:5003/api'

// 数据模型
const users = ref([])
const roles = ref([])
const dialogVisible = ref(false)
const editingUser = ref(null)
const userForm = ref({
  username: '',
  email: '',
  password: '',
  role_id: '',
  status: 'active'
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  role_id: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 获取用户列表
const getUsers = async () => {
  try {
    const response = await axios.get('/users')
    users.value = response.data.users
  } catch (error) {
    ElMessage.error('获取用户列表失败：' + error.message)
  }
}

// 获取角色列表
const getRoles = async () => {
  try {
    const response = await axios.get('/roles')
    roles.value = response.data.roles
  } catch (error) {
    ElMessage.error('获取角色列表失败：' + error.message)
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  editingUser.value = null
  userForm.value = {
    username: '',
    email: '',
    password: '',
    role_id: '',
    status: 'active'
  }
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (user) => {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    email: user.email,
    password: '', // 编辑时不显示密码
    role_id: user.role_id,
    status: user.status
  }
  dialogVisible.value = true
}

// 保存用户
const saveUser = async () => {
  try {
    if (editingUser.value) {
      // 编辑用户，移除空密码
      const formData = { ...userForm.value }
      if (!formData.password) {
        delete formData.password
      }
      await axios.put(`/users/${editingUser.value.id}`, formData)
      ElMessage.success('用户更新成功')
    } else {
      // 创建用户
      await axios.post('/users', userForm.value)
      ElMessage.success('用户创建成功')
    }
    dialogVisible.value = false
    getUsers()
  } catch (error) {
    ElMessage.error('保存用户失败：' + error.message)
  }
}

// 删除用户
const deleteUser = async (userId) => {
  try {
    await axios.delete(`/users/${userId}`)
    ElMessage.success('用户删除成功')
    getUsers()
  } catch (error) {
    ElMessage.error('删除用户失败：' + error.message)
  }
}

// 页面挂载时获取用户和角色列表
onMounted(() => {
  getUsers()
  getRoles()
})
</script>

<template>
  <div class="user-management-container">
    <div class="header">
      <h1>用户管理</h1>
      <el-button type="primary" @click="openCreateDialog">添加用户</el-button>
    </div>
    
    <el-table :data="users" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role_name" label="角色" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
            {{ scope.row.status === 'active' ? '活跃' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="200" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="primary" size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteUser(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 用户创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingUser ? '编辑用户' : '添加用户'" width="500px">
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" placeholder="请输入密码" type="password" :show-password="true" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="userForm.role_id" placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="userForm.status" placeholder="请选择状态">
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.user-management-container {
  padding: 20px;
  height: 100%;
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