<template>
  <div v-if="!isLoading" class="mx-10 my-5">
    <Header1 text="Create a Project Site" />
    <div v-if="!isLoading">
      <v-alert
        v-if="error"
        density="compact"
        role="alert"
        :text="error"
        type="warning"
      />
      <div class="align-center d-flex justify-center pb-8 pt-4">
        <div class="pr-3">
          <label
            for="page-create-project-site-name"
            class="text-subtitle-1 font-weight-medium"
          >
            Project Site Name
          </label>
        </div>
        <div class="mr-16 w-50">
          <v-text-field
            id="page-create-project-site-name"
            v-model="name"
            class="w-100"
            density="comfortable"
            :disabled="isCreating"
            hide-details
            maxlength="255"
            variant="outlined"
            @keydown.enter="create"
          />
        </div>
      </div>
      <div class="d-flex justify-end">
        <v-btn
          id="create-project-site-button"
          class="mr-1"
          color="primary"
          type="submit"
          :disabled="isCreating || !trim(name)"
          @click="create"
        >
          <span v-if="!isCreating">Create a Project Site</span>
          <span v-if="isCreating">
            <v-progress-circular
              class="mr-1"
              indeterminate
              size="18"
            />
            Creating<span aria-hidden="true">...</span><span class="sr-only"> Project Site</span>
          </span>
        </v-btn>
        <v-btn
          id="cancel-and-return-to-site-creation"
          aria-label="Cancel and return to Site Creation Overview"
          :disabled="isCreating"
          type="button"
          variant="tonal"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import {createProjectSite} from '@/api/canvas-site'
import {iframeParentLocation} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'CreateProjectSite',
  components: {Header1},
  mixins: [Context],
  data: () => ({
    isCreating: undefined,
    error: undefined,
    name: undefined
  }),
  created() {
    this.$ready()
  },
  methods: {
    cancel() {
      this.$router.push({path: '/manage_sites'})
    },
    create() {
      if (!this.isCreating && trim(this.name)) {
        this.error = null
        this.isCreating = true
        this.alertScreenReader('Creating project site.')
        createProjectSite(this.name).then(
          data => {
            this.alertScreenReader('Done. Loading new project site.')
            if (this.$isInIframe) {
              iframeParentLocation(data.url)
            } else {
              window.location.href = data.url
            }
          },
          error => {
            this.error = error
          }
        ).finally(() => {
          this.isCreating = false
        })
      }
    },
    trim
  }
}
</script>
