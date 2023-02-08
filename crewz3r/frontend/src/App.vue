<script setup lang="ts">
import { ref, provide } from 'vue'
import { RouterView } from 'vue-router'
// ES modules
import { io } from 'socket.io-client'

const socket = io(":5000");

const users = ref([]);

socket.on("user list", (user_string) => {
  const user_obj = JSON.parse(user_string);
  const temp_u = [];
  
  for (const id in user_obj) temp_u.push({name: user_obj[id]})

  users.value = temp_u
});

provide('socket', socket)
provide('users', users)
</script>

<template>
  <RouterView />
</template>