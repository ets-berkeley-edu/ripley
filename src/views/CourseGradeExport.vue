<template>
  <div v-if="!isLoading">
    <div v-if="appState === 'error'">
      <div class="ma-2 pl-2 pr-4">
        <h1 class="grade-export-header mb-3 mt-2">Error</h1>
        <v-alert
          v-if="error"
          role="alert"
          :text="error"
          type="warning"
        >
          <div v-if="contactSupport" class="py-1">
            If this is not expected, please contact
            <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses support</OutboundLink>
            for further assistance.
          </div>
        </v-alert>
        <div v-if="showRetryOption" class="py-6 text-center">
          <v-btn
            id="retry-selection-btn"
            class="px-10"
            color="primary"
            @click="retrySelection"
          >
            Retry
          </v-btn>
        </div>
      </div>
    </div>
    <v-container v-if="appState === 'preselection'">
      <v-row no-gutters>
        <v-col>
          <BackToGradebook />
          <h1 class="grade-export-header mb-3 mt-2">Before exporting your E-Grades:</h1>
          <h2 class="grade-export-sub-header">1. Select a grading scheme</h2>
          <div class="pb-4 pl-5 pt-2">
            <span v-if="!noGradingStandardEnabled">
              You have already set a grading scheme.
              You can view your grading scheme or select an alternate grading scheme in <CanvasCourseSettingsLink />.
            </span>
            <span v-if="noGradingStandardEnabled">
              Set a grading scheme in <CanvasCourseSettingsLink /> and return once completed.
            </span>
            <div class="pt-1">
              For detailed instructions, see:
              "<OutboundLink href="https://community.canvaslms.com/docs/DOC-26521-how-do-i-enable-a-grading-scheme-for-a-course">How do I enable a grading scheme for a course?</OutboundLink>"
            </div>
          </div>
          <h2 class="grade-export-sub-header">2. Post all assignment grades:</h2>
          <div class="pb-8 pl-5 pt-2">
            <div>
              All assignment grades must be posted (published/unmuted) to ensure that your E-Grades export matches what you see in the gradebook. To confirm that all grades have been posted, review all columns in
              <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">your gradebook</a>
              for any assignments with a crossed-out eye icon
              <span class="nowrap">
                (<img class="grade-export-image-inline" src="@/assets/images/crossed_out_eye.png" alt="Crossed-out eye icon">)
              </span>
              indicating that an assignment has unposted grades.
            </div>
            <div class="pt-2">
              To post unposted grades:
            </div>
            <ol class="ml-6 mb-3 mt-1">
              <li>
                Mouse over the assignment name and select the three vertical dot menu
                <span class="nowrap">(<img class="grade-export-image-inline" src="@/assets/images/three_vertical_dots.png" alt="Three vertical dots">)</span>
              </li>
              <li>Select "Post grades"</li>
              <li>Select whether you wish to post grades for "Everyone," or only "Graded" students and click "Post"</li>
            </ol>
            <div>
              <span>
                For detailed instructions, see: "<OutboundLink href="https://community.canvaslms.com/docs/DOC-17330-41521116619">How do I post grades for an assignment?</OutboundLink>"
              </span>
            </div>
            <div class="py-2">
              <strong>
                In order to avoid errors, we suggest cross-checking final grades in the bCourses gradebook with the
                output CSV to confirm grades were exported as expected.
              </strong>
            </div>
            <div>
              If you have used the
              <OutboundLink href="https://community.canvaslms.com/t5/Instructor-Guide/How-do-I-override-a-student-s-final-grade-in-the-Gradebook/ta-p/946">Final Grade Override</OutboundLink>
              feature to set student grades, the override grades will be included in the export.
            </div>
          </div>
          <div class="text-right">
            <v-btn
              id="cancel-button"
              class="mr-2"
              variant="outlined"
              @click="goToGradebook"
            >
              Cancel<span class="sr-only"> and return to Gradebook</span>
            </v-btn>
            <v-btn
              id="continue-button"
              color="primary"
              :disabled="noGradingStandardEnabled"
              @click="switchToSelection"
            >
              Continue
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <v-container v-if="appState === 'selection'">
      <v-row no-gutters aria-hidden="true">
        <v-col>
          <BackToGradebook />
          <h1
            id="grade-export-header"
            class="grade-export-header mb-3 mt-2"
            tabindex="-1"
          >
            Export E-Grades
          </h1>
          <v-alert
            v-if="filenameDownloaded"
            class="ma-2"
            :closable="true"
            role="alert"
            :text="`The job is done. The file '${filenameDownloaded}' should be in your downloads folder.`"
            type="info"
          />
        </v-col>
      </v-row>
      <v-row class="sr-only">
        <BackToGradebook />
      </v-row>
      <v-row v-if="officialSections.length > 1" no-gutters>
        <v-col md="5">
          <h2 class="pb-2">Select section</h2>
          <div class="pl-3">
            <select
              id="course-sections"
              v-model="selectedSection"
              class="w-50"
            >
              <option :value="null">Choose...</option>
              <option v-for="section in officialSections" :key="section.canvasName" :value="section">
                {{ section.canvasName }}
              </option>
            </select>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <div class="py-4">
            <h2>Configure P/NP grade options</h2>
            <div class="pl-2 pt-2">
              <div class="d-flex">
                <div>
                  <input
                    id="input-enable-pnp-conversion-true"
                    v-model="enablePnpConversion"
                    class="mr-2"
                    type="radio"
                    name="enablePnpCoversion"
                    value="true"
                    @change="selectedPnpCutoffGrade = null"
                  />
                </div>
                <label for="input-enable-pnp-conversion-true">
                  Automatically convert letter grades in the E-Grades export to the student-selected grading option.
                  Please select the lowest passing letter grade.
                </label>
              </div>
              <div class="pb-4 pl-4 pt-1">
                <select
                  id="select-pnp-grade-cutoff"
                  v-model="selectedPnpCutoffGrade"
                  class="grade-export-select-pnp-cutoff"
                  :disabled="enablePnpConversion !== 'true'"
                >
                  <option :value="null">Select a grade</option>
                  <option
                    v-for="grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']"
                    :key="grade"
                    :value="grade"
                  >
                    {{ grade.replace('-', '&minus;').replace('+', '&plus;') }}
                  </option>
                </select>
              </div>
            </div>
            <div class="pl-2 pt-1">
              <div class="d-flex">
                <div>
                  <input
                    id="input-enable-pnp-conversion-false"
                    v-model="enablePnpConversion"
                    class="mr-2"
                    type="radio"
                    name="enablePnpConversion"
                    value="false"
                    @change="selectedPnpCutoffGrade = ''"
                  />
                </div>
                <label for="input-enable-pnp-conversion-false">
                  Do not automatically convert any letter grades to P/NP. I have applied a P/NP grading scheme to
                  all grades in this course, or will manually adjust the grades in the E-Grades Export CSV to
                  reflect the student-selected grading option.
                </label>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <h2>What would you like to download?</h2>
          <div class="pl-2 pt-1">
            <h3>Current Grades</h3>
            <div>
              Current grades download ignores unsubmitted assignments when calculating grades.
              Use this download when you want to excuse unsubmitted assignments.
            </div>
            <div class="py-2">
              <v-btn
                id="download-current-grades-button"
                :disabled="!selectedSection || (enablePnpConversion !== 'false' && !selectedPnpCutoffGrade)"
                color="primary"
                @click="preloadGrades('current')"
              >
                Download Current Grades
              </v-btn>
            </div>
          </div>
          <div class="pl-2 pt-1">
            <h3>Final Grades</h3>
            <div>
              Final grades download counts unsubmitted assignments as zeroes when calculating grades.
              Use this download when you want to include all unsubmitted assignments as part of the grade.
            </div>
            <div class="py-2">
              <v-btn
                id="download-final-grades-button"
                color="primary"
                :disabled="!selectedSection || (enablePnpConversion !== 'false' && !selectedPnpCutoffGrade)"
                @click="preloadGrades('final')"
              >
                Download Final Grades
              </v-btn>
            </div>
          </div>
          <div class="pb-4 pl-2 pt-3">
            For more information, see
            <OutboundLink href="https://berkeley.service-now.com/kb?id=kb_article_view&sysparm_article=KB0010659&sys_kb_id=8b7818e11b1837ccbc27feeccd4bcbbe">From bCourses to E-Grades</OutboundLink>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col v-if="currentUser.canvasSiteId" class="grade-export-grade-link">
          <BackToGradebook />
        </v-col>
      </v-row>
    </v-container>

    <div aria-live="polite">
      <v-container v-if="appState === 'loading'">
        <v-row no-gutters>
          <v-col>
            <h1 class="grade-export-header mb-3 mt-2">Preparing E-Grades for Download</h1>
          </v-col>
        </v-row>
        <div class="align-center d-flex ma-3">
          <v-progress-circular
            class="mr-3"
            color="primary"
            indeterminate
            size="small"
          />
          <div class="job-progress text-subtitle-1">The job {{ jobStatus === 'started' ? 'has' : 'is' }} {{ jobStatus }}</div>
        </div>
      </v-container>
    </div>
  </div>
