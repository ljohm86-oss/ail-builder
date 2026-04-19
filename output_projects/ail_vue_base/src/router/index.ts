import { createRouter, createWebHistory } from "vue-router";
import { routes as generatedRoutes } from "./routes.generated";

const fallback = [
  { path: "/", name: "Home", component: () => import("@/views/Home.vue") },
];

const routes = generatedRoutes?.length ? generatedRoutes : fallback;

export default createRouter({
  history: createWebHistory(),
  routes,
});
