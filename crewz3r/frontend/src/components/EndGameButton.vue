<script setup lang="ts">

import {inject} from "vue";

const socket = inject('socket')

const end_game = () => {
    socket.emit("end game");
}
</script>

<template>
        <button type="button" class="button" id="end_game_button" @click="end_game">
          Spiel abbrechen
        </button>
</template>

<style scoped>

#end_game_button {
    position: fixed;
    right: 1rem;
    top: 1rem;
    background: var(--card-red);
}

</style>
