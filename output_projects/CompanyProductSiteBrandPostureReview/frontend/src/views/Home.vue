<template>
  <AILSlotHost name="page.home.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "page", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
  <section class="landing-page">
    <header class="landing-header" data-landing="Header">
      <button class="brand" type="button" @click="go('/')">品牌官网</button>
      <div class="company-header-note">
        <span v-for="item in companyHeaderItems" :key="`company-header-${item}`">{{ item }}</span>
      </div>
      <nav>
        <button type="button" v-for="link in navLinks" :key="`${link.target}-${link.label}`" @click="go(link.target)">{{ link.label }}</button>
      </nav>
    </header>
<AILSlotHost name="page.home.section.hero.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "hero", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="hero" class="landing-hero" data-landing="Hero">
      <span class="hero-kicker">PRODUCT SITE / FIT / TRUST</span>
      <div class="hero-brand-row">
        <strong class="hero-brand-mark">品牌官网</strong>
        <span class="hero-brand-tag">定位清楚，演示更顺</span>
      </div>
      <div class="hero-brand-posture">
        <span class="hero-brand-posture-label">BRAND POSTURE</span>
        <strong>先把产品值不值得继续看讲清，再把演示、咨询和下一步动作留给真的有兴趣的人。</strong>
        <div class="hero-brand-posture-grid">
          <article v-for="item in companyBrandPostureItems" :key="`company-posture-${item.label}`" class="hero-brand-posture-card">
            <span>{{ item.label }}</span>
            <em>{{ item.value }}</em>
          </article>
        </div>
      </div>
<AILSlotHost name="page.home.section.hero.slot.brand-grid.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "hero", slotKey: "brand-grid", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="hero-brand-grid">
        <article class="hero-brand-card hero-brand-card--fit">
          <span>01 适合对象</span>
          <strong>产品团队 / 创业团队</strong>
          <em>先看是否相关</em>
        </article>
        <article class="hero-brand-card hero-brand-card--scenario">
          <span>02 场景线索</span>
          <strong>定位澄清 / 价值承接</strong>
          <em>先看问题是否成立</em>
        </article>
        <article class="hero-brand-card hero-brand-card--next">
          <span>03 下一步动作</span>
          <strong>FAQ / 演示 / 联系入口</strong>
          <em>先看怎么继续</em>
        </article>
      </div>
<AILSlotHost name="page.home.section.hero.slot.brand-grid.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "hero", slotKey: "brand-grid", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="hero-copy-block">
        <h1>先把产品价值讲明白</h1>
        <p>先说清适合对象、关键场景和价值差异，再把产品能力、FAQ、预约演示和联系入口接成同一条首页路径。</p>
      </div>
      <div class="hero-decision-block">
      <div class="hero-memory-strip">
        <strong class="hero-memory-label">首页判断法</strong>
        <span>先定对象</span>
        <span>再亮差异</span>
        <span>后接动作</span>
      </div>
<AILSlotHost name="page.home.section.hero.slot.hero-actions.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "hero", slotKey: "hero-actions", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="hero-actions">
        <button type="button" @click="go('#contact')">预约演示</button>
        <button type="button" class="ghost" @click="go('#features')">先看适用场景</button>
      </div>
<AILSlotHost name="page.home.section.hero.slot.hero-actions.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "hero", slotKey: "hero-actions", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      </div>
      <div class="hero-signal-strip">
        <article v-for="item in aboutHighlights.slice(0, 3)" :key="`hero-signal-${item}`" class="hero-signal-card">
          <span class="hero-signal-dot"></span>
          <strong>{{ item }}</strong>
        </article>
      </div>
    </section>
<AILSlotHost name="page.home.section.hero.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "hero", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.about.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "about", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="about" class="landing-section about-section" data-landing="About">
      <h2>为什么这类官网更容易把产品讲明白</h2>
      <div class="section-path-strip">
        <span class="section-path-current">01 产品介绍</span>
        <span class="section-path-next">下一步：产品能力</span>
      </div>
      <div class="about-shell">
        <div class="about-copy">
          <p>与其把首页做成一组抽象卖点，我们更倾向先说明产品适合谁、解决什么问题、和现有做法相比差在哪里，再用能力、FAQ 和联系入口把这条认知路径接稳。</p>
          <p class="about-note">这尤其适合还在持续验证定位、准备预约演示、或者希望减少销售和产品同学重复解释成本的产品团队、创业团队和服务型产品。</p>
        </div>
        <div class="about-points">
          <article v-for="item in aboutHighlights" :key="`about-${item}`">
            <span class="about-point-dot"></span>
            <strong>{{ item }}</strong>
          </article>
        </div>
      </div>
      <div class="section-proof-bridge section-proof-bridge--about">
        <span class="section-proof-bridge-label">ABOUT TO FEATURES</span>
        <strong>适合对象、关键场景和价值差异已经对齐，下一步看首页怎么把这些判断承接成更具体的能力表达。</strong>
        <div class="section-proof-bridge-strip">
          <span class="section-proof-bridge-current">当前：对象 / 场景 / 差异</span>
          <span class="section-proof-bridge-next">下一步：能力承接</span>
        </div>
      </div>
    </section>
<AILSlotHost name="page.home.section.about.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "about", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.features.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "features", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="features" class="landing-section" data-landing="FeatureGrid">
      <h2>产品能力</h2>
      <div class="section-path-strip">
        <span class="section-path-current">02 产品能力</span>
        <span class="section-path-next">下一步：客户评价</span>
      </div>
      <div class="pill-grid">
        <article v-for="(item, index) in featureItems" :key="`feature-${item}`">
          <strong>{{ item }}</strong>
          <span>{{ featureDescriptions[index] || item }}</span>
        </article>
      </div>
      <div class="section-proof-bridge section-proof-bridge--features">
        <span class="section-proof-bridge-label">FEATURES TO TRUST</span>
        <strong>能力层先回答这页怎么承接前面的判断，下一步再看真实团队为什么会觉得这种官网更好用。</strong>
        <div class="section-proof-bridge-strip">
          <span class="section-proof-bridge-current">当前：能力承接</span>
          <span class="section-proof-bridge-next">下一步：团队反馈</span>
        </div>
      </div>
    </section>
<AILSlotHost name="page.home.section.features.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "features", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.testimonials.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "testimonials", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="testimonials" class="landing-section" data-landing="Testimonial">
      <h2>客户评价</h2>
      <p class="section-lead">这些反馈更像真实团队在官网上线后最先感受到的变化：解释成本有没有下降、来访者理解是否更快、询盘是否更聚焦。</p>
      <div class="section-path-strip">
        <span class="section-path-current">03 客户评价</span>
        <span class="section-path-next">下一步：常见问题</span>
      </div>
<AILSlotHost name="page.home.section.testimonials.slot.quote-grid.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "testimonials", slotKey: "quote-grid", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="quote-grid">
        <article v-for="item in testimonialCards" :key="`quote-${item.quote}-${item.role}`" class="quote-card">
          <span v-if="item.context" class="quote-context">{{ item.context }}</span>
          <p class="quote-copy">{{ item.quote }}</p>
          <div class="quote-meta">
            <strong>{{ item.role }}</strong>
            <span>{{ item.result }}</span>
          </div>
        </article>
      </div>
<AILSlotHost name="page.home.section.testimonials.slot.quote-grid.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "testimonials", slotKey: "quote-grid", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="section-proof-bridge section-proof-bridge--trust">
        <span class="section-proof-bridge-label">TRUST TO FAQ</span>
        <strong>团队反馈先说明这类首页为什么更容易承接销售和演示，下一步再把来访者最常见的判断问题提前讲清楚。</strong>
        <div class="section-proof-bridge-strip">
          <span class="section-proof-bridge-current">当前：团队反馈</span>
          <span class="section-proof-bridge-next">下一步：售前判断</span>
        </div>
      </div>
    </section>
<AILSlotHost name="page.home.section.testimonials.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "testimonials", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.faq.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "faq", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="faq" class="landing-section" data-landing="FAQ">
      <h2>常见问题</h2>
      <p class="section-lead">把团队在定位、销售前置和上线准备里最常被问到的问题提前讲清，帮助来访者在预约演示前先完成一轮场景判断。</p>
      <div class="section-path-strip">
        <span class="section-path-current">04 常见问题</span>
        <span class="section-path-next">下一步：预约演示 / 联系我们</span>
      </div>
<AILSlotHost name="page.home.section.faq.slot.scan-strip.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "faq", slotKey: "scan-strip", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="faq-scan-strip">
        <span>定位澄清</span>
        <span>销售前置</span>
        <span>上线准备</span>
      </div>
<AILSlotHost name="page.home.section.faq.slot.scan-strip.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "faq", slotKey: "scan-strip", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="faq-list">
        <details v-for="item in faqItems" :key="`faq-${item.q}`" class="faq-item">
          <summary>
            <span class="faq-question">{{ item.q }}</span>
            <span class="faq-summary-hint">查看建议</span>
          </summary>
          <div class="faq-body">
            <span v-if="item.context" class="faq-context">{{ item.context }}</span>
            <div class="faq-copy-block">
              <span class="faq-copy-label">核心判断</span>
              <p class="faq-answer">{{ item.a }}</p>
            </div>
            <div v-if="item.followup" class="faq-followup-block">
              <span class="faq-followup-label">下一步建议</span>
              <p class="faq-followup">{{ item.followup }}</p>
            </div>
          </div>
        </details>
      </div>
      <div class="faq-contact-bridge">
        <span class="faq-contact-bridge-label">FAQ TO CONTACT</span>
        <strong>如果这些问题已经帮你完成一轮判断，下一步就把当前阶段、首页目标和希望承接的动作一起发来。</strong>
        <div class="faq-contact-bridge-strip">
          <span class="faq-contact-bridge-current">带着当前判断进入预约演示 / 联系我们</span>
          <span class="faq-contact-bridge-next">先发阶段、目标和承接动作</span>
        </div>
      </div>
    </section>
