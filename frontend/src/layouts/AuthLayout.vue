<template>
  <div class="auth-shell">
    <header class="auth-header">
      <RouterLink :to="{ name: 'landing' }" class="brand-link" aria-label="Pro CV Maker Studio home">
        <span class="brand-mark" aria-hidden="true"><i class="bi bi-file-earmark-richtext"></i></span>
        <span class="fw-semibold">Pro CV Maker Studio</span>
      </RouterLink>
    </header>
    <main class="auth-main">
      <RouterView />
    </main>
  </div>
</template>
