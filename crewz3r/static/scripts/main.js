const socket = io();
let cards = [];
let tasks = [];
let activeView = document.querySelector(".start_view");

//************************************************************
//        Function Declarations
//************************************************************

// Sends name to server
const emit_name = () => {
  const name = document.querySelector("[name='name']");
  socket.emit("update name", name.value);
};

const get_unique_colors_of_cards = () => {
  let colors = new Set();

  for (const card of cards) {
    colors.add(card[0]);
  }

  return Array.from(colors).sort();
};

const get_number_list_for_color = (card_color) => {
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

const get_color_tab_button = (color_name) => {
  const tabButton = document.createElement("button");
  tabButton.type = "button";
  tabButton.classList.add("tablink");
  tabButton.classList.add(`card_color_${color_name}`);
  tabButton.dataset.target = color_name;

  return tabButton;
};

const get_color_tab_content_wrapper = (color_name) => {
  const wrapper = document.createElement("div");
  wrapper.classList.add("tabcontent");
  wrapper.classList.add(`card_color_${color_name}`);
  wrapper.classList.add(`tab_${color_name}`);

  return wrapper;
};

const get_task_order_radio = (symbol, color_name) => {
  const id = `${color_name}_task_order_${symbol}`;
  const input = document.createElement("input");
  input.id = id;
  input.setAttribute("type", "radio");
  input.setAttribute("name", `${color_name}_task_order`);
  input.setAttribute("value", symbol);
  input.classList.add("task_order");

  const label = document.createElement("label");
  label.setAttribute("for", id);
  label.innerText = symbol;

  const wrapper = document.createElement("div");
  wrapper.classList.add(`task_wrapper`);
  wrapper.classList.add(`task_order_${symbol}`);
  wrapper.appendChild(input);
  wrapper.appendChild(label);

  return wrapper;
};

const get_color_number_input = (
  prefix,
  color_name,
  number,
  type = "checkbox",
) => {
  const id = `${prefix}_${color_name}_${number}`;
  const input = document.createElement("input");
  input.id = id;
  input.setAttribute("type", type);
  input.setAttribute("name", color_name);
  input.setAttribute("value", number);
  input.classList.add("card_number");

  const label = document.createElement("label");
  label.setAttribute("for", id);
  label.innerText = number;

  const wrapper = document.createElement("div");
  wrapper.classList.add("color_wrapper");
  wrapper.appendChild(input);
  wrapper.appendChild(label);

  return wrapper;
};

const add_task_order_radios = (tab_content_wrapper, color_name) => {
  // TODO get from game logic
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
  for (const symbol of symbols) {
    const task_order_radio = get_task_order_radio(symbol, color_name);
    tab_content_wrapper.appendChild(task_order_radio);
  }

  tab_content_wrapper.querySelector(`.task_order`).checked = true;
};

const add_tab_for_color = (color_name) => {
  const isTaskSelection = activeView.classList.contains("task_selection_view");
  let number_input_type = "checkbox";
  let prefix = "card_selection";

  const tab = activeView.querySelector(".tab");
  const tab_button = get_color_tab_button(color_name);
  const tab_content_wrapper = get_color_tab_content_wrapper(color_name);

  if (isTaskSelection) {
    add_task_order_radios(tab_content_wrapper, color_name);
    number_input_type = "radio";
    prefix = "task_selection";
  }

  for (number of get_number_list_for_color(color_name)) {
    const color_number_checkbox = get_color_number_input(
      prefix,
      color_name,
      number,
      number_input_type,
    );
    tab_content_wrapper.appendChild(color_number_checkbox);
  }

  tab.appendChild(tab_button);
  tab.after(tab_content_wrapper);
};

const updated_selected_cards = (card_type, cards_list) => {
  const target_element = activeView.querySelector(`.selected_${card_type}`);
  target_element.innerHTML = "";

  for (const card of cards_list) {
    let card_element = document.createElement("div");
    card_element.classList.add(`card`);
    card_element.dataset.color = card[0];
    card_element.innerHTML = card[1];
    target_element.append(card_element);
  }
};

//************************************************************
//        Reaction to Socket Messages
//************************************************************

// Connection banner

socket.on("connect", () => {
  document.getElementById("connection-banner").classList.add("connected");
  emit_name();
});

socket.on("disconnect", () => {
  document.getElementById("connection-banner").classList.remove("connected");
});

// start page

socket.on("user list", (user_string) => {
  const users_element = document.getElementById("users");
  const user_count_element = document.querySelector("[data-user-count]");

  let users = JSON.parse(user_string);

  // update user count
  user_count_element.innerText = Object.keys(users).length;

  // empty and update username list
  users_element.innerHTML = "";

  for (const id in users) {
    const user_element = document.createElement("li");
    const name = users[id];

    user_element.innerText = name === "" ? "Unknown name" : name;
    users_element.append(user_element);
  }
});

socket.on("not enough players", () => {
  // TODO display info
});

// card selection page
socket.on("open card selection view", () => {
  console.log("starting card selection");
  document.querySelector("main").classList.remove("task_selection");
  document.querySelector("main").classList.add("card_selection");
  activeView = document.querySelector(".card_selection_view");
});

// task selection page
socket.on("open task selection view", () => {
  console.log("starting task selection");
  document.querySelector("main").classList.remove("card_selection");
  document.querySelector("main").classList.add("task_selection");
  activeView = document.querySelector(".task_selection_view");
  console.log("update cards");
  updated_selected_cards("cards", cards);
});

socket.on("open result view", () => {
  console.log("display result");
  document.querySelector("main").classList.remove("task_selection");
  document.querySelector("main").classList.add("display_result");
  activeView = document.querySelector(".display_result_view");
});

socket.on("game ended", () => {
  console.log("game ended");
  document.querySelector("main").classList.remove("task_selection");
  document.querySelector("main").classList.remove("card_selection");
});

socket.on("cards updated", (cardsJsonString) => {
  cards = JSON.parse(cardsJsonString);

  for (const color of get_unique_colors_of_cards()) {
    add_tab_for_color(color);
  }

  activeView.querySelector(".tab .tablink").click();
});

socket.on("selected cards updated", (cardsJsonString) => {
  cards = JSON.parse(cardsJsonString);
  updated_selected_cards("cards", cards);
});

socket.on("set card selection checkboxes", (cardsJsonString) => {
  cards = JSON.parse(cardsJsonString);
  for (const card of cards) {
    document.getElementById(
      `card_selection_${card[0]}_${card[1]}`,
    ).checked = true;
  }
});

socket.on("selected tasks updated", (cardsJsonString) => {
  tasks = JSON.parse(cardsJsonString);
  updated_selected_cards("tasks", tasks);
});

//************************************************************
//        Initialization of EventListeners
//************************************************************

document.getElementById("name").addEventListener("submit", (event) => {
  event.preventDefault();
  emit_name();
});

document.getElementById("start_game").addEventListener("click", () => {
  socket.emit("start card selection");
});

document.getElementById("end_game").addEventListener("click", () => {
  socket.emit("end game");
});

document
  .getElementById("back_to_card_selection")
  .addEventListener("click", () => {
    socket.emit("back to card selection");
  });

document
  .getElementById("finish_task_selection")
  .addEventListener("click", () => {
    socket.emit("finish task selection");
  });
// Send card data
document
  .getElementById("card_selection_form")
  .addEventListener("submit", (event) => {
    event.preventDefault();
    for (data of new FormData(event.target)) {
      const color = parseInt(data[0]);
      const number = parseInt(data[1]);
      // TODO send all cards with one call and finish selection
      socket.emit("card_or_task taken", JSON.stringify([color, number]));
      setTimeout(() => {
        socket.emit("finish card selection");
      }, 2000);
    }
  });

// Send task data
document
  .getElementById("task_selection_form")
  .addEventListener("submit", (event) => {
    event.preventDefault();
    for (data of new FormData(event.target)) {
      const color = parseInt(data[0]);
      const number = parseInt(data[1]);
      // TODO how to pass order
      socket.emit("card_or_task taken", JSON.stringify([color, number]));
    }
  });

//document.querySelectorAll(".finish_task_selection").forEach((element) => {
//  element.addEventListener("click", () => {
//    socket.emit("finish task selection");
//  });
//});

// Tab logic

document.querySelectorAll(".tab").forEach((tab_element) => {
  tab_element.addEventListener("click", ({ target }) => {
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