<AILSlotHost name="page.home.section.faq.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "faq", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.contact.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "contact", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="contact" class="landing-section" data-landing="Contact">
      <h2>预约演示 / 联系我们</h2>
      <p class="section-lead">如果你已经基本判断这类官网适合当前阶段，可以把产品、目标和希望承接的动作发给我们，我们会先按场景给出更具体的建议。</p>
      <div class="section-path-strip">
        <span class="section-path-current">05 预约演示 / 联系我们</span>
        <span class="section-path-next">下一步：发送咨询信息</span>
      </div>
      <div class="contact-entry-bridge">
        <span class="contact-entry-bridge-label">FROM FAQ</span>
        <strong>如果你已经完成了适合对象、场景和 FAQ 的一轮判断，这里就把下一步收成一次更短的咨询 intake。</strong>
      </div>
      <div class="contact-response-strip">
        <span v-for="item in contactResponseItems" :key="`contact-response-${item}`">{{ item }}</span>
      </div>
      <div class="contact-intake-bridge">
        <span class="contact-intake-bridge-label">DECISION TO INTAKE</span>
        <strong>先把当前阶段、首页目标和想承接的动作写清，页面就能更快从判断层进入真正的咨询 intake。</strong>
        <div class="contact-intake-bridge-strip">
          <span class="contact-intake-bridge-current">当前：带着判断进入</span>
          <span class="contact-intake-bridge-next">下一步：发阶段 / 目标 / 动作</span>
        </div>
      </div>
      <div class="contact-handoff-grid">
        <article v-for="item in contactHandoffCards" :key="`contact-handoff-${item.label}`" class="contact-handoff-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </article>
      </div>
      <div :class="['contact-form-shell', { 'contact-form-shell--business': !personalPortfolioMode }]">
        <div class="contact-form-intake">
          <strong>把这三项先发给我们，会更快进入建议阶段</strong>
          <div class="contact-form-checklist">
            <span>产品现在在什么阶段</span>
            <span>最想先讲清的价值差异</span>
            <span>希望官网承接什么动作</span>
          </div>
        </div>
        <div class="contact-form-panel">
          <form class="contact-form" @submit.prevent="submitContact">
            <label v-if="contactFields.includes('name')" class="contact-field"><span>怎么称呼你</span><input v-model="contactForm.name" type="text" placeholder="例如：产品负责人 / 创始人" required /></label>
            <label v-if="contactFields.includes('email')" class="contact-field"><span>联系邮箱</span><input v-model="contactForm.email" type="email" placeholder="例如：team@yourcompany.com" required /></label>
            <label v-if="contactFields.includes('message')" class="contact-field"><span>想先讨论什么</span><textarea v-model="contactForm.message" rows="4" placeholder="请写下产品阶段、最想先讲清的价值差异，以及希望官网承接的动作。" required></textarea><small class="contact-field-hint">建议直接写产品阶段、首页目标和希望承接的动作，2 到 4 句就足够开始。</small></label>
            <div class="contact-form-actions">
              <button type="submit" :disabled="contactSent">{{ contactSent ? '已收到咨询' : '发送咨询信息' }}</button>
              <span class="contact-submit-hint">不会直接进入冗长流程，我们通常会先回一版简短建议，再决定下一步怎么推进。</span>
            </div>
          </form>
          <p class="contact-form-note">收到后我们通常会先回一版建议：先收哪一屏、FAQ 要不要先上、演示入口怎么接。</p>
          <div v-if="contactSent" class="contact-success-card">
            <strong>已收到你的咨询</strong>
            <p>我们会先按当前阶段整理一版更短的首页建议，让下一步更容易判断。</p>
            <div class="contact-success-steps">
              <span v-for="item in contactSuccessItems" :key="`contact-success-${item}`">{{ item }}</span>
            </div>
          </div>
        </div>
      </div>
      <p v-if="contactSent && personalPortfolioMode" class="contact-success">已收到您的咨询，我们会尽快联系您。</p>
    </section>
<AILSlotHost name="page.home.section.contact.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "contact", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.cta.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "cta", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <section id="cta" class="landing-section cta" data-landing="CTA">
      <h2>如果你希望官网先把适合对象、价值差异和预约动作讲顺，我们可以一起把第一屏到联系入口收成同一条路径</h2>
      <div class="intake-closure-bridge">
        <span class="intake-closure-bridge-label">INTAKE TO CLOSURE</span>
        <strong>前面已经把阶段、首页目标和承接动作收进咨询 intake，下一步就把预期收成更短的 closing loop，避免最后只剩一个孤立按钮。</strong>
        <div class="intake-closure-bridge-strip">
          <span class="intake-closure-bridge-current">当前：已发阶段 / 目标 / 动作</span>
          <span class="intake-closure-bridge-next">下一步：确认建议与推进方式</span>
        </div>
      </div>
      <p class="cta-note">更适合：官网重写 / 首次上线 / 预约演示前置页</p>
<AILSlotHost name="page.home.section.cta.slot.capture-strip.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "cta", slotKey: "capture-strip", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="cta-capture-strip">
        <span v-for="item in ctaCaptureItems" :key="`cta-capture-${item}`">{{ item }}</span>
      </div>
<AILSlotHost name="page.home.section.cta.slot.capture-strip.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "cta", slotKey: "capture-strip", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div v-if="contactSent && !personalPortfolioMode" class="cta-success-bridge">
        <span class="cta-success-bridge-label">POST SUBMIT</span>
        <strong>咨询已收到，接下来我们会先回一版更短的首页建议，再决定要不要继续推进页面制作。</strong>
        <div class="cta-success-bridge-strip">
          <span class="cta-success-bridge-current">已收到当前阶段与目标</span>
          <span class="cta-success-bridge-next">先看首页建议</span>
          <span class="cta-success-bridge-next">再决定是否继续推进</span>
        </div>
      </div>
      <div v-if="contactSent && !personalPortfolioMode" class="cta-landing-bridge">
        <span class="cta-landing-bridge-label">CLOSURE TO LANDING</span>
        <strong>前面已经确认过建议和推进方式，下一步就把这次咨询收进一个更明确的最终页面落点，而不是直接掉进普通 footer。</strong>
        <div class="cta-landing-bridge-strip">
          <span class="cta-landing-bridge-current">当前：已确认建议与推进方式</span>
          <span class="cta-landing-bridge-next">下一步：进入最终页面落点</span>
        </div>
      </div>
<AILSlotHost name="page.home.section.cta.slot.close-strip.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "cta", slotKey: "close-strip", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div class="cta-close-strip">
        <span class="cta-close-current">01 发来当前阶段与目标</span>
        <span class="cta-close-next">02 收到首页建议</span>
        <span class="cta-close-next">03 再决定怎么推进</span>
      </div>
<AILSlotHost name="page.home.section.cta.slot.close-strip.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "cta", slotKey: "close-strip", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <button type="button" @click="go('#contact')">预约演示</button>
    </section>
<AILSlotHost name="page.home.section.cta.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "cta", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
<AILSlotHost name="page.home.section.footer.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "footer", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
    <footer id="footer" class="landing-footer" data-landing="Footer">
<AILSlotHost name="page.home.section.footer.slot.success-bridge.before" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "footer", slotKey: "success-bridge", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <div v-if="contactSent && !personalPortfolioMode" class="footer-success-bridge">
        <span class="footer-success-bridge-label">FINAL LANDING</span>
        <strong>咨询已经进入后续沟通，你可以继续回看产品介绍、客户评价，或回到联系我们补充更多上下文。</strong>
        <div class="footer-success-bridge-strip">
          <span class="footer-success-bridge-current">已进入后续沟通</span>
          <span class="footer-success-bridge-next">继续回看产品介绍 / 客户评价</span>
        </div>
      </div>
<AILSlotHost name="page.home.section.footer.slot.success-bridge.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "slot", sectionKey: "footer", slotKey: "success-bridge", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
      <strong>品牌官网</strong>
      <div class="company-footer-signoff">
        <span class="company-footer-signoff-label">FINAL BRAND LINE</span>
        <div class="company-footer-signoff-grid">
          <span v-for="item in companyFooterItems" :key="`company-footer-${item}`">{{ item }}</span>
        </div>
      </div>
      <div class="links">
        <button type="button" v-for="item in footerLinks" :key="`footer-${item}`" @click="go(linkToTarget(item))">{{ item }}</button>
      </div>
      <small>© 2026 品牌官网. All rights reserved.</small>
    </footer>
