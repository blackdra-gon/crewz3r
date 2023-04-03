<script setup lang="ts">
import {computed, inject, onMounted, reactive, ref} from "vue";

//type Card = [number, number] // color / value

const socket = inject("socket");

const emit = defineEmits(['selection_form_submit'])

const selected_cards_strings = ref([])

function stringToArray(str) {
  // Remove the square brackets from the string
  str = str.slice(1, -1);
  // Split the string by the comma and convert each element to a number
  return str.split(",").map(Number);
}

const selected_cards = computed( () => {
    const selected_cards_array = []
    for (const card_string of selected_cards_strings.value) {
        selected_cards_array.push(stringToArray(card_string))
    }
    return selected_cards_array
})

const cards/*: [Card]*/ = inject('cards_for_selection')



const color_list = computed(() => {
    let colors = new Set();

  for (const card of cards) {
    colors.add(card[0]);
  }

  return Array.from(colors).sort();
});

const number_list = (card_color) => {
      const numbers = new Set();

  for (const card of cards) {
    const color = card[0];
    const number = card[1];

    if (color == card_color) {
      numbers.add(number);
    }
  }

  return Array.from(numbers).sort();
};

onMounted( () => {
    document.querySelector(".tab .tablink").click();
    document.querySelectorAll(".tab").forEach((tab_element) => {
        tab_element.addEventListener("click", ({target}) => {
            if (target.classList.contains("tablink")) {
                const tabContent = tab_element.parentNode.querySelector(
                    `.tabcontent.tab_${target.dataset.target}`,
                );

                tabContent.parentNode.childNodes.forEach((el) =>
                    el.classList?.remove("active"),
                );
                tabContent.classList.add("active");
            }
        });
    });

    document
    .getElementById("card_selection_form")
    .addEventListener("submit", (event) => {
        event.preventDefault();
        emit("selection_form_submit", selected_cards);
    //socket.emit("finish card selection");
  });

})
//v-bind:value="'('+color+','+number+')'"
</script>

<template>
<form id="card_selection_form" class="card_selection_form">
          <div class="tab">
              <button v-for="color in color_list" type="button" class="tablink" :class="'card_color_'+color" v-bind:data-target="color"></button>
              <button type="submit" class="finish button">Auswahl beenden</button>
          </div>
          <div v-for="color in color_list" class="tabcontent" :class="'tab_'+color, 'card_color_'+color">
                <div v-for="number in number_list(color)" class="color_wrapper">
                    <input  type="checkbox" v-bind:id="'prefix_'+color+'_'+number"
                            v-bind:name="color" class="card_number" v-bind:value="'['+color+','+number+']'"
                            v-model="selected_cards_strings">
                    <label v-bind:for="'prefix_'+color+'_'+number">{{number}}</label>
                </div>
          </div>
        </form>
  <div>Selected Cards: {{ selected_cards_strings }}</div>
  <p> Selected Cards Array: {{ selected_cards }}</p>
</template>

<style>

:root {
    --card-width: 70px;
    --card-height: calc(70px / 0.65);
    --card-trump: black;
    --card-red: #ea5cb5;
    --card-green: #66c75d;
    --card-blue: #52c4b0;
    --card-yellow: #e0ab2c;
    --card-undefined: gray;
    --card-color--1: var(--card-trump);
    --card-color-0: var(--card-red);
    --card-color-1: var(--card-green);
    --card-color-2: var(--card-blue);
    --card-color-3: var(--card-yellow);
    --primary-color: #254a9a;
    --task-order-color: #502891;
}

* {
    box-sizing: border-box;
}

html {
    font-family: sans-serif;
}

button {
    cursor: pointer;
}


/* Hide input boxes */
.card_number,
.task_order {
    height: 0;
    width: 0;
    position: absolute;
    opacity: 0;
}

.card_number + label,
.task_order + label {
    cursor: pointer;
    background-color: var(--card-color, var(--card-undefined));
    border-radius: 2px;
    color: white;
    display: flex;
    justify-content: center;
    padding: 1rem 0.25rem;
    position: relative;
    height: 100%;
}

