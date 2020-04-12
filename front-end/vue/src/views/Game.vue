<template>
  <v-container class="my-5" fluid app>
    <v-row justify="center">
      <v-btn v-on:click="post">Click to POST</v-btn>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "Game",
  methods: {
    post() {
      console.log("posting..");
    }
  },
  data() {
    return {};
  }
};
</script>
