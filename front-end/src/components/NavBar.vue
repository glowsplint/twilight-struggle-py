<template>
  <div>
    <!-- Navigation Bar -->
    <v-navigation-drawer v-model="drawer" color="rgb(245,245,245)" app clipped>
      <v-list dense>
        <v-list-item
          v-for="item in sidebar"
          :key="item.title"
          :to="item.link"
          :disabled="item.disabled"
        >
          <v-list-item-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Header -->
    <v-app-bar color="rgb(68, 102, 143)" dark app clipped-left>
      <v-app-bar-nav-icon @click.stop="toggleDrawer" />
      <v-toolbar-title>Twilight Struggle</v-toolbar-title>
      <v-spacer />
      <transition name="error-fade" mode="out-in">
        <v-chip
          class="ma-4"
          :color="connectionStatus ? `green` : `red`"
          text-color="white"
          v-bind:key="connectionStatus"
          >{{ connectionStatus ? 'Connected' : 'Disconnected' }}</v-chip
        >
      </transition>
      <router-link to="/">
        <v-img src="@/assets/ts_icon_1024.png" max-height="40" max-width="40" />
      </router-link>
    </v-app-bar>
  </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
  mounted() {
    this.$nextTick(function() {
      window.addEventListener('keydown', event => {
        if (!event.ctrlKey && event.key === '`') {
          this.toggleDrawer()
        }
      })
    })
  },
  methods: {
    toggleDrawer() {
      this.drawer = !this.drawer
      this.updateGameListItem()
    },
    updateGameListItem() {
      this.sidebar.find(item => item.title == 'Game').disabled = !this
        .gameInProgress
    }
  },
  computed: {
    connectionStatus() {
      return this.$socket.connected
    },
    ...mapState({
      gameInProgress: state => state.locals.gameInProgress,
      replaceInProgress: state => state.locals.replaceInProgress
    })
  },
  data() {
    return {
      drawer: false,
      sidebar: [
        { title: 'Home', link: '/', icon: 'mdi-home', disabled: false },
        { title: 'Game', link: '/game', icon: 'mdi-nuke', disabled: true },
        {
          title: 'Analysis',
          link: '/analysis',
          icon: 'mdi-chart-scatter-plot',
          disabled: true
        },
        {
          title: 'Replay Viewer',
          link: 'replay',
          icon: 'mdi-play-speed',
          disabled: true
        },
        {
          title: 'Card Gallery',
          link: 'cards',
          icon: 'mdi-cards-outline',
          disabled: true
        }
      ]
    }
  }
}
</script>

<style>
a,
.link,
.link:hover {
  color: white;
  text-decoration: none;
  background-color: none;
  font-weight: normal;
}

#error {
  color: red;
  font-weight: bold;
}

.error-fade-enter,
.error-fade-leave-to {
  opacity: 0;
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: all 0.2s ease;
}
</style>
