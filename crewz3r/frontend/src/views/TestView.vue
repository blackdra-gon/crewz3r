<script setup lang="ts">

import router from "../router";
import {onMounted, ref} from "vue";

const back = () => {
    router.back()
}

const view_1 = ref(false)


onMounted( () => {
    const content = document.createElement("p")
    content.innerText = "Hello World"
    document.getElementById("dynamic_content").appendChild(content)
})
</script>

<template>
    <p>Test View</p>
    <button type="button" @click="back"> Back </button>
    <div id="dynamic_content"></div>
    <button @click="view_1 = !view_1">Toggle View</button>
    <p v-if="view_1">view 1</p>
    <p v-else>view_2</p>
</template>

<style scoped>

</style>
