<script setup lang="ts">
import GenericCardSelection from "../components/GenericCardSelection.vue";
import {inject, provide, unref} from "vue";
import {useRouter} from "vue-router";
const tasks = inject('tasks');
const socket = inject('socket');
const router = useRouter()

provide("cards_for_selection", tasks)

const selection_submit = (selected_cards) => {
    //socket.emit("cards selected", JSON.stringify(selected_cards.value));
    router.push("../taskOrderSelection")
}
</script>

<template>
<div class="card_selection_view">
        <button type="button" class="button" id="end_game_card">
          Spiel abbrechen
        </button>
        <div class="card_deck">
          <h2>Deine Aufträge</h2>
          <p>Um Aufträge hinzu zu fügen, nutze die Eingabeleiste unten</p>
          <div class="selected_cards card_list"></div>
        </div>
        <div v-if="tasks.length != 0">  <!-- wait for cards to be loaded -->
        <generic-card-selection
          @selection_form_submit="selection_submit"
        />
        </div>
        <div v-else>Lade Karten</div>
      </div>
</template>

<style>
</style>
