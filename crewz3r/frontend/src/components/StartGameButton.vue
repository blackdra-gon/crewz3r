<script setup lang="ts">
    import { inject } from 'vue'

    const socket = inject('socket')
  
    const start_game = () => {
        console.log("hallo", socket);
        socket.emit('start card selection')
    }
</script>

<template>
    <button type="button" @click="start_game">
        Spiel starten
    </button>
</template>
