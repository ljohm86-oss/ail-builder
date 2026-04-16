<template>
  <span class="brand-hero-copy-patch" aria-hidden="true"></span>
</template>

<script setup lang="ts">
import { nextTick, onMounted } from "vue";

function applyBrandHeroCopy() {
  const hero = document.querySelector<HTMLElement>(".landing-page:not(.personal-portfolio) #hero");
  if (!hero) return;

  const brandTag = hero.querySelector<HTMLElement>(".hero-brand-tag");
  const headline = hero.querySelector<HTMLElement>(".hero-copy-block h1");
  const body = hero.querySelector<HTMLElement>(".hero-copy-block p");
  const primaryCta = hero.querySelector<HTMLButtonElement>(".hero-actions button:not(.ghost)");
  const secondaryCta = hero.querySelector<HTMLButtonElement>(".hero-actions .ghost");

  if (brandTag) brandTag.textContent = "先帮来访者判断，再把品牌说深";
  if (headline) headline.textContent = "先让对的人留下，再把产品讲深";
  if (body) {
    body.textContent =
      "我们更相信首页先把适合对象、业务处境和判断路径讲透，再让能力、FAQ 和演示动作顺着品牌自己的语气往下接，而不是先铺一层热闹的产品话术。";
  }
  if (primaryCta) primaryCta.textContent = "先看是否值得演示";
  if (secondaryCta) secondaryCta.textContent = "查看判断路径";
}

onMounted(() => {
  nextTick(() => {
    applyBrandHeroCopy();
    requestAnimationFrame(applyBrandHeroCopy);
  });
});
</script>
