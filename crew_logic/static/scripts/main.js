const socket = io();
let cards = [];
let colors = new Set();
let numbers = new Set();

// Sends name to server
const emit_name = () => {
  const name = document.querySelector("[name='name']");
  socket.emit("update name", name.value);
};

const update_buttons = (prefix, ids) => {
  old_elements = document.querySelectorAll(`[id*=${prefix}_]`);

  for (const element of old_elements) {
      element.disabled = true;
  }

  for (id of ids) {
    const element = document.getElementById(`${prefix}_${id}`);

    if (element) {
      element.disabled = false;
    } else {
      add_new_button(prefix, id);
    }
  }

  const checked_element = document.querySelector(`[id*=${prefix}_]:checked`);
  if (checked_element && checked_element.disabled == true) {
    checked_element.checked = false;
  }
}

const add_new_button = (prefix, id) => {
  const input_element = document.createElement("input");
  input_element.setAttribute("type", "radio")
  input_element.classList.add(prefix);
  input_element.setAttribute("name", prefix)
  input_element.setAttribute("id", `${prefix}_${id}`)
  input_element.setAttribute("value", id);

  const label_element = document.createElement("label")
  label_element.setAttribute("for", `${prefix}_${id}`)
  label_element.innerText = id;

  document.getElementById("card").appendChild(input_element)
  document.getElementById("card").appendChild(label_element);
}

const cards_contain_card = (card_comp) => {
  let contains_card = false;

  for (const card of cards) {
    if (card[0] == card_comp[0] && card[1] == card_comp[1]) {
      contains_card = true;
      break;
    }
  }

  return contains_card;
}

socket.on("connect", () => {
  document.getElementById("connection-banner").classList.add("connected");
  emit_name();
});

socket.on("disconnect", () => {
  document.getElementById("connection-banner").classList.remove("connected");
});

socket.on("user list", (user_string) => {
  const users_element = document.getElementById("users");
  const user_count_element = document.querySelector("[data-user-count]");

  users = JSON.parse(user_string);

  // update user count
  user_count_element.innerText = Object.keys(users).length;

  // empty and update user name list
  users_element.innerHTML = "";

  for (const id in users) {
    const user_element = document.createElement("li");
    const name = users[id];

    user_element.innerText = name === "" ? "Unknown name" : name;
    users_element.append(user_element);
  }
});

socket.on("game started", () => {
  console.log("game started");
  document.querySelector("main").classList.add("game_started");
});

socket.on("game ended", () => {
  console.log("game ended");
  document.querySelector("main").classList.remove("game_started");
});


socket.on('cards updated', (cardsJsonString) => {
  cards = JSON.parse(cardsJsonString);

  colors.clear();
  numbers.clear();

  for (const item of cards) {
    colors.add(item[0]);
    numbers.add(item[1]);
  }

  update_buttons("card_color", Array.from(colors).sort());
  update_buttons("card_number", Array.from(numbers).sort());
});

document.getElementById("name").addEventListener("submit", (event) => {
  event.preventDefault();
  emit_name();
});

document.getElementById("start_game").addEventListener("click", () => {
  socket.emit("start game");
});

document.getElementById("end_game").addEventListener("click", () => {
  socket.emit("end game");
});

document.getElementById("card").addEventListener("change", (event) => {
  const number_element = document.querySelector("[name='card_number']:checked");
  const color_element = document.querySelector("[name='card_color']:checked");

  if (number_element !== null && color_element !== null) {
    const number = parseInt(number_element.value);
    const color = parseInt(color_element.value);

    socket.emit("card taken", JSON.stringify([color, number]));
    return;
  }

  if (number_element !== null) {
    const number = parseInt(number_element.value);

    for (const color of colors) {
      if (cards_contain_card([color, number])) {
        document.getElementById(`card_color_${color}`).disabled = false;
      }
      else {
        document.getElementById(`card_color_${color}`).disabled = true;

      }
    }
  }

  if (color_element !== null) {
    const color = parseInt(color_element.value);

    for (const number of numbers) {
      if (cards_contain_card([color, number])) {
        document.getElementById(`card_number_${number}`).disabled = false;
      }
      else {
        document.getElementById(`card_number_${number}`).disabled = true;
      }
    }
  }
});
