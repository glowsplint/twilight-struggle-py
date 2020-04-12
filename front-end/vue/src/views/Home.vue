<template>
  <v-container class="my-5" fluid app>
    <v-row>
      <v-col cols="12">
        <v-img src="../assets/TitleSplash.png" max-height="25%" contain />
        <v-row justify="center">
          <v-btn
            class="ma-2"
            v-for="clickable in clickables"
            :key="clickable.title"
          >
            <v-icon class="mr-3">{{ clickable.icon }}</v-icon>
            {{ clickable.title }}
          </v-btn>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      justify: "space-around",
      clickables: [
        { title: "New Game", icon: "mdi-controller-classic-outline" },
        { title: "Load Game", icon: "mdi-folder-upload-outline" },
        { title: "Save Game", icon: "mdi-content-save-move-outline" }
      ]
    };
  }
};
</script>
