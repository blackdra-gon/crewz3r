<script setup lang="ts">
import GenericCardSelection from "../components/GenericCardSelection.vue";
import {inject, unref} from "vue";
const cards = inject('cards')
console.log(cards)
console.log(cards.length != 0)
</script>

<template>
<div class="card_selection_view">
        <button type="button" class="button" id="end_game_card">
          Spiel abbrechen
        </button>
        <div class="card_deck">
          <h2>Deine Karten</h2>
          <p>Um Karten hinzu zu fügen, nutze die Eingabeleiste unten</p>
          <div class="selected_cards card_list"></div>
        </div>
        <div v-if="cards.length != 0">  <!-- wait for cards to be loaded -->
        <generic-card-selection />
        </div>
        <div v-else>Lade Karten</div>
      </div>
</template>

<style>
</style>
