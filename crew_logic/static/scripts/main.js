const socket = io();

// Sends name to server
const emit_name = () => {
  const name = document.querySelector("[name='name']");
  socket.emit("update name", name.value);
};

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
