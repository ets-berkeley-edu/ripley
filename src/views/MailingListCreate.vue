<template>
  <div v-if="!contextStore.isLoading" class="px-5 pb-5">
    <div>
      <Header1 text="Create Mailing List" />
      <v-alert
        v-if="!error && !success"
        class="mb-3"
        density="compact"
        role="none"
        text="No Mailing List has been created for this site."
        type="info"
      />
      <div id="mailing-lists-alert" aria-live="polite">
        <v-alert
          v-if="success"
          :closable="true"
          density="compact"
          role="none"
          :text="success"
          type="success"
        />
        <v-alert
          v-if="error"
          density="compact"
          role="none"
          :text="error"
          type="warning"
        />
      </div>
    </div>
    <v-card
      v-if="!error"
      id="mailing-list-details"
      class="ma-0 pa-4"
      elevation="2"
    >
      <v-card-text>
        <div v-if="!isAdminToolMode" class="mb-1">
          bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site
          by giving the site its own email address. Messages sent to this address from the
          <span class="font-weight-bold">official berkeley.edu email address</span> of a Teacher, TA, Lead TA or Reader
          will be sent to the official email addresses of all site members. Students and people not in the site cannot
          send messages through Mailing Lists.
        </div>
        <div>
          <v-container class="pa-0" fluid>
            <v-row v-if="isAdminToolMode" no-gutters>
              <v-col cols="auto" class="me-auto">
                <h2 v-if="get(canvasSite, 'url')">
                  <OutboundLink
                    id="course-site-href"
                    class="align-start d-flex font-size-18"
                    :href="canvasSite.url"
                    title="View course site"
                  >
                    {{ canvasSite.name }}
                  </OutboundLink>
                </h2>
                <div v-if="!get(canvasSite, 'url')">
                  <h2>{{ canvasSite.name }}</h2>
                </div>
              </v-col>
            </v-row>
            <v-row v-if="isAdminToolMode" no-gutters>
              <v-col>
                <div class="mb-4 w-auto">
                  <div v-if="get(canvasSite, 'term')" class="text-subtitle-1">{{ canvasSite.term.name }}</div>
                  <div>bCourses Site ID {{ get(canvasSite, 'canvasSiteId') }}</div>
                </div>
              </v-col>
            </v-row>
            <v-row align="center" no-gutters>
              <v-col>
                <v-text-field
                  id="mailing-list-name-input"
                  v-model="mailingListName"
                  :aria-invalid="hasInvalidCharacters || !mailingListName"
                  :aria-labelledby="undefined"
                  aria-required="true"
                  autocomplete="on"
                  density="comfortable"
                  :disabled="isCreating"
                  label="Mailing list name"
                  maxlength="50"
                  required
                  :rules="validationRules"
                  validate-on="lazy invalid-input"
                  variant="outlined"
                  @keydown.enter="create"
                />
              </v-col>
              <v-col>
                <div class="text-no-wrap text-subtitle-1">-{{ mailingListSuffix }}@{{ mailgunDomain }}</div>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <div class="d-flex float-right mt-8">
                  <div :class="{'mr-2': isAdminToolMode}">
                    <v-btn
                      id="btn-create-mailing-list"
                      color="primary"
                      :disabled="isCreating || !trim(mailingListName) || hasInvalidCharacters"
                      @click="create"
                    >
                      <span v-if="!isCreating">Create mailing list</span>
                      <span v-if="isCreating">
                        <SpinnerWithinButton /> Creating...
                      </span>
                    </v-btn>
                  </div>
                  <div v-if="isAdminToolMode">
                    <v-btn
                      id="btn-cancel"
                      :disabled="isCreating"
                      variant="tonal"
                      @click="cancel"
                    >
                      Cancel
                    </v-btn>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import {get, size, trim} from 'lodash'
import {nextTick, onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useRoute, useRouter} from 'vue-router'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {createMailingList, getMailingList, getSuggestedMailingListName} from '@/api/mailing-list'
import {getCanvasSite} from '@/api/canvas-site'
import {alertScreenReader, toInt} from '@/utils'
import {useContextStore} from '@/stores/context'
import {useMailingListStore} from '@/stores/mailing-list'

const canvasSiteId = ref(undefined)
const contextStore = useContextStore()
const error = ref(undefined)
const hasInvalidCharacters = ref(false)
const isAdminToolMode = ref(undefined)
const isCreating = ref(false)
const mailgunDomain = ref(undefined)
const mailingListName = ref(undefined)
const mailingListStore = useMailingListStore()
const {canvasSite} = storeToRefs(mailingListStore)
const mailingListSuffix = ref(undefined)
const route = useRoute()
const router = useRouter()
const success = ref(undefined)
const validationRules = [
  s => !!s || 'Mailing list name is required',
  s => validateName(s) || 'Only lowercase alphanumeric, underscore and hyphen characters allowed.'
]
const VALID_NAME_REGEX = /[a-z0-9_-]/g

contextStore.loadingStart()

onMounted(() => {
  const canvasSiteIdFromRoute = toInt(get(route, 'params.canvasSiteId'))
  mailingListStore.init()
  isAdminToolMode.value = !!canvasSiteIdFromRoute
  canvasSiteId.value = canvasSiteIdFromRoute || contextStore.currentUser.canvasSiteId
  getMailingList(canvasSiteId.value).then(
    mailingListResponse => {
      mailingListStore.setMailingList(mailingListResponse)
      if (mailingListResponse) {
        goToNextPage()
      } else {
        getSite().then(canvasSiteResponse => {
          mailingListStore.setCanvasSite(canvasSiteResponse)
          getSuggestedMailingListName(canvasSiteId.value).then(suggestion => {
            const suffix = suggestion.suffix
            mailgunDomain.value = suggestion.mailgunDomain
            mailingListName.value = suggestion.name
            mailingListSuffix.value = suffix
            contextStore.loadingComplete()
          })
        })
      }
    },
    e => {
      error.value = e
      contextStore.loadingComplete()
    }
  )
})

const cancel = () => {
  alertScreenReader('Canceled. Nothing saved.', 'assertive')
  nextTick(router.push({path: '/mailing_list/select_course'}))
}

const create = () => {
  const name = trim(mailingListName.value)
  if (name && !hasInvalidCharacters.value) {
    const createTimer = setInterval(() => {
      alertScreenReader('Still creating mailing list.')
    }, 7000)
    isCreating.value = true
    alertScreenReader('Creating mailing list.')
    createMailingList(
      canvasSiteId.value,
      `${name}-${mailingListSuffix.value}`,
      !isAdminToolMode.value
    ).then(
      data => {
        alertScreenReader('The mailing list has been created. To add members, click the "Update Memberships" button below.', 'assertive')
        error.value = null
        mailingListStore.setMailingList(data)
        nextTick(goToNextPage())
      },
      e => {
        alertScreenReader('Error.', 'assertive')
        error.value = e
      }
    ).finally(() => {
      clearInterval(createTimer)
      isCreating.value = false
    })
  }
}

const getSite = () => {
  return new Promise(resolve => {
    if (canvasSite.value) {
      resolve(canvasSite.value)
    } else {
      getCanvasSite(canvasSiteId.value).then(resolve)
    }
  })
}

const goToNextPage = () => {
  const path = isAdminToolMode.value ? '/mailing_list/update' : '/mailing_list/send_welcome_email'
  router.push({path})
}

const validateName = s => {
  const name = trim(s)
  const isValid = name.length && size(name.match(VALID_NAME_REGEX)) === name.length && name[0].match(/[a-z]/)
  hasInvalidCharacters.value = !isValid
  return isValid
}
</script>
