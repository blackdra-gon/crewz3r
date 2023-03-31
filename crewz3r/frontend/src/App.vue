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

<style>
:root {
    --card-width: 70px;
    --card-height: calc(70px / 0.65);
    --card-trump: black;
    --card-red: #ea5cb5;
    --card-green: #66c75d;
    --card-blue: #52c4b0;
    --card-yellow: #e0ab2c;
    --card-undefined: gray;
    --card-color--1: var(--card-trump);
    --card-color-0: var(--card-red);
    --card-color-1: var(--card-green);
    --card-color-2: var(--card-blue);
    --card-color-3: var(--card-yellow);
    --primary-color: #254a9a;
    --task-order-color: #502891;
}


</style>
