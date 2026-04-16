import { createApp } from "vue";
import "./style.css";
import "./ail-overrides/theme.tokens.css";
import "./ail-overrides/custom.css";
import App from "./App.vue";
import AILSlotHost from "./ail-managed/system/AILSlotHost.vue";
import router from "./router"

const app = createApp(App)
app.component("AILSlotHost", AILSlotHost)
app.use(router)
app.mount("#app")
