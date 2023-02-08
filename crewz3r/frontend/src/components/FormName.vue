<script setup lang="ts">
    import { Socket } from "socket.io-client";
    import { inject } from 'vue'

    const socket: Socket = inject('socket')

    const submit = (e) => {
        const formData = new FormData(e.target);
        socket.emit("update name", formData.get("name"))
    }
</script>

<template>
    <form @submit.prevent="submit">
        <input type="text" name="name" />
        <button class="button" type="submit">Name ändern</button>
    </form>
</template>