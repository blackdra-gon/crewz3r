<script setup lang="ts">
import GenericCardSelection from "../components/GenericCardSelection.vue";
import {inject, provide, unref} from "vue";
import {useRouter} from "vue-router";
import EndGameButton from "../components/EndGameButton.vue";

const tasks = inject('tasks');
const selected_tasks = inject('selected_tasks')
const socket = inject('socket');
const router = useRouter()

provide("cards_for_selection", tasks)

const selection_submit = (selected_cards) => {
    //socket.emit("cards selected", JSON.stringify(selected_cards.value));
    selected_tasks.value = selected_cards.value;
    router.push("../taskOrderSelection")
}
</script>

<template>
<div class="card_selection_view">
        <EndGameButton />
        <div class="card_deck">
          <h2>Deine Aufträge</h2>
          <p>Um Aufträge hinzu zu fügen, nutze die Eingabeleiste unten</p>
          <div class="selected_cards card_list"></div>
        </div>
        <div>
        <generic-card-selection
          @selection_form_submit="selection_submit"
        />
        </div>
      </div>
</template>

<style>
</style>
