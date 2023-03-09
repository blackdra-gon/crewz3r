<script setup lang="ts">
import {ref, provide, inject} from 'vue'
import { RouterView } from 'vue-router'

// ES modules
import { io } from 'socket.io-client'
import {VueCookies} from "vue-cookies";

const socket = io(":5000");

const users = ref([]);




// Set cookie
const $cookies = inject<VueCookies>('$cookies');
let user_id: unknown = "1";
if (!$cookies.isKey('crewz3r_id')) {
  (async function() {
  const getCookieId = () => new Promise(resolve => {
      socket.emit('new cookie required');
      socket.on('cookie value', response => {
        resolve(response);
      });

  });

  user_id = await getCookieId(); // Waits here until it is done.
  $cookies.set('crewz3r_id', user_id)

  }());
}

// Connect to Backend-Server
socket.emit('connect backend', $cookies.get('crewz3r_id'))



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
