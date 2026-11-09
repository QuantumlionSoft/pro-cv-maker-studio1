<script setup>
defineProps({
  template: { type: String, required: true },
})
</script>

<template>
  <div class="template-thumb" :class="`template-thumb--${template}`" aria-hidden="true">
    <div class="thumb-paper">
      <div class="thumb-header">
        <span class="thumb-avatar"></span>
        <span class="thumb-identity">
          <i class="thumb-line thumb-line--name"></i>
          <i class="thumb-line thumb-line--role"></i>
        </span>
      </div>
      <div class="thumb-body">
        <div class="thumb-sidebar">
          <i class="thumb-line thumb-line--heading"></i>
          <i class="thumb-line"></i>
          <i class="thumb-line thumb-line--short"></i>
          <i class="thumb-line thumb-line--heading"></i>
          <i class="thumb-line"></i>
          <i class="thumb-line thumb-line--short"></i>
        </div>
        <div class="thumb-main">
          <i class="thumb-line thumb-line--heading"></i>
          <i class="thumb-line"></i>
          <i class="thumb-line"></i>
          <i class="thumb-line thumb-line--short"></i>
          <i class="thumb-line thumb-line--heading"></i>
          <i class="thumb-line"></i>
          <i class="thumb-line thumb-line--short"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.template-thumb {
  --thumb-accent: #4f46e5;
  --thumb-header: #172033;
  --thumb-sidebar: #f1f5f9;
  position: relative;
  width: 100%;
  height: 154px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 10px;
  background: #eef1f7;
}
.thumb-paper {
  width: 108px;
  height: 142px;
  margin-top: 20px;
  overflow: hidden;
  background: #fff;
  border-radius: 3px 3px 0 0;
  box-shadow: 0 8px 22px rgba(30, 41, 59, .15);
}
.thumb-header {
  height: 37px;
  padding: 10px 9px;
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--thumb-header);
  border-bottom: 2px solid var(--thumb-accent);
}
.thumb-avatar { width: 18px; height: 18px; flex: 0 0 auto; border-radius: 4px; background: rgba(255,255,255,.35); }
.thumb-identity { display: grid; gap: 5px; width: 58px; }
.thumb-line { display: block; width: 100%; height: 3px; border-radius: 3px; background: #dce2ea; }
.thumb-header .thumb-line { background: rgba(255,255,255,.8); }
.thumb-line--name { width: 82%; height: 5px; }
.thumb-line--role { width: 55%; background: var(--thumb-accent) !important; }
.thumb-line--short { width: 58%; }
.thumb-line--heading { width: 52%; height: 4px; margin: 5px 0 6px; background: var(--thumb-accent); }
.thumb-body { display: flex; height: 105px; }
.thumb-sidebar { width: 34%; height: 100%; padding: 5px 7px; background: var(--thumb-sidebar); }
.thumb-sidebar .thumb-line { background: #c9d2df; }
.thumb-sidebar .thumb-line--heading { background: var(--thumb-accent); }
.thumb-main { flex: 1; padding: 5px 7px; }
.thumb-main .thumb-line + .thumb-line { margin-top: 4px; }

.template-thumb--professional { --thumb-accent: #2563eb; }
.template-thumb--professional .thumb-body,
.template-thumb--minimal .thumb-body,
.template-thumb--academic .thumb-body,
.template-thumb--elegant .thumb-body,
.template-thumb--compact .thumb-body { display: block; padding: 5px 10px; }
.template-thumb--professional .thumb-sidebar,
.template-thumb--minimal .thumb-sidebar,
.template-thumb--academic .thumb-sidebar,
.template-thumb--elegant .thumb-sidebar,
.template-thumb--compact .thumb-sidebar { display: none; }
.template-thumb--professional .thumb-main { padding: 0; }
.template-thumb--minimal { --thumb-accent: #475569; --thumb-header: #fff; }
.template-thumb--minimal .thumb-header { border-bottom-width: 1px; border-bottom-color: #dce2ea; }
.template-thumb--minimal .thumb-header .thumb-line { background: #64748b; }
.template-thumb--minimal .thumb-header .thumb-line--role { background: #94a3b8 !important; }
.template-thumb--minimal .thumb-avatar { display: none; }
.template-thumb--minimal .thumb-main .thumb-line--heading { background: #64748b; }
.template-thumb--executive { --thumb-accent: #d7b56d; --thumb-header: #111c2e; --thumb-sidebar: #e8edf3; }
.template-thumb--executive .thumb-avatar { border-radius: 50%; }
.template-thumb--executive .thumb-sidebar { width: 38%; }
.template-thumb--corporate { --thumb-accent: #0f766e; --thumb-header: #fff; --thumb-sidebar: #eef8f6; }
.template-thumb--corporate .thumb-header { border-bottom-width: 4px; }
.template-thumb--corporate .thumb-header .thumb-line { background: #334155; }
.template-thumb--corporate .thumb-header .thumb-line--role { background: var(--thumb-accent) !important; }
.template-thumb--corporate .thumb-sidebar { width: 29%; }
.template-thumb--creative { --thumb-accent: #ec4899; --thumb-header: #6d28d9; --thumb-sidebar: #f5f3ff; }
.template-thumb--creative .thumb-header { margin: 5px 5px 0; height: 34px; border-radius: 5px; border: 0; }
.template-thumb--creative .thumb-sidebar { width: 38%; }
.template-thumb--developer { --thumb-accent: #22c55e; --thumb-header: #111827; --thumb-sidebar: #eef2f7; }
.template-thumb--developer .thumb-sidebar { width: 39%; }
.template-thumb--developer .thumb-line--heading { height: 3px; border-radius: 0; }
.template-thumb--academic { --thumb-accent: #7c2d12; --thumb-header: #fff; }
.template-thumb--academic .thumb-header { border-bottom: 1px solid #a8a29e; }
.template-thumb--academic .thumb-header .thumb-line { background: #44403c; }
.template-thumb--academic .thumb-avatar { display: none; }
.template-thumb--academic .thumb-main .thumb-line--heading { border-radius: 0; }
.template-thumb--elegant { --thumb-accent: #a16207; --thumb-header: #fff; }
.template-thumb--elegant .thumb-header { height: 43px; justify-content: center; border-bottom: 1px solid #d6d3d1; }
.template-thumb--elegant .thumb-avatar { border-radius: 50%; background: #e7e5e4; }
.template-thumb--elegant .thumb-header .thumb-line { background: #57534e; }
.template-thumb--elegant .thumb-main .thumb-line--heading { margin-inline: auto; }
.template-thumb--compact { --thumb-accent: #0369a1; --thumb-header: #e0f2fe; }
.template-thumb--compact .thumb-header { height: 30px; padding-block: 6px; }
.template-thumb--compact .thumb-header .thumb-line { background: #334155; }
.template-thumb--compact .thumb-avatar { width: 15px; height: 15px; }
.template-thumb--compact .thumb-main .thumb-line { margin-bottom: 2px; }
.template-thumb--compact .thumb-main .thumb-line--heading { margin-block: 3px; }
</style>
