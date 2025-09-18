<template>
  <div class="flex h-full overflow-hidden">
    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-5 pb-3 pt-3">
        <div class="flex items-center gap-2">
          <h1 class="text-xl font-semibold text-gray-900">Partners</h1>
          <Badge
            v-if="partners.data?.length"
            :label="partners.data.length.toString()"
            theme="gray"
            size="md"
          />
        </div>
        <div class="flex gap-2">
          <Button
            label="Add Partner"
            @click="showAddPartnerModal = true"
            :loading="partners.loading"
          >
            <template #prefix><LucidePlus class="h-4 w-4" /></template>
          </Button>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex items-center gap-2 px-5 pb-3">
        <div class="flex gap-2">
          <Autocomplete
            :options="partnerTypeOptions"
            v-model="filters.partner_type"
            placeholder="Partner Type"
            @change="updateFilter"
          />
          <Autocomplete
            :options="partnerTierOptions"
            v-model="filters.partner_tier"
            placeholder="Partner Tier"
            @change="updateFilter"
          />
          <Autocomplete
            :options="statusOptions"
            v-model="filters.status"
            placeholder="Status"
            @change="updateFilter"
          />
          <Autocomplete
            :options="territoryOptions"
            v-model="filters.territory"
            placeholder="Territory"
            @change="updateFilter"
          />
        </div>
        <div class="ml-auto">
          <TextInput
            v-model="searchQuery"
            placeholder="Search partners..."
            @input="searchPartners"
          >
            <template #prefix><LucideSearch class="h-4 w-4" /></template>
          </TextInput>
        </div>
      </div>

      <!-- Partners List -->
      <div class="flex-1 overflow-auto px-5">
        <div v-if="partners.loading" class="flex justify-center py-8">
          <LoadingIndicator />
        </div>

        <div v-else-if="!partners.data?.length" class="flex flex-col items-center justify-center py-20">
          <div class="text-center">
            <LucideUsers class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No partners found</h3>
            <p class="mt-1 text-sm text-gray-500">
              {{ searchQuery ? 'Try adjusting your search or filters' : 'Get started by adding your first partner' }}
            </p>
            <div class="mt-6" v-if="!searchQuery">
              <Button @click="showAddPartnerModal = true">
                Add Partner
              </Button>
            </div>
          </div>
        </div>

        <div v-else class="space-y-3 pb-5">
          <div
            v-for="partner in partners.data"
            :key="partner.name"
            class="flex items-center justify-between rounded-lg border border-gray-200 p-4 hover:bg-gray-50 cursor-pointer"
            @click="router.push({ name: 'Partner', params: { partnerId: partner.name } })"
          >
            <!-- Partner Info -->
            <div class="flex items-center gap-4">
              <Avatar
                :label="partner.partner_name"
                :image="partner.image"
                size="lg"
              />
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-900">{{ partner.partner_name }}</h3>
                  <Badge
                    :label="partner.partner_tier"
                    :theme="getTierTheme(partner.partner_tier)"
                    size="sm"
                  />
                </div>
                <div class="flex items-center gap-4 text-sm text-gray-600">
                  <span>{{ partner.partner_type }}</span>
                  <span v-if="partner.territory">{{ partner.territory }}</span>
                  <span v-if="partner.email">{{ partner.email }}</span>
                </div>
              </div>
            </div>

            <!-- Partner Metrics -->
            <div class="flex items-center gap-8">
              <!-- Partner Score -->
              <div class="text-center">
                <div class="text-lg font-semibold text-gray-900">
                  {{ partner.partner_score || 0 }}
                </div>
                <div class="text-xs text-gray-500">Score</div>
              </div>

              <!-- Deals Closed -->
              <div class="text-center">
                <div class="text-lg font-semibold text-gray-900">
                  {{ partner.total_deals_closed || 0 }}
                </div>
                <div class="text-xs text-gray-500">Deals</div>
              </div>

              <!-- Revenue -->
              <div class="text-center">
                <div class="text-lg font-semibold text-gray-900">
                  {{ formatCurrency(partner.total_revenue_generated) }}
                </div>
                <div class="text-xs text-gray-500">Revenue</div>
              </div>

              <!-- Status -->
              <Badge
                :label="partner.status"
                :theme="getStatusTheme(partner.status)"
                size="md"
              />

              <!-- Actions -->
              <Dropdown :options="getPartnerActions(partner)">
                <template #default="{ open }">
                  <Button variant="ghost" :class="{ 'bg-gray-100': open }">
                    <LucideMoreHorizontal class="h-4 w-4" />
                  </Button>
                </template>
              </Dropdown>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Partner Modal -->
    <PartnerModal
      v-if="showAddPartnerModal"
      @close="showAddPartnerModal = false"
      @success="onPartnerAdded"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call, createResource } from 'frappe-ui'
