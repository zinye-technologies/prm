<template>
  <div class="flex h-full overflow-hidden">
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Loading state -->
      <div v-if="partner.loading" class="flex h-full items-center justify-center">
        <LoadingIndicator />
      </div>

      <!-- Error state -->
      <div v-else-if="partner.error" class="flex h-full items-center justify-center">
        <div class="text-center">
          <LucideAlertCircle class="mx-auto h-12 w-12 text-red-500" />
          <h3 class="mt-2 text-lg font-medium text-gray-900">Failed to load partner</h3>
          <p class="mt-1 text-sm text-gray-500">{{ partner.error }}</p>
          <Button class="mt-4" @click="partner.reload()">Try Again</Button>
        </div>
      </div>

      <!-- Partner Details -->
      <div v-else-if="partner.data" class="flex flex-1 flex-col overflow-hidden">
        <!-- Header -->
        <div class="border-b border-gray-200 px-5 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <Button variant="ghost" @click="router.back()">
                <LucideArrowLeft class="h-4 w-4" />
              </Button>
              <Avatar
                :label="partner.data.partner.partner_name"
                :image="partner.data.partner.image"
                size="xl"
              />
              <div>
                <div class="flex items-center gap-2">
                  <h1 class="text-2xl font-semibold text-gray-900">
                    {{ partner.data.partner.partner_name }}
                  </h1>
                  <Badge
                    :label="partner.data.partner.partner_tier"
                    :theme="getTierTheme(partner.data.partner.partner_tier)"
                    size="lg"
                  />
                  <Badge
                    :label="partner.data.partner.status"
                    :theme="getStatusTheme(partner.data.partner.status)"
                    size="lg"
                  />
                </div>
                <div class="flex items-center gap-4 text-sm text-gray-600">
                  <span>{{ partner.data.partner.partner_type }}</span>
                  <span v-if="partner.data.partner.territory">{{ partner.data.partner.territory }}</span>
                  <span v-if="partner.data.partner.partner_code">Code: {{ partner.data.partner.partner_code }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <Button variant="white" @click="editPartner">
                <template #prefix><LucideEdit class="h-4 w-4" /></template>
                Edit
              </Button>
              <Dropdown :options="partnerActions">
                <Button variant="white">
                  <LucideMoreHorizontal class="h-4 w-4" />
                </Button>
              </Dropdown>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200 px-5">
          <nav class="-mb-px flex space-x-8">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="[
                'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium',
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              ]"
            >
              <component :is="tab.icon" class="mr-2 h-4 w-4 inline" />
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 overflow-auto p-5">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <!-- Performance Metrics -->
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <div class="rounded-lg border border-gray-200 p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <LucideTrendingUp class="h-8 w-8 text-green-600" />
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Partner Score</p>
                    <p class="text-2xl font-semibold text-gray-900">
                      {{ partner.data.partner.partner_score || 0 }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-gray-200 p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <LucideTarget class="h-8 w-8 text-blue-600" />
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Total Deals</p>
                    <p class="text-2xl font-semibold text-gray-900">
                      {{ partner.data.partner.total_deals_closed || 0 }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-gray-200 p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <LucideDollarSign class="h-8 w-8 text-yellow-600" />
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Total Revenue</p>
                    <p class="text-2xl font-semibold text-gray-900">
                      {{ formatCurrency(partner.data.partner.total_revenue_generated) }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-gray-200 p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <LucidePercent class="h-8 w-8 text-purple-600" />
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Conversion Rate</p>
                    <p class="text-2xl font-semibold text-gray-900">
                      {{ (partner.data.partner.lead_conversion_rate || 0).toFixed(1) }}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Partner Information -->
            <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <!-- Basic Information -->
              <div class="rounded-lg border border-gray-200 p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
                <dl class="space-y-3">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Primary Contact</dt>
                    <dd class="text-sm text-gray-900">{{ partner.data.partner.primary_contact || 'N/A' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Email</dt>
                    <dd class="text-sm text-gray-900">{{ partner.data.partner.email || 'N/A' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Phone</dt>
                    <dd class="text-sm text-gray-900">{{ partner.data.partner.phone || 'N/A' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Website</dt>
                    <dd class="text-sm text-gray-900">
                      <a v-if="partner.data.partner.website" :href="partner.data.partner.website" target="_blank" class="text-blue-600 hover:text-blue-500">
                        {{ partner.data.partner.website }}
                      </a>
                      <span v-else>N/A</span>
                    </dd>
                  </div>
                </dl>
              </div>

              <!-- Business Details -->
              <div class="rounded-lg border border-gray-200 p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Business Details</h3>
                <dl class="space-y-3">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Industry</dt>
                    <dd class="text-sm text-gray-900">{{ partner.data.partner.industry || 'N/A' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Company Size</dt>
                    <dd class="text-sm text-gray-900">{{ partner.data.partner.company_size || 'N/A' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Annual Revenue</dt>
                    <dd class="text-sm text-gray-900">
                      {{ partner.data.partner.annual_revenue ? formatCurrency(partner.data.partner.annual_revenue) : 'N/A' }}
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Years in Business</dt>
                    <dd class="text-sm text-gray-900">{{ partner.data.partner.years_in_business || 'N/A' }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="rounded-lg border border-gray-200 p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
              <div class="space-y-4">
                <div v-if="partner.data.recent_deals?.length">
                  <h4 class="text-sm font-medium text-gray-700 mb-2">Recent Deals</h4>
                  <div class="space-y-2">
                    <div
                      v-for="deal in partner.data.recent_deals.slice(0, 3)"
                      :key="deal.name"
                      class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ deal.organization }}</p>
                        <p class="text-xs text-gray-500">{{ formatDate(deal.modified) }}</p>
                      </div>
                      <div class="text-right">
                        <p class="text-sm font-medium text-gray-900">{{ formatCurrency(deal.deal_value) }}</p>
                        <Badge :label="deal.status" :theme="getDealStatusTheme(deal.status)" size="sm" />
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else>
                  <p class="text-sm text-gray-500">No recent activity</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Performance Tab -->
          <div v-else-if="activeTab === 'performance'">
            <PartnerPerformance :partner-id="partnerId" :performance-data="partner.data.performance" />
          </div>

          <!-- Deals Tab -->
          <div v-else-if="activeTab === 'deals'">
            <PartnerDeals :partner-id="partnerId" :deals="partner.data.recent_deals" />
          </div>

          <!-- Leads Tab -->
          <div v-else-if="activeTab === 'leads'">
            <PartnerLeads :partner-id="partnerId" :leads="partner.data.recent_leads" />
          </div>

          <!-- Training Tab -->
          <div v-else-if="activeTab === 'training'">
            <PartnerTraining :partner="partner.data.partner" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import {
  Avatar,
  Badge,
  Button,
  Dropdown,
  LoadingIndicator
} from 'frappe-ui'

// Components
import PartnerPerformance from '@/components/Partners/PartnerPerformance.vue'
import PartnerDeals from '@/components/Partners/PartnerDeals.vue'
import PartnerLeads from '@/components/Partners/PartnerLeads.vue'
import PartnerTraining from '@/components/Partners/PartnerTraining.vue'

// Icons
import {
  LucideArrowLeft,
  LucideEdit,
  LucideMoreHorizontal,
  LucideAlertCircle,
  LucideTrendingUp,
  LucideTarget,
  LucideDollarSign,
  LucidePercent,
  LucideUser,
  LucideBarChart,
  LucideHandshake,
  LucideUsers,
  LucideGraduationCap
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// Props
const partnerId = computed(() => route.params.partnerId)

// State
const activeTab = ref('overview')

// Tabs configuration
const tabs = [
  { key: 'overview', label: 'Overview', icon: LucideUser },
  { key: 'performance', label: 'Performance', icon: LucideBarChart },
  { key: 'deals', label: 'Deals', icon: LucideHandshake },
  { key: 'leads', label: 'Leads', icon: LucideUsers },
  { key: 'training', label: 'Training', icon: LucideGraduationCap }
]

// Resources
const partner = createResource({
  url: 'crm.api.partner.get_partner_details',
  params: computed(() => ({
    partner_name: partnerId.value
  })),
  auto: true
})

// Partner actions dropdown
const partnerActions = [
  {
    label: 'Send Email',
    icon: 'mail',
    onClick: () => sendEmail()
  },
  {
    label: 'Assign Lead',
    icon: 'user-plus',
    onClick: () => assignLead()
  },
  {
    label: 'Create Deal',
    icon: 'plus-circle',
    onClick: () => createDeal()
  },
  {
    label: 'View Portal',
    icon: 'external-link',
    onClick: () => viewPortal()
  }
]

// Methods
const formatCurrency = (amount) => {
  if (!amount) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact'
  }).format(amount)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getTierTheme = (tier) => {
  const themes = {
    'Diamond': 'purple',
    'Platinum': 'blue',
    'Gold': 'yellow',
    'Silver': 'gray',
    'Bronze': 'orange'
  }
  return themes[tier] || 'gray'
}

const getStatusTheme = (status) => {
  const themes = {
    'Active': 'green',
    'Pending Approval': 'yellow',
    'Inactive': 'gray',
    'Suspended': 'red',
    'Terminated': 'red'
  }
  return themes[status] || 'gray'
}

const getDealStatusTheme = (status) => {
  const themes = {
    'Won': 'green',
    'Lost': 'red',
    'Open': 'blue',
    'Qualified': 'yellow'
  }
  return themes[status] || 'gray'
}

const editPartner = () => {
  console.log('Edit partner')
}

const sendEmail = () => {
  console.log('Send email to partner')
}

const assignLead = () => {
  console.log('Assign lead to partner')
}

const createDeal = () => {
  console.log('Create deal for partner')
}

const viewPortal = () => {
  console.log('View partner portal')
}
</script>