.task_order:focus-visible + label,
.card_number:focus-visible + label {
    outline: 2px solid var(--card-undefined);
}

.task_order:checked + label::before,
.card_number:checked  + label::before {
    content: "\2713";
    height: 10px;
    width: 10px;
    background-color: white;
    color: var(--card-color);
    padding: 0.3em;
    border-radius: 100%;
    position: absolute;
    top: 0.2em;
    right: 0.2em;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
}

.task_order + label {
    --card-color: var(--task-order-color);
}

.button {
    border: none;
    border-radius: 5px;
    padding: 0.5em 1em;
    background: var(--primary-color);
    color: white;
}

.button.add,
.button.finish {
    grid-column: -1;
    line-height: 1;
    margin-bottom: 2px;
    padding-top: 0;
    padding-bottom: 0;
}

.button.add {
    background-color: var(--card-green);
    grid-column: -2;
}

#end_game_card, #end_game_task {
    position: fixed;
    right: 1rem;
    top: 1rem;
    background: var(--card-red);
}

.card_list {
    --min-width: 2em;
    display: grid;
    gap: 0.5em;
    min-height: var(--card-height);
    grid-template-columns: repeat(auto-fit, minmax(var(--min-width), min-content));
    padding-right: calc(var(--card-width) - var(--min-width));
}

.card {
    --card-color: var(--card-undefined);
    position: relative;
    height: var(--card-height);
    width: var(--card-width);
    border-radius: 5px;
    border: 1px solid black;
    font-size: 3rem;
    font-weight: bold;
    display: grid;
    align-content: center;
    justify-content: center;
    color: white;
    background-color: var(--card-color);
    overflow: hidden;
}

.card::before,
.card::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    border: 0.1em solid white;
}

.card::after {
    border-radius: 8px;
}

.card.red {
    --card-color: var(--card-red);
}

.card_color_-1,
.card[data-color="-1"] {
    --card-color: var(--card-color--1);
}

.card_color_0,
.card[data-color="0"] {
    --card-color: var(--card-color-0);
}

.card_color_1,
.card[data-color="1"] {
    --card-color: var(--card-color-1);
}

.card_color_2,
.card[data-color="2"] {
    --card-color: var(--card-color-2);
}

.card_color_3,
.card[data-color="3"] {
    --card-color: var(--card-color-3);
}

.card_color_4,
.card[data-color="4"] {
    --card-color: var(--card-color-4);
}

.card_selection_form {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #eee;
    padding: 0.5em;
}

.card_selection_form .tab {
    border: 0;
    display: grid;
    gap: 0.2em;
    grid-template-columns: repeat(5, minmax(32px, 4rem)) minmax(16px, 1fr) minmax(max-content, 1fr) minmax(min-content, 1fr);
}

.card_selection_form .tab .tablink {
    height: 2.5rem;
    background-color: var(--card-color);
    border-top-left-radius: 2px;
    border-top-right-radius: 2px;
    grid-row: 1;
}

.card_selection_form .tabcontent {
    border: 2px solid var(--card-color);
    border-radius: 0 2px 2px 2px;
    padding: 0.25em;
    gap: 0.25em;
}

.card_selection_form .tabcontent.active {
    display: grid;
    grid-template-columns: repeat(6, minmax(32px, 10rem));
    grid-template-rows: repeat(3, 1fr);
}

.color_wrapper {
    grid-column: span 2;
}

.task_wrapper.task_order_Kein {
    grid-row: span 2;
}

.task_wrapper.task_order_Kein label {
    display: flex;
    align-items: center;
}

.tab {
    overflow: hidden;
    border: 1px solid #ccc;
    background-color: #f1f1f1;
}

.tab .tablink {
    border: none;
    cursor: pointer;
    padding: 14px 16px;
}

/* Create an active/current tablink class */
.tab .tablink.active {
    background-color: #ccc;
}

/* Style the tab content */
.tabcontent {
    display: none;
    padding: 6px 12px;
    border: 1px solid #ccc;
    border-top: none;
}

.tabcontent.active {
    display: block;
}

</style>
