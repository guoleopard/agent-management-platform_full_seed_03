import { createRouter, createWebHistory } from 'vue-router'
import ModelSetting from '../views/ModelSetting.vue'
import AgentCreate from '../views/AgentCreate.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router