</template>

<script>
import BackToGradebook from '@/components/bcourses/egrades/BackToGradebook.vue'
import CanvasCourseSettingsLink from '@/components/bcourses/shared/CanvasCourseSettingsLink.vue'
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import {downloadGradeCsv, getExportJobStatus, getExportOptions, prepareGradesCacheJob} from '@/api/egrades-export'
import {getTermName, iframeParentLocation, iframeScrollToTop, putFocusNextTick} from '@/utils'

export default {
  name: 'CourseGradeExport',
  components: {BackToGradebook, CanvasCourseSettingsLink, OutboundLink},
  mixins: [Context],
  data: () => ({
    appState: null,
    error: null,
    backgroundJobId: null,
    contactSupport: false,
    courseUserRoles: [],
    enablePnpConversion: null,
    exportTimer: null,
    filenameDownloaded: false,
    jobStatus: null,
    noGradingStandardEnabled: false,
    officialSections: [],
    selectedPnpCutoffGrade: null,
    selectedSection: null,
    selectedType: null,
    showRetryOption: null
  }),
  beforeUnmount() {
    clearInterval(this.exportTimer)
  },
  created() {
    if (this.currentUser.isTeaching || this.currentUser.isAdmin) {
      this.loadExportOptions().then(() => {
        this.$ready()
      })
    } else {
      this.appState = 'error'
      this.error = 'You must be a teacher in this bCourses course to export to E-Grades CSV.'
      this.$ready()
    }
  },
  methods: {
    downloadGrades() {
      const termId = this.selectedSection.termId
      const termName = getTermName(termId).toLowerCase().replace(' ', '-')
      this.filenameDownloaded = `egrades-${this.selectedType}-${this.selectedSection.id}-${termName}-${this.currentUser.canvasSiteId}.csv`
      downloadGradeCsv(this.filenameDownloaded, this.backgroundJobId).then(() => {
        setTimeout(() => {
          this.filenameDownloaded = null
        }, 30000)
      })
    },
    goToGradebook() {
      const gradebookUrl = `${this.config.canvasApiUrl}/courses/${this.currentUser.canvasSiteId}/grades`
      if (this.$isInIframe) {
        iframeParentLocation(gradebookUrl)
      } else {
        window.location.href = gradebookUrl
      }
    },
    initializePnpCutoffGrades() {
      this.enablePnpConversion = 'true'
      this.selectedPnpCutoffGrade = null
    },
    loadExportOptions() {
      return getExportOptions(false).then(
        data => {
          this.loadSectionTerms(data.sectionTerms)
          if (this.appState !== 'error') {
            this.loadOfficialSections(data.officialSections)
          }
          if (this.appState !== 'error') {
            this.appState = 'preselection'
            if (!data.gradingStandardEnabled) {
              this.noGradingStandardEnabled = true
            }
            this.initializePnpCutoffGrades()
          }
        },
        error => {
          this.appState = 'error'
          this.error = error
        }
      )
    },
    loadOfficialSections(officialSections) {
      if (!officialSections || !officialSections.length) {
        this.appState = 'error'
        this.error = 'None of the sections within this course site are associated with UC Berkeley course catalog sections.'
        this.contactSupport = true
      } else {
        this.officialSections = officialSections
        this.selectedSection = null
      }
    },
    loadSectionTerms(sectionTerms) {
      if (!sectionTerms.length) {
        this.appState = 'error'
        this.error = 'No sections found in this course representing a currently maintained campus term.'
        this.contactSupport = true
      } else if (sectionTerms.length > 1) {
        this.appState = 'error'
        this.error = 'This course site contains sections from multiple terms. Only sections from a single term should be present.'
        this.contactSupport = true
      } else {
        this.sectionTerms = sectionTerms
      }
    },
    preloadGrades(type) {
      this.filenameDownloaded = null
      this.selectedType = type
      this.appState = 'loading'
      this.jobStatus = 'started'
      iframeScrollToTop()
      const pnpCutoff = this.enablePnpConversion === 'false' ? 'ignore' : encodeURIComponent(this.selectedPnpCutoffGrade)
      prepareGradesCacheJob(
        this.selectedType,
        pnpCutoff,
        this.selectedSection.id,
        this.selectedSection.termId
      ).then(
        data => {
          this.backgroundJobId = data.jobId
          this.startExportJob()
        },
        error => {
          this.appState = 'error'
          this.error = error || 'E-Grades job preparation failed.'
          this.showRetryOption = true
          this.contactSupport = true
        }
      )
    },
    retrySelection() {
      this.appState = 'selection'
      this.contactSupport = false
      this.error = null
      this.showRetryOption = false
    },
    startExportJob() {
      this.exportTimer = setInterval(() => {
        getExportJobStatus(this.backgroundJobId).then(
          data => {
            this.jobStatus = data.jobStatus
            if (['canceled', 'deferred', 'failed', 'stopped'].includes(this.jobStatus)) {
              clearInterval(this.exportTimer)
              this.switchToSelection()
              this.error = `Sorry, the eGrades download ${this.jobStatus === 'failed' ? 'has' : 'was'} ${this.jobStatus}.`
              this.contactSupport = true
              this.appState = 'error'
            } else if (this.jobStatus === 'finished') {
              clearInterval(this.exportTimer)
              this.switchToSelection()
              this.$announcer.polite('Downloading export. Export form options presented for an additional download.')
              this.downloadGrades()
            } else if (this.config.isVueAppDebugMode) {
              console.log(`[DEBUG] jobStatus: ${this.jobStatus}`)
            }
          },
          error => {
            this.error = error
          }
        )
      }, 2000)
    },
    switchToSelection() {
      iframeScrollToTop()
      this.appState = 'selection'
      putFocusNextTick('grade-export-header')
    }
  }
}
</script>

<style scoped lang="scss">
.grade-export-header {
  font-size: 23px;
  font-weight: 400;
  padding: 12px 0 0;
}
.grade-export-sub-header {
  font-size: 20px;
  font-weight: 400;
}
.grade-export-image-inline {
  height: 15px;
  margin-bottom: -3px;
}
.grade-export-refresh-button {
  font-size: 11px;
  padding: 1px 5px;
  text-decoration: none;
}
.grade-export-select-pnp-cutoff {
  padding-right: 25px;
  width: fit-content;
}
.job-progress:after {
  animation: ellipsis steps(4,end) 1800ms infinite;
  content: "\2026";
  display: inline-block;
  overflow: hidden;
  vertical-align: bottom;
  width: 0;
  -webkit-animation: ellipsis steps(4,end) 1800ms infinite;
}
@keyframes ellipsis {
  to {
    width: 1.25em;
  }
}
@-webkit-keyframes ellipsis {
  to {
    width: 1.25em;
  }
}
</style>
