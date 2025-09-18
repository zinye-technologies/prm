<template>
  <div class="space-y-6">
    <!-- Performance Summary -->
    <div class="rounded-lg border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Performance Summary</h3>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-600">
            {{ performanceData?.current_quarter?.deals || 0 }}
          </div>
          <div class="text-sm text-gray-500">Deals This Quarter</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">
            {{ formatCurrency(performanceData?.current_quarter?.revenue) }}
          </div>
          <div class="text-sm text-gray-500">Revenue This Quarter</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-purple-600">
            {{ performanceData?.summary_period || 'Last 12 Months' }}
          </div>
          <div class="text-sm text-gray-500">Analysis Period</div>
        </div>
      </div>
    </div>

    <!-- Monthly Trends Charts -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Deals Trend -->
      <div class="rounded-lg border border-gray-200 p-6">
        <h4 class="text-lg font-medium text-gray-900 mb-4">Monthly Deals</h4>
        <div v-if="dealsChartData.length" class="h-64">
          <canvas ref="dealsChart"></canvas>
        </div>
        <div v-else class="flex h-64 items-center justify-center text-gray-500">
          No deals data available
        </div>
      </div>

      <!-- Revenue Trend -->
      <div class="rounded-lg border border-gray-200 p-6">
        <h4 class="text-lg font-medium text-gray-900 mb-4">Monthly Revenue</h4>
        <div v-if="revenueChartData.length" class="h-64">
          <canvas ref="revenueChart"></canvas>
        </div>
        <div v-else class="flex h-64 items-center justify-center text-gray-500">
          No revenue data available
        </div>
      </div>
    </div>

    <!-- Lead Conversion -->
    <div class="rounded-lg border border-gray-200 p-6">
      <h4 class="text-lg font-medium text-gray-900 mb-4">Lead Conversion Trends</h4>
      <div v-if="leadsChartData.length" class="h-64">
        <canvas ref="leadsChart"></canvas>
      </div>
      <div v-else class="flex h-64 items-center justify-center text-gray-500">
        No leads data available
      </div>
    </div>

    <!-- Performance Metrics Table -->
    <div class="rounded-lg border border-gray-200 p-6">
      <h4 class="text-lg font-medium text-gray-900 mb-4">Monthly Breakdown</h4>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Month
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Deals Closed
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Revenue
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Leads
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Conversion Rate
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="month in monthlyBreakdown" :key="month.month">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ formatMonth(month.month) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ month.deals_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatCurrency(month.revenue) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ month.total_leads || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ month.total_leads ? ((month.converted_leads / month.total_leads) * 100).toFixed(1) : 0 }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

// Props
const props = defineProps({
  partnerId: {
    type: String,
    required: true
  },
  performanceData: {
    type: Object,
    default: () => ({})
  }
})

// Chart refs
const dealsChart = ref(null)
const revenueChart = ref(null)
const leadsChart = ref(null)

// Chart instances
let dealsChartInstance = null
let revenueChartInstance = null
let leadsChartInstance = null

// Computed data for charts
const dealsChartData = computed(() => {
  return props.performanceData?.monthly_trends?.deals || []
})

const revenueChartData = computed(() => {
  return props.performanceData?.monthly_trends?.deals || []
})

const leadsChartData = computed(() => {
  return props.performanceData?.monthly_trends?.leads || []
})

const monthlyBreakdown = computed(() => {
  const deals = props.performanceData?.monthly_trends?.deals || []
  const leads = props.performanceData?.monthly_trends?.leads || []

  // Merge deals and leads data by month
  const monthsMap = new Map()

  deals.forEach(deal => {
    monthsMap.set(deal.month, {
      month: deal.month,
      deals_count: deal.deals_count,
      revenue: deal.revenue,
      total_leads: 0,
      converted_leads: 0
    })
  })

  leads.forEach(lead => {
    const existing = monthsMap.get(lead.month) || {
      month: lead.month,
      deals_count: 0,
      revenue: 0
    }
    existing.total_leads = lead.total_leads
    existing.converted_leads = lead.converted_leads
    monthsMap.set(lead.month, existing)
  })

  return Array.from(monthsMap.values()).sort((a, b) => a.month.localeCompare(b.month))
})

// Methods
const formatCurrency = (amount) => {
  if (!amount) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact'
  }).format(amount)
}

const formatMonth = (monthStr) => {
  if (!monthStr) return ''
  const [year, month] = monthStr.split('-')
  const date = new Date(parseInt(year), parseInt(month) - 1)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
}

const createDealsChart = () => {
  if (!dealsChart.value || !dealsChartData.value.length) return

  const ctx = dealsChart.value.getContext('2d')

  dealsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dealsChartData.value.map(d => formatMonth(d.month)),
      datasets: [{
        label: 'Deals Closed',
        data: dealsChartData.value.map(d => d.deals_count),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  })
}

const createRevenueChart = () => {
  if (!revenueChart.value || !revenueChartData.value.length) return

  const ctx = revenueChart.value.getContext('2d')

  revenueChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: revenueChartData.value.map(d => formatMonth(d.month)),
      datasets: [{
        label: 'Revenue',
        data: revenueChartData.value.map(d => d.revenue),
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return formatCurrency(value)
            }
          }
        }
      }
    }
  })
}

const createLeadsChart = () => {
  if (!leadsChart.value || !leadsChartData.value.length) return

  const ctx = leadsChart.value.getContext('2d')

  leadsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: leadsChartData.value.map(d => formatMonth(d.month)),
      datasets: [
        {
          label: 'Total Leads',
          data: leadsChartData.value.map(d => d.total_leads),
          borderColor: 'rgb(168, 85, 247)',
          backgroundColor: 'rgba(168, 85, 247, 0.1)',
          fill: false,
          tension: 0.4
        },
        {
          label: 'Converted Leads',
          data: leadsChartData.value.map(d => d.converted_leads),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: false,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  })
}

const initializeCharts = async () => {
  await nextTick()

  // Destroy existing charts
  if (dealsChartInstance) {
    dealsChartInstance.destroy()
    dealsChartInstance = null
  }
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
    revenueChartInstance = null
  }
  if (leadsChartInstance) {
    leadsChartInstance.destroy()
    leadsChartInstance = null
  }

  // Create new charts
  createDealsChart()
  createRevenueChart()
  createLeadsChart()
}

onMounted(() => {
  initializeCharts()
})

onUnmounted(() => {
  if (dealsChartInstance) {
    dealsChartInstance.destroy()
  }
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
  }
  if (leadsChartInstance) {
    leadsChartInstance.destroy()
  }
})

// Watch for data changes and reinitialize charts
watch(() => props.performanceData, () => {
  initializeCharts()
}, { deep: true })
</script>