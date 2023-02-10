<template>
  <div>
    <div v-if="!$_.size(teachingSemesters)" role="alert">
      <p>You are currently not listed as the instructor of record for any courses, so you cannot create a course site in bCourses.</p>
    </div>
    <div v-if="$_.size(teachingSemesters)">
      <div>
        <div id="bc-page-create-course-select-semesters" class="bc-buttonset">
          <h2 class="bc-page-create-course-site-header bc-page-create-course-site-header2">Term</h2>
          <span v-for="(semester, index) in teachingSemesters" :key="index">
            <input
              :id="`semester${index}`"
              type="radio"
              name="semester"
              class="cc-visuallyhidden"
              :aria-selected="currentSemester === semester.slug"
              role="tab"
              @click="switchSemester(semester)"
            />
            <label
              :for="`semester${index}`"
              class="bc-buttonset-button"
              role="button"
              aria-disabled="false"
              :class="{
                'bc-buttonset-button-active': currentSemester === semester.slug,
                'bc-buttonset-corner-left': !index,
                'bc-buttonset-corner-right': (index === $_.size(teachingSemesters) - 1)
              }"
            >
              {{ semester.name }}
            </label>
          </span>
        </div>
      </div>
      <div class="pt-2">
        <h2 class="bc-page-create-course-site-header bc-page-create-course-site-header2">Official Sections</h2>
        <p>All official sections you select below will be put in ONE, single course site.</p>
        <div class="bc-page-help-notice bc-page-create-course-site-help-notice">
          <fa icon="question-circle" class="cc-left bc-page-help-notice-icon"></fa>
          <div class="bc-page-help-notice-left-margin pl-1">
            <button
              class="bc-button-link"
              aria-haspopup="true"
              aria-controls="section-selection-help"
              :aria-expanded="`${toggle.displayHelp}`"
              @click="toggle.displayHelp = !toggle.displayHelp"
            >
              Need help deciding which official sections to select?
            </button>
            <div aria-live="polite">
              <div
                v-if="toggle.displayHelp"
                id="section-selection-help"
                class="bc-page-help-notice-content"
              >
                <p>If you have a course with multiple sections, you will need to decide whether you want to:</p>
                <ol class="bc-page-create-course-site-help-notice-ordered-list">
                  <li>
                    Create one, single course site which includes official sections for both your primary and secondary sections, or
                  </li>
                  <li>
                    Create multiple course sites, perhaps with one for each section, or
                  </li>
                  <li>
                    Create separate course sites based on instruction mode.
                    <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010732#instructionmode">
                      Learn more about instruction modes in bCourses.
                    </OutboundLink>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div>
        <form class="bc-canvas-page-form" @submit="showConfirmation">
          <ul class="bc-page-create-course-site-section-margin">
            <li v-for="course in coursesList" :key="course.course_id" class="bc-sections-course-container bc-sections-course-container-bottom-margin">
              <v-btn
                :aria-expanded="`${course.visible}`"
                class="d-flex p-0"
                variant="link"
                @click="toggleShowHide(course)"
              >
                <div class="toggle-show-hide">
                  <fa :icon="course.visible ? 'caret-down' : 'caret-right'" />
                  <span class="sr-only">Toggle course sections list</span>
                </div>
                <div class="btn-course-title-text pr-2 pt-1">
                  <h3 class="bc-sections-course-title">{{ course.course_code }}<span v-if="course.title">: {{ course.title }}</span></h3>
                </div>
                <div v-if="$_.size(course.sections)" class="btn-course-title-text pt-1">
                  ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                </div>
              </v-btn>
              <v-collapse :id="course.course_id" v-model="course.visible">
                <CourseSectionsTable
                  mode="createCourseForm"
                  :sections="course.sections"
                  :update-selected="updateSelected"
                />
              </v-collapse>
            </li>
          </ul>
          <div class="bc-form-actions">
            <v-btn
              id="bc-page-create-course-site-continue"
              class="bc-canvas-button bc-canvas-button-primary"
              type="button"
              :disabled="!selectedSectionsList.length"
              aria-controls="bc-page-create-course-site-steps-container"
              aria-label="Continue to next step"
              @click="showConfirmation"
            >
              Next
            </v-btn>
            <v-btn
              id="bc-page-create-course-site-cancel"
              aria-label="Cancel and return to Site Creation Overview"
              class="bc-canvas-button"
              variant="link"
              @click="cancel"
            >
              Cancel
            </v-btn>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import IFrameMixin from '@/mixins/IFrameMixin'
import OutboundLink from '@/components/utils/OutboundLink'
import Utils from '@/mixins/Utils'

export default {
  name: 'SelectSectionsStep',
  mixins: [IFrameMixin, Utils],
  components: {CourseSectionsTable, OutboundLink},
  props: {
    coursesList: {
      required: true,
      type: Array
    },
    currentSemester: {
      required: true,
      type: String
    },
    selectedSectionsList: {
      required: true,
      type: Array
    },
    showConfirmation: {
      required: true,
      type: Function
    },
    switchSemester: {
      required: true,
      type: Function
    },
    teachingSemesters: {
      required: true,
      type: Array
    },
    updateSelected: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    linkToSiteOverview: undefined,
    toggle: {
      displayHelp: false
    }
  }),
  methods: {
    cancel() {
      this.$router.push({path: this.isInIframe ? '/canvas/embedded/site_creation' : '/canvas/site_creation'})
    },
    toggleShowHide: course => course.visible = !course.visible
  }
}
</script>

<style scoped lang="scss">
.bc-page-create-course-site-help-notice {
  margin-bottom: 20px;
  .bc-page-create-course-site-help-notice-ordered-list {
    margin-bottom: 10px;
    margin-left: 20px;
  }

  .bc-page-create-course-site-help-notice-paragraph {
    margin-bottom: 7px;
  }
}
.bc-page-create-course-site-form-select-all-option {
  font-size: 12px;
  font-weight: normal;
  margin: 6px 0 4px 2px;
}
.bc-page-create-course-site-header {
  color: $bc-color-headers;
  font-family: $bc-base-font-family;
  font-weight: normal;
  line-height: 40px;
  margin: 5px 0;
}
.bc-page-create-course-site-header2 {
  font-size: 18px;
  margin: 10px 0;
}
.bc-page-create-course-site-section-margin {
  margin: 0;
  overflow: hidden;
}
.btn-course-title-text {
  color: $cc-color-black;
  font-weight: 300;
  text-decoration: none;
}
.toggle-show-hide {
  line-height: 1.8;
  width: 20px;
}
</style>