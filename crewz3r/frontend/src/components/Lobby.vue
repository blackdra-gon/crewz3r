<script setup lang="ts">
import {computed, inject, ref} from 'vue'
import {VueCookies} from "vue-cookies";

type Users = [{
  name: string;
}];

const users: Users = inject('users')

</script>

<template>
    <p>
        <span data-user-count>{{ users.length }}</span> in der Lobby
    </p>
    <ul v-for="user in users">
        <li>{{ user.name }}</li>
    </ul>
</template>
