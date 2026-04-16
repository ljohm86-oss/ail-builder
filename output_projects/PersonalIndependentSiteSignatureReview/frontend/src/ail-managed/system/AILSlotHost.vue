<template>
  <component :is="resolvedComponent" v-if="resolvedComponent" :context="props.context" :hook-name="props.name" class="ail-slot-host ail-slot-host--component" />
  <div v-else-if="resolvedPartial" class="ail-slot-host ail-slot-host--partial" :data-ail-hook="props.name" :data-ail-context="serializedContext" v-html="resolvedPartial"></div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  name: string;
  context?: Record<string, unknown> | null;
}>();

const componentModules = import.meta.glob("../../ail-overrides/components/**/*.vue", { eager: true });
const partialModules = import.meta.glob("../../ail-overrides/components/**/*.html", { eager: true, query: "?raw", import: "default" });

function hookKey(path: string): string {
  const normalized = path.replace(/\\/g, "/");
  const marker = "/ail-overrides/components/";
  const relative = normalized.includes(marker) ? normalized.split(marker)[1] : normalized.split("/").pop() || normalized;
  return relative.replace(/\.(vue|html)$/i, "").replace(/\//g, ".");
}

const componentRegistry = Object.fromEntries(
  Object.entries(componentModules).map(([path, mod]) => [hookKey(path), (mod as { default?: unknown }).default ?? mod]),
);

const partialRegistry = Object.fromEntries(
  Object.entries(partialModules).map(([path, mod]) => [hookKey(path), typeof mod === "string" ? mod : ""]),
);

const resolvedComponent = computed(() => componentRegistry[props.name] ?? null);
const resolvedPartial = computed(() => partialRegistry[props.name] ?? "");
const serializedContext = computed(() => JSON.stringify(props.context ?? null));
</script>

<style scoped>
.ail-slot-host {
  width: 100%;
}
.ail-slot-host--partial :deep(*) {
  box-sizing: border-box;
}
</style>
