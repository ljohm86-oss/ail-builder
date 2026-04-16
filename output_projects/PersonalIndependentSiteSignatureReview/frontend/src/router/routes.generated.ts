export const routes = [
  { path: "/", name: "Home", component: () => import("@/ail-managed/views/Home.vue") },
  { path: "/403", name: "Forbidden", component: () => import("@/ail-managed/views/Forbidden.vue") },
];
