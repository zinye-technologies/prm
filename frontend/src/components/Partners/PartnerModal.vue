<template>
  <Dialog
    :options="{
      title: isEditing ? 'Edit Partner' : 'Add Partner',
      size: '4xl'
    }"
    v-model="show"
    @close="$emit('close')"
  >
    <template #body>
      <div class="space-y-6">
        <!-- Basic Information -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormControl
              type="text"
              label="Partner Name"
              v-model="form.partner_name"
              :error="errors.partner_name"
              required
            />
            <FormControl
              type="text"
              label="Partner Code"
              v-model="form.partner_code"
              :error="errors.partner_code"
              placeholder="Auto-generated if empty"
            />
            <FormControl
              type="select"
              label="Partner Type"
              v-model="form.partner_type"
              :options="partnerTypeOptions"
              :error="errors.partner_type"
              required
            />
            <FormControl
              type="select"
              label="Partner Tier"
              v-model="form.partner_tier"
              :options="partnerTierOptions"
              :error="errors.partner_tier"
              required
            />
          </div>
        </div>

        <!-- Contact Information -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormControl
              type="text"
              label="Primary Contact"
              v-model="form.primary_contact"
              :error="errors.primary_contact"
            />
            <FormControl
              type="email"
              label="Email"
              v-model="form.email"
              :error="errors.email"
              required
            />
            <FormControl
              type="text"
              label="Phone"
              v-model="form.phone"
              :error="errors.phone"
            />
            <FormControl
              type="url"
              label="Website"
              v-model="form.website"
              :error="errors.website"
            />
          </div>
        </div>

        <!-- Address -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Address</h3>
          <div class="space-y-4">
            <FormControl
              type="text"
              label="Address Line 1"
              v-model="form.address_line_1"
              :error="errors.address_line_1"
            />
            <FormControl
              type="text"
              label="Address Line 2"
              v-model="form.address_line_2"
              :error="errors.address_line_2"
            />
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <FormControl
                type="text"
                label="City"
                v-model="form.city"
                :error="errors.city"
              />
              <FormControl
                type="text"
                label="State/Province"
                v-model="form.state"
                :error="errors.state"
              />
              <FormControl
                type="text"
                label="Postal Code"
                v-model="form.postal_code"
                :error="errors.postal_code"
              />
            </div>
            <FormControl
              type="autocomplete"
              label="Country"
              v-model="form.country"
              :options="countryOptions"
              :error="errors.country"
            />
          </div>
        </div>

        <!-- Business Details -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Business Details</h3>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormControl
              type="autocomplete"
              label="Industry"
              v-model="form.industry"
              :options="industryOptions"
              :error="errors.industry"
            />
            <FormControl
              type="select"
              label="Company Size"
              v-model="form.company_size"
              :options="companySizeOptions"
              :error="errors.company_size"
            />
            <FormControl
              type="currency"
              label="Annual Revenue"
              v-model="form.annual_revenue"
              :error="errors.annual_revenue"
            />
            <FormControl
              type="number"
              label="Years in Business"
              v-model="form.years_in_business"
              :error="errors.years_in_business"
            />
            <FormControl
              type="autocomplete"
              label="Territory"
              v-model="form.territory"
              :options="territoryOptions"
              :error="errors.territory"
            />
          </div>
        </div>

        <!-- Agreement Details -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Agreement Details</h3>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormControl
              type="date"
              label="Agreement Start Date"
              v-model="form.agreement_start_date"
              :error="errors.agreement_start_date"
            />
            <FormControl
              type="date"
              label="Agreement End Date"
              v-model="form.agreement_end_date"
              :error="errors.agreement_end_date"
            />
            <FormControl
              type="number"
              label="Commission Rate (%)"
              v-model="form.commission_rate"
              :error="errors.commission_rate"
              :min="0"
              :max="100"
            />
            <FormControl
              type="number"
              label="Discount Level (%)"
              v-model="form.discount_level"
              :error="errors.discount_level"
              :min="0"
              :max="100"
            />
            <FormControl
              type="currency"
              label="Credit Limit"
              v-model="form.credit_limit"
              :error="errors.credit_limit"
            />
            <FormControl
              type="select"
              label="Payment Terms"
              v-model="form.payment_terms"
              :options="paymentTermsOptions"
              :error="errors.payment_terms"
            />
          </div>
        </div>

        <!-- Specializations -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Specializations</h3>
          <div class="space-y-4">
            <FormControl
              type="textarea"
              label="Products Specialization"
              v-model="form.products_specialization"
              :error="errors.products_specialization"
              rows="3"
            />
            <FormControl
              type="textarea"
              label="Services Offered"
              v-model="form.services_offered"
              :error="errors.services_offered"
              rows="3"
            />
            <FormControl
              type="textarea"
              label="Target Market"
              v-model="form.target_market"
              :error="errors.target_market"
              rows="3"
            />
          </div>
        </div>

        <!-- Partner Manager Assignment -->
        <div v-if="!isEditing">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Assignment</h3>
          <FormControl
            type="autocomplete"
            label="Assigned Partner Manager"
            v-model="form.assigned_partner_manager"
            :options="userOptions"
            :error="errors.assigned_partner_manager"
          />
        </div>

        <!-- Notes -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">Notes</h3>
          <FormControl
            type="textarea"
            label="Internal Notes"
            v-model="form.internal_notes"
            :error="errors.internal_notes"
            rows="4"
          />
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex gap-2">
        <Button variant="white" @click="$emit('close')">Cancel</Button>
        <Button
          :loading="saving"
          @click="savePartner"
        >
          {{ isEditing ? 'Update Partner' : 'Create Partner' }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { call } from 'frappe-ui'
import { Dialog, FormControl, Button } from 'frappe-ui'

// Props
const props = defineProps({
  partner: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'success'])

// State
const show = ref(true)
const saving = ref(false)
const errors = reactive({})

const isEditing = computed(() => !!props.partner)

// Form data
const defaultForm = {
  partner_name: '',
  partner_code: '',
  partner_type: '',
  partner_tier: '',
  primary_contact: '',
  email: '',
  phone: '',
  website: '',
  address_line_1: '',
  address_line_2: '',
  city: '',
  state: '',
  country: '',
  postal_code: '',
  industry: '',
  company_size: '',
  annual_revenue: null,
  years_in_business: null,
  territory: '',
  agreement_start_date: '',
  agreement_end_date: '',
  commission_rate: null,
  discount_level: null,
  credit_limit: null,
  payment_terms: '',
  products_specialization: '',
  services_offered: '',
  target_market: '',
  assigned_partner_manager: '',
  internal_notes: ''
}

const form = reactive({ ...defaultForm })

// Options
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

const companySizeOptions = [
  { label: '1-10 employees', value: '1-10 employees' },
  { label: '11-50 employees', value: '11-50 employees' },
  { label: '51-200 employees', value: '51-200 employees' },
  { label: '201-500 employees', value: '201-500 employees' },
  { label: '501-1000 employees', value: '501-1000 employees' },
  { label: '1000+ employees', value: '1000+ employees' }
]

const paymentTermsOptions = [
  { label: 'Net 15', value: 'Net 15' },
  { label: 'Net 30', value: 'Net 30' },
  { label: 'Net 45', value: 'Net 45' },
  { label: 'Net 60', value: 'Net 60' },
  { label: 'COD', value: 'COD' },
  { label: 'Prepaid', value: 'Prepaid' }
]

const countryOptions = ref([])
const industryOptions = ref([])
const territoryOptions = ref([])
const userOptions = ref([])

// Methods
const clearErrors = () => {
  Object.keys(errors).forEach(key => {
    delete errors[key]
  })
}

const validateForm = () => {
  clearErrors()
  let isValid = true

  // Required fields validation
  const requiredFields = ['partner_name', 'partner_type', 'partner_tier', 'email']

  requiredFields.forEach(field => {
    if (!form[field]) {
      errors[field] = 'This field is required'
      isValid = false
    }
  })

  // Email validation
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  // Date validation
  if (form.agreement_start_date && form.agreement_end_date) {
    if (new Date(form.agreement_start_date) >= new Date(form.agreement_end_date)) {
      errors.agreement_end_date = 'End date must be after start date'
      isValid = false
    }
  }

  // Percentage validation
  if (form.commission_rate && (form.commission_rate < 0 || form.commission_rate > 100)) {
    errors.commission_rate = 'Commission rate must be between 0 and 100'
    isValid = false
  }

  if (form.discount_level && (form.discount_level < 0 || form.discount_level > 100)) {
    errors.discount_level = 'Discount level must be between 0 and 100'
    isValid = false
  }

  return isValid
}

const savePartner = async () => {
  if (!validateForm()) {
    return
  }

  saving.value = true

  try {
    const method = isEditing.value
      ? 'prm.api.partner.update_partner'
      : 'prm.api.partner.create_partner'

    const params = isEditing.value
      ? {
          partner_name: props.partner.name,
          partner_data: form
        }
      : {
          partner_data: form
        }

    const result = await call(method, params)

    if (result.success) {
      emit('success', result.partner)
    }
  } catch (error) {
    console.error('Failed to save partner:', error)

    // Handle validation errors from backend
    if (error.exc_type === 'ValidationError') {
      const message = error.exc || error.message
      // Try to extract field-specific errors
      if (message.includes('Partner Code')) {
        errors.partner_code = message
      } else if (message.includes('Email')) {
        errors.email = message
      } else {
        errors.general = message
      }
    }
  } finally {
    saving.value = false
  }
}

const loadOptions = async () => {
  try {
    // Load countries
    const countries = await call('frappe.client.get_list', {
      doctype: 'Country',
      fields: ['name'],
      limit_page_length: 300
    })
    countryOptions.value = countries.map(c => ({
      label: c.name,
      value: c.name
    }))

    // Load industries
    const industries = await call('frappe.client.get_list', {
      doctype: 'CRM Industry',
      fields: ['name'],
      limit_page_length: 200
    })
    industryOptions.value = industries.map(i => ({
      label: i.name,
      value: i.name
    }))

    // Load territories
    const territories = await call('frappe.client.get_list', {
      doctype: 'Territory',
      fields: ['name'],
      limit_page_length: 200
    })
    territoryOptions.value = territories.map(t => ({
      label: t.name,
      value: t.name
    }))

    // Load users for partner manager assignment
    const users = await call('frappe.client.get_list', {
      doctype: 'User',
      filters: {
        enabled: 1,
        user_type: 'System User'
      },
      fields: ['name', 'full_name', 'email'],
      limit_page_length: 100
    })
    userOptions.value = users.map(u => ({
      label: `${u.full_name} (${u.email})`,
      value: u.name
    }))

  } catch (error) {
    console.error('Failed to load options:', error)
  }
}

// Initialize form with partner data if editing
watch(() => props.partner, (partner) => {
  if (partner) {
    Object.keys(form).forEach(key => {
      if (partner[key] !== undefined) {
        form[key] = partner[key]
      }
    })
  }
}, { immediate: true })

onMounted(() => {
  loadOptions()
})
</script>