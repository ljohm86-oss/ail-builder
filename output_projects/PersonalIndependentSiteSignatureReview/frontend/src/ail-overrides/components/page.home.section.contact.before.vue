<template>
  <span class="author-contact-copy-patch" aria-hidden="true"></span>
</template>

<script setup lang="ts">
import { nextTick, onMounted } from "vue";

function applyAuthorContactCopy() {
  const contact = document.querySelector<HTMLElement>(".landing-page.personal-portfolio #contact");
  if (!contact) return;

  const heading = contact.querySelector<HTMLElement>("h2");
  const lead = contact.querySelector<HTMLElement>(".section-lead");
  const fieldLabels = contact.querySelectorAll<HTMLElement>(".contact-field > span");
  const nameInput = contact.querySelector<HTMLInputElement>('input[type="text"]');
  const emailInput = contact.querySelector<HTMLInputElement>('input[type="email"]');
  const messageInput = contact.querySelector<HTMLTextAreaElement>("textarea");
  const hint = contact.querySelector<HTMLElement>(".contact-field-hint");
  const submitButton = contact.querySelector<HTMLButtonElement>(".contact-form button");

  if (heading) heading.textContent = "把当前目标发来";
  if (lead) {
    lead.textContent =
      "如果你已经知道想先整理哪一页、哪段表达或哪种合作入口，可以直接把目标、现有内容和时间节奏发给我。我通常会先回一版更短的首页判断，而不是先把事情讲得很满。";
  }

  if (fieldLabels[0]) fieldLabels[0].textContent = "我该怎么称呼你";
  if (fieldLabels[1]) fieldLabels[1].textContent = "我该回到哪个邮箱";
  if (fieldLabels[2]) fieldLabels[2].textContent = "你现在想先讲清什么";

  if (nameInput) nameInput.placeholder = "例如：怎么称呼你会更自然";
  if (emailInput) emailInput.placeholder = "例如：你最常看的邮箱";
  if (messageInput) messageInput.placeholder = "先写目标、现有内容和时间节奏就够了。";
  if (hint) hint.textContent = "建议先写你最想先讲清什么、现在已有多少内容，以及希望什么时候上线。";

  if (submitButton && submitButton.textContent?.trim() !== "已收到咨询") {
    submitButton.textContent = "发送当前目标";
  }
}

onMounted(() => {
  nextTick(() => {
    applyAuthorContactCopy();
    requestAnimationFrame(applyAuthorContactCopy);
  });
});
</script>
