<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card budget-card">
      <label class="budget-label" for="budget-slider">{{ t('restocking.budgetLabel') }}</label>
      <div class="budget-control">
        <input
          id="budget-slider"
          v-model.number="budget"
          type="range"
          min="0"
          max="75000"
          step="500"
          class="budget-slider"
        />
        <span class="budget-value">{{ formatMoney(budget) }}</span>
      </div>
    </div>

    <div v-if="successMessage" class="success-banner">
      {{ successMessage }}
      <router-link to="/orders">{{ t('restocking.ordersLink') }}</router-link>
    </div>
    <div v-if="submitError" class="error">{{ submitError }}</div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.summary.budget') }}</div>
          <div class="stat-value">{{ formatMoney(recommendations.budget) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.summary.itemsRecommended') }}</div>
          <div class="stat-value">{{ recommendations.items_recommended }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.summary.totalEstimatedCost') }}</div>
          <div class="stat-value">{{ formatMoney(recommendations.total_estimated_cost) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.summary.remainingBudget') }}</div>
          <div class="stat-value">{{ formatMoney(recommendations.remaining_budget) }}</div>
        </div>
      </div>

      <div v-if="recommendations.items_recommended === 0" class="card empty-state">
        {{ t('restocking.emptyState') }}
      </div>

      <template v-else>
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('restocking.recommendedItems') }}</h3>
            <button
              class="btn-primary"
              :disabled="recommendations.items_recommended === 0 || submitting"
              @click="handlePlaceOrder"
            >
              {{ t('restocking.placeOrder') }}
            </button>
          </div>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>{{ t('restocking.table.sku') }}</th>
                  <th>{{ t('restocking.table.itemName') }}</th>
                  <th>{{ t('restocking.table.warehouse') }}</th>
                  <th>{{ t('restocking.table.category') }}</th>
                  <th>{{ t('restocking.table.stockReorderPoint') }}</th>
                  <th>{{ t('restocking.table.forecastedDemand') }}</th>
                  <th>{{ t('restocking.table.gap') }}</th>
                  <th>{{ t('restocking.table.recommendedQty') }}</th>
                  <th>{{ t('restocking.table.unitCost') }}</th>
                  <th>{{ t('restocking.table.estimatedCost') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in recommendations.recommended_items" :key="item.sku">
                  <td><strong>{{ item.sku }}</strong></td>
                  <td>{{ translateProductName(item.name) }}</td>
                  <td>{{ translateWarehouse(item.warehouse) }}</td>
                  <td>{{ translateCategory(item.category) }}</td>
                  <td>{{ item.quantity_on_hand }} / {{ item.reorder_point }}</td>
                  <td>{{ item.forecasted_demand }}</td>
                  <td>{{ item.gap }}</td>
                  <td>{{ item.recommended_quantity }}</td>
                  <td>{{ formatMoney(item.unit_cost) }}</td>
                  <td><strong>{{ formatMoney(item.estimated_cost) }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()

    const budget = ref(10000)
    const loading = ref(true)
    const error = ref(null)
    const recommendations = ref({
      budget: 0,
      recommended_items: [],
      total_estimated_cost: 0,
      remaining_budget: 0,
      items_considered: 0,
      items_recommended: 0
    })

    const submitting = ref(false)
    const successMessage = ref(null)
    const submitError = ref(null)

    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    const formatMoney = (amount) => {
      return formatCurrency(amount || 0, currentCurrency.value)
    }

    const translateCategory = (category) => {
      const categoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }
      return categoryMap[category] || category
    }

    const loadRecommendations = async () => {
      successMessage.value = null
      submitError.value = null
      try {
        loading.value = true
        error.value = null
        const filters = getCurrentFilters()
        recommendations.value = await api.getRestockingRecommendations(budget.value, filters)
      } catch (err) {
        error.value = 'Failed to load restocking recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const handlePlaceOrder = async () => {
      submitting.value = true
      successMessage.value = null
      submitError.value = null
      try {
        const filters = getCurrentFilters()
        const order = await api.submitRestockingOrder(budget.value, filters)

        // Refresh recommendations quietly (do not clear the banner we're about to show)
        const refreshed = await api.getRestockingRecommendations(budget.value, getCurrentFilters())
        recommendations.value = refreshed

        successMessage.value = t('restocking.successMessage', {
          orderNumber: order.order_number,
          leadTime: order.lead_time_days
        })
      } catch (err) {
        submitError.value = err.response?.data?.detail || t('restocking.errorMessage')
      } finally {
        submitting.value = false
      }
    }

    watch([selectedLocation, selectedCategory, budget], () => {
      loadRecommendations()
    })

    onMounted(loadRecommendations)

    return {
      t,
      budget,
      loading,
      error,
      recommendations,
      submitting,
      successMessage,
      submitError,
      formatMoney,
      translateProductName,
      translateWarehouse,
      translateCategory,
      handlePlaceOrder
    }
  }
}
</script>

<style scoped>
.budget-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.budget-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.budget-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  border: 1px solid #cbd5e1;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  transition: background 0.2s;
}

.budget-slider::-webkit-slider-thumb:hover {
  background: #2563eb;
}

.budget-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.budget-slider::-moz-range-thumb:hover {
  background: #2563eb;
}

.budget-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  min-width: 100px;
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

.success-banner {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.success-banner a {
  color: #059669;
  font-weight: 600;
  text-decoration: underline;
}
</style>
