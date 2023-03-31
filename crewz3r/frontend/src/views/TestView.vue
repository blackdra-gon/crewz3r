<script setup lang="ts">

import router from "../router";
import {onMounted} from "vue";

const back = () => {
    router.back()
}

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
</template>

<style scoped>

</style>
