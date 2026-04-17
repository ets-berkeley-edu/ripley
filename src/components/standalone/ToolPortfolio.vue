<template>
  <v-card class="pb-2 px-8" :class="vCardClass" :width="width">
    <v-card-title>
      <div
        class="align-end d-flex mt-6"
        :class="{'mb-2': config.devAuthEnabled}"
      >
        <div class="mb-1 mr-2">
          <v-icon
            color="primary"
            :icon="mdiStackOverflow"
            size="large"
          />
        </div>
        <div>
          <h2>{{ config.devAuthEnabled ? 'LTI Portfolio' : 'Tools' }}</h2>
        </div>
      </div>
    </v-card-title>
    <v-card-text :class="{'ml-2': !config.devAuthEnabled}">
      <h3 v-if="config.devAuthEnabled" class="mb-0">Account Tools</h3>
      <StandaloneToolsList :tools="adminTools" />
      <div v-if="config.devAuthEnabled && currentUser.canAccessStandaloneView" class="mt-3">
        <h3 class="mb-0">Canvas Site Tools</h3>
        <v-alert
          v-if="!currentUser.canvasSiteId"
          class="mt-2"
          density="compact"
          role="none"
          type="info"
        >
          Enter a Canvas site ID (below) to enable site tools.
        </v-alert>
        <div v-if="currentUser.canvasSiteId" class="pl-4 pt-2">
          <a
            :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}`"
            class="text-subtitle-1"
            target="_blank"
            title="Open course site in new tab"
          >
            <span class="canvas-site-name">{{ currentUser.canvasSiteName }}</span><v-icon class="ml-1" :icon="mdiOpenInNew" size="small" />
          </a>
        </div>
        <StandaloneToolsList class="pt-1" :tools="embeddedTools" />
        <div class="align-center d-flex pl-4 py-2">
          <div class="pr-2">
            <v-text-field
              id="update-canvas-course-id"
              v-model="canvasSiteId"
              autocomplete="on"
              density="compact"
              :disabled="isUpdatingCanvasSiteId"
              :error="!!canvasSiteId && !isCanvasSiteIdValid"
              hide-details
              label="Canvas site ID"
              maxlength="10"
              style="width: 124px"
              variant="outlined"
              @update:model-value="() => error = undefined"
              @keydown.enter="updateCanvasSiteId"
            />
          </div>
          <div>
            <v-btn
              id="update-canvas-site-id-btn"
              color="primary"
              :disabled="isUpdatingCanvasSiteId || !canvasSiteId || !isCanvasSiteIdValid"
              @click="updateCanvasSiteId"
            >
              <span v-if="isUpdatingCanvasSiteId">
                <SpinnerWithinButton />
                <span v-if="currentUser.canvasSiteId">Updating</span>
                <span v-if="!currentUser.canvasSiteId">Setting</span>
                Canvas Site ID...
              </span>
              <span v-if="!isUpdatingCanvasSiteId">
                <span v-if="currentUser.canvasSiteId">Change</span>
                <span v-if="!currentUser.canvasSiteId">Set</span>
                Canvas Site ID
              </span>
            </v-btn>
          </div>
        </div>
        <div v-if="error" class="font-weight-medium pl-4 pt-1 text-red">
          {{ error }}
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>
import {
  mdiAccountMultiple,
  mdiAccountPlusOutline,
  mdiAccountSchool,
  mdiChartBarStacked,
  mdiEmailMultipleOutline,
  mdiExport,
  mdiOpenInNew,
  mdiStackOverflow,
  mdiWeb
} from '@mdi/js'
import type {StandaloneToolOption} from '@/lib/types'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import StandaloneToolsList from '@/components/utils/StandaloneToolsList.vue'
import {computed, onMounted, ref} from 'vue'
import {isValidCanvasSiteId} from '@/utils'
import {sortBy, toString} from 'lodash'
import {updateUserSession} from '@/api/auth'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

defineProps({
  vCardClass: {
    default: undefined,
    required: false,
    type: String
  },
  width: {
    default: undefined,
    required: false,
    type: Number
  }
})

const contextStore = useContextStore()
const adminTools = ref<StandaloneToolOption[]>([])
const canvasSiteId = ref<number>(contextStore.currentUser.canvasSiteId)
const config = contextStore.config
const currentUser = contextStore.currentUser
const embeddedTools = ref<StandaloneToolOption[]>([])
const error = ref(undefined)
const eventHub = contextStore.eventHub
const isCanvasSiteIdValid = computed(() => {
  return isValidCanvasSiteId(toString(canvasSiteId.value))
})
const isUpdatingCanvasSiteId = ref(false)
const router = useRouter()

onMounted(() => {
  canvasSiteId.value = currentUser.canvasSiteId
  loadTools()
  eventHub.on('current-user-update', () => {
    canvasSiteId.value = currentUser.canvasSiteId
    loadTools()
  })
  contextStore.loadingComplete()

})

const loadTools = () => {
  const canvasSiteId = currentUser.canvasSiteId
  adminTools.value = sortBy([
    {disabled: false, icon: mdiWeb, path: '/manage_sites', title: 'Manage Sites'},
    {disabled: false, icon: mdiAccountPlusOutline, path: '/provision_user', title: 'User Provision'},
    {disabled: false, icon: mdiEmailMultipleOutline, path: '/mailing_list/select_course', title: 'Mailing Lists Manager'},
  ], tool => tool.title)
  embeddedTools.value = sortBy([
    {disabled: !canvasSiteId, icon: mdiEmailMultipleOutline, path: '/mailing_list/create', title: 'Mailing List'},
    {disabled: !canvasSiteId, icon: mdiExport, path: '/export_grade', title: 'E-Grade Export'},
    {disabled: !canvasSiteId, icon: mdiChartBarStacked, path: '/grade_distribution', title: 'Grade Distribution'},
    {disabled: !canvasSiteId, icon: mdiAccountSchool, path: '/add_user', title: 'Find a Person to Add'},
    {disabled: !canvasSiteId, icon: mdiAccountMultiple, path: '/roster', title: 'Roster Photos'}
  ], tool => tool.title)
}

const updateCanvasSiteId = () => {
  // const canvasSiteId = trim(canvasSiteId.value) || null
  if (canvasSiteId.value && isCanvasSiteIdValid.value && currentUser.isAuthenticated) {
    isUpdatingCanvasSiteId.value = true
    updateUserSession(canvasSiteId.value).then(
      data => {
        contextStore.setCurrentUser(data)
        canvasSiteId.value = currentUser.canvasSiteId
        router.go(1)
      },
      e => {
        error.value = e
      }
    ).finally(() => {
      isUpdatingCanvasSiteId.value = false
    })
  }
}
</script>

<style scoped>
.canvas-site-name {
  font-weight: 410;
}
</style>
