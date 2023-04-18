<script setup lang="ts">
import GenericCardSelection from "../components/GenericCardSelection.vue";
import {inject, provide, unref} from "vue";
import {useRouter} from "vue-router";
import EndGameButton from "../components/EndGameButton.vue";
const cards = inject('cards');
const socket = inject('socket');
const router = useRouter()
console.log(cards)
console.log(cards.length != 0)

provide('cards_for_selection', cards)

const selection_submit = (selected_cards) => {
    socket.emit("cards selected", JSON.stringify(selected_cards.value));
    router.push("../taskSelection")
}
</script>

<template>
<div class="card_selection_view">
        <EndGameButton />
        <div class="card_deck">
          <h2>Deine Karten</h2>
          <p>Um Karten hinzu zu fügen, nutze die Eingabeleiste unten</p>
          <div class="selected_cards card_list"></div>
        </div>
        <div v-if="cards.length != 0">  <!-- wait for cards to be loaded -->
        <generic-card-selection
          @selection_form_submit="selection_submit"
        />
        </div>
        <div v-else>Lade Karten</div>
      </div>
</template>

<style>
</style>
