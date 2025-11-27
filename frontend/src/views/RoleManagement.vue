<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElTable, ElTableColumn, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElTag, ElCheckboxGroup, ElCheckbox } from 'element-plus'

// 配置axios基础URL
axios.defaults.baseURL = 'http://localhost:5003/api'

// 数据模型
const roles = ref([])
const users = ref([])
const dialogVisible = ref(false)
const userAssignmentDialogVisible = ref(false)
const editingRole = ref(null)
const roleForm = ref({
  name: '',
  description: '',
  status: 'active'
})
const selectedRole = ref(null)
const selectedUsers = ref([])

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ]
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

// 获取用户列表
const getUsers = async () => {
  try {
    const response = await axios.get('/users')
    users.value = response.data.users
  } catch (error) {
    ElMessage.error('获取用户列表失败：' + error.message)
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  editingRole.value = null
  roleForm.value = {
    name: '',
    description: '',
    status: 'active'
  }
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (role) => {
  editingRole.value = role
  roleForm.value = {
    name: role.name,
    description: role.description,
    status: role.status
  }
  dialogVisible.value = true
}

// 打开用户分配对话框
const openUserAssignmentDialog = (role) => {
  selectedRole.value = role
  // 初始化已选用户
  selectedUsers.value = role.users.map(user => user.id)
  userAssignmentDialogVisible.value = true
}

// 保存角色
const saveRole = async () => {
  try {
    if (editingRole.value) {
      // 编辑角色
      await axios.put(`/roles/${editingRole.value.id}`, roleForm.value)
      ElMessage.success('角色更新成功')
    } else {
      // 创建角色
      await axios.post('/roles', roleForm.value)
      ElMessage.success('角色创建成功')
    }
    dialogVisible.value = false
    getRoles()
  } catch (error) {
    ElMessage.error('保存角色失败：' + error.message)
  }
}

// 分配用户给角色
const assignUsersToRole = async () => {
  try {
    await axios.post(`/roles/${selectedRole.value.id}/assign-users`, { user_ids: selectedUsers.value })
    ElMessage.success('用户分配成功')
    userAssignmentDialogVisible.value = false
    getRoles() // 刷新角色列表以更新用户信息
  } catch (error) {
    ElMessage.error('用户分配失败：' + error.message)
  }
}

// 删除角色
const deleteRole = async (roleId) => {
  try {
    await axios.delete(`/roles/${roleId}`)
    ElMessage.success('角色删除成功')
    getRoles()
  } catch (error) {
    ElMessage.error('删除角色失败：' + error.message)
  }
}

// 页面挂载时获取角色和用户列表
onMounted(() => {
  getRoles()
  getUsers()
})
</script>

<template>
  <div class="role-management-container">
    <div class="header">
      <h1>角色管理</h1>
      <el-button type="primary" @click="openCreateDialog">添加角色</el-button>
    </div>
    
    <el-table :data="roles" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="角色名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="user_count" label="用户数量" width="120">
        <template #default="scope">
          <span>{{ scope.row.users.length }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
            {{ scope.row.status === 'active' ? '活跃' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="200" />
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button type="primary" size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button type="success" size="small" @click="openUserAssignmentDialog(scope.row)">分配用户</el-button>
          <el-button type="danger" size="small" @click="deleteRole(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 角色创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingRole ? '编辑角色' : '添加角色'" width="500px">
      <el-form :model="roleForm" :rules="rules" ref="roleFormRef" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" placeholder="请输入描述" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="roleForm.status" placeholder="请选择状态">
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRole">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 用户分配对话框 -->
    <el-dialog v-model="userAssignmentDialogVisible" title="分配用户" width="600px">
      <div v-if="selectedRole" class="user-assignment-container">
        <h3>角色：{{ selectedRole.name }}</h3>
        <el-checkbox-group v-model="selectedUsers" style="max-height: 400px; overflow-y: auto; display: block;">
          <el-checkbox
            v-for="user in users"
            :key="user.id"
            :label="user.id"
            style="display: block; margin-bottom: 10px;"
          >
            {{ user.username }} ({{ user.email }})
          </el-checkbox>
        </el-checkbox-group>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userAssignmentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="assignUsersToRole">保存分配</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.role-management-container {
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

.user-assignment-container {
  padding: 20px 0;
}

.user-assignment-container h3 {
  margin-top: 0;
  margin-bottom: 20px;
}
</style>