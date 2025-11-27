import { createRouter, createWebHistory } from 'vue-router'
import ModelSetting from '../views/ModelSetting.vue'
import AgentCreate from '../views/AgentCreate.vue'
import UserManagement from '../views/UserManagement.vue'
import RoleManagement from '../views/RoleManagement.vue'

const routes = [
  { 
    path: '/', 
    name: 'ModelSetting', 
    component: ModelSetting 
  },
  { 
    path: '/agent-create', 
    name: 'AgentCreate', 
    component: AgentCreate 
  },
  { 
    path: '/user-management', 
    name: 'UserManagement', 
    component: UserManagement 
  },
  { 
    path: '/role-management', 
    name: 'RoleManagement', 
    component: RoleManagement 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router