<template>
  <v-app>
    <NavBar />
    <v-content>
      <!-- <HelloWorld /> -->
    </v-content>
  </v-app>
</template>

<script>
import NavBar from "./components/NavBar";

export default {
  components: { NavBar },
  name: "App",
  data: () => ({
    //
  })
};
</script>