import { debounce } from 'lodash'
import {
  Avatar,
  Badge,
  Button,
  TextInput,
  Autocomplete,
  Dropdown,
  LoadingIndicator
} from 'frappe-ui'
import PartnerModal from '@/components/Partners/PartnerModal.vue'

// Icons
import {
  LucidePlus,
  LucideSearch,
  LucideUsers,
  LucideMoreHorizontal
} from 'lucide-vue-next'

const router = useRouter()

// State
const showAddPartnerModal = ref(false)
const searchQuery = ref('')
const filters = reactive({
  partner_type: '',
  partner_tier: '',
  status: '',
  territory: ''
})

// Resources
const partners = createResource({
  url: 'prm.api.partner.get_partner_list',
  params: computed(() => ({
    filters: Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value)
    ),
    search_term: searchQuery.value || undefined,
    limit: 50
  })),
  auto: true
})

// Options for filters
const partnerTypeOptions = [
  { label: 'Reseller', value: 'Reseller' },
  { label: 'Distributor', value: 'Distributor' },
  { label: 'Affiliate', value: 'Affiliate' },
  { label: 'System Integrator', value: 'System Integrator' },
  { label: 'Consultant', value: 'Consultant' },
  { label: 'Technology Partner', value: 'Technology Partner' },
  { label: 'Channel Partner', value: 'Channel Partner' }
]

const partnerTierOptions = [
  { label: 'Bronze', value: 'Bronze' },
  { label: 'Silver', value: 'Silver' },
  { label: 'Gold', value: 'Gold' },
  { label: 'Platinum', value: 'Platinum' },
  { label: 'Diamond', value: 'Diamond' }
]

const statusOptions = [
  { label: 'Active', value: 'Active' },
  { label: 'Pending Approval', value: 'Pending Approval' },
  { label: 'Inactive', value: 'Inactive' },
  { label: 'Suspended', value: 'Suspended' }
]

const territoryOptions = ref([])

// Methods
const updateFilter = () => {
  partners.reload()
}

const searchPartners = debounce(() => {
  partners.reload()
}, 300)

const formatCurrency = (amount) => {
  if (!amount) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact'
  }).format(amount)
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

const getPartnerActions = (partner) => {
  return [
    {
      label: 'View Details',
      icon: 'eye',
      onClick: () => router.push({ name: 'Partner', params: { partnerId: partner.name } })
    },
    {
      label: 'Edit Partner',
      icon: 'edit',
      onClick: () => editPartner(partner)
    },
    {
      label: 'Assign Lead',
      icon: 'user-plus',
      onClick: () => assignLead(partner)
    },
    {
      label: 'View Performance',
      icon: 'trending-up',
      onClick: () => viewPerformance(partner)
    }
  ]
}

const editPartner = (partner) => {
  // Implementation for editing partner
  console.log('Edit partner:', partner)
}

const assignLead = (partner) => {
  // Implementation for assigning lead
  console.log('Assign lead to partner:', partner)
}

const viewPerformance = (partner) => {
  // Implementation for viewing performance
  console.log('View performance for partner:', partner)
}

const onPartnerAdded = () => {
  showAddPartnerModal.value = false
  partners.reload()
}

// Load territories
const loadTerritories = async () => {
  try {
    const territories = await call('frappe.client.get_list', {
      doctype: 'Territory',
      fields: ['name'],
      limit_page_length: 100
    })

    territoryOptions.value = territories.map(t => ({
      label: t.name,
      value: t.name
    }))
  } catch (error) {
    console.error('Failed to load territories:', error)
  }
}

onMounted(() => {
  loadTerritories()
})
</script>