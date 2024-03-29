<template>
  <div v-if="!isLoading" class="ma-5">
    <Header1 text="Mailing List" />
    <v-alert
      density="compact"
      role="alert"
      type="success"
    >
      A Mailing List has been created at <strong>{{ mailingList.name }}@{{ mailingList.domain }}</strong>.
      Messages can now be sent through this address.
    </v-alert>
    <div>
      <div class="ml-3 my-3">
        bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site by
        giving the site its own email address. Messages sent to this address from the
        <strong>official berkeley.edu email address</strong>
        of a Teacher, TA, Lead TA or Reader will be sent to the official email addresses of all site
        members. Students and people not in the site cannot send messages through Mailing Lists.
      </div>
      <div v-if="mailingList.welcomeEmailLastSent" class="mb-3">
        <h2 id="download-log-file-header" class="my-2" tabindex="-1">
          Download Log of Sent Messages
        </h2>
        <div class="ml-3">
          <div class="mb-2 my-1">
            <v-btn
              id="btn-download-sent-message-log"
              color="primary"
              :disabled="isDownloading || refreshing"
              @click="downloadMessageLog"
            >
              <span class="mr-1">
                <v-progress-circular
                  v-if="isDownloading"
                  class="mr-1"
                  indeterminate
                  size="18"
                  width="3"
                />
                <v-icon v-if="!isDownloading" :icon="mdiFileDownloadOutline" size="large" />
              </span>
              {{ isDownloading ? 'Downloading' : 'Download' }}
            </v-btn>
          </div>
          <div>
            <span class="font-weight-bold">NOTE:</span>
            Welcome email last sent on {{ $moment(mailingList.welcomeEmailLastSent).format('MMM D, YYYY') }}
          </div>
        </div>
      </div>
      <h2 id="send-welcome-email-header" class="my-2" tabindex="-1">
        Send Welcome Email
      </h2>
      <div class="mb-3 ml-3">
        <div class="mb-3">
          The Welcome Email tool automatically sends a customizable message by email to all members of your course site,
          even if the site has not yet been published. For more information, visit
          <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900">
            How to Create a Welcome Email with the bCourses Mailing List
          </OutboundLink>.
        </div>
        <div class="mt-2">
          <v-alert
            density="compact"
            role="alert"
            :type="isWelcomeEmailActive ? 'success' : 'info'"
          >
            <span v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject">
              <span v-if="isWelcomeEmailActive">Welcome email {{ isToggling ? 'is being' : '' }} activated.</span>
              <span v-if="!isWelcomeEmailActive">Sending welcome emails is paused.</span>
            </span>
            <span v-if="!mailingList.welcomeEmailBody || !mailingList.welcomeEmailSubject">
              You can activate the welcome email
              <span class="font-italic">after</span> you enter email subject and message below.
            </span>
          </v-alert>
          <div class="ml-5 w-25">
            <v-switch
              id="toggle-welcome-email-active"
              v-model="isWelcomeEmailActive"
              color="success"
              :disabled="!mailingList.welcomeEmailBody || !mailingList.welcomeEmailSubject || isSaving || isToggling"
              hide-details
              @change="toggle"
            >
              <template #label>
                <v-progress-circular
                  v-if="isToggling"
                  indeterminate
                  size="24"
                  class="ms-2"
                />
                <span v-if="!isToggling" class="text-no-wrap">
                  {{ isWelcomeEmailActive ? 'Active' : 'Inactive' }}
                </span>
              </template>
            </v-switch>
          </div>
        </div>
        <div class="container pb-5 pt-3 px-5">
          <template v-if="isEditing">
            <label for="input-subject" class="text-subtitle-1">
              Subject
            </label>
            <v-text-field
              id="input-subject"
              v-model="subject"
              aria-required="true"
              class="bg-white"
              density="compact"
              hide-details
              maxlength="255"
              :rules="[s => !!s || 'Required']"
              variant="outlined"
              @keydown.enter="saveWelcomeEmail"
            />
          </template>
          <template v-else>
            <div class="text-subtitle-1">
              Subject
            </div>
            <div id="page-site-mailing-list-subject">
              {{ mailingList.welcomeEmailSubject }}
            </div>
          </template>
          <div class="mt-3">
            <template v-if="isEditing">
              <label for="input-message" class="text-subtitle-1">
                Message
              </label>
              <ckeditor
                id="input-message"
                v-model="body"
                :config="{
                  codeBlock: {
                    indentSequence: '  '
                  },
                  initialData: '',
                  link: {
                    addTargetToExternalLinks: true,
                    defaultProtocol: 'http://'
                  },
                  toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link']
                }"
                :editor="editor"
                tag-name="textarea"
              />
            </template>
            <template v-else>
              <div class="text-subtitle-1">
                Message
              </div>
              <div class="pb-3 pt-1">
                <div id="page-site-mailing-list-body" v-html="mailingList.welcomeEmailBody"></div>
              </div>
            </template>
          </div>
          <div class="mt-3">
            <div v-if="isEditing">
              <v-btn
                id="btn-save-welcome-email"
                class="mr-2"
                color="primary"
                :disabled="isSaving || isToggling || !isWelcomeEmailValid"
                @click="saveWelcomeEmail"
              >
                <span v-if="!isSaving">Save welcome email</span>
                <span v-if="isSaving">
                  <SpinnerWithinButton /> Saving...
                </span>
              </v-btn>
              <v-btn
                v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject"
                id="btn-cancel-welcome-email-edit"
                :disabled="isSaving || isToggling"
                variant="tonal"
                @click="cancelEditMode"
              >
                Cancel
              </v-btn>
            </div>
            <div v-if="!isEditing">
              <v-btn
                id="btn-edit-welcome-email"
                color="primary"
                :disabled="isToggling"
                @click="setEditMode"
              >
                Edit welcome email
              </v-btn>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiFileDownloadOutline} from '@mdi/js'
