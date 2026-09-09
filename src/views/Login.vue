<template>
  <v-container
    class="background-splash"
    fill-height
    fluid
    :style="{backgroundImage: `url(${nostromoCrew})`}"
  >
    <Header1 id="page-title" class="sr-only" text="Login" />
    <v-row>
      <v-col v-if="!currentUser.isAuthenticated">
        <div class="py-5">
          <v-btn
            id="cas-auth-submit-button"
            @click="toCasLogin"
          >
            CalNet Login
          </v-btn>
        </div>
        <div>
          <hr>
        </div>
        <div v-if="config.devAuthEnabled" class="pt-3">
          <h2 class="sr-only">DevAuth</h2>
          <div class="w-50">
            <v-expand-transition>
              <v-alert
                v-if="devAuthError"
                border
                class="dev-auth-error mb-4 py-3"
                color="error"
                rounded
              >
                {{ devAuthError }}
              </v-alert>
            </v-expand-transition>
            <div class="pb-2">
              <v-text-field
                id="basic-auth-uid"
                v-model="uid"
                autocomplete="on"
                class="text-field"
                density="comfortable"
                :disabled="isLoggingIn"
                :error="!trim(uid) && devAuthError"
                hide-details
                label="UID"
                required
                variant="solo"
                width="24rem"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <div class="pb-2">
              <v-text-field
                id="basic-auth-password"
                v-model="password"
                autocomplete="off"
                class="my-2 text-field"
                density="comfortable"
                :disabled="isLoggingIn"
                :error="!trim(password) && devAuthError"
                hide-details
                label="Password"
                required
                type="password"
                variant="solo"
                width="24rem"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <div class="pb-2">
              <v-text-field
                id="basic-auth-canvas-course-id"
                v-model="canvasSiteId"
                autocomplete="on"
                class="text-field"
                density="comfortable"
                :disabled="isLoggingIn"
                hide-details
                label="Canvas Course ID (optional)"
                required
                variant="solo"
                width="24rem"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <div class="pb-4">
              <v-text-field
                id="basic-auth-canvas-masquerading-user-id"
                v-model="canvasMasqueradingUserId"
                autocomplete="on"
                class="my-2 text-field"
                density="comfortable"
                :disabled="isLoggingIn"
                hide-details
                label="Canvas Masquerading User ID (optional)"
                required
                variant="solo"
                width="24rem"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <v-btn
              id="basic-auth-submit-button"
              :disabled="disableSubmit || isLoggingIn"
              @click="devAuth"
            >
              <span v-if="isLoggingIn">
                <v-progress-circular
                  class="mr-1"
                  indeterminate
                  size="18"
                />
                Dev Auth
              </span>
              <span v-if="!isLoggingIn">Dev Auth</span>
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {get, trim} from 'lodash'
import {useRouter} from 'vue-router'
import Header1 from '@/components/utils/Header1.vue'
import nostromoCrew from '@/assets/images/nostromo-crew-eating-breakfast.png'
import {alertScreenReader, putFocusNextTick} from '@/utils'
import {devAuthLogIn, getCasLoginURL} from '@/api/auth'
import {useContextStore} from '@/stores/context'

const canvasMasqueradingUserId = ref(undefined)
const canvasSiteId = ref(undefined)
const contextStore = useContextStore()
const config = contextStore.config
const currentUser = contextStore.currentUser
const devAuthError = ref(undefined)
const isLoggingIn = ref(false)
const password = ref(undefined)
const router = useRouter()
const uid = ref(undefined)

const disableSubmit = computed(() => {
  return !trim(password.value) || !trim(uid.value)
})

onMounted(() => {
  const showDevAuth = false
  contextStore.loadingComplete()
  return {showDevAuth}
})

const clearErrors = () => {
  devAuthError.value = null
}

const devAuth = () => {
  clearErrors()
  const passwordTrimmed = trim(password.value)
  const uidTrimmed = trim(uid.value)
  if (uidTrimmed && passwordTrimmed) {
    isLoggingIn.value = true
    devAuthLogIn(trim(canvasSiteId.value), uidTrimmed, passwordTrimmed, trim(canvasMasqueradingUserId.value)).then(
      data => {
        if (data.isAuthenticated) {
          contextStore.setCurrentUser(data)
          router.push({path: '/welcome'})
        } else {
          const message = get(data, 'error') || get(data, 'message') || 'Authentication failed'
          reportError(message)
        }
      },
      error => {
        reportError(error)
      }
    ).finally(() => {
      isLoggingIn.value = false
    })
  } else if (uidTrimmed) {
    reportError('Password required', 'basic-auth-password')
  } else {
    reportError('Both UID and password are required')
  }
}

const reportError = (message, putFocus) => {
  devAuthError.value = typeof message === 'string' ? message : get(message, 'message')
  alertScreenReader(devAuthError.value || 'Uh oh, an error occurred.')
  putFocusNextTick(putFocus || 'basic-auth-uid')
}

const toCasLogin = () => {
  getCasLoginURL().then(data => {
    window.location.href = data.casLoginUrl
  })
}
</script>

<style>
.dev-auth-error {
  width: 24rem !important;
}
.text-field .v-field {
  background-color: rgba(255, 255, 255, 0.7);
}
</style>
