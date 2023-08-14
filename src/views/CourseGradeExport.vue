<template>
  <div v-if="!isLoading" class="canvas-application grade-export">
    <div>
      appState: {{ appState }}
    </div>
    <div v-if="appState === 'error'">
      <v-alert
        v-if="error"
        class="ma-2"
        density="compact"
        prominent
        role="alert"
        type="warning"
      >
        <div class="pt-1">
          {{ error }}
        </div>
        <div v-if="showRetryOption" class="pt-2">
          <v-btn id="retry-selection-btn" color="primary" @click="retrySelection">
            Retry
          </v-btn>
        </div>
        <div v-if="contactSupport" class="py-2">
          If this is not expected, please contact
          <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses support</OutboundLink>
          for further assistance.
        </div>
      </v-alert>
      <div v-if="error" role="alert">
      </div>
    </div>
    <v-container v-if="appState === 'preselection'">
      <v-row no-gutters>
        <v-col md="12">
          <div class="align-center d-flex">
            <BackToGradebook />
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h1 class="grade-export-header">Before exporting your E-Grades:</h1>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h2 class="grade-export-sub-header">1. Select a grading scheme:</h2>
          <p v-if="!noGradingStandardEnabled" class="grade-export-download-description">
            You have already set a grading scheme. You can view your grading scheme or select an alternate grading scheme in
            <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/settings#tab-details`" target="_top">Course Settings</a>.
          </p>
          <p v-if="noGradingStandardEnabled" class="grade-export-download-description">
            Set a grading scheme in
            <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/settings#tab-details`" target="_top">Course Settings</a>
            and return once completed.
          </p>
          <p class="grade-export-download-description">
            For detailed instructions, see: "<OutboundLink href="https://community.canvaslms.com/docs/DOC-26521-how-do-i-enable-a-grading-scheme-for-a-course">How do I enable a grading scheme for a course?</OutboundLink>"
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h2 class="grade-export-sub-header">2. Post all assignment grades:</h2>
          <p class="grade-export-download-description">
            All assignment grades must be posted (published/unmuted) to ensure that your E-Grades export matches what you see in the gradebook. To confirm that all grades have been posted, review all columns in
            <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">your gradebook</a>
            for any assignments with a crossed-out eye icon
            <span class="nowrap">
              (<img class="grade-export-image-inline" src="@/assets/images/crossed_out_eye.png" alt="Crossed-out eye icon">)
            </span>
            indicating that an assignment has unposted grades.
          </p>
          <p class="grade-export-download-description">
            To post unposted grades:
          </p>
          <ul class="grade-export-download-list">
            <li>
              Mouse over the assignment name and select the three vertical dot menu
              <span class="nowrap">(<img class="grade-export-image-inline" src="@/assets/images/three_vertical_dots.png" alt="Three vertical dots">)</span>
            </li>
            <li>Select "Post grades"</li>
            <li>Select whether you wish to post grades for "Everyone," or only "Graded" students and click "Post"</li>
          </ul>
          <p class="grade-export-download-description">
            For detailed instructions, see:
            "<OutboundLink href="https://community.canvaslms.com/docs/DOC-17330-41521116619">How do I post grades for an assignment?</OutboundLink>"
          </p>
          <p class="grade-export-download-description">
            <strong>In order to avoid errors, we suggest cross-checking final grades in the bCourses gradebook with the output CSV to confirm grades were exported as expected.</strong>
          </p>
          <p class="grade-export-download-description">
            If you have used the <OutboundLink href="https://community.canvaslms.com/t5/Instructor-Guide/How-do-I-override-a-student-s-final-grade-in-the-Gradebook/ta-p/946">Final Grade Override</OutboundLink> feature to set student grades, the override grades will be included in the export.
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
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
        <v-col md="12">
          <BackToGradebook />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h1
            id="grade-export-header"
            class="grade-export-header"
            tabindex="-1"
          >
            Export E-Grades
          </h1>
        </v-col>
      </v-row>
      <v-row class="sr-only">
        <BackToGradebook />
      </v-row>
      <v-row v-if="officialSections.length > 1" no-gutters>
        <h2 class="grade-export-download-header">Select section</h2>
      </v-row>
      <v-row v-if="officialSections.length > 1" no-gutters>
        <v-col md="5">
          <select
            id="course-sections"
            v-model="selectedSection"
            class="form-input-select w-100"
          >
            <option :value="null">Choose...</option>
            <option v-for="section in officialSections" :key="section.canvasName" :value="section">
              {{ section.canvasName }}
            </option>
          </select>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <h2 class="grade-export-download-header">Configure P/NP grade options</h2>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="grade-export-download-description">
            <label for="input-enable-pnp-conversion-true">
              <input
                id="input-enable-pnp-conversion-true"
                v-model="enablePnpConversion"
                class="mr-2"
                type="radio"
                name="enablePnpCoversion"
                value="true"
                @change="selectedPnpCutoffGrade = null"
              />
              Automatically convert letter grades in the E-Grades export to the student-selected grading option.
              Please select the lowest passing letter grade.
            </label>
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="grade-export-download-description">
            <select
              id="select-pnp-grade-cutoff"
              v-model="selectedPnpCutoffGrade"
              class="form-input-select grade-export-select-pnp-cutoff"
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
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="grade-export-download-description">
            <label for="input-enable-pnp-conversion-true">
              <input
                id="input-enable-pnp-conversion-false"
                v-model="enablePnpConversion"
                class="mr-2"
                type="radio"
                name="enablePnpConversion"
                value="false"
                @change="selectedPnpCutoffGrade = ''"
              />
              Do not automatically convert any letter grades to P/NP. I have applied a P/NP grading scheme to
              all grades in this course, or will manually adjust the grades in the E-Grades Export CSV to
              reflect the student-selected grading option.
            </label>
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <h2 class="grade-export-download-header">What would you like to download?</h2>
      </v-row>
      <v-row no-gutters>
        <h3 class="grade-export-download-header">Current Grades</h3>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="grade-export-download-description">
            Current grades download ignores unsubmitted assignments when calculating grades.
            Use this download when you want to excuse unsubmitted assignments.
          </p>
          <v-btn
            id="download-current-grades-button"
            :disabled="!selectedSection || (enablePnpConversion !== 'false' && !selectedPnpCutoffGrade)"
            color="primary"
            @click="preloadGrades('current')"
          >
            Download Current Grades
          </v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <h3 class="grade-export-download-header">Final Grades</h3>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="grade-export-download-description">
            Final grades download counts unsubmitted assignments as zeroes when calculating grades.
            Use this download when you want to include all unsubmitted assignments as part of the grade.
          </p>
          <v-btn
            id="download-final-grades-button"
            color="primary"
            :disabled="enablePnpConversion !== 'false' && !selectedPnpCutoffGrade"
            @click="preloadGrades('final')"
          >
            Download Final Grades
          </v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <div class="grade-export-more-info-container">
            <p class="grade-export-more-info">
              For more information, see
              <OutboundLink href="https://berkeley.service-now.com/kb?id=kb_article_view&sysparm_article=KB0010659&sys_kb_id=8b7818e11b1837ccbc27feeccd4bcbbe">From bCourses to E-Grades</OutboundLink>
            </p>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col v-if="currentUser.canvasSiteId" md="12" class="grade-export-grade-link">
          <BackToGradebook />
        </v-col>
      </v-row>
    </v-container>

    <div aria-live="polite">
      <v-container v-if="appState === 'loading'">
        <v-row no-gutters>
          <v-col md="5">
            <h1 class="grade-export-header">Preparing E-Grades for Download</h1>
          </v-col>
        </v-row>
        <div v-if="!jobStatus" class="grade-export-notice-pending-request">
          <v-progress-circular
            class="mr-2"
            color="primary"
            indeterminate
          />
          Sending preparation request...
        </div>
        <div v-if="jobStatus === 'New'" class="grade-export-notice-pending-request">
          <v-progress-circular
            class="mr-2"
            color="primary"
            indeterminate
          />
          Preparation request sent. Awaiting processing....
        </div>
        <div v-if="jobStatus">
          <ProgressBar :percent-complete-rounded="percentCompleteRounded" />
        </div>
      </v-container>
    </div>
  </div>
