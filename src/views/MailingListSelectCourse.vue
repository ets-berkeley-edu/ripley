<template>
  <div v-if="!isLoading" class="pb-5 px-5">
    <div class="pl-3">
      <Header1 text="Manage Mailing Lists" />
      <div
        v-if="error"
        id="mailing-lists-alert"
        aria-live="polite"
        class="pb-3"
      >
        <v-alert
          class="my-2"
          density="compact"
          role="alert"
          type="warning"
        >
          {{ error }}
        </v-alert>
      </div>
    </div>
    <div v-if="currentUser.isAdmin || currentUser.isCanvasAdmin" class="align-center d-flex flex-wrap px-3">
      <div class="pr-3">
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="canvasSiteId"
          :aria-describedby="!!trim(canvasSiteId) && !isCanvasSiteIdValid ? 'mailing-list-site-id-messages' : null"
          aria-label="bCourses Course ID"
          aria-required="true"
          density="comfortable"
          :error="!!trim(canvasSiteId) && !isCanvasSiteIdValid"
          hide-details
          maxlength="10"
          label="bCourses Course ID"
          style="width: 200px"
          variant="outlined"
          @keydown.enter="proceed"
        />
        <span v-if="!!trim(canvasSiteId) && !isCanvasSiteIdValid" id="mailing-list-site-id-messages" class="position-absolute validation-messages">
          <span class="sr-only">Invalid entry. </span>{{ 'Only numbers allowed.' }}
        </span>
      </div>
      <div>
        <v-btn
          id="btn-get-mailing-list"
          color="primary"
          :disabled="isProcessing || !isCanvasSiteIdValid"
          size="large"
          @click="proceed"
        >
          <span v-if="!isProcessing">Get Mailing List</span>
          <span v-if="isProcessing">
            <SpinnerWithinButton /> Searching...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import MailingList from '@/mixins/MailingList'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {getMailingList} from '@/api/mailing-list'
import {isValidCanvasSiteId, putFocusNextTick} from '@/utils'
import {nextTick} from 'vue'
import {trim} from 'lodash'

export default {
  name: 'MailingListSelectCourse',
  components: {Header1, SpinnerWithinButton},
  mixins: [Context, MailingList],
  data: () => ({
    canvasSiteId: undefined,
    error: undefined,
    isProcessing: false
  }),
  computed: {
    isCanvasSiteIdValid() {
      return isValidCanvasSiteId(this.canvasSiteId)
    }
  },
  mounted() {
    if (this.currentUser.isAdmin || this.currentUser.isCanvasAdmin) {
      this.init()
    } else {
      this.error = 'Unauthorized'
    }
    this.$ready()
  },
  methods: {
    proceed() {
      if (!this.isProcessing) {
        this.isProcessing = true
        this.alertScreenReader('Searching for mailing list.')
        let searchTimer = setInterval(() => {
          this.alertScreenReader('Still searching.')
        }, 7000)
        getMailingList(this.canvasSiteId).then(
          data => {
            this.error = undefined
            if (data) {
              this.alertScreenReader('Mailing list found.', 'assertive')
              this.setMailingList(data)
              this.$router.push('/mailing_list/update')
            } else {
              this.alertScreenReader('No mailing list found.', 'assertive')
              nextTick(() => this.$router.push(`/mailing_list/create/${this.canvasSiteId}`))
            }
          },
          error => {
            this.error = error
            this.isProcessing = false
            putFocusNextTick('btn-get-mailing-list')
          }
        ).finally(() => clearInterval(searchTimer))
      }
    },
    trim
  }
}
</script>
