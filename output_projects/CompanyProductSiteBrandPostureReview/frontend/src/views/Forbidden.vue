<template>
  <AILSlotHost name="page.forbidden.before" :context='{ pageKey: "forbidden", pageName: "Forbidden", pagePath: "/403", profiles: ["landing"], hookScope: "page" }' />
  <section class="forbidden-page">
    <h2>403 Forbidden</h2>
    <p>You don't have permission</p>
    <router-link class="home-btn" to="/">Back to Home</router-link>
  </section>
  <AILSlotHost name="page.forbidden.after" :context='{ pageKey: "forbidden", pageName: "Forbidden", pagePath: "/403", profiles: ["landing"], hookScope: "page" }' />
</template>

<script setup>
</script>

<style scoped>
.forbidden-page { display: grid; gap: 10px; max-width: 420px; }
.home-btn { display: inline-block; width: fit-content; padding: 8px 12px; border: 1px solid #3f3f46; border-radius: 8px; color: #f4f4f5; text-decoration: none; }
</style>