<AILSlotHost name="page.home.section.footer.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "section", sectionKey: "footer", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
  </section>
  <AILSlotHost name="page.home.after" :context='{ pageKey: "home", pageName: "Home", pagePath: "/", profiles: ["landing"], hookScope: "page", runtime: { singlePageLanding: !!singlePageLanding, navCount: navLinks.length, faqCount: faqItems.length, contactEnabled: !!contactSectionEnabled, contactSent: !!contactSent, leadSent: !!leadSent, portfolioMode: !!personalPortfolioMode } }' />
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const singlePageLanding = true
const navLinks = [{"label": "产品介绍", "target": "#about"}, {"label": "产品能力", "target": "#features"}, {"label": "客户评价", "target": "#testimonials"}, {"label": "联系我们", "target": "#contact"}]
const aboutHighlights = ["适合对象先讲透", "价值差异先于功能堆砌", "FAQ 与演示入口接进同一条认知链"]
const featureItems = ["适合对象更明确", "关键场景更容易代入", "客户疑问提前回答", "演示与询盘入口更顺手"]
const featureDescriptions = ["先回答这款产品服务谁、谁最容易从中受益，减少首页一上来就只谈功能堆砌的模糊感。", "用真实业务场景去承接产品价值，让来访者更容易把自己代入进去，而不是只看抽象流程。", "把销售会被反复追问的问题提前放进页面里，减少演示前后的重复解释成本。", "把预约演示、FAQ 和联系入口接成一条更自然的下一步动作，让官网更像一个稳定的承接面。"]
const testimonialItems = ["价值表达更清楚", "演示沟通更顺畅", "询盘转化更自然"]
const testimonialCards = [{"quote": "官网上线后，第一次来访的客户不用等到演示里才弄清我们适合什么场景，首页本身就把适合对象和价值差异讲清楚了。", "role": "增长负责人 / B2B SaaS", "result": "演示前解释成本明显下降", "context": "官网重写 / 销售前置页 / 首次访问承接"}, {"quote": "以前很多定位和边界都要靠口头补充，现在首页先把适合谁、为什么值得继续了解讲明白了，真正进入演示时大家讨论得更快更准。", "role": "产品负责人 / 创业团队", "result": "咨询更快进入真实需求", "context": "早期产品 / 定位澄清 / 预约演示入口"}, {"quote": "客户评价、FAQ 和联系入口放在同一条叙事里后，官网终于不只是静态展示页，而是一个能持续承接询盘和销售动作的前置页面。", "role": "联合创始人 / 服务型产品", "result": "官网开始稳定承接销售动作", "context": "服务转化 / FAQ 承接 / 联系动作收口"}]
const pricingItems = ["基础版", "专业版", "企业版"]
const contactFields = ["name", "email", "message"]
const contactResponseItems = ["24 小时内回复", "定位 / FAQ / 演示承接可拆分讨论", "先对齐目标，再进入页面制作"]
const contactSuccessItems = ["我们会先按场景回一版简短建议", "通常会先判断首页、FAQ 和预约动作谁该先收", "如果方向明确，再进入页面细化和制作"]
const contactHandoffCards = [{"label": "回复节奏", "value": "24 小时内回复"}, {"label": "讨论范围", "value": "定位 / FAQ / 演示承接可拆分讨论"}, {"label": "推进方式", "value": "先对齐目标，再进入页面制作"}]
const ctaCaptureItems = ["官网重写", "首次上线", "预约演示前置页"]
const footerLinks = ["产品介绍", "产品能力", "客户评价", "联系我们"]
const personalHeaderItems = []
const personalFooterItems = []
const companyHeaderItems = ["少讲形容词", "多讲对象与动作", "首页先收判断"]
const companyFooterItems = ["Fit before hype", "Proof before promise", "Action after clarity"]
const singlePageLabelTargets = {"home": "#hero", "首页": "#hero", "about": "#about", "关于": "#about", "关于我们": "#about", "关于我": "#about", "about me": "#about", "产品介绍": "#about", "features": "#features", "功能": "#features", "能力": "#features", "产品能力": "#features", "服务": "#features", "服务说明": "#features", "services": "#features", "客户评价": "#testimonials", "评价": "#testimonials", "testimonials": "#testimonials", "portfolio": "#portfolio", "work": "#portfolio", "works": "#portfolio", "projects": "#portfolio", "案例": "#portfolio", "作品": "#portfolio", "作品展示": "#portfolio", "项目作品": "#portfolio", "pricing": "#cta", "价格": "#cta", "方案": "#cta", "contact": "#contact", "联系我们": "#contact", "联系": "#contact", "联系方式": "#contact", "联系我": "#contact"}
const faqItems = [{"q": "如果团队还在反复解释产品适合谁，官网最先应该讲清什么？", "a": "先把适合对象、关键场景和价值差异摆在第一屏和产品介绍里，让第一次访问的人先完成一轮判断，再决定要不要继续预约演示或留下联系方式。", "context": "定位澄清 / 首次访问承接", "followup": "最稳的起点 usually 是：首页主张、产品介绍和 FAQ 用同一套判断逻辑。"}, {"q": "产品还在持续迭代，这样的官网会不会很快过时？", "a": "不会。当前结构本来就适合跟着产品一起扩展，后面可以继续补能力页、场景页、案例、FAQ 和更多转化入口，而不用每次都重写整套首页。", "context": "早期产品 / 内容可扩展", "followup": "先把稳定的主张和场景写清，再把会变化的细节留给后续模块逐步补齐。"}, {"q": "如果销售和演示还很依赖人工解释，这页实际能帮到什么？", "a": "它会先把适合对象、关键问题、能力边界和常见疑问讲在前面，让销售和演示不必每次都从零解释，官网会更像一个稳定的销售前置页。", "context": "销售前置 / 演示承接", "followup": "比较理想的状态是：官网先完成第一轮解释，演示再往更具体的场景里走。"}, {"q": "如果团队还在早期阶段、客户案例不多，这样的官网也值得先上线吗？", "a": "值得。早期阶段更需要先把定位、适合对象、关键场景、FAQ 和联系入口讲清楚，用结构化表达替代还没积累起来的大量客户案例。", "context": "早期阶段 / 信任补强", "followup": "没有太多案例时，可以先把 FAQ、信任反馈和预约演示入口做扎实。"}]
const teamMembers = []
const statsItems = []
const logoItems = []
const jobsItems = ["产品经理", "前端工程师", "设计师"]
const heroPersonaItems = []
const heroSignatureItems = []
const companyBrandPostureItems = [{"label": "判断句", "value": "先把产品值不值得继续看讲清。"}, {"label": "首页职责", "value": "先收对象、差异和下一步动作。"}, {"label": "演示方式", "value": "先让人判断，再决定要不要约演示。"}]
const portfolioItems = ["企业官网", "SaaS 控制台", "品牌落地页"]
const portfolioCurationItems = []
const portfolioMeta = ["品牌表达 / 页面结构 / 交付质量", "复杂功能 / 信息组织 / 稳定体验", "定位叙事 / 视觉方向 / 落地执行"]
const portfolioDetails = ["企业官网 / 核心信息重组", "后台产品 / 复杂路径梳理", "品牌专题 / 表达与落地协同"]
const portfolioOutcomes = ["品牌辨识度更清楚", "关键功能路径更顺手", "页面表达更完整可复用"]
const portfolioDescriptions = ["展示核心成果、视觉表达与落地质量。", "展示核心成果、视觉表达与落地质量。", "展示核心成果、视觉表达与落地质量。"]
const portfolioSequenceNotes = []
const personalPortfolioMode = false
const pageName = "Home"
const contactSectionEnabled = true
const contactFlowEnabled = false
const contactFlowId = "contact_form"
const leadCaptureEnabled = false
const leadCaptureField = "email"
const contactSent = ref(false)
const leadSent = ref(false)
const contactForm = reactive({ name: '', email: '', message: '' })
const leadForm = reactive({ email: '' })

function linkToTarget(label) {
  const text = String(label || '').trim().toLowerCase()
  if (singlePageLanding && singlePageLabelTargets[text]) return singlePageLabelTargets[text]
  if (text === 'home' || text === '首页') return '/'
  if (text === 'about' || text === '关于' || text === '关于我们') return '/about'
  if (text === 'features' || text === '功能' || text === '能力') return '/features'
  if (text === 'pricing' || text === '价格' || text === '方案') return '/pricing'
  if (text === 'contact' || text === '联系我们' || text === '联系') return '/contact'
  return '/'
}

function scrollToTarget(target) {
  if (!singlePageLanding || !target || !target.startsWith('#')) return false
  const node = document.getElementById(target.slice(1))
  if (!node) return false
  node.scrollIntoView({ behavior: 'smooth', block: 'start' })
  if (window.location.hash !== target) {
    window.history.replaceState(null, '', target)
  }
  return true
}

function go(target) {
  if (!target) return
  if (scrollToTarget(target)) return
  router.push(target)
}

function submitContact() {
  if (!contactSectionEnabled) return
  if (contactFlowEnabled) {
    console.log('CONTACT_SUBMIT', { form_id: contactFlowId, payload: { ...contactForm } })
  }
  contactSent.value = true
  contactForm.name = ''
  contactForm.email = ''
  contactForm.message = ''
}

function submitLeadCapture() {
  if (!leadCaptureEnabled) return
  console.log('LEAD_CAPTURE', { field: leadCaptureField, payload: { ...leadForm } })
  leadSent.value = true
}
</script>

