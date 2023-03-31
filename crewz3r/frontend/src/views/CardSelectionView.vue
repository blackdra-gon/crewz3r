<script setup lang="ts">
import genericCardSelection from "../components/GenericCardSelection.vue";
import GenericCardSelection from "../components/GenericCardSelection.vue";
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
        <generic-card-selection />
      </div>
</template>
