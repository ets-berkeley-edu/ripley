<template>
  <div v-if="!isLoading" class="canvas-application page-course-official-sections">
    <div v-if="feedFetched && !displayError">
      <div v-if="currentWorkflowStep === 'staging'">
        <MaintenanceNotice course-action-verb="site is updated" />
      </div>

      <h1 id="page-header" class="page-course-official-sections-header1">Official Sections</h1>

      <div v-if="currentWorkflowStep === 'preview'">
        <v-alert
          id="page-course-official-sections-job-status-notice"
          v-model="showAlert"
          class="d-flex align-center justify-space-between my-2"
          closable
          close-label="Hide notice"
          :type="jobStatus !== 'finished' ? 'error' : 'success'"
          density="compact"
          role="alert"
          variant="tonal"
        >
          <div class="font-size-16">{{ jobStatusMessage }}</div>
          <div v-if="$_.size(jobStatusDetails)" class="font-weight-bold py-2">Messages:</div>
          <ul class="px-4" aria-label="error messages">
            <li v-for="(msg, index) in jobStatusDetails" :key="index">{{ msg }}</li>
          </ul>
        </v-alert>

        <h2 id="sr-context-header" class="sr-only">Viewing Sections</h2>

        <div class="page-course-official-sections-sections-area page-course-official-sections-current-sections-white-border">
          <div class="d-flex justify-space-between pb-1">
            <h3 id="course-site-sections-header" class="my-4 pb-4">
              Sections in this Course Site
            </h3>
            <div class="d-flex align-end">
              <v-btn
                v-if="canvasSite.canEdit"
                class="canvas-button canvas-button-primary canvas-no-decoration page-course-official-sections-button"
                @click="changeWorkflowStep('staging')"
              >
                Edit Sections
              </v-btn>
            </div>
          </div>
          <v-row no-gutters class="page-course-official-sections-courses-container">
            <v-col md="12" class="page-course-official-sections-current-course">
              <CourseSectionsTable
                mode="preview"
                :sections="existingCourseSections"
                :row-class-logic="rowClassLogic"
                :row-display-logic="rowDisplayLogic"
              />
            </v-col>
          </v-row>
        </div>
      </div>

      <div v-if="currentWorkflowStep === 'staging'">
        <div class="page-course-official-sections-sections-area page-course-official-sections-current-sections-grey-border">
          <h2 id="sr-context-header" class="sr-only">Managing Sections</h2>

          <div class="page-course-official-sections-current-sections-header">
            <h3 id="course-site-sections" class="page-course-official-sections-existing-sections-header-label">
              Sections in this Course Site
            </h3>
            <div class="text-right">
              <v-btn
                class="canvas-button mx-1"
                aria-label="Cancel section modifications for this course site"
                @click="cancel"
              >
                Cancel
              </v-btn>
              <v-btn
                class="canvas-button canvas-button-primary"
                :disabled="totalStagedCount === 0"
                aria-label="Apply pending modifications to this course site"
                @click="saveChanges"
              >
                Save Changes
              </v-btn>
            </div>
          </div>
          <v-row no-gutters class="page-course-official-sections-courses-container">
            <v-col md="12" class="page-course-official-sections-current-course">
              <CourseSectionsTable
                mode="currentStaging"
                :sections="allSections"
                :unstage-action="unstage"
                :stage-delete-action="stageDelete"
                :stage-update-action="stageUpdate"
                :row-class-logic="rowClassLogic"
                :row-display-logic="rowDisplayLogic"
              ></CourseSectionsTable>
            </v-col>
          </v-row>
          <v-row v-if="totalStagedCount > 12" class="row">
            <v-col md="12" class="text-right">
              <v-btn
                class="canvas-button canvas-no-decoration"
                aria-label="Cancel section modifications for this course site"
                @click="changeWorkflowStep('preview')"
              >
                Cancel
              </v-btn>
              <v-btn
                :disabled="totalStagedCount === 0"
                class="canvas-button canvas-button-primary canvas-no-decoration"
                aria-label="Apply pending modifications to this course site"
                @click="saveChanges"
              >
                Save Changes
              </v-btn>
            </v-col>
          </v-row>
        </div>
        <div class="page-course-official-sections-sections-area">
          <v-row no-gutters>
            <v-col md="12">
              <h3 id="available-sections-header" class="page-course-official-sections-available-sections-header-label">
                All sections available to add to this Course Site
              </h3>
            </v-col>
          </v-row>
          <v-expansion-panels
            v-if="courseSemesterClasses.length > 0"
            v-model="availableSectionsPanel"
            multiple
          >
            <v-expansion-panel
              v-for="course in courseSemesterClasses"
              :id="`sections-course-${course.slug}`"
              :key="course.courseCode"
              class="container px-1 mt-4"
              style="border-radius: 3px !important"
              :value="course.slug"
            >
              <v-expansion-panel-title
                class="d-flex flex-row-reverse height-unset pa-0"
                collapse-icon="mdi-menu-down"
                expand-icon="mdi-menu-right"
              >
                <div class="d-flex flex-wrap flex-grow-1">
                  <h4 id="available-course-header" class="sections-course-title d-flex align-center">
                    {{ course.courseCode }}<span v-if="course.title"> : {{ course.title }}</span>
                  </h4>
                  <span v-if="course.sections && (course.sections.length === 1)" class="sections-course-subtitle text-no-wrap">&nbsp;(1 section)</span>
                  <span v-if="course.sections && (course.sections.length !== 1)" class="sections-course-subtitle text-no-wrap">&nbsp;({{ course.sections.length }} sections)</span>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div v-if="course.sections.length > 1" class="mx-2 mb-1">
                  <v-btn
                    v-if="!allSectionsAdded(course)"
                    id="page-course-official-sections-form-select-all-option-button"
                    aria-label="Add all sections for this course to the list of sections to be added"
                    color="primary"
                    variant="link"
                    @click="addAllSections(course)"
                  >
                    Add All
                  </v-btn>
                  <span v-if="allSectionsAdded(course)" class="d-inline-block px-4 py-2">All Added</span>
                </div>
                <v-row no-gutters>
                  <v-col md="12">
                    <CourseSectionsTable
                      mode="availableStaging"
                      :sections="course.sections"
                      :unstage-action="unstage"
                      :stage-add-action="stageAdd"
                      :row-class-logic="rowClassLogic"
                      :row-display-logic="rowDisplayLogic"
                    ></CourseSectionsTable>
                  </v-col>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </div>

      <div v-if="currentWorkflowStep === 'processing'" aria-live="polite">
        <h2 id="updating-sections-header" class="page-course-official-sections-existing-sections-header-label">
          Updating Official Sections in Course Site
        </h2>
        <div v-if="jobStatus === 'sendingRequest'" class="pending-request-step">
          Sending request...
        </div>
        <div v-if="$_.includes(['queued', 'initializing', 'created'], jobStatus)" class="pending-request-step">
          Request sent. Awaiting processing...
        </div>
        <div v-if="$_.includes(['started', 'importing'], jobStatus)" class="pending-request-step">
          Request received. Updating sections...
        </div>
        <v-progress-linear
          class="mx-4"
          color="primary"
          height="10"
          indeterminate
        />
      </div>
    </div>

    <div v-if="displayError" class="alert-container" role="alert">
      <i class="fa fa-warning canvas-notice-icon"></i>
      <div class="notice-text-container">
        <h1 id="notice-text-header" class="notice-text-header">Error</h1>
        <p>{{ displayError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'

import {courseProvisionJobStatus, getCourseSections, updateSiteSections} from '@/api/canvas-site'

export default {
  name: 'CourseManageOfficialSections',
  components: {
    CourseSectionsTable,
    MaintenanceNotice
  },
  mixins: [Context],
  data: () => ({
    adminActingAs: null,
    adminSemesters: null,
    availableSectionsPanel: [],
    canvasSite: {},
    courseSemesterClasses: [],
    currentWorkflowStep: null,
    displayError: null,
    existingCourseSections: [],
    feedFetched: false,
    isAdmin: false,
    isCourseCreator: false,
    jobStatus: null,
    jobStatusDetails: [],
    jobStatusMessage: '',
    showAlert: false
  }),
  created() {
    this.fetchFeed().then(() => {
      this.$ready()
    })
  },
  watch: {
    jobStatusMessage(msg) {
      if (msg.length) {
        this.showAlert = true
      }
    }
  },
  computed: {
    allSections() {
      return this.$_.flatMap(this.courseSemesterClasses, classItem => {
        return classItem.sections
      })
    },
    totalStagedCount() {
      return this.$_.size(this.$_.filter(this.allSections, section => {
        return (section.isCourseSection && this.$_.includes(this.$_.keys(section), 'stagedState')) || (!section.isCourseSection && section.stagedState === 'add')
      }))
    }
  },
  methods: {
    addAllSections(course) {
      this.$announcer.polite('All sections selected for course: ' + course.title)
      course.sections.forEach(section => {
        if (section.isCourseSection) {
          section.stagedState = null
        } else {
          section.stagedState = 'add'
        }
      })
      this.eventHub.emit('sections-table-updated')
    },
    allSectionsAdded(course) {
      return !this.$_.find(course.sections, section => {
        return (!section.isCourseSection && section.stagedState !== 'add') || (section.isCourseSection && section.stagedState === 'delete')
      })
    },
    cancel() {
      this.changeWorkflowStep('preview')
      this.unstageAll()
    },
    changeWorkflowStep(step) {
      if (step === 'staging') {
        this.$announcer.polite('Edit section form loaded')
        this.jobStatus = null
        this.jobStatusMessage = ''
      } else if (step === 'preview') {
        this.$announcer.polite('Read only section list loaded')
      }
      this.currentWorkflowStep = step
    },
    fetchFeed() {
      return getCourseSections(this.currentUser.canvasSiteId).then(
        response => {
          this.jobProgress = null
          if (response.canvasSite) {
            this.canvasSite = response.canvasSite
            this.refreshFromFeed(response)
          } else {
            this.displayError = 'Failed to retrieve section data.'
          }
        },
        this.$errorHandler
      )
    },
    getStagedSections() {
      const sections = {
        addSections: [],
        deleteSections: [],
        updateSections: []
      }
      let valid = false
      this.courseSemesterClasses.forEach(classItem => {
        classItem.sections.forEach(section => {
          if (section.stagedState === 'add') {
            sections.addSections.push(section.id)
            valid = true
          } else if (section.stagedState === 'delete') {
            sections.deleteSections.push(section.id)
            valid = true
          } else if (section.stagedState === 'update') {
            sections.updateSections.push(section.id)
            valid = true
          }
        })
      })
      return valid ? sections : false
    },
    loadCourseLists(teachingTerms) {
      const courseSemester = this.$_.find(teachingTerms, semester => {
        return (this.$_.toString(semester.termId) === this.$_.toString(this.canvasSite.term.id))
      })
      if (courseSemester) {
        this.availableSectionsPanel = []
        this.courseSemesterClasses = courseSemester.classes
        this.usersClassCount = this.courseSemesterClasses.length
        this.existingCourseSections = this.canvasSite.officialSections
        this.courseSemesterClasses.forEach(classItem => {
          classItem.sections.forEach(teachingSection => {
            teachingSection.courseSlug = classItem.slug
            if (teachingSection.isCourseSection) {
              this.availableSectionsPanel = [classItem.slug]
            }
            this.canvasSite.officialSections.forEach(officialSection => {
              if (officialSection.id === teachingSection.id) {
                if (officialSection.canvasName !== `${teachingSection.courseCode} ${teachingSection.name}`) {
                  this.$_.set(teachingSection, 'nameDiscrepancy', true)
                }
              }
            })
          })
        })
      } else {
        this.usersClassCount = 0
      }
    },
    refreshFromFeed(feed) {
      if (feed.teachingTerms) {
        this.loadCourseLists(feed.teachingTerms)
      }
      this.isAdmin = feed.is_admin
      this.adminActingAs = feed.admin_acting_as
      this.adminSemesters = feed.admin_semesters
      this.isCourseCreator = this.usersClassCount > 0
      this.feedFetched = true
      this.currentWorkflowStep = 'preview'
    },
    rowClassLogic(listMode, section) {
      return {
        'template-sections-table-row-added': (listMode === 'currentStaging' && section.stagedState === 'add'),
        'template-sections-table-row-deleted': (listMode === 'availableStaging' && section.stagedState === 'delete'),
        'template-sections-table-row-disabled': (
          listMode === 'availableStaging' &&
          (
            section.stagedState === 'add' ||
            (section.isCourseSection && section.stagedState !== 'delete')
          )
        )
      }
    },
    rowDisplayLogic(listMode, section) {
      return (listMode === 'preview') ||
        (listMode === 'availableStaging') ||
        (listMode === 'currentStaging' && section && section.isCourseSection && section.stagedState !== 'delete') ||
        (listMode === 'currentStaging' && section && !section.isCourseSection && section.stagedState === 'add')
    },
    saveChanges() {
      const update = this.getStagedSections()
      if (update) {
        this.changeWorkflowStep('processing')
        this.jobStatus = 'sendingRequest'
        updateSiteSections(
          this.currentUser.canvasSiteId,
          update.addSections,
          update.deleteSections,
          update.updateSections
        ).then(
          response => {
            this.backgroundJobId = response.jobId
            this.jobStatus = response.jobStatus
            this.trackSectionUpdateJob()
          }
        ).catch(
          () => {
            this.currentWorkflowStep = 'preview'
            this.jobStatus = 'error'
            this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
            clearInterval(this.exportTimer)
          }
        )
      }
    },
    sectionString(section) {
      return section.courseCode + ' ' + section.name
    },
    stageAdd(section) {
      if (!section.isCourseSection) {
        this.$_.set(section, 'stagedState', 'add')
        this.$announcer.polite('Included in the list of sections to be added')
      } else {
        this.displayError = 'Unable to add ' + this.sectionString(section) + ', as it already exists within the course site.'
      }
    },
    stageDelete(section) {
      if (section.isCourseSection) {
        this.availableSectionsPanel = this.$_.union(this.availableSectionsPanel, [section.courseSlug])
        this.$_.set(section, 'stagedState', 'delete')
        this.$announcer.polite('Included in the list of sections to be deleted')
      } else {
        this.displayError = 'Unable to delete Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
    },
    stageUpdate(section) {
      if (section.isCourseSection) {
        this.availableSectionsPanel = this.$_.union(this.availableSectionsPanel, [section.courseSlug])
        this.$_.set(section, 'stagedState', 'update')
        this.$announcer.polite('Included in the list of sections to be updated')
      } else {
        this.displayError = 'Unable to update Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
    },
    trackSectionUpdateJob() {
      this.exportTimer = setInterval(() => {
        courseProvisionJobStatus(this.backgroundJobId).then(
          response => {
            this.jobStatus = response.jobStatus
            if (!this.jobStatus || !this.$_.includes(['started', 'queued', 'initializing', 'created', 'importing'], this.jobStatus)) {
              clearInterval(this.exportTimer)
              if (this.$_.includes(['imported', 'finished'], this.jobStatus) && response.workflowState === 'imported') {
                this.jobStatusMessage = 'The sections in this course site have been updated successfully.'
              } else {
                this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
                if (response.workflowState === 'imported_with_messages' && this.$_.size(response.messages)) {
                  this.jobStatusDetails = this.$_.map(response.messages, message => this.$_.last(message))
                }
              }
              this.fetchFeed()
            }
          }
        ).catch(
          (error, vm, info) => {
            this.currentWorkflowStep = 'preview'
            this.jobStatus = 'error'
            this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
            clearInterval(this.exportTimer)
            this.$errorHandler((error, vm, info))
          }
        )
      }, 2000)
    },
    unstage(section) {
      if (section.stagedState === 'add') {
        this.availableSectionsPanel = this.$_.union(this.availableSectionsPanel, [section.courseSlug])
        this.$announcer.polite('Removed section from the list of sections to be added')
      } else if (section.stagedState === 'delete') {
        this.$announcer.polite('Removed section from the list of sections to be deleted')
      } else if (section.stagedState === 'update') {
        this.$announcer.polite('Removed section from the list of sections to be updated')
      }
      section.stagedState = null
    },
    unstageAll() {
      this.existingCourseSections = this.canvasSite.officialSections
    }
  }
}
</script>

<style scoped lang="scss">
.pending-request-step {
  margin: 20px 0;
  text-align: center;
}
.page-course-official-sections {
  background-color: $color-white;
  font-family: $body-font-family;
  padding: 25px;
  .button {
    padding: 10px;
  }
  .page-course-official-sections-header1 {
    font-size: 24px;
    font-weight: 400;
    line-height: 30px;
    margin: 15px 0 16px;
  }
  .page-course-official-sections-button {
    white-space: nowrap;
  }
  .page-course-official-sections-courses-container {
    margin: 0;
  }
  .page-course-official-sections-current-sections-grey-border {
    border: $color-grey-area-border-dark solid 1px;
    .page-course-official-sections-courses-container {
      margin-bottom: 15px;
    }
  }
  .page-course-official-sections-current-course {
    margin-left: 0;
    margin-top: 10px;
  }
  .page-course-official-sections-current-sections-white-border {
    border: $color-white solid 1px;
  }
  .page-course-official-sections-sections-area.page-course-official-sections-current-sections-grey-border {
    padding: 15px;
  }
  .page-course-official-sections-sections-area + .page-course-official-sections-sections-area {
    margin-top: 25px;
  }
  .page-course-official-sections-available-sections-header-label {
    font-size: 19px;
  }
  @media #{$small-only} {
    .page-course-official-sections-small-only-align-left {
      text-align: left;
    }
  }
  h3.sections-course-title {
    display: inline !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 20px;
  }
  .sections-course-subtitle {
    font-size: 14px !important;
    font-weight: 400;
    line-height: 20px;
  }
}
</style>

<style lang="scss">
.page-course-official-sections {
  .v-expansion-panel-title__overlay {
    background-color: transparent !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 6px 4px 0px 4px;
  }
  .v-expansion-panel__shadow {
    display: none !important;
  }
  .v-expansion-panel::after {
    border: none !important;
  }
}
</style>
