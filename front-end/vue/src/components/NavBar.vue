<template>
    <v-app id="inspire">
        <!-- Navigation Bar -->
        <v-navigation-drawer v-model="drawer" color="rgb(245,245,245)" app clipped>
            <v-list dense>
                <v-list-item link>
                    <v-list-item-action>
                        <v-icon>mdi-home</v-icon>
                    </v-list-item-action>
                    <v-list-item-content>
                        <v-list-item-title>Home</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item link>
                    <v-list-item-action>
                        <v-icon>mdi-hexagon-slice-2</v-icon>
                    </v-list-item-action>
                    <v-list-item-content>
                        <v-list-item-title>Analysis</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list>
        </v-navigation-drawer>

        <!-- Header -->
        <v-app-bar app color="rgb(68, 102, 143)" dark clipped-left>
            <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
            <v-toolbar-title>Twilight Struggle</v-toolbar-title>
        </v-app-bar>

        <!-- Footer -->
        <v-content>
            <v-container class="fill-height" fluid>
                <v-row align="center" justify="center">
                    <v-col class="text-center">
                        <span class="my-2">
                            <v-btn>
                                <v-icon class="mr-3">mdi-controller-classic-outline</v-icon>New Game
                            </v-btn>
                        </span>
                    </v-col>
                </v-row>
            </v-container>
        </v-content>
        <v-footer color="rgb(68, 102, 143)" app>
            <span class="white--text">
                <b>
                    <a href="https://github.com/glowsplint/twilight-struggle-py">
                        <img src="../assets/GitHub-Mark-Light-64px.png" height="12px" class="mr-1" />
                        <span class="link">Developed by twilight-struggle-py team</span>
                    </a>
                </b>
            </span>
        </v-footer>
    </v-app>
</template>

<script>
export default {
    props: {
        source: String
    },
    data: () => ({
        drawer: null
    })
};
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