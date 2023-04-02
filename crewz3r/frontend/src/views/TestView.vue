<script setup lang="ts">

import router from "../router";
import {onMounted, ref} from "vue";

const back = () => {
    router.back()
}

const colors = [-1, 0, 1, 2, 3]

const view_1 = ref(false)


onMounted( () => {
    const content = document.createElement("p")
    content.innerText = "Hello World"
    const checkbox = document.createElement("input")
    checkbox.setAttribute("type", "checkbox")
    checkbox.setAttribute("v-model", "view_1")
    document.getElementById("dynamic_content").appendChild(content)
    document.getElementById("dynamic_content").appendChild(checkbox)
})
</script>

<template>
    <p>Test View</p>
    <button type="button" @click="back"> Back </button>
    <div id="dynamic_content"></div>
    <button @click="view_1 = !view_1">Toggle View</button>
    <p v-if="view_1">view 1</p>
    <p v-else>view_2</p>
    <input type="checkbox" v-model="view_1">
    <button v-for="color in colors">{{ color }}</button>
</template>

<style scoped>

</style>
