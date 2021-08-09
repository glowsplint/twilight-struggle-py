import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import VueDragscroll from 'vue-dragscroll'
import VueSocketIOExt from 'vue-socket.io-extended'
import io from 'socket.io-client'
import VueKonva from 'vue-konva'

const socket = io('http://localhost:5000')
Vue.use(VueSocketIOExt, socket, { store })
Vue.use(VueDragscroll)
Vue.use(VueKonva)
Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  store,
  render: (h) => h(App),
}).$mount('#app')
