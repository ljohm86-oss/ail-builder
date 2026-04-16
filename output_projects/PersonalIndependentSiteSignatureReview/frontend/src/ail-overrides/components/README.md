# AIL Component Hooks

Files in this folder are unmanaged and safe to edit.

Hook naming:

- `page.home.before.vue`
- `page.home.after.vue`
- `page.home.before.html`
- `page.contact.after.vue`

Rules:

- filename without extension becomes the hook name
- Vue components (`.vue`) render as dynamic components
- HTML partials (`.html`) render as raw named partials
- rebuilds keep this folder intact
- long-term structure/content changes still belong in `.ail/source.ail`
