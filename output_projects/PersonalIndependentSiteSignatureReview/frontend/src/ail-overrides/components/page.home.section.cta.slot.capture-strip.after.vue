<template>
  <span class="author-cta-copy-patch" aria-hidden="true"></span>
</template>

<script setup lang="ts">
import { nextTick, onMounted } from "vue";

function applyAuthorCtaCopy() {
  const ctaSection = document.querySelector<HTMLElement>(".landing-page.personal-portfolio #cta");
  if (!ctaSection) return;

  const ctaButton = ctaSection.querySelector<HTMLButtonElement>("button");
  if (ctaButton) ctaButton.textContent = "先发当前目标";
}

onMounted(() => {
  nextTick(() => {
    applyAuthorCtaCopy();
    requestAnimationFrame(applyAuthorCtaCopy);
  });
});
</script>
