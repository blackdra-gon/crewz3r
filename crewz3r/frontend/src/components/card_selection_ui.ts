export {}

type Card = [number, number] // color / value

let cards: Card[] = [];
const get_unique_colors_of_cards = () => {
  let colors = new Set();

  for (const card of cards) {
    colors.add(card[0]);
  }

  return Array.from(colors).sort();
};

const get_number_list_for_color = (card_color: number) => {
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

const get_color_tab_button = (color_name: string) => {
  const tabButton = document.createElement("button");
  tabButton.type = "button";
  tabButton.classList.add("tablink");
  tabButton.classList.add(`card_color_${color_name}`);
  tabButton.dataset.target = color_name;

  return tabButton;
};

const get_color_tab_content_wrapper = (color_name: string) => {
  const wrapper = document.createElement("div");
  wrapper.classList.add("tabcontent");
  wrapper.classList.add(`card_color_${color_name}`);
  wrapper.classList.add(`tab_${color_name}`);

  return wrapper;
};

const get_task_order_radio = (symbol: string, color_name: string) => {
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
  prefix: string,
  color_name: string,
  number: number,
  type = "checkbox",
) => {
  const id = `${prefix}_${color_name}_${number}`;
  const input = document.createElement("input");
  input.id = id;
  input.setAttribute("type", type);
  input.setAttribute("name", color_name);
  input.setAttribute("value", String(number));
  input.classList.add("card_number");

  const label = document.createElement("label");
  label.setAttribute("for", id);
  label.innerText = String(number);

  const wrapper = document.createElement("div");
  wrapper.classList.add("color_wrapper");
  wrapper.appendChild(input);
  wrapper.appendChild(label);

  return wrapper;
};

const add_task_order_radios = (tab_content_wrapper: HTMLDivElement, color_name: string) => {
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
  let number;
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
