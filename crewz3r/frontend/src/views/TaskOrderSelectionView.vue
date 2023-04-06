<script setup lang="ts">
import {inject, onMounted, ref} from "vue";

const socket = inject('socket')
const selected_tasks = inject('selected_tasks')

const symbols = [
    "Kein",
    "1",
    "2",
    "3",
    "4",
    "5",
    "❯",
    "❯❯",
    "❯❯❯",
    "❯❯❯❯",
    "Ω",
  ];

const tasks_with_order = ref([])

for (const task of selected_tasks.value) {
    //const task_order_entry = task.slice()
    //task_order_entry.push('Kein')
    tasks_with_order.value.push(task + ',Kein')
}

const submit = () => {
    socket.emit("tasks selected", JSON.stringify(tasks_with_order.value));
}
onMounted( () => {
    document.querySelector(".task_wrapper")
    document.querySelectorAll(".selected_tasks_wrapper").forEach((card_element) => {
        card_element.addEventListener("click", ({target}) => {
            console.log(`Button clicked ${target.name}`)
            const tabContent = card_element.parentNode.querySelector(
                        `.task_order_${target.name}`,
                    );

                    tabContent.parentNode.childNodes.forEach((el) =>
                        el.classList?.remove("active"),
                    );
                    tabContent.classList.add("active");
        });
    });
});
</script>

<template>
    <p>{{selected_tasks}}</p>
    <p>{{tasks_with_order}}</p>
<p>
 <button class="button" @click="submit">Auswahl beenden</button>
</p>
<div class="selected_tasks_wrapper">
    <button v-for="card in selected_tasks" class="card selected_tasks" v-bind:name="card[0]+'_'+card[1]" v-bind:data-color="card[0]"> {{card[1]}}</button>
</div>
    <div>
        <div v-for="(card, index) in selected_tasks" class="task_wrapper" :class="'task_order_'+card[0]+'_'+card[1]">
            <div v-for="symbol in symbols" :class="'task_order_'+symbol">
                <input  v-bind:id="card+'_task_order_'+symbol" v-bind:name="card+'_task_order'"
                type="radio" v-bind:value="card +','+ symbol" class="task_order" :checked="symbol == 'Kein'"
                v-model="tasks_with_order[index]">
                <label v-bind:for="card+'_task_order_'+symbol">
                    {{ symbol }}
                </label>
            </div>
        </div>
    </div>

</template>

<style scoped>

.selected_tasks {
    display: inline-block;
}

.task_wrapper {
    display: none;
}

.task_wrapper.active {
    display: block;
}

</style>
