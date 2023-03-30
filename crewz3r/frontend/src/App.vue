<script setup lang="ts">
import {ref, provide, inject} from 'vue'
import { RouterView, useRouter } from 'vue-router'

// ES modules
import { io } from 'socket.io-client'
import {VueCookies} from "vue-cookies";


const users = ref([]);

const socket = io(":5000", {
  withCredentials: true
});

const router = useRouter();


// Set cookie
const $cookies = inject<VueCookies>('$cookies');

socket.on('cookie value', (cookie_value) => {
        $cookies.set('crewz3r_id', cookie_value);
      });

socket.on("user list", (user_string) => {
  const user_obj = JSON.parse(user_string);
  const temp_u = [];

  for (const id in user_obj) temp_u.push({name: user_obj[id]})

  users.value = temp_u
});

socket.on("open card selection view", () => {
  router.push("/cardSelection");
  console.log("hello from server")
});



provide('socket', socket)
provide('users', users)
</script>

<template>
  <RouterView />
</template>