</script>

<script>
import CKEditor from '@ckeditor/ckeditor5-vue'
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import MailingList from '@/mixins/MailingList'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {
  activateWelcomeEmail,
  deactivateWelcomeEmail,
  downloadWelcomeEmailCsv,
  getMyMailingList,
  updateWelcomeEmail
} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'SendWelcomeEmail',
  components: {
    ckeditor: CKEditor.component,
    Header1,
    OutboundLink,
    SpinnerWithinButton
  },
  mixins: [Context, MailingList],
  data: () => ({
    alerts: {
      error: [],
      success: []
    },
    body: '',
    editor: ClassicEditor,
    errorMessages: [],
    isCreating: false,
    isDownloading: false,
    isEditing: false,
    isSaving: false,
    isToggling: false,
    isWelcomeEmailActive: false,
    subject: ''
  }),
  computed: {
    isWelcomeEmailValid() {
      return !!trim(this.subject) && !!trim(this.body)
    }
  },
  created() {
    getMyMailingList().then(
      data => {
        this.updateDisplay(data)
        this.$ready('page-header')
      }
    )
  },
  methods: {
    cancelEditMode() {
      this.isEditing = false
      this.body = this.mailingList.welcomeEmailBody || ''
      this.subject = this.mailingList.welcomeEmailSubject
      putFocusNextTick('send-welcome-email-header')
    },
    downloadMessageLog() {
      this.isDownloading = true
      this.alertScreenReader('Downloading')
      downloadWelcomeEmailCsv().then(() => {
        this.isDownloading = false
        this.alertScreenReader('Downloaded.')
      })
    },
    saveWelcomeEmail() {
      if (this.isWelcomeEmailValid) {
        this.alertScreenReader('Saving welcome email')
        this.isSaving = true
        updateWelcomeEmail(false, this.body, this.subject).then(
          response => {
            this.updateDisplay(response)
            putFocusNextTick('send-welcome-email-header')
          }
        ).then(() => {
          this.isSaving = false
        })
      }
    },
    setEditMode() {
      this.isEditing = true
      putFocusNextTick('input-subject')
    },
    toggle() {
      this.isToggling = true
      const toggleEmailActivation = this.isWelcomeEmailActive ? activateWelcomeEmail : deactivateWelcomeEmail
      toggleEmailActivation().then(data => {
        this.isWelcomeEmailActive = !!data.welcomeEmailActive
        this.isToggling = false
        this.alertScreenReader(`${this.isWelcomeEmailActive ? 'Enabled' : 'Disabled' } welcome email`)
      })
    },
    updateDisplay(data) {
      this.setMailingList(data)
      this.isWelcomeEmailActive = this.mailingList.welcomeEmailActive
      this.body = this.mailingList.welcomeEmailBody || ''
      this.subject = this.mailingList.welcomeEmailSubject
      this.errorMessages = this.mailingList.errorMessages || []
      this.isEditing = !this.body && !this.subject
      this.isCreating = false
    }
  }
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type -->
<style>
ol {
  margin-left: 16px;
}
ul {
  margin-left: 16px;
}
.ck.ck-editor__editable_inline {
  min-height: 150px;
  padding: 0 15px;
}
.ck.ck-editor__editable_inline ol {
  margin: 0 0 10px 20px;
}
.ck.ck-editor__editable_inline p {
  margin: 0 0 10px 0;
}
.ck.ck-editor__editable_inline ul {
  list-style-type: disc;
  margin: 0 0 10px 20px;
}
</style>
