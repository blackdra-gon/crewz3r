<script setup lang="ts">
    import { inject } from 'vue'
    import router from "../router";

    const socket = inject('socket')

    const start_game = () => {
        console.log("start game, socket object:", socket);
        socket.emit('start card selection')
    }

    const test_view = () => {
        router.push("testView")
    }
</script>

<template>
    <button type="button" @click="start_game">
        Spiel starten
    </button>
    <button type="button"  @click="test_view"> Test View </button>
</template>
