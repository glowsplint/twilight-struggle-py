<template>
  <v-app>
    <v-content>
      <router-view></router-view>
    </v-content>
    <NavBar />
    <Footer />
  </v-app>
</template>

<script>
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";

export default {
  name: "App",
  components: { NavBar, Footer }
};
</script>
