<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <h1>{{ t('nav.companyName') }}</h1>
      <span class="subtitle">{{ t('nav.subtitle') }}</span>
    </div>

    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <LayoutDashboard class="nav-icon" :size="18" />
        <span>{{ t('nav.overview') }}</span>
      </router-link>
      <router-link to="/inventory" class="nav-item" :class="{ active: $route.path === '/inventory' }">
        <Boxes class="nav-icon" :size="18" />
        <span>{{ t('nav.inventory') }}</span>
      </router-link>
      <router-link to="/orders" class="nav-item" :class="{ active: $route.path === '/orders' }">
        <ShoppingCart class="nav-icon" :size="18" />
        <span>{{ t('nav.orders') }}</span>
      </router-link>
      <router-link to="/spending" class="nav-item" :class="{ active: $route.path === '/spending' }">
        <Wallet class="nav-icon" :size="18" />
        <span>{{ t('nav.finance') }}</span>
      </router-link>
      <router-link to="/demand" class="nav-item" :class="{ active: $route.path === '/demand' }">
        <TrendingUp class="nav-icon" :size="18" />
        <span>{{ t('nav.demandForecast') }}</span>
      </router-link>
      <router-link to="/restocking" class="nav-item" :class="{ active: $route.path === '/restocking' }">
        <RefreshCw class="nav-icon" :size="18" />
        <span>{{ t('nav.restocking') }}</span>
      </router-link>
      <router-link to="/reports" class="nav-item" :class="{ active: $route.path === '/reports' }">
        <BarChart class="nav-icon" :size="18" />
        <span>{{ t('nav.reports') }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script>
import {
  LayoutDashboard,
  Boxes,
  ShoppingCart,
  Wallet,
  TrendingUp,
  RefreshCw,
  BarChart
} from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Sidebar',
  components: {
    LayoutDashboard,
    Boxes,
    ShoppingCart,
    Wallet,
    TrendingUp,
    RefreshCw,
    BarChart
  },
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 256px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 50;
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-5) var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--sidebar-border);
}

.sidebar-brand h1 {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-slate-900);
  letter-spacing: -0.025em;
}

.sidebar-brand .subtitle {
  font-size: 0.813rem;
  color: var(--color-slate-500);
  font-weight: 400;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0.625rem var(--space-4);
  color: var(--color-slate-500);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.938rem;
  border-radius: var(--radius-sm);
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-item:hover {
  color: var(--color-slate-900);
  background: var(--color-slate-100);
}

.nav-item.active {
  color: var(--color-primary-600);
  background: var(--sidebar-active-bg);
  border-left-color: var(--color-primary-600);
}
</style>
