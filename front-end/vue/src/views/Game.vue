<template>
    <div>
        <v-container class="my-n3" fluid app>
            <v-row class="img-wrapper" v-dragscroll="true">
                <img src="@/assets/big.jpg" />
            </v-row>
            <v-row justify="center">
                <v-btn v-on:click="post">Click to POST</v-btn>
            </v-row>
        </v-container>
    </div>
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

<style>
.img-wrapper {
    overflow: hidden;
    height: 80vh;
    background-color: black;
    position: relative;
}

.img-wrapper > img {
    height: 400%;
    vertical-align: bottom;
}
</style>