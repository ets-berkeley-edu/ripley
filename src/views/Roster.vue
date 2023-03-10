<template>
  <div v-if="!isLoading" class="page-roster">
    <v-container v-if="roster && !error" fluid>
      <v-row align-v="start" class="page-roster print-hide roster-search pb-3" no-gutters>
        <v-col class="pb-2 pr-2" sm="3">
          <v-text-field
            id="roster-search"
            v-model="search"
            aria-label="Search people by name or SID"
            placeholder="Search People"
            size="lg"
          />
        </v-col>
        <v-col class="pb-2" sm="3">
          <div v-if="roster.sections">
            <v-select
              id="section-select"
              v-model="section"
              aria-label="Search specific section (defaults to all sections)"
              :options="roster.sections"
              size="lg"
              text-field="name"
              value-field="ccn"
              @change="updateStudentsFiltered"
            >
              <template #first>
                <v-select-option :value="null">All sections</v-select-option>
              </template>
            </v-select>
          </div>
        </v-col>
        <v-col cols="auto" sm="6">
          <div class="d-flex flex-wrap float-right">
            <div class="pr-2">
              <v-btn
                id="download-csv"
                class="text-light"
                :disabled="!roster.students.length"
                size="md"
                variant="outline-secondary"
                @click="downloadCsv"
              >
                <fa class="text-secondary" icon="download" size="1x" /> Export<span class="sr-only"> CSV file</span>
              </v-btn>
            </div>
            <div>
              <v-btn
                id="print-roster"
                variant="outline-secondary"
                @click="printRoster"
              >
                <v-icon icon="mdi-print" size="1x" variant="primary" /> Print<span class="sr-only"> roster of students</span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col sm="12">
          <RosterPhotos v-if="studentsFiltered.length" :course-id="canvasCourseId" :students="studentsFiltered" />
          <div v-if="!studentsFiltered.length">
            <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
            Students have not yet signed up for this class.
          </div>
        </v-col>
      </v-row>
    </v-container>
    <div v-if="!roster & !error">
      <v-progress-circular
        color="primary"
        indeterminate
      />
      <div aria-live="polite" class="pt-5 text-center w-100" role="alert">
        Downloading rosters. This may take a minute for larger classes.
      </div>
    </div>
    <div v-if="error" role="alert">
      <v-icon icon="mdi-exclamation-triangle" class="icon-red" />
      You must be a teacher in this bCourses course to view official student rosters.
    </div>
    <div v-if="!error && roster && !roster.sections" role="alert">
      <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
      There are no currently maintained official sections in this course site.
    </div>
    <div v-if="!error && roster && roster.sections && !roster.students" role="alert">
      <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
      Students have not yet signed up for this class.
    </div>
  </div>
</template>

<script>
import CanvasUtils from '@/mixins/CanvasUtils'
import Context from '@/mixins/Context'
import RosterPhotos from '@/components/bcourses/roster/RosterPhotos'
import Utils from '@/mixins/Utils'
import {getCourseUserRoles, getRoster, getRosterCsv} from '@/api/course'

export default {
  name: 'Roster',
  mixins: [CanvasUtils, Context, Utils],
  components: {RosterPhotos},
  watch: {
    search() {
      this.updateStudentsFiltered()
    }
  },
  data: () => ({
    canvasCourseId: undefined,
    error: null,
    search: undefined,
    roster: undefined,
    section: null,
    studentsFiltered: [],
  }),
  created() {
    this.getCanvasCourseId()
    if (this.canvasCourseId === 'embedded') {
      getCourseUserRoles(this.canvasCourseId).then(
        data => {
          this.canvasCourseId = data.courseId
          this.$ready('Roster Photos')
        },
        this.$errorHandler
      )
    } else {
      this.$ready('Roster Photos')
    }
  },
  mounted() {
    getRoster(this.canvasCourseId).then(data => {
      this.roster = data
      const students = []
      this.$_.each(this.roster.students, student => {
        student.idx = this.idx(`${student.first_name} ${student.last_name} ${student.student_id}`)
        students.push(student)
      })
      this.studentsFiltered = this.sort(students)
      this.$ready('Roster')
    }, error => {
      this.error = error
      this.$ready('Roster')
    })
  },
  methods: {
    downloadCsv() {
      getRosterCsv(this.canvasCourseId).then(
        () => {
          this.$announcer.polite(`${this.roster.canvas_course.name} CSV downloaded`)
        },
        this.$errorHandler
      )
    },
    idx(value) {
      return value && this.$_.trim(value).replace(/[^\w\s]/gi, '').toLowerCase()
    },
    printRoster() {
      this.printPage(`${this.idx(this.roster.canvas_course.name).replace(/\s/g, '-')}_roster`)
    },
    sort(students) {
      return this.$_.sortBy(students, s => s.last_name)
    },
    updateStudentsFiltered() {
      const snippet = this.idx(this.search)
      const students = this.$_.filter(this.roster.students, student => {
        let idxMatch = !snippet || student.idx.includes(snippet)
        return idxMatch && (!this.section || this.$_.includes(student.section_ccns, this.section.toString()))
      })
      this.studentsFiltered = this.sort(students)
      let alert = this.section ? `Showing the ${this.studentsFiltered.length} students of section ${this.section}` : 'Showing all students'
      if (snippet) {
        alert += ` with '${snippet}' in name.`
      }
      this.$announcer.polite(alert)
    }
  }
}
</script>

<style scoped lang="scss">
button {
  height: 38px;
  width: 76px;
}
.page-roster {
  background: $color-white;
  overflow: hidden;
  padding: 20px;

  .roster-search {
    background: transparent;
    border: 0;
    border-bottom: 1px solid $color-very-light-grey;
    margin: 0 0 15px;
    overflow: hidden;
    padding: 7px 0 5px;
  }

  @media print {
    overflow: visible;
    padding: 0;
    .roster-search {
      display: none;
    }
  }
}
</style>