</template>

<script>
import BackToGradebook from '@/components/bcourses/egrades/BackToGradebook.vue'
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import ProgressBar from '@/components/bcourses/shared/ProgressBar'
import {downloadGradeCsv, getExportJobStatus, getExportOptions, prepareGradesCacheJob} from '@/api/canvas-site'
import {iframeParentLocation, iframeScrollToTop, putFocusNextTick} from '@/utils'

export default {
  name: 'CourseGradeExport',
  components: {BackToGradebook, OutboundLink, ProgressBar},
  mixins: [Context],
  data: () => ({
    appState: null,
    error: null,
    backgroundJobId: null,
    contactSupport: false,
    courseUserRoles: [],
    enablePnpConversion: null,
    exportTimer: null,
    jobStatus: null,
    noGradingStandardEnabled: false,
    officialSections: [],
    percentCompleteRounded: null,
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
      const pnpCutoff = this.enablePnpConversion === 'false' ? 'ignore' : encodeURIComponent(this.selectedPnpCutoffGrade)
      console.log(`downloadGrades:
        selectedType: ${this.selectedType}
        selectedSection.id: ${this.selectedSection.id}
        selectedSection.termId: ${this.selectedSection.termId}
        pnpCutoff: ${pnpCutoff}
      `)
      downloadGradeCsv(
        this.selectedType,
        this.selectedSection.id,
        this.selectedSection.termId,
        pnpCutoff
      )
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
      this.selectedType = type
      this.appState = 'loading'
      this.jobStatus = 'New'
      iframeScrollToTop()
      console.log(`preloadGrades:
        selectedType: ${type}
      `)
      prepareGradesCacheJob(this.currentUser.canvasSiteId).then(
        data => {
          console.log(`post-prepareGradesCacheJob:
            data: ${data}
          `)
          if (data.jobRequestStatus === 'Success') {
            this.backgroundJobId = data.jobId
            this.startExportJob()
          } else {
            this.appState = 'error'
            this.error = 'Grade download request failed'
            this.showRetryOption = true
            this.contactSupport = false
          }
        },
        error => {
          this.error = error
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
      console.log(`startExportJob:
        currentUser.canvasSiteId: ${this.currentUser.canvasSiteId, this.backgroundJobId}
        backgroundJobId: ${this.backgroundJobId}
      `)
      this.exportTimer = setInterval(() => {
        getExportJobStatus(this.currentUser.canvasSiteId, this.backgroundJobId).then(
          data => {
            console.log(`post-getExportJobStatus:
              data: ${data}
            `)
            this.jobStatus = data.jobStatus
            this.percentCompleteRounded = Math.round(data.percentComplete * 100)
            if (this.jobStatus !== 'New' && this.jobStatus !== 'Processing') {
              this.percentCompleteRounded = null
              clearInterval(this.exportTimer)
              this.$announcer.polite('Downloading export. Export form options presented for an additional download.')
              this.switchToSelection()
              this.downloadGrades()
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
.grade-export {
  p {
    font-size: 14px;
    font-weight: 300;
    margin-bottom: 10px;
  }
  .grade-export-button-link {
    font-weight: 300;
  }
  .grade-export-header {
    font-size: 23px;
    font-weight: 400;
    padding: 12px 0 0;
  }
  .grade-export-sub-header {
    font-size: 20px;
    font-weight: 400;
    margin: 15px 0;
  }
  .grade-export-download-button-container {
    border: $color-off-black 1px solid;
    margin: 10px;
  }
  .grade-export-download-description {
    line-height: 18px;
    margin-bottom: 10px;
    padding: 4px 0;
  }
  .grade-export-download-header {
    font-size: 20px;
    font-weight: 400;
    margin: 30px 0 5px;
  }
  .grade-export-download-list {
    line-height: 18px;
    list-style-position: inside;
    list-style-type: disc;
    margin-bottom: 10px;
    padding: 4px 0;
  }
  .grade-export-image-inline {
    height: 15px;
    margin-bottom: -3px;
  }
  .grade-export-more-info-container {
    margin-top: 40px;
  }
  .grade-export-more-info {
    margin: 20px 0;
  }
  .grade-export-section {
    margin: 10px 0;
  }
  .grade-export-form-label {
    display: inline-block;
    margin: 8px 0;
  }
  .grade-export-notice-pending-request {
    margin: 15px auto;
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
}
</style>
