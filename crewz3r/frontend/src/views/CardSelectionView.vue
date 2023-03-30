<script setup lang="ts">
import Lobby from '../components/Lobby.vue'
import FormName from '../components/FormName.vue'
import StartGameButton from '../components/StartGameButton.vue'
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
        <form id="card_selection_form" class="card_selection_form">
          <div class="tab">
            <button type="submit" class="finish button">Auswahl beenden</button>
          </div>
        </form>
      </div>
</template>
