<template>
  <div class="app">
    <Sidebar />
    <div class="content-wrapper">
      <header class="top-bar">
        <FilterBar />
        <div class="top-bar-actions">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import Sidebar from './components/Sidebar.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
    Sidebar
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
:root {
  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-8: 48px;

  /* Color: slate */
  --color-slate-50: #f8fafc;
  --color-slate-100: #f1f5f9;
  --color-slate-200: #e2e8f0;
  --color-slate-300: #cbd5e1;
  --color-slate-400: #94a3b8;
  --color-slate-500: #64748b;
  --color-slate-600: #475569;
  --color-slate-700: #334155;
  --color-slate-900: #0f172a;

  /* Color: primary */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;

  /* Color: status */
  --color-success-bg: #d1fae5;
  --color-success-text: #065f46;
  --color-warning-bg: #fed7aa;
  --color-warning-text: #92400e;
  --color-danger-bg: #fecaca;
  --color-danger-text: #991b1b;
  --color-info-bg: #dbeafe;
  --color-info-text: #1e40af;

  /* Color: extras */
  --color-purple: #8b5cf6;
  --color-amber: #f59e0b;

  /* Color: sidebar */
  --sidebar-bg: #ffffff;
  --sidebar-border: #e2e8f0;
  --sidebar-active-bg: #eff6ff;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;

  /* Shadow */
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 20px 50px rgba(0, 0, 0, 0.15);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--color-slate-50);
  color: #1e293b;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app {
  display: flex;
  min-height: 100vh;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  margin-left: 256px;
}

.top-bar {
  background: #ffffff;
  border-bottom: 1px solid var(--color-slate-200);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 90;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: 0 var(--space-5);
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-slate-900);
  margin-bottom: 0.375rem;
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--color-slate-500);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-5);
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-slate-200);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--color-slate-300);
  box-shadow: var(--shadow-md);
}

.stat-label {
  color: var(--color-slate-500);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.625rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-slate-900);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: #ea580c;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.danger .stat-value {
  color: #dc2626;
}

.stat-card.info .stat-value {
  color: var(--color-primary-600);
}

.card {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  border: 1px solid var(--color-slate-200);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--color-slate-200);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-slate-900);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-slate-50);
  border-top: 1px solid var(--color-slate-200);
  border-bottom: 1px solid var(--color-slate-200);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--color-slate-600);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--color-slate-100);
  color: var(--color-slate-700);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--color-slate-50);
}

.badge {
  display: inline-block;
  padding: 0.313rem var(--space-3);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: var(--color-success-bg);
  color: var(--color-success-text);
}

.badge.warning {
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.badge.danger {
  background: var(--color-danger-bg);
  color: var(--color-danger-text);
}

.badge.info {
  background: var(--color-info-bg);
  color: var(--color-info-text);
}

.badge.increasing {
  background: var(--color-success-bg);
  color: var(--color-success-text);
}

.badge.decreasing {
  background: var(--color-danger-bg);
  color: var(--color-danger-text);
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: var(--color-danger-bg);
  color: var(--color-danger-text);
}

.badge.medium {
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.badge.low {
  background: var(--color-info-bg);
  color: var(--color-info-text);
}

.loading {
  text-align: center;
  padding: var(--space-6);
  color: var(--color-slate-500);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid var(--color-danger-bg);
  color: var(--color-danger-text);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: 0.938rem;
}

.btn-primary {
  padding: 0.625rem 1.5rem;
  background: var(--color-primary-500);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.938rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-600);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