<style scoped>
.landing-page { display: grid; gap: 18px; width: min(1120px, calc(100% - 24px)); margin: 0 auto; padding: 18px 0 28px; font-family: 'Avenir Next', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
.landing-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 12px 16px; background: rgba(15, 23, 42, 0.94); color: #f8fafc; box-shadow: 0 18px 50px rgba(15, 23, 42, 0.16); backdrop-filter: blur(10px); }
.landing-header .brand { border: 0; background: transparent; font-weight: 700; font-size: 18px; letter-spacing: 0.02em; color: inherit; cursor: pointer; }
.landing-header nav { display: flex; gap: 8px; flex-wrap: wrap; }
.landing-header nav button { border: 1px solid rgba(226, 232, 240, 0.24); background: rgba(255, 255, 255, 0.96); color: #0f172a; border-radius: 999px; padding: 7px 14px; cursor: pointer; font-weight: 600; }
.landing-hero { position: relative; overflow: hidden; border: 1px solid #cfe0ff; background: radial-gradient(circle at top left, rgba(255,255,255,0.98), rgba(231,242,255,0.95) 52%, rgba(217,229,255,0.92)); border-radius: 22px; padding: 38px 28px; display: grid; gap: 14px; box-shadow: 0 28px 60px rgba(37, 99, 235, 0.12); }
.landing-hero::after { content: ''; position: absolute; right: -40px; top: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(59,130,246,0.22), rgba(59,130,246,0)); pointer-events: none; }
.hero-kicker { position: relative; z-index: 1; display: inline-flex; width: fit-content; padding: 6px 10px; border-radius: 999px; background: rgba(15, 23, 42, 0.06); color: #1d4ed8; font-size: 12px; letter-spacing: 0.12em; font-weight: 700; }
.landing-hero h1 { position: relative; z-index: 1; margin: 0; max-width: 10ch; font-size: 44px; line-height: 1.05; letter-spacing: -0.03em; color: #eff6ff; text-shadow: 0 1px 0 rgba(15, 23, 42, 0.05); }
.landing-page:not(.personal-portfolio) .landing-header { position: relative; overflow: hidden; border-color: rgba(56, 189, 248, 0.28); background: linear-gradient(135deg, rgba(8, 15, 31, 0.99), rgba(11, 31, 58, 0.98) 38%, rgba(15, 23, 42, 0.97)); box-shadow: 0 22px 58px rgba(15, 23, 42, 0.32); }
.landing-page:not(.personal-portfolio) .landing-header::before { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(103,232,249,0.14), rgba(255,255,255,0) 28%, rgba(96,165,250,0.12) 72%, rgba(255,255,255,0)); pointer-events: none; }
.landing-page:not(.personal-portfolio) .landing-header::after { content: ''; position: absolute; left: 16px; right: 16px; bottom: 0; height: 1px; background: linear-gradient(90deg, rgba(103,232,249,0.42), rgba(59,130,246,0.12), rgba(103,232,249,0)); pointer-events: none; }
.landing-page:not(.personal-portfolio) .landing-header .brand, .landing-page:not(.personal-portfolio) .landing-footer strong { letter-spacing: 0.16em; text-transform: uppercase; font-size: 12px; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-weight: 800; }
.landing-page:not(.personal-portfolio) .landing-header .brand { position: relative; padding-left: 16px; }
.landing-page:not(.personal-portfolio) .landing-header .brand::before { content: ''; position: absolute; left: 0; top: 50%; width: 10px; height: 10px; border-radius: 999px; transform: translateY(-50%); background: radial-gradient(circle, rgba(103,232,249,1), rgba(59,130,246,0.92)); box-shadow: 0 0 0 5px rgba(103,232,249,0.16); }
.landing-page:not(.personal-portfolio) .landing-header nav button { position: relative; border-color: rgba(125, 211, 252, 0.22); background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(15,23,42,0.18)); color: #e0f2fe; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }
.landing-page:not(.personal-portfolio) .landing-header nav button::after { content: ''; position: absolute; inset: 0; border-radius: inherit; background: linear-gradient(90deg, rgba(103,232,249,0.08), rgba(255,255,255,0)); opacity: 0.72; pointer-events: none; }
.landing-page:not(.personal-portfolio) .company-header-note { position: relative; z-index: 1; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; flex: 1; }
.landing-page:not(.personal-portfolio) .company-header-note span { display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(8,15,31,0.18)); border: 1px solid rgba(125,211,252,0.22); color: #dbeafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }
.landing-page:not(.personal-portfolio) .landing-hero { border-color: rgba(56, 189, 248, 0.28); background: linear-gradient(145deg, rgba(5,10,24,1), rgba(8,47,73,0.98) 28%, rgba(14,116,144,0.94) 56%, rgba(29,78,216,0.94)); box-shadow: 0 46px 100px rgba(10, 18, 34, 0.34); padding: 46px 32px; gap: 18px; }
.landing-page:not(.personal-portfolio) .landing-hero::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(34,211,238,0.08), rgba(255,255,255,0) 42%, rgba(59,130,246,0.14)); pointer-events: none; }
.landing-page:not(.personal-portfolio) .landing-hero::after { right: -20px; top: -36px; width: 280px; height: 280px; background: radial-gradient(circle, rgba(103,232,249,0.28), rgba(96,165,250,0)); }
.landing-page:not(.personal-portfolio) .landing-hero .hero-kicker::after { content: ''; width: 26px; height: 1px; margin-left: 10px; background: linear-gradient(90deg, rgba(103,232,249,0.9), rgba(255,255,255,0)); }
.landing-page:not(.personal-portfolio) .hero-brand-row { position: relative; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: -2px; }
.landing-page:not(.personal-portfolio) .hero-brand-mark { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.16), rgba(15,23,42,0.18)); border: 1px solid rgba(125,211,252,0.26); color: #f8fafc; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-weight: 800; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 10px 24px rgba(8,15,31,0.18); }
.landing-page:not(.personal-portfolio) .hero-brand-tag { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 999px; background: rgba(8,15,31,0.24); border: 1px solid rgba(191,219,254,0.2); color: #dbeafe; font-size: 12px; letter-spacing: 0.06em; }
.landing-page:not(.personal-portfolio) .hero-brand-posture { position: relative; z-index: 1; display: grid; gap: 12px; max-width: 760px; padding: 16px; border-radius: 18px; border: 1px solid rgba(125,211,252,0.24); background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(8,15,31,0.16) 42%, rgba(8,47,73,0.22)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 16px 30px rgba(8,15,31,0.18); }
.landing-page:not(.personal-portfolio) .hero-brand-posture-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(207,250,254,0.14); border: 1px solid rgba(103,232,249,0.28); color: #cffafe; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 800; }
.landing-page:not(.personal-portfolio) .hero-brand-posture strong { color: #f8fafc; font-size: 16px; line-height: 1.7; max-width: 58ch; }
.landing-page:not(.personal-portfolio) .hero-brand-posture-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.landing-page:not(.personal-portfolio) .hero-brand-posture-card { display: grid; gap: 6px; padding: 12px 14px; border-radius: 16px; border: 1px solid rgba(125,211,252,0.2); background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(8,15,31,0.14)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }
.landing-page:not(.personal-portfolio) .hero-brand-posture-card span { color: #67e8f9; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.landing-page:not(.personal-portfolio) .hero-brand-posture-card em { color: rgba(224,242,254,0.88); font-style: normal; font-size: 13px; line-height: 1.55; }
.landing-page:not(.personal-portfolio) .hero-brand-grid { position: relative; z-index: 1; display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; max-width: 760px; }
.landing-page:not(.personal-portfolio) .hero-brand-card { display: grid; gap: 7px; border: 1px solid rgba(125,211,252,0.24); border-radius: 16px; padding: 12px 14px; background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(8,15,31,0.16) 42%, rgba(8,47,73,0.22)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 14px 28px rgba(8, 15, 31, 0.16); }
.landing-page:not(.personal-portfolio) .hero-brand-card span { color: rgba(191, 219, 254, 0.9); font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; }
.landing-page:not(.personal-portfolio) .hero-brand-card strong { color: #f8fafc; font-size: 14px; line-height: 1.45; font-weight: 700; }
.landing-page:not(.personal-portfolio) .hero-brand-card em { font-style: normal; color: rgba(224, 242, 254, 0.86); font-size: 12px; line-height: 1.45; }
.landing-page:not(.personal-portfolio) .hero-brand-card--fit { border-color: rgba(103,232,249,0.34); background: linear-gradient(180deg, rgba(207,250,254,0.16), rgba(8,15,31,0.18) 42%, rgba(8,47,73,0.24)); }
.landing-page:not(.personal-portfolio) .hero-brand-card--scenario { border-color: rgba(147,197,253,0.34); background: linear-gradient(180deg, rgba(219,234,254,0.16), rgba(8,15,31,0.18) 42%, rgba(10,36,79,0.24)); }
.landing-page:not(.personal-portfolio) .hero-brand-card--next { border-color: rgba(96,165,250,0.34); background: linear-gradient(180deg, rgba(191,219,254,0.16), rgba(15,23,42,0.2) 42%, rgba(29,78,216,0.22)); }
.landing-page:not(.personal-portfolio) .hero-copy-block { position: relative; z-index: 1; display: grid; gap: 12px; max-width: 64ch; margin-top: 2px; padding: 18px 18px 10px 18px; border-top: 1px solid rgba(125,211,252,0.24); border-left: 3px solid rgba(103,232,249,0.7); border-radius: 0 18px 18px 18px; background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(8,15,31,0.04)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }
.landing-page:not(.personal-portfolio) .landing-hero h1 { position: relative; color: #f8fafc; text-shadow: none; max-width: 9.3ch; font-size: 60px; line-height: 0.98; letter-spacing: -0.06em; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-weight: 800; padding-bottom: 18px; margin-bottom: 2px; }
.landing-page:not(.personal-portfolio) .landing-hero h1::after { content: ''; position: absolute; left: 2px; bottom: 0; width: 104px; height: 6px; border-radius: 999px; background: linear-gradient(90deg, rgba(103,232,249,0.96), rgba(59,130,246,0.92)); box-shadow: 0 0 0 4px rgba(103,232,249,0.08); }
.landing-page:not(.personal-portfolio) .landing-hero p { color: rgba(226, 232, 240, 0.92); max-width: 54ch; font-size: 18px; line-height: 1.8; }
.landing-page:not(.personal-portfolio) .hero-decision-block { position: relative; z-index: 1; display: grid; gap: 10px; width: fit-content; max-width: 100%; padding: 10px 12px 12px; border-radius: 18px; border: 1px solid rgba(125,211,252,0.22); background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(8,15,31,0.08)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }
.landing-page:not(.personal-portfolio) .hero-memory-strip { position: relative; z-index: 1; display: flex; flex-wrap: wrap; gap: 8px; margin-top: -2px; }
.landing-page:not(.personal-portfolio) .hero-memory-label { display: inline-flex; align-items: center; min-height: 32px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(34,211,238,0.18), rgba(37,99,235,0.16)); border: 1px solid rgba(103,232,249,0.28); color: #f8fafc; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }
.landing-page:not(.personal-portfolio) .hero-memory-strip span { display: inline-flex; align-items: center; min-height: 32px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(8,15,31,0.18)); border: 1px solid rgba(191,219,254,0.22); color: #e0f2fe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }
.landing-page:not(.personal-portfolio) .hero-kicker { background: linear-gradient(180deg, rgba(56,189,248,0.16), rgba(59,130,246,0.12)); color: #dbeafe; border: 1px solid rgba(125, 211, 252, 0.24); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }
.landing-page:not(.personal-portfolio) .hero-actions { gap: 12px; margin-top: 0; align-items: center; }
.landing-page:not(.personal-portfolio) .hero-actions button { min-height: 48px; padding: 0 18px; border-radius: 14px; font-size: 14px; font-weight: 700; }
.landing-page:not(.personal-portfolio) .hero-actions button:first-child { position: relative; min-height: 52px; padding: 0 48px 0 20px; border-radius: 16px; letter-spacing: 0.01em; background: linear-gradient(135deg, #2563eb, #1d4ed8 58%, #0f4cc7); box-shadow: 0 20px 40px rgba(29, 78, 216, 0.32), inset 0 1px 0 rgba(255,255,255,0.16); }
.landing-page:not(.personal-portfolio) .hero-actions button:first-child::after { content: '↗'; position: absolute; right: 14px; top: 50%; transform: translateY(-50%); width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; border-radius: 999px; background: rgba(255,255,255,0.16); color: #eff6ff; font-size: 12px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.2); }
.landing-page:not(.personal-portfolio) .hero-actions .ghost { position: relative; min-height: 46px; padding: 0 34px 0 18px; background: linear-gradient(180deg, rgba(15,23,42,0.08), rgba(15,23,42,0.18)); color: rgba(239,246,255,0.92); border-color: rgba(191, 219, 254, 0.18); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); backdrop-filter: blur(6px); }
.landing-page:not(.personal-portfolio) .hero-actions .ghost::after { content: '→'; position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: rgba(224,242,254,0.72); font-size: 13px; font-weight: 700; }
.landing-page:not(.personal-portfolio) .hero-signal-strip { position: relative; z-index: 1; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 8px; padding-top: 8px; }
.landing-page:not(.personal-portfolio) .hero-signal-card { display: flex; gap: 10px; align-items: center; border: 1px solid rgba(125, 211, 252, 0.22); background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(8,47,73,0.18) 40%, rgba(15,23,42,0.28)); color: #eff6ff; border-radius: 14px; padding: 12px 14px; min-height: 56px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 16px 30px rgba(8, 15, 31, 0.2); }
.landing-page:not(.personal-portfolio) .hero-signal-card strong { font-size: 13px; line-height: 1.4; font-weight: 700; letter-spacing: 0.01em; }
.landing-page:not(.personal-portfolio) .hero-signal-dot { width: 8px; height: 8px; border-radius: 999px; background: #67e8f9; box-shadow: 0 0 0 5px rgba(103,232,249,0.18); flex: none; }
.landing-page:not(.personal-portfolio) .landing-section { position: relative; border-color: rgba(96, 165, 250, 0.18); box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08); }
.landing-page:not(.personal-portfolio) .landing-section::before { content: ''; position: absolute; inset: 0 0 auto 0; height: 1px; background: linear-gradient(90deg, rgba(255,255,255,0.76), rgba(255,255,255,0)); opacity: 0.8; pointer-events: none; }
.landing-page:not(.personal-portfolio) .section-path-strip { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 18px; }
.landing-page:not(.personal-portfolio) .section-path-strip span { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.landing-page:not(.personal-portfolio) .section-path-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); border: 1px solid rgba(56,189,248,0.22); color: #0f4cc7; box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }
.landing-page:not(.personal-portfolio) .section-path-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); border: 1px solid rgba(191,219,254,0.56); color: #1e3a8a; }
.landing-page:not(.personal-portfolio) .section-proof-bridge { display: grid; gap: 10px; margin-top: 14px; padding: 14px; border-radius: 18px; border: 1px solid rgba(191,219,254,0.6); background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.92)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.06); }
.landing-page:not(.personal-portfolio) .section-proof-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.18); color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.82)); }
.landing-page:not(.personal-portfolio) .section-proof-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.65; }
.landing-page:not(.personal-portfolio) .section-proof-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.landing-page:not(.personal-portfolio) .section-proof-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.18); }
.landing-page:not(.personal-portfolio) .section-proof-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; }
.landing-page:not(.personal-portfolio) .section-proof-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; }
.landing-page:not(.personal-portfolio) .about-section { border-color: rgba(56, 189, 248, 0.24); background: linear-gradient(160deg, rgba(255,255,255,0.99), rgba(240,249,255,0.97) 54%, rgba(224,242,254,0.93)); }
.landing-page:not(.personal-portfolio) #features { border-color: rgba(96, 165, 250, 0.24); background: linear-gradient(160deg, rgba(255,255,255,0.99), rgba(239,246,255,0.97) 48%, rgba(224,231,255,0.93)); }
.landing-page:not(.personal-portfolio) #testimonials { border-color: rgba(45, 212, 191, 0.24); background: linear-gradient(165deg, rgba(248,250,252,0.99), rgba(236,253,245,0.96) 50%, rgba(224,242,254,0.94)); }
.landing-page:not(.personal-portfolio) #faq { border-color: rgba(251, 191, 36, 0.24); background: linear-gradient(165deg, rgba(255,255,255,0.99), rgba(255,251,235,0.96) 46%, rgba(248,250,252,0.94)); }
.landing-page:not(.personal-portfolio) #contact { border-color: rgba(59, 130, 246, 0.22); background: linear-gradient(165deg, rgba(255,255,255,0.99), rgba(248,250,252,0.96) 42%, rgba(239,246,255,0.94)); }
.landing-page:not(.personal-portfolio) #cta { border-color: rgba(30, 64, 175, 0.28); background: linear-gradient(160deg, rgba(239,246,255,0.98), rgba(224,231,255,0.96) 38%, rgba(219,234,254,0.94)); }
.landing-page:not(.personal-portfolio) #about .section-path-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(14,165,233,0.1)); border-color: rgba(34,211,238,0.28); color: #0f766e; }
.landing-page:not(.personal-portfolio) #about .section-path-next { border-color: rgba(125,211,252,0.54); color: #155e75; }
.landing-page:not(.personal-portfolio) #features .section-path-current { background: linear-gradient(180deg, rgba(96,165,250,0.18), rgba(37,99,235,0.12)); border-color: rgba(96,165,250,0.3); color: #1d4ed8; }
.landing-page:not(.personal-portfolio) #features .section-path-next { border-color: rgba(165,180,252,0.52); color: #3730a3; }
.landing-page:not(.personal-portfolio) #testimonials .section-path-current { background: linear-gradient(180deg, rgba(45,212,191,0.18), rgba(16,185,129,0.12)); border-color: rgba(45,212,191,0.3); color: #047857; }
.landing-page:not(.personal-portfolio) #testimonials .section-path-next { border-color: rgba(110,231,183,0.52); color: #065f46; }
.landing-page:not(.personal-portfolio) #faq .section-path-current { background: linear-gradient(180deg, rgba(251,191,36,0.18), rgba(245,158,11,0.1)); border-color: rgba(251,191,36,0.34); color: #b45309; }
.landing-page:not(.personal-portfolio) #faq .section-path-next { border-color: rgba(252,211,77,0.48); color: #92400e; }
.landing-page:not(.personal-portfolio) #contact .section-path-current { background: linear-gradient(180deg, rgba(99,102,241,0.14), rgba(59,130,246,0.12)); border-color: rgba(99,102,241,0.3); color: #3730a3; }
.landing-page:not(.personal-portfolio) #contact .section-path-next { border-color: rgba(129,140,248,0.42); color: #312e81; }
.landing-page:not(.personal-portfolio) .section-proof-bridge--about { border-color: rgba(34,211,238,0.34); background: linear-gradient(180deg, rgba(240,249,255,0.98), rgba(224,242,254,0.92)); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--about .section-proof-bridge-label { color: #0f766e; background: linear-gradient(180deg, rgba(204,251,241,0.94), rgba(207,250,254,0.9)); border-color: rgba(45,212,191,0.3); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--about .section-proof-bridge-current { background: linear-gradient(180deg, rgba(45,212,191,0.16), rgba(20,184,166,0.1)); color: #0f766e; border-color: rgba(45,212,191,0.24); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--about .section-proof-bridge-next { color: #155e75; border-color: rgba(125,211,252,0.46); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--features { border-color: rgba(96,165,250,0.34); background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(224,231,255,0.92)); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--features .section-proof-bridge-label { color: #1d4ed8; background: linear-gradient(180deg, rgba(219,234,254,0.94), rgba(224,231,255,0.9)); border-color: rgba(96,165,250,0.28); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--features .section-proof-bridge-current { background: linear-gradient(180deg, rgba(96,165,250,0.16), rgba(37,99,235,0.1)); color: #1d4ed8; border-color: rgba(96,165,250,0.26); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--features .section-proof-bridge-next { color: #3730a3; border-color: rgba(165,180,252,0.46); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--trust { border-color: rgba(45,212,191,0.34); background: linear-gradient(180deg, rgba(236,253,245,0.98), rgba(224,242,254,0.92)); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--trust .section-proof-bridge-label { color: #047857; background: linear-gradient(180deg, rgba(220,252,231,0.94), rgba(204,251,241,0.9)); border-color: rgba(45,212,191,0.3); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--trust .section-proof-bridge-current { background: linear-gradient(180deg, rgba(45,212,191,0.16), rgba(16,185,129,0.1)); color: #047857; border-color: rgba(45,212,191,0.24); }
.landing-page:not(.personal-portfolio) .section-proof-bridge--trust .section-proof-bridge-next { color: #065f46; border-color: rgba(110,231,183,0.48); }
.landing-page:not(.personal-portfolio) .faq-scan-strip span { background: linear-gradient(180deg, rgba(224,242,254,0.82), rgba(219,234,254,0.7)); color: #0f4cc7; border-color: rgba(56,189,248,0.28); box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }
.landing-page:not(.personal-portfolio) .faq-scan-strip span:nth-child(1) { background: linear-gradient(180deg, rgba(254,240,138,0.28), rgba(252,211,77,0.18)); color: #92400e; border-color: rgba(251,191,36,0.28); }
.landing-page:not(.personal-portfolio) .faq-scan-strip span:nth-child(2) { background: linear-gradient(180deg, rgba(191,219,254,0.28), rgba(147,197,253,0.18)); color: #1d4ed8; border-color: rgba(96,165,250,0.28); }
.landing-page:not(.personal-portfolio) .faq-scan-strip span:nth-child(3) { background: linear-gradient(180deg, rgba(220,252,231,0.32), rgba(187,247,208,0.18)); color: #166534; border-color: rgba(110,231,183,0.28); }
.landing-page:not(.personal-portfolio) .faq-copy-block { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(241,245,249,0.94)); border-color: rgba(226,232,240,0.96); }
.landing-page:not(.personal-portfolio) .faq-followup-block { background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(224,242,254,0.92)); border-color: rgba(147,197,253,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.86); }
.landing-page:not(.personal-portfolio) .faq-contact-bridge { background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(224,242,254,0.92)); border-color: rgba(147,197,253,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }
.landing-page:not(.personal-portfolio) .faq-contact-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }
.landing-page:not(.personal-portfolio) .faq-contact-bridge strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .faq-contact-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }
.landing-page:not(.personal-portfolio) .faq-contact-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }
.landing-page:not(.personal-portfolio) .contact-entry-bridge { background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(248,250,252,0.96)); border-color: rgba(191,219,254,0.84); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88); }
.landing-page:not(.personal-portfolio) .contact-entry-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }
.landing-page:not(.personal-portfolio) .contact-entry-bridge strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .contact-response-strip span { background: linear-gradient(180deg, rgba(224,242,254,0.82), rgba(219,234,254,0.68)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }
.landing-page:not(.personal-portfolio) .contact-intake-bridge { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.92)); border-color: rgba(191,219,254,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 16px 28px rgba(15,23,42,0.06); }
.landing-page:not(.personal-portfolio) .contact-intake-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }
.landing-page:not(.personal-portfolio) .contact-intake-bridge strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .contact-intake-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }
.landing-page:not(.personal-portfolio) .contact-intake-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }
.landing-page:not(.personal-portfolio) .contact-handoff-card { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(224,242,254,0.92)); border-color: rgba(96,165,250,0.2); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 16px 30px rgba(15, 23, 42, 0.08); }
.landing-page:not(.personal-portfolio) .contact-handoff-card span { color: #0f4cc7; }
.landing-page:not(.personal-portfolio) .contact-handoff-card strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .intake-closure-bridge { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.92)); border-color: rgba(191,219,254,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }
.landing-page:not(.personal-portfolio) .intake-closure-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }
.landing-page:not(.personal-portfolio) .intake-closure-bridge strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .intake-closure-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }
.landing-page:not(.personal-portfolio) .intake-closure-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }
.landing-page:not(.personal-portfolio) .cta-note { color: #1e3a8a; max-width: 48ch; font-weight: 600; }
.landing-page:not(.personal-portfolio) .cta-capture-strip span { background: linear-gradient(180deg, rgba(224,242,254,0.82), rgba(219,234,254,0.68)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }
.landing-page:not(.personal-portfolio) .cta-success-bridge { background: linear-gradient(180deg, rgba(236,253,245,0.98), rgba(240,253,250,0.96)); border-color: rgba(110,231,183,0.56); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }
.landing-page:not(.personal-portfolio) .cta-success-bridge-label { color: #166534; background: linear-gradient(180deg, rgba(220,252,231,0.96), rgba(209,250,229,0.92)); border-color: rgba(134,239,172,0.72); }
.landing-page:not(.personal-portfolio) .cta-success-bridge strong { color: #14532d; }
.landing-page:not(.personal-portfolio) .cta-success-bridge-current { background: linear-gradient(180deg, rgba(220,252,231,0.96), rgba(209,250,229,0.9)); color: #166534; border-color: rgba(134,239,172,0.72); }
.landing-page:not(.personal-portfolio) .cta-success-bridge-next { background: linear-gradient(180deg, rgba(248,250,252,0.96), rgba(241,245,249,0.9)); color: #166534; border-color: rgba(187,247,208,0.7); }
.landing-page:not(.personal-portfolio) .cta-landing-bridge { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(224,242,254,0.92)); border-color: rgba(147,197,253,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }
.landing-page:not(.personal-portfolio) .cta-landing-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }
.landing-page:not(.personal-portfolio) .cta-landing-bridge strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .cta-landing-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }
.landing-page:not(.personal-portfolio) .cta-landing-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }
.landing-page:not(.personal-portfolio) .footer-success-bridge { background: linear-gradient(180deg, rgba(240,253,250,0.2), rgba(15,23,42,0.08)); border: 1px solid rgba(134,239,172,0.2); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }
.landing-page:not(.personal-portfolio) .footer-success-bridge-label { color: #bbf7d0; background: rgba(34,197,94,0.12); border-color: rgba(134,239,172,0.26); }
.landing-page:not(.personal-portfolio) .footer-success-bridge strong { color: #ecfdf5; }
.landing-page:not(.personal-portfolio) .footer-success-bridge-current { background: rgba(34,197,94,0.16); color: #dcfce7; border-color: rgba(134,239,172,0.26); }
.landing-page:not(.personal-portfolio) .footer-success-bridge-next { background: rgba(255,255,255,0.06); color: #dbeafe; border-color: rgba(191,219,254,0.18); }
.landing-page:not(.personal-portfolio) .landing-footer { position: relative; overflow: hidden; border-color: rgba(59,130,246,0.24); background: linear-gradient(145deg, rgba(5,10,24,0.99), rgba(10,25,49,0.98) 40%, rgba(15,23,42,0.97)); box-shadow: 0 24px 48px rgba(8,15,31,0.26); }
.landing-page:not(.personal-portfolio) .landing-footer::before { content: ''; position: absolute; inset: 0; background: linear-gradient(120deg, rgba(103,232,249,0.08), rgba(255,255,255,0) 38%, rgba(59,130,246,0.08)); pointer-events: none; }
.landing-page:not(.personal-portfolio) .landing-footer::after { content: ''; position: absolute; left: 16px; right: 16px; top: 0; height: 1px; background: linear-gradient(90deg, rgba(103,232,249,0.38), rgba(59,130,246,0.12), rgba(103,232,249,0)); pointer-events: none; }
.landing-page:not(.personal-portfolio) .landing-footer .links { position: relative; z-index: 1; }
.landing-page:not(.personal-portfolio) .landing-footer button { border-color: rgba(125,211,252,0.2); background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(15,23,42,0.18)); color: #dbeafe; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }
.landing-page:not(.personal-portfolio) .landing-footer small { color: rgba(191,219,254,0.72); }
.landing-page:not(.personal-portfolio) .company-footer-signoff { position: relative; z-index: 1; display: grid; gap: 8px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(125,211,252,0.16); }
.landing-page:not(.personal-portfolio) .company-footer-signoff-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(103,232,249,0.12); border: 1px solid rgba(125,211,252,0.22); color: #cffafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.landing-page:not(.personal-portfolio) .company-footer-signoff-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.landing-page:not(.personal-portfolio) .company-footer-signoff-grid span { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(15,23,42,0.18)); border: 1px solid rgba(191,219,254,0.18); color: #dbeafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.landing-page:not(.personal-portfolio) #cta .cta-note { color: #1e40af; }
.landing-page:not(.personal-portfolio) #cta .cta-capture-strip span:nth-child(1) { background: linear-gradient(180deg, rgba(219,234,254,0.9), rgba(191,219,254,0.74)); color: #1d4ed8; }
.landing-page:not(.personal-portfolio) #cta .cta-capture-strip span:nth-child(2) { background: linear-gradient(180deg, rgba(224,231,255,0.92), rgba(199,210,254,0.76)); color: #3730a3; }
.landing-page:not(.personal-portfolio) #cta .cta-capture-strip span:nth-child(3) { background: linear-gradient(180deg, rgba(220,252,231,0.92), rgba(187,247,208,0.76)); color: #166534; }
.landing-page:not(.personal-portfolio) .cta-close-strip span { box-shadow: inset 0 1px 0 rgba(255,255,255,0.86); }
.landing-page:not(.personal-portfolio) .cta-close-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }
.landing-page:not(.personal-portfolio) .cta-close-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }
.landing-page:not(.personal-portfolio) .quote-card { border-color: rgba(96, 165, 250, 0.24); border-top: 3px solid rgba(14,165,233,0.9); background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.96)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.8); }
.landing-page:not(.personal-portfolio) .quote-card::before { content: 'TRUST SIGNAL'; display: inline-flex; width: fit-content; padding: 5px 9px; border-radius: 999px; background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.08)); color: #0f4cc7; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; }
.landing-page:not(.personal-portfolio) .quote-copy { color: #1e293b; }
.landing-page:not(.personal-portfolio) .quote-meta strong { color: #0f172a; }
.landing-page:not(.personal-portfolio) .quote-meta span { color: #0f4cc7; }
.landing-page:not(.personal-portfolio) .landing-section h2 { position: relative; padding-left: 18px; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-size: 28px; letter-spacing: -0.045em; }
.landing-page:not(.personal-portfolio) .landing-section h2::before { content: ''; position: absolute; left: 0; top: 4px; width: 6px; height: 24px; border-radius: 999px; background: linear-gradient(180deg, #38bdf8, #2563eb); box-shadow: 0 0 0 4px rgba(59,130,246,0.12); }
.landing-page:not(.personal-portfolio) .faq-item { border-left: 3px solid rgba(14,165,233,0.9); }
.landing-page:not(.personal-portfolio) .faq-summary-hint { background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); color: #0f4cc7; border: 1px solid rgba(56,189,248,0.18); }
.landing-page.personal-portfolio { gap: 22px; }
.landing-page.personal-portfolio .landing-header { border-color: rgba(217, 119, 6, 0.16); background: linear-gradient(135deg, rgba(252,248,243,0.98), rgba(255,250,245,0.97)); color: #172554; box-shadow: 0 18px 42px rgba(148, 163, 184, 0.12); }
.landing-page.personal-portfolio .landing-header .brand, .landing-page.personal-portfolio .landing-footer strong { letter-spacing: 0.08em; text-transform: uppercase; font-size: 13px; color: #1e3a8a; }
.landing-page.personal-portfolio .personal-header-note { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; flex: 1; }
.landing-page.personal-portfolio .personal-header-note span { display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,255,255,0.72); border: 1px solid rgba(251,191,36,0.22); color: #9a3412; font-size: 11px; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }
.landing-page.personal-portfolio .landing-header nav button { border-color: rgba(191, 219, 254, 0.55); background: rgba(255,255,255,0.86); color: #1e3a8a; box-shadow: inset 0 1px 0 rgba(255,255,255,0.85); }
.landing-page.personal-portfolio .landing-hero { border-color: rgba(251, 191, 36, 0.34); background: linear-gradient(145deg, rgba(255,252,247,0.99), rgba(255,244,232,0.98) 38%, rgba(239,246,255,0.96) 70%, rgba(219,234,254,0.95)); box-shadow: 0 34px 80px rgba(37, 99, 235, 0.12), 0 12px 28px rgba(245, 158, 11, 0.12); }
.landing-page.personal-portfolio .landing-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 18% 18%, rgba(251,191,36,0.12), rgba(251,191,36,0) 30%), radial-gradient(circle at 84% 22%, rgba(59,130,246,0.12), rgba(59,130,246,0) 26%); pointer-events: none; }
.landing-page.personal-portfolio .landing-section h2, .landing-page.personal-portfolio .landing-hero h1 { font-family: 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', 'Songti SC', serif; }
.landing-page.personal-portfolio .landing-hero h1 { color: #0f172a; font-size: 56px; max-width: 11ch; text-shadow: none; letter-spacing: -0.045em; }
.landing-page.personal-portfolio .landing-hero p { color: #1e293b; max-width: 58ch; font-size: 17px; }
.landing-page.personal-portfolio .hero-kicker { background: linear-gradient(180deg, rgba(251,191,36,0.16), rgba(59,130,246,0.08)); color: #92400e; border: 1px solid rgba(245,158,11,0.2); }
.landing-page.personal-portfolio .hero-persona-row { position: relative; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; margin-top: -2px; }
.landing-page.personal-portfolio .hero-persona-chip { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 999px; background: rgba(255,255,255,0.82); border: 1px solid rgba(251,191,36,0.24); color: #92400e; font-size: 12px; letter-spacing: 0.06em; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); }
.landing-page.personal-portfolio .hero-signature-strip { position: relative; z-index: 1; display: grid; gap: 12px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,250,244,0.92)); border: 1px solid rgba(251,191,36,0.24); box-shadow: 0 14px 28px rgba(245,158,11,0.08); }
.landing-page.personal-portfolio .hero-signature-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,237,213,0.92); border: 1px solid rgba(251,191,36,0.3); color: #9a3412; font-size: 11px; letter-spacing: 0.08em; font-weight: 800; text-transform: uppercase; }
.landing-page.personal-portfolio .hero-signature-strip strong { color: #3f1d0d; font-size: 15px; line-height: 1.7; max-width: 56ch; }
.landing-page.personal-portfolio .hero-signature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.landing-page.personal-portfolio .hero-signature-card { display: grid; gap: 6px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.9); border: 1px solid rgba(191,219,254,0.34); box-shadow: inset 0 1px 0 rgba(255,255,255,0.85); }
.landing-page.personal-portfolio .hero-signature-card span { color: #9a3412; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 800; }
.landing-page.personal-portfolio .hero-signature-card em { color: #1e293b; font-style: normal; line-height: 1.6; font-size: 13px; }
.landing-page.personal-portfolio .hero-actions button { background: linear-gradient(135deg, #1d4ed8, #2563eb); box-shadow: 0 16px 28px rgba(37, 99, 235, 0.18); }
.landing-page.personal-portfolio .hero-actions .ghost { background: rgba(255,255,255,0.8); color: #92400e; border-color: rgba(245,158,11,0.28); }
.landing-page.personal-portfolio .about-section { border-color: rgba(245, 158, 11, 0.16); background: linear-gradient(180deg, rgba(255,252,248,0.98), rgba(255,247,237,0.96)); }
.landing-page.personal-portfolio .about-note { color: #7c2d12; font-size: 14px; }
.landing-page.personal-portfolio .about-points article { border-color: rgba(251,191,36,0.26); background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,247,237,0.92)); box-shadow: 0 10px 22px rgba(245, 158, 11, 0.08); }
.landing-page.personal-portfolio .about-point-dot { background: #f59e0b; box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.14); }
.landing-page.personal-portfolio .landing-section { border-color: rgba(191, 219, 254, 0.2); box-shadow: 0 16px 38px rgba(15, 23, 42, 0.05); }
.landing-page.personal-portfolio .landing-section h2 { position: relative; padding-left: 18px; }
.landing-page.personal-portfolio .landing-section h2::before { content: ''; position: absolute; left: 0; top: 5px; width: 6px; height: 22px; border-radius: 999px; background: linear-gradient(180deg, #f59e0b, #f97316); box-shadow: 0 0 0 4px rgba(245,158,11,0.12); }
.landing-page.personal-portfolio .portfolio-curation-strip { display: grid; gap: 12px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,252,248,0.98), rgba(255,245,234,0.94)); border: 1px solid rgba(251,191,36,0.24); box-shadow: 0 14px 30px rgba(245,158,11,0.08); }
.landing-page.personal-portfolio .portfolio-curation-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,237,213,0.94); border: 1px solid rgba(251,191,36,0.3); color: #9a3412; font-size: 11px; letter-spacing: 0.08em; font-weight: 800; text-transform: uppercase; }
.landing-page.personal-portfolio .portfolio-curation-strip strong { color: #431407; line-height: 1.7; font-size: 15px; max-width: 58ch; }
.landing-page.personal-portfolio .portfolio-curation-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.landing-page.personal-portfolio .portfolio-curation-card { display: grid; gap: 6px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.92); border: 1px solid rgba(251,191,36,0.18); }
.landing-page.personal-portfolio .portfolio-curation-card span { color: #9a3412; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 800; }
.landing-page.personal-portfolio .portfolio-curation-card em { color: #1e293b; font-style: normal; line-height: 1.6; font-size: 13px; }
.landing-page.personal-portfolio .portfolio-card { border-color: rgba(251,191,36,0.22); background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(255,247,237,0.96)); box-shadow: 0 16px 30px rgba(148, 163, 184, 0.08); }
.landing-page.personal-portfolio .portfolio-sequence { display: inline-flex; width: fit-content; align-items: center; min-height: 26px; padding: 0 9px; border-radius: 999px; background: rgba(30,64,175,0.08); border: 1px solid rgba(59,130,246,0.18); color: #1e3a8a; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
.landing-page.personal-portfolio .portfolio-meta { color: #9a3412; background: rgba(255,237,213,0.95); border-color: rgba(251,191,36,0.3); }
.landing-page.personal-portfolio .portfolio-brief span { background: rgba(255,252,248,0.96); border-color: rgba(251,191,36,0.2); }
.landing-page.personal-portfolio .portfolio-brief strong { color: #9a3412; }
.landing-page.personal-portfolio .portfolio-brief em { color: #7c2d12; }
.landing-page.personal-portfolio .portfolio-editor-note { display: inline-flex; width: fit-content; margin-top: auto; padding: 6px 10px; border-radius: 999px; background: rgba(255,250,245,0.96); border: 1px solid rgba(251,191,36,0.18); color: #7c2d12; font-size: 12px; line-height: 1.5; }
.landing-page.personal-portfolio .portfolio-detail { color: #7c2d12; background: rgba(255,247,237,0.92); border: 1px solid rgba(251,191,36,0.18); }
.landing-page.personal-portfolio .portfolio-outcome { background: rgba(219,234,254,0.75); color: #1e3a8a; }
.landing-page.personal-portfolio .landing-footer { border-color: rgba(191, 219, 254, 0.24); background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(30,41,59,0.96)); }
.landing-page.personal-portfolio .footer-signoff-strip { display: grid; gap: 8px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(191,219,254,0.14); }
.landing-page.personal-portfolio .footer-signoff-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,255,255,0.08); border: 1px solid rgba(191,219,254,0.18); color: #dbeafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.landing-page.personal-portfolio .footer-signoff-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.landing-page.personal-portfolio .footer-signoff-grid span { display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,255,255,0.08); border: 1px solid rgba(191,219,254,0.16); color: #dbeafe; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; }
.landing-page.personal-portfolio .landing-footer button { border-color: rgba(191,219,254,0.22); background: rgba(255,255,255,0.96); color: #1e3a8a; }
.landing-hero p { position: relative; z-index: 1; margin: 0; max-width: 64ch; color: #334155; font-size: 16px; line-height: 1.7; }
.hero-actions { position: relative; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; }
.hero-actions button { border: 1px solid #2563eb; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-radius: 10px; padding: 10px 14px; cursor: pointer; font-weight: 700; box-shadow: 0 12px 26px rgba(37, 99, 235, 0.22); }
.hero-actions .ghost { background: rgba(255, 255, 255, 0.92); color: #1d4ed8; box-shadow: none; }
.landing-section { border: 1px solid #e5e7eb; background: rgba(255, 255, 255, 0.98); border-radius: 18px; padding: 18px; display: grid; gap: 12px; box-shadow: 0 16px 38px rgba(15, 23, 42, 0.06); }
.landing-section h1, .landing-section h2 { margin: 0; }
.landing-section h2 { font-size: 24px; letter-spacing: -0.02em; color: #0f172a; }
.section-lead { margin: 0; max-width: 64ch; color: #475569; font-size: 14px; line-height: 1.7; }
.about-section { background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); }
.about-shell { display: grid; gap: 16px; max-width: 940px; grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.9fr); align-items: start; }
.about-copy { display: grid; gap: 10px; }
.about-shell p { margin: 0; color: #334155; line-height: 1.8; font-size: 15px; }
.about-note { color: #475569; font-size: 14px; }
.about-points { display: grid; gap: 10px; }
.about-points article { border: 1px solid rgba(148, 163, 184, 0.22); background: rgba(241,245,249,0.88); color: #0f172a; border-radius: 14px; padding: 12px 14px; font-size: 13px; font-weight: 600; display: flex; gap: 10px; align-items: center; }
.about-point-dot { width: 8px; height: 8px; border-radius: 999px; background: #2563eb; flex: none; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12); }
.pill-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.pill-grid article { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 16px; display: grid; gap: 8px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); min-height: 138px; }
.pill-grid article strong { font-size: 15px; color: #0f172a; }
.pill-grid article span { color: #475569; font-size: 14px; line-height: 1.5; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }
.stat-card { border: 1px solid #e4e4e7; border-radius: 10px; padding: 14px; display: grid; gap: 6px; text-align: center; }
.stat-card strong { font-size: 24px; color: #1d4ed8; }
.stat-card span { color: #475569; }
.logo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }
.logo-card { border: 1px dashed #cbd5e1; border-radius: 10px; min-height: 72px; display: grid; place-items: center; background: #f8fafc; color: #475569; }
.team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.team-card { border: 1px solid #e4e4e7; border-radius: 10px; padding: 14px; display: grid; gap: 6px; justify-items: center; text-align: center; }
.team-card .avatar { width: 48px; height: 48px; border-radius: 999px; background: #dbeafe; color: #1d4ed8; display: grid; place-items: center; font-weight: 700; }
.team-card span { color: #475569; }
.jobs-grid, .portfolio-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.jobs-card, .portfolio-card { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 18px; padding: 16px; display: grid; gap: 8px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); min-height: 146px; }
.portfolio-meta { display: inline-flex; width: fit-content; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219, 234, 254, 0.9); border: 1px solid rgba(96, 165, 250, 0.24); border-radius: 999px; padding: 5px 10px; }
.jobs-card span { color: #475569; font-size: 14px; }
.portfolio-card strong { font-size: 16px; color: #0f172a; }
.portfolio-card p { margin: 0; color: #475569; font-size: 14px; line-height: 1.65; }
.portfolio-brief { display: grid; gap: 8px; margin-top: auto; }
.portfolio-brief span { display: grid; gap: 4px; padding: 8px 10px; border-radius: 12px; background: rgba(248,250,252,0.92); border: 1px solid rgba(148,163,184,0.16); }
.portfolio-brief strong { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; }
.portfolio-brief em { font-style: normal; font-size: 13px; color: #0f172a; line-height: 1.55; }
.portfolio-detail { display: inline-flex; width: fit-content; color: #475569; background: rgba(241,245,249,0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600; }
.portfolio-outcome { margin-top: auto; display: inline-flex; width: fit-content; color: #0f172a; background: rgba(226, 232, 240, 0.75); border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600; }
.faq-scan-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.faq-scan-strip span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 11px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219,234,254,0.62); border: 1px solid rgba(96,165,250,0.2); }
.faq-list { display: grid; gap: 12px; }
.faq-item { border: 1px solid #e4e4e7; border-radius: 14px; padding: 12px 14px; background: rgba(255,255,255,0.98); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04); display: grid; gap: 10px; }
.faq-item[open] { box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08); }
.faq-item summary { cursor: pointer; font-weight: 700; color: #0f172a; list-style: none; display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.faq-item summary::-webkit-details-marker { display: none; }
.faq-question { flex: 1; line-height: 1.55; }
.faq-summary-hint { display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 9px; background: rgba(241,245,249,0.9); color: #475569; font-size: 11px; font-weight: 700; white-space: nowrap; }
.faq-body { display: grid; gap: 10px; }
.faq-context { display: inline-flex; width: fit-content; padding: 5px 10px; border-radius: 999px; background: rgba(219,234,254,0.72); color: #1d4ed8; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.faq-copy-block, .faq-followup-block { display: grid; gap: 8px; padding: 10px 12px; border-radius: 12px; }
.faq-copy-block { background: rgba(248,250,252,0.92); border: 1px solid rgba(226,232,240,0.9); }
.faq-followup-block { background: rgba(239,246,255,0.8); border: 1px solid rgba(191,219,254,0.72); }
.faq-copy-label, .faq-followup-label { display: inline-flex; width: fit-content; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }
.faq-copy-label { color: #64748b; }
.faq-followup-label { color: #0f4cc7; }
.faq-answer { margin: 0; color: #475569; line-height: 1.7; }
.faq-followup { margin: 0; color: #0f172a; line-height: 1.65; font-size: 13px; font-weight: 600; }
.faq-contact-bridge { display: grid; gap: 10px; margin-top: 12px; padding: 14px; border-radius: 16px; background: rgba(239,246,255,0.82); border: 1px solid rgba(191,219,254,0.72); }
.faq-contact-bridge-label, .contact-entry-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.faq-contact-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }
.faq-contact-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.faq-contact-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.faq-contact-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }
.faq-contact-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }
.quote-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.quote-card { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 18px; padding: 16px; display: grid; gap: 12px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); min-height: 174px; }
.quote-context { display: inline-flex; width: fit-content; padding: 5px 10px; border-radius: 999px; background: rgba(226,232,240,0.72); color: #475569; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.quote-copy { margin: 0; color: #334155; line-height: 1.75; font-size: 14px; }
.quote-meta { margin-top: auto; display: grid; gap: 4px; }
.quote-meta strong { color: #0f172a; font-size: 13px; }
.quote-meta span { color: #1d4ed8; font-size: 12px; font-weight: 600; }
.cta { text-align: center; background: linear-gradient(135deg, rgba(239,246,255,0.98), rgba(219,234,254,0.96)); }
.cta-note { margin: 0 auto 10px; max-width: 52ch; color: #475569; font-size: 14px; line-height: 1.65; }
.cta-capture-strip { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 0 auto 12px; }
.cta-capture-strip span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 11px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219,234,254,0.62); border: 1px solid rgba(96,165,250,0.2); }
.cta-success-bridge { display: grid; gap: 10px; margin: 0 auto 12px; max-width: 720px; padding: 14px; border-radius: 16px; background: rgba(236,253,245,0.92); border: 1px solid rgba(110,231,183,0.55); text-align: left; }
.cta-success-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(134,239,172,0.7); }
.cta-success-bridge strong { color: #14532d; font-size: 14px; line-height: 1.6; }
.cta-success-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.cta-success-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(134,239,172,0.7); }
.cta-success-bridge-current { color: #166534; background: rgba(220,252,231,0.92); }
.cta-success-bridge-next { color: #166534; background: rgba(240,253,244,0.96); }
.cta-landing-bridge { display: grid; gap: 10px; margin: 0 auto 12px; max-width: 720px; padding: 14px; border-radius: 16px; background: rgba(248,250,252,0.94); border: 1px solid rgba(191,219,254,0.72); text-align: left; }
.cta-landing-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.cta-landing-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }
.cta-landing-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.cta-landing-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.cta-landing-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }
.cta-landing-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }
.cta-close-strip { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 0 auto 14px; }
.cta-close-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.cta-close-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }
.cta-close-next { color: #334155; background: rgba(241,245,249,0.92); }
.cta button { border: 1px solid #2563eb; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-radius: 10px; padding: 10px 16px; cursor: pointer; font-weight: 700; box-shadow: 0 14px 26px rgba(37, 99, 235, 0.18); }
.price-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
.price-grid article { border: 1px solid #e4e4e7; border-radius: 8px; padding: 12px; display: grid; gap: 8px; }
.price-grid button { border: 1px solid #0f766e; background: #0f766e; color: #fff; border-radius: 8px; padding: 6px 10px; cursor: pointer; width: fit-content; }
.contact-response-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.contact-response-strip span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 11px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219,234,254,0.62); border: 1px solid rgba(96,165,250,0.2); }
.contact-entry-bridge { display: grid; gap: 8px; margin-bottom: 14px; padding: 12px 14px; border-radius: 16px; background: rgba(239,246,255,0.78); border: 1px solid rgba(191,219,254,0.72); }
.contact-entry-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }
.contact-intake-bridge { display: grid; gap: 10px; margin: 12px 0 14px; padding: 14px; border-radius: 16px; background: rgba(248,250,252,0.94); border: 1px solid rgba(191,219,254,0.72); }
.contact-intake-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.contact-intake-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }
.contact-intake-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.contact-intake-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.contact-intake-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }
.contact-intake-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }
.contact-handoff-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.contact-handoff-card { border: 1px solid rgba(148,163,184,0.22); border-radius: 16px; padding: 14px; display: grid; gap: 6px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); }
.contact-handoff-card span { font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; }
.contact-handoff-card strong { color: #0f172a; font-size: 14px; line-height: 1.55; }
.intake-closure-bridge { display: grid; gap: 10px; margin: 0 auto 14px; max-width: 760px; padding: 14px; border-radius: 16px; background: rgba(248,250,252,0.94); border: 1px solid rgba(191,219,254,0.72); text-align: left; }
.intake-closure-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.intake-closure-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }
.intake-closure-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.intake-closure-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }
.intake-closure-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }
.intake-closure-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }
.contact-form-shell { display: grid; gap: 12px; max-width: 760px; }
.contact-form-shell--business { grid-template-columns: minmax(220px, 0.9fr) minmax(0, 1.15fr); align-items: start; }
.contact-form-intake { display: grid; gap: 10px; padding: 14px; border-radius: 16px; background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(248,250,252,0.96)); border: 1px solid rgba(191,219,254,0.9); }
.contact-form-intake strong { color: #0f172a; font-size: 14px; line-height: 1.6; }
.contact-form-checklist { display: flex; flex-wrap: wrap; gap: 8px; }
.contact-form-checklist span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #0f4cc7; background: rgba(219,234,254,0.76); border: 1px solid rgba(96,165,250,0.2); }
.contact-form-panel { display: grid; gap: 12px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.97)); border: 1px solid rgba(148,163,184,0.18); box-shadow: 0 18px 36px rgba(15,23,42,0.08); }
.contact-form { display: grid; gap: 12px; max-width: 640px; }
.contact-field { display: grid; gap: 7px; }
.contact-field span { color: #334155; font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.contact-field-hint { color: #64748b; font-size: 12px; line-height: 1.55; }
.contact-form input:hover, .contact-form textarea:hover { border-color: rgba(59,130,246,0.32); }
.contact-form input, .contact-form textarea { border: 1px solid #cbd5e1; border-radius: 12px; padding: 12px 13px; background: rgba(255,255,255,0.98); color: #0f172a; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); }
.contact-form input:focus, .contact-form textarea:focus { outline: none; border-color: rgba(37,99,235,0.56); box-shadow: 0 0 0 3px rgba(59,130,246,0.14); }
.contact-form textarea { min-height: 132px; resize: vertical; }
.contact-form input::placeholder, .contact-form textarea::placeholder { color: #94a3b8; }
.contact-form-actions { display: grid; gap: 8px; }
.contact-form button { border: 1px solid #2563eb; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-radius: 12px; padding: 12px 16px; cursor: pointer; width: 100%; font-weight: 700; box-shadow: 0 14px 26px rgba(37, 99, 235, 0.18); transition: transform 160ms ease, box-shadow 160ms ease, opacity 160ms ease; }
.contact-form button:hover { transform: translateY(-1px); box-shadow: 0 18px 30px rgba(37, 99, 235, 0.24); }
.contact-form button:disabled { cursor: default; opacity: 0.82; transform: none; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.14); }
.contact-submit-hint { color: #64748b; font-size: 12px; line-height: 1.6; }
.contact-form-note { margin: 0; color: #475569; font-size: 13px; line-height: 1.7; }
.contact-success-card { display: grid; gap: 10px; padding: 14px; border-radius: 16px; background: linear-gradient(180deg, rgba(236,253,245,0.96), rgba(240,253,250,0.96)); border: 1px solid rgba(110,231,183,0.55); }
.contact-success-card strong { color: #166534; font-size: 15px; }
.contact-success-card p { margin: 0; color: #14532d; line-height: 1.65; font-size: 13px; }
.contact-success-steps { display: flex; flex-wrap: wrap; gap: 8px; }
.contact-success-steps span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; color: #166534; background: rgba(220,252,231,0.92); border: 1px solid rgba(134,239,172,0.7); }
.contact-success { color: #15803d; margin: 0; }
.landing-footer { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 16px; display: grid; gap: 10px; background: rgba(15, 23, 42, 0.96); color: #f8fafc; }
.footer-success-bridge { display: grid; gap: 10px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.04); }
.footer-success-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(134,239,172,0.22); }
.footer-success-bridge strong { color: #f8fafc; font-size: 14px; line-height: 1.6; }
.footer-success-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }
.footer-success-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(148,163,184,0.22); }
.footer-success-bridge-current { color: #dcfce7; background: rgba(34,197,94,0.16); }
.footer-success-bridge-next { color: #dbeafe; background: rgba(255,255,255,0.06); }
.landing-footer .links { display: flex; gap: 8px; flex-wrap: wrap; }
.landing-footer button { border: 1px solid rgba(226, 232, 240, 0.24); background: rgba(255, 255, 255, 0.96); color: #0f172a; border-radius: 999px; padding: 6px 12px; cursor: pointer; font-weight: 600; }
.landing-footer small { color: #94a3b8; }
@media (max-width: 900px) { .landing-page { width: min(100%, calc(100% - 16px)); padding: 12px 0 24px; } .landing-header { padding: 12px; } .landing-hero { padding: 26px 18px; } .landing-hero h1 { font-size: 34px; max-width: none; } .landing-page.personal-portfolio .landing-hero h1 { font-size: 42px; } .about-shell { grid-template-columns: 1fr; } .pill-grid, .jobs-grid, .portfolio-grid { grid-template-columns: 1fr; } .contact-form-shell--business { grid-template-columns: 1fr; } }
</style>
