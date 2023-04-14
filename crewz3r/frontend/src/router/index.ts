import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CardSelectionView from '../views/CardSelectionView.vue'
import TestView from '../views/TestView.vue'
import TaskSelectionView from '../views/TaskSelectionView.vue'
import TaskOrderSelectionView from "../views/TaskOrderSelectionView.vue";
import ResultView from "../views/ResultView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/cardSelection',
      name: 'cardSelection',
      component: CardSelectionView
    },
    {
      path: '/taskSelection',
      name: 'taskSelection',
      component: TaskSelectionView
    },
    {
      path: '/taskOrderSelection',
      name: 'taskOrderSelection',
      component: TaskOrderSelectionView
    },
        {
      path: '/result',
      name: 'result',
      component: ResultView
    },
    {
      path: '/testView',
      name: 'testView',
      component: TestView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router
