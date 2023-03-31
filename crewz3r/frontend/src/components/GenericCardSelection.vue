<script setup lang="ts">
import {inject, onMounted} from "vue";

//type Card = [number, number] // color / value

const cards/*: [Card]*/ = inject('cards')

const get_unique_colors_of_cards = () => {
  let colors = new Set();

  for (const card of cards) {
    colors.add(card[0]);
  }

  return Array.from(colors).sort();
};
onMounted( () => {
for (const color of get_unique_colors_of_cards()) {
    const color_element = document.createElement('p')
    color_element.innerText = color
    document.getElementById("card_selection_form").appendChild(color_element)
    //add_tab_for_color(color);
  }
})
</script>

<template>
<form id="card_selection_form" class="card_selection_form">
          <div class="tab">
            <button type="submit" class="finish button">Auswahl beenden</button>
          </div>
        </form>
</template>

<style scoped>

</style>
