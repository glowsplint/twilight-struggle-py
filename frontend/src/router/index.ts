import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Twilight Struggle' },
  },
  {
    path: '/game',
    name: 'Game',
    component: () => import('@/views/Game.vue'),
    meta: { title: 'Twilight Struggle' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: 'Game Analysis' },
  },
  {
    path: '/cards',
    name: 'Cards',
    component: () => import('@/views/Cards.vue'),
    meta: { title: 'Card Gallery' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  next()
})

export default router
