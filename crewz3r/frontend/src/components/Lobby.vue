<script setup lang="ts">
import {computed, inject, ref} from 'vue'
import {VueCookies} from "vue-cookies";

type Users = [{
  name: string;
}];

const users: Users = inject('users')
const $cookies = inject<VueCookies>('$cookies');
const cookie_id = computed( () =>  {
  return $cookies.get('crewz3r_id')  // cookies are not reactive, so displaying the newly set cookies requires page reload
});
</script>

<template>
    <p>
      {{ cookie_id }}
    </p>
    <p>
        <span data-user-count>{{ users.length }}</span> in der Lobby
    </p>
    <ul v-for="user in users">
        <li>{{ user.name }}</li>
    </ul>
</template>
