<script setup lang="ts">
import {ref, provide, inject, reactive} from 'vue'
import { RouterView, useRouter } from 'vue-router'

// ES modules
import { io } from 'socket.io-client'
import {VueCookies} from "vue-cookies";


const users = ref([]);

type Card = [number, number] // color / value

const cards = reactive([])

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

  users.value = temp_u;
});

socket.on("card list", (cards_string) => {
  const cards_obj = JSON.parse(cards_string);

  for (const id in cards_obj) cards.push(cards_obj[id])

  console.log(cards)
});

socket.on("open card selection view", () => {
  router.push("/cardSelection");
  console.log("server: open card selection view")
});



provide('socket', socket)
provide('users', users)
provide('cards', cards)
</script>

<template>
  <RouterView />
</template>
