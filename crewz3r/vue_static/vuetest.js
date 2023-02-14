const start = {
  template:
    '      <div class="start_view">\n' +
    "        <p><span data-user-count>0</span> in der Lobby</p>\n" +
    '        <ul id="users"></ul>\n' +
    '        <form id="name">\n' +
    '          <input type="text" name="name" />\n' +
    '          <button class="button" type="submit">Name ändern</button>\n' +
    "        </form>\n" +
    '        <button class="button" type="button" id="start_game">\n' +
    "          Spiel starten\n" +
    "        </button>\n" +
    "      </div>",
};
const view_2 = { template: "<div>Second View</div>" };

const routes = [
  { path: "/", component: start },
  { path: "/view_2", component: view_2 },
];

const router = VueRouter.createRouter({
  // 4. Provide the history implementation to use. We are using the hash history for simplicity here.
  history: VueRouter.createWebHashHistory(),
  routes, // short for `routes: routes`
});

const app = Vue.createApp({
  data() {
    return {
      message: "Hello Vue!",
      user_list: [],
    };
  },
});

app.use(router);

app.mount("#app");
