<script setup lang="ts">
import {inject, provide, ref} from 'vue'
import {RouterView} from 'vue-router'

// ES modules
import {io} from 'socket.io-client'
import {VueCookies} from "vue-cookies";


const users = ref([]);

const $cookies = inject<VueCookies>('$cookies');
/*if (!$cookies.isKey('crewz3r_id')) {
  fetch("http://".concat(window.location.hostname.concat(":5000/cookie")))
    .then(response => { return response.text(); })
    .then(text => $cookies.set('crewz3r_id', text));
}*/

function request_cookie() {
  fetch("http://".concat(window.location.hostname.concat(":5000/cookie")))
    .then(response => { return response.text(); })
    .then(text => $cookies.set('crewz3r_id', text));
}

function check_for_cookie() {
  if ($cookies.isKey('crewz3r_id')) {
    return;
  } else {
    request_cookie();
  }
}

let socket;

async function connect_to_backend() {
  await check_for_cookie();
  socket = io(":5000", {withCredentials: true});


}

//connect_to_backend()


function get_cookie(callback) {
  if (!$cookies.isKey('crewz3r_id')) {
    request_cookie();
  }
  callback();
}

function open_socket() {
  socket = io(":5000", {withCredentials: true});
  provide('socket', socket)

}


get_cookie(open_socket);

socket.on("user list", (user_string) => {
  const user_obj = JSON.parse(user_string);
  const temp_u = [];

  for (const id in user_obj) temp_u.push({name: user_obj[id]})

  users.value = temp_u
});






provide('users', users)
</script>

<template>
  <RouterView />
</template>
