<template>
  <div>
    <!-- Navigation Bar -->
    <v-navigation-drawer v-model="drawer" color="rgb(245,245,245)" app clipped>
      <v-list dense>
        <v-list-item v-for="item in sidebar" :key="item.title" :to="item.link">
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
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title>Twilight Struggle</v-toolbar-title>
    </v-app-bar>
  </div>
</template>

<script>
export default {
  props: {
    source: String
  },
  data() {
    return {
      drawer: false,
      sidebar: [
        { title: 'Home', link: '/', icon: 'mdi-home' },
        { title: 'Game', link: '/game', icon: 'mdi-gamepad' },
        {
          title: 'Analysis',
          link: '/analysis',
          icon: 'mdi-chart-scatter-plot'
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
</style>
