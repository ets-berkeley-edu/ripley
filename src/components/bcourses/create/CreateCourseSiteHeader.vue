<template>
  <div class="page-create-course-site-admin-options">
    <h2 class="sr-only">Administrator Options</h2>
    <v-btn
      id="toggle-admin-mode-button"
      aria-controls="page-create-course-site-admin-section-loader-form"
      class="canvas-button canvas-button-small page-create-course-site-admin-mode-switch pb-2 ptl-3 pr-2 pt-2"
      @click="setMode(adminMode === 'act_as' ? 'by_ccn' : 'act_as')"
    >
      Switch to {{ adminMode === 'act_as' ? 'CCN input' : 'acting as instructor' }}
    </v-btn>
    <div id="page-create-course-site-admin-section-loader-form">
      <div v-if="adminMode === 'act_as'">
        <h3 class="sr-only">Load Sections By Instructor UID</h3>
        <form
          id="page-create-course-site-act-as-form"
          class="canvas-page-form page-create-course-site-act-as-form"
          @submit.prevent="submit"
        >
          <v-row no-gutters>
            <v-col cols="auto">
              <label for="instructor-uid" class="sr-only">Instructor UID</label>
              <v-text-field
                id="instructor-uid"
                v-model="uid"
                placeholder="Instructor UID"
                role="search"
              ></v-text-field>
            </v-col>
            <v-col cols="auto">
              <div>
                <v-btn
                  id="sections-by-uid-button"
                  type="submit"
                  class="canvas-button canvas-button-primary"
                  :disabled="!uid"
                  aria-label="Load official sections for instructor"
                  aria-controls="page-create-course-site-steps-container"
                >
                  As instructor
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </form>
      </div>
      <div v-if="adminMode === 'by_ccn'">
        <h3 id="load-sections-by-ccn" class="sr-only">Load Sections By Course Control Numbers (CCN)</h3>
        <form id="load-sections-by-ccn-form" class="canvas-page-form" @submit.prevent="submit">
          <div v-if="$_.size(adminSemesters)">
            <div class="buttonset">
              <span v-for="(semester, index) in adminSemesters" :key="index">
                <input
                  :id="`semester${index}`"
                  type="radio"
                  name="adminSemester"
                  class="sr-only"
                  :aria-selected="currentAdminSemester === semester.slug"
                  role="tab"
                  @click="switchAdminSemester(semester)"
                  @keyup.enter="switchAdminSemester(semester)"
                />
                <label
                  :for="`semester${index}`"
                  class="buttonset-button"
                  role="button"
                  aria-disabled="false"
                  :class="{
                    'buttonset-button-active': currentAdminSemester === semester.slug,
                    'buttonset-corner-left': index === 0,
                    'buttonset-corner-right': index === ($_.size(adminSemesters) - 1)
                  }"
                >
                  {{ semester.name }}
                </label>
              </span>
            </div>
            <label
              for="page-create-course-site-ccn-list"
              class="sr-only"
            >
              Provide CCN List Separated by Commas or Spaces
            </label>
            <textarea
              id="page-create-course-site-ccn-list"
              v-model="ccns"
              placeholder="Paste your list of CCNs here, separated by commas or spaces"
            ></textarea>
            <v-btn
              id="sections-by-ids-button"
              class="canvas-button canvas-button-primary"
              aria-controls="page-create-course-site-steps-container"
              :disabled="!$_.trim(ccns)"
              type="submit"
            >
              Review matching CCNs
            </v-btn>
          </div>
        </form>
      </div>
      <div
        v-if="error"
        aria-live="polite"
        class="has-error pl-2 pt-2"
        role="alert"
      >
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'CreateCourseSiteHeader',
  mixins: [Context, Utils],
  watch: {
    ccns() {
      this.error = null
    },
    uid() {
      this.error = null
    }
  },
  props: {
    adminMode: {
      required: true,
      type: String
    },
    adminSemesters: {
      default: undefined,
      required: false,
      type: Array
    },
    currentAdminSemester: {
      required: true,
      type: String
    },
    fetchFeed: {
      required: true,
      type: Function
    },
    setAdminActingAs: {
      required: true,
      type: Function
    },
    setAdminByCcns: {
      required: true,
      type: Function
    },
    setAdminMode: {
      required: true,
      type: Function
    },
    showMaintenanceNotice: {
      required: true,
      type: Boolean
    },
    switchAdminSemester: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    ccns: '',
    error: undefined,
    uid: undefined
  }),
  methods: {
    setMode(mode) {
      this.setAdminMode(mode)
      if (mode === 'by_ccn') {
        this.$announcer.polite('Input mode switched to section ID')
        this.$putFocusNextTick('load-sections-by-ccn')
      } else {
        this.$announcer.polite(`Input mode switched to ${mode === 'by_ccn' ? 'section ID' : 'UID'}`)
        this.$putFocusNextTick(mode === 'by_ccn' ? 'load-sections-by-ccn' : 'instructor-uid')
      }
    },
    submit() {
      if (this.adminMode === 'by_ccn') {
        const trimmed = this.$_.trim(this.ccns)
        const split = this.$_.split(trimmed, /[,\r\n\t ]+/)
        const notNumeric = this.$_.partition(split, ccn => /^\d+$/.test(this.$_.trim(ccn)))[1]
        if (notNumeric.length) {
          this.error = 'CCNs must be numeric.'
          this.$putFocusNextTick('page-create-course-site-ccn-list')
        } else {
          this.setAdminByCcns(split)
          this.fetchFeed()
        }
      } else {
        const trimmed = this.$_.trim(this.uid)
        if (/^\d+$/.test(trimmed)) {
          this.setAdminActingAs(trimmed)
          this.fetchFeed()
        } else {
          this.error = 'UID must be numeric.'
          this.$putFocusNextTick('instructor-uid')
        }
      }
    }
  }
}
</script>

<style scoped lang="scss">
.page-create-course-site-act-as-form {
  margin: 5px 0;
  input[type="text"] {
    font-family: $body-font-family;
    font-size: 14px;
    margin: 2px 10px 0 0;
    padding: 8px 12px;
    width: 140px;
  }
}
.page-create-course-site-admin-options {
  margin-bottom: 15px;
}
.page-create-course-site-admin-mode-switch {
  margin-bottom: 5px;
  outline: none;
}
.page-create-course-site-header {
  color: $color-headers;
  font-family: $body-font-family;
  font-weight: normal;
  line-height: 40px;
  margin: 5px 0;
}
.has-error {
  color: $color-alert-error-foreground;
  font-size: 14px;
  font-weight: bolder;
}
</style>
