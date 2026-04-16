<template>
  <span class="brand-cta-button-patch" aria-hidden="true"></span>
</template>

<script setup lang="ts">
import { nextTick, onMounted } from "vue";

function applyQualifiedCtaCopy() {
  const ctaSection = document.querySelector<HTMLElement>(".landing-page:not(.personal-portfolio) #cta");
  if (!ctaSection) return;

  const ctaButton = ctaSection.querySelector<HTMLButtonElement>("button");
  if (ctaButton) ctaButton.textContent = "先收首页建议";
}

onMounted(() => {
  nextTick(() => {
    applyQualifiedCtaCopy();
    requestAnimationFrame(applyQualifiedCtaCopy);
  });
});
</script>
