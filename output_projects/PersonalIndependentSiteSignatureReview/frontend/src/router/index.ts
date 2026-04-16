import { createRouter, createWebHistory } from "vue-router";
import { routes as generatedRoutes } from "@/ail-managed/router/routes.generated";
import { roleRequired } from "@/ail-managed/router/roles.generated";

const fallback = [
  { path: "/", name: "Home", component: () => import("@/ail-managed/views/Home.vue") },
];

const routes = generatedRoutes?.length ? generatedRoutes : fallback;
let cachedRole: string | null = null;
let cachedToken: string | null = null;
const authEnabled = false;

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem("token") || localStorage.getItem("access_token");
  if (authEnabled && !token && to.path !== "/" && to.path !== "/login" && to.path !== "/403") {
    next("/login");
    return;
  }
  const requiredRole = roleRequired[to.path];
  if (authEnabled && token && requiredRole) {
    try {
      if (cachedToken !== token) {
        cachedToken = token;
        cachedRole = null;
      }
      if (!cachedRole) {
        const response = await fetch('/api/me', { headers: { Authorization: `Bearer ${token}` } });
        if (!response.ok) {
          next("/403");
          return;
        }
        const data = await response.json().catch(() => ({}));
        cachedRole = typeof data?.role === 'string' ? data.role.toLowerCase() : 'user';
      }
      const allowedRoles = String(requiredRole)
        .split('|')
        .map((r) => r.trim().toLowerCase())
        .filter(Boolean);
      if (!allowedRoles.includes(String(cachedRole || '').toLowerCase())) {
        next("/403");
        return;
      }
    } catch (_error) {
      next("/403");
      return;
    }
  }
  if (authEnabled && !token) {
    cachedRole = null;
    cachedToken = null;
  }
  next();
});

export default router;
