import Vue from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import VueDragscroll from 'vue-dragscroll'
import VueSocketIO from 'vue-socket.io'

Vue.use(VueDragscroll)
Vue.use(
  new VueSocketIO({
    debug: true,
    connection: 'http://localhost:5000'
  })
)
Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')
