<template>
  <div v-if="!contextStore.isLoading" class="py-3 px-6">
    <Header1 class="mb-2 mt-0" :text="canvasSite ? `Manage official sections for ${canvasSite.name}` : 'Manage Official Sections'" />
    <div aria-live="polite">
      <v-alert
        v-if="error"
        id="error-alert"
        class="my-3"
        density="compact"
        role="none"
        :text="error"
        type="warning"
      />
    </div>
    <div v-if="feedFetched">
      <h2 id="bcourses-site-header" class="pt-3">bCourses Site</h2>
      <div class="pl-3 pb-6 pt-1">
        <OutboundLink
          id="link-to-canvas-site"
          aria-describedby="bcourses-site-header"
          :href="canvasSite.url"
        >
          <span class="text-subtitle-2">
            <span v-if="get(canvasSite.term, 'name')">
              {{ canvasSite.term.name }}&nbsp;
            </span>
            <span>
              {{ canvasSite.courseCode }}
            </span>
          </span>
        </OutboundLink>
      </div>
      <h2 id="official-sections-header" class="mb-2">Official Sections</h2>
      <div v-if="currentWorkflowStep === 'preview'">
        <div aria-live="polite">
          <v-alert
            id="page-course-official-sections-job-status-notice"
            v-model="showAlert"
            class="my-2"
            closable
            close-label="Hide notice"
            density="compact"
            role="none"
            :type="jobStatus !== 'finished' ? 'error' : 'success'"
            variant="tonal"
          >
            <div class="font-size-16">{{ jobStatusMessage }}</div>
          </v-alert>
        </div>
        <CourseSectionsTable
          id="template-sections-table-preview"
          mode="preview"
          :row-class-logic="rowClassLogic"
          :row-display-logic="rowDisplayLogic"
          :sections="existingCourseSections"
          table-caption="Official sections in this course. To edit, use the Edit Sections button above."
        />
      </div>
      <div v-if="currentWorkflowStep === 'staging'">
        <h3 class="sr-only">Managing Sections</h3>
        <CourseSectionsTable
          mode="currentStaging"
          :row-class-logic="rowClassLogic"
          :row-display-logic="rowDisplayLogic"
          :sections="allSections"
          :stage-delete-action="stageDelete"
          :stage-update-action="stageUpdate"
          table-caption="Official sections in this course. Use the buttons in the Actions column to make changes."
          :unstage-action="unstage"
        />
        <div v-if="totalStagedCount > 12" class="pb-2">
          <v-btn
            id="official-sections-secondary-save-btn"
            aria-label="Apply pending modifications to this course site"
            class="mt-4 ml-3 w-100 w-sm-auto text-no-wrap"
            color="primary"
            :disabled="totalStagedCount === 0"
            @click="saveChanges"
          >
            Save Changes
          </v-btn>
          <v-btn
            id="official-sections-secondary-cancel-btn"
            aria-label="Cancel section modifications for this course site"
            class="mt-4 ml-3 w-100 w-sm-auto"
            variant="tonal"
            @click="cancel"
          >
            Cancel<span class="sr-only"> edit sections</span>
          </v-btn>
        </div>
        <h2 class="mb-2 mt-5">Sections Available to Add</h2>
        <div>
          <v-expansion-panels
            v-if="courseSemesterClasses.length > 0"
            v-model="availableSectionsPanel"
            multiple
          >
            <v-expansion-panel
              v-for="(course, index) in courseSemesterClasses"
              :id="`sections-course-${course.slug}`"
              :key="index"
              bg-color="blue-lighten-5"
              :value="course.slug"
            >
              <v-expansion-panel-title :id="`sections-course-${course.slug}-btn`">
                <template #actions="{ expanded }">
                  <v-icon :icon="expanded ? mdiMenuDown : mdiMenuRight" />
                </template>
                <h3
                  :id="`sections-course-${course.slug}-available-course-header`"
                  class="sections-course-title"
                >
                  {{ course.courseCode }}
                  <span v-if="course.title">&mdash; {{ course.title }}</span>
                  <span v-if="size(course.sections)">
                    ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                  </span>
                </h3>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-btn
                  v-if="course.sections.length > 1"
                  :id="`course-${index}-add-all-sections-btn`"
                  aria-label="Add all sections listed below to the course site"
                  class="mx-4"
                  :color="allSectionsAdded(course) ? '' : 'primary'"
                  :disabled="allSectionsAdded(course)"
                  @click="addAllSections(course)"
                >
                  <span v-if="allSectionsAdded(course)">All Added</span>
                  <span v-else>Add All</span>
                </v-btn>
                <CourseSectionsTable
                  :id="`template-sections-table-availableStaging-${index}`"
                  class="mb-1 mt-3 mx-4 mx-lg-0 mx-xl-4"
                  mode="availableStaging"
                  :row-class-logic="rowClassLogic"
                  :row-display-logic="rowDisplayLogic"
                  :sections="course.sections"
                  :stage-add-action="stageAdd"
                  :table-caption="availableSectionsTableCaption(course)"
                  :unstage-action="unstage"
                />
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </div>
      <div v-if="currentWorkflowStep === 'processing'" aria-live="polite">
        <h3 id="updating-sections-header" class="mt-6 text-no-wrap">
          Updating Official Sections in Course Site
        </h3>
        <div class="py-3">
          <div v-if="jobStatus === 'sendingRequest'">
            Sending request...
          </div>
          <div v-if="'queued' === jobStatus">
            Request sent. Awaiting processing...
          </div>
          <div v-if="'started' === jobStatus">
            Request received. Updating sections...
          </div>
          <div v-if="'finished' === jobStatus">
            Finishing up...
          </div>
        </div>
        <v-progress-linear
          color="primary"
          height="10"
          indeterminate
        />
      </div>
      <div v-if="canvasSite.canEdit" class="mb-5">
        <div v-if="currentWorkflowStep === 'preview'" class="d-flex flex-wrap justify-end">
          <v-btn
            id="official-sections-edit-btn"
            class="mt-4 ml-3 w-100 w-sm-auto text-no-wrap"
            color="primary"
            @click="changeWorkflowStep('staging')"
          >
            Edit Sections
          </v-btn>
          <v-btn
            id="official-sections-cancel"
            aria-label="Cancel and return to Manage Sites"
            class="mt-4 ml-3 w-100 w-sm-auto"
            variant="tonal"
            @click="exit"
          >
            Cancel
          </v-btn>
        </div>
        <div v-if="currentWorkflowStep === 'staging'" class="d-flex flex-wrap justify-end">
          <v-btn
            id="official-sections-save-btn"
            aria-label="Apply pending modifications to this course site"
            class="mt-4 ml-3 w-100 w-sm-auto text-no-wrap"
            color="primary"
            :disabled="totalStagedCount === 0"
            @click="saveChanges"
          >
            Save Changes
          </v-btn>
          <v-btn
            id="official-sections-cancel-btn"
            aria-label="Cancel section modifications for this course site"
            class="mt-4 ml-3 w-100 w-sm-auto"
            variant="tonal"
            @click="cancel"
          >
            Cancel<span class="sr-only"> edit sections</span>
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {each, filter, find, flatMap, get, includes, set, size, toString, union, unset} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable.vue'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink.vue'
import {alertScreenReader, pluralize, putFocusNextTick, toInt} from '@/utils'
import {courseProvisionJobStatus, getCourseSections, updateSiteSections} from '@/api/canvas-site'
import {useContextStore} from '@/stores/context'
import {computed, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {Course, Section, SectionEdit, Semester} from '@/lib/types'

const contextStore = useContextStore()
const availableSectionsPanel = ref<string[]>([])
const backgroundJobId = ref()
const canvasSite = ref()
const canvasSiteId = ref()
const courseSemesterClasses = ref<Course<SectionEdit>[]>([])
const currentWorkflowStep = ref()
const error = ref()
const existingCourseSections = ref([])
const exportTimer = ref()
const feedFetched = ref<boolean>()
const jobStatus = ref()
const jobStatusMessage = ref('')
const router = useRouter()

const allSections = computed<Section[]>(() => {
  return flatMap(courseSemesterClasses.value, c => c.sections)
})

const showAlert = computed({
  get: () => {
    return !!size(jobStatusMessage.value)
  },
  set: (show: boolean) => {
    if (!show) {
      jobStatusMessage.value = ''
    }
  }
})

const totalStagedCount = computed(() => {
  return size(filter(allSections.value, (section: SectionEdit) => {
    const isCourseSection = section.isCourseSection
    return (isCourseSection && get(section, 'stagedState')) || (!isCourseSection && section.stagedState === 'add')
  }))
})

onMounted(() => {
  canvasSiteId.value = toInt(get(useRoute(), 'params.canvasSiteId'))
  fetchFeed().finally(() => contextStore.loadingComplete())
})

const addAllSections = (course: Course<SectionEdit>) => {
  each(course.sections, section => section.stagedState = section.isCourseSection ? undefined : 'add')
  alertScreenReader(`Linked all ${course.title} sections to the course site.`)
  putFocusNextTick(`sections-course-${course.slug}-btn`)
  contextStore.eventHub.emit('sections-table-updated')
}

const allSectionsAdded = (course: Course<SectionEdit>) => {
  return !find(course.sections, section => {
    return (!section.isCourseSection && section.stagedState !== 'add') || (section.isCourseSection && section.stagedState === 'delete')
  })
}

const availableSectionsTableCaption = (course: Course<SectionEdit>) => {
  let caption = 'Official sections in this course.'
  if (course.sections.length > 1) {
    caption += `${allSectionsAdded(course) ? ' All sections linked to the course site.' : ' Use the Add All button above, or '}`
  }
  caption += 'Use the buttons in the Actions column to make changes.'
  return caption
}

const cancel = () => {
  unstageAll()
  changeWorkflowStep('preview')
  alertScreenReader('Canceled. Nothing saved.', 'assertive')
}

const changeWorkflowStep = (step: string) => {
  currentWorkflowStep.value = step
  if (step === 'staging') {
    alertScreenReader('Edit sections form loaded')
    jobStatus.value = null
    jobStatusMessage.value = ''
    putFocusNextTick(getStagingEntryFocusTarget())
  } else if (step === 'preview') {
    alertScreenReader('Read-only sections list loaded')
    if (canvasSite.value.canEdit) {
      putFocusNextTick('official-sections-edit-btn')
    }
  }
}

const exit = () => {
  router.push({path: '/manage_sites'})
}

const fetchFeed = () => {
  return getCourseSections(canvasSiteId.value).then(data => {
    if (data.canvasSite) {
      canvasSite.value = data.canvasSite
      if (data.teachingTerms) {
        loadCourseLists(data.teachingTerms)
      }
      feedFetched.value = true
      changeWorkflowStep('preview')
    } else {
      error.value = 'Failed to retrieve section data.'
    }
  }, data => {
    error.value = data
  })
}

const loadCourseLists = (teachingTerms) => {
  const courseSemester: Semester<SectionEdit> = find(teachingTerms, semester => {
    return (toString(semester.termId) === toString(canvasSite.value.term.id))
  })
  if (courseSemester) {
    availableSectionsPanel.value = []
    courseSemesterClasses.value = courseSemester.classes
    existingCourseSections.value = canvasSite.value.officialSections
    each(courseSemesterClasses.value, classItem => {
      each(classItem.sections, teachingSection => {
        teachingSection.courseSlug = classItem.slug
        if (teachingSection.isCourseSection) {
          availableSectionsPanel.value = [classItem.slug]
        }
        each(canvasSite.value.officialSections, officialSection => {
          if (officialSection.id === teachingSection.id) {
            if (officialSection.canvasName !== `${teachingSection.courseCode} ${teachingSection.name}`) {
              set(teachingSection, 'nameDiscrepancy', true)
            }
          }
        })
      })
    })
  }
}

const rowClassLogic = (listMode: string, section: SectionEdit) => {
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
}

const rowDisplayLogic = (listMode: string, section: SectionEdit) => {
  return (listMode === 'preview') ||
    (listMode === 'availableStaging') ||
    (listMode === 'currentStaging' && section && section.isCourseSection && section.stagedState !== 'delete') ||
    (listMode === 'currentStaging' && section && !section.isCourseSection && section.stagedState === 'add')
}

const saveChanges = () => {
  type Bundle = {addSections: string[], deleteSections: string[], updateSections: string[]}
  const sections: Bundle = {
    addSections: [],
    deleteSections: [],
    updateSections: []
  }
  let valid = false
  each(courseSemesterClasses.value, classItem => {
    each(classItem.sections, section => {
      if (section.stagedState === 'add') {
        sections.addSections.push(toString(section.id))
        valid = true
      } else if (section.stagedState === 'delete') {
        sections.deleteSections.push(toString(section.id))
        valid = true
      } else if (section.stagedState === 'update') {
        sections.updateSections.push(toString(section.id))
        valid = true
      }
    })
  })
  if (valid) {
    changeWorkflowStep('processing')
    jobStatus.value = 'sendingRequest'
    jobStatusMessage.value = ''
    updateSiteSections(
      canvasSiteId.value,
      sections.addSections,
      sections.deleteSections,
      sections.updateSections
    ).then(
      data => {
        backgroundJobId.value = data.jobId
        jobStatus.value = data.jobStatus
        trackSectionUpdateJob()
      }
    ).catch(
      () => {
        changeWorkflowStep('preview')
        jobStatus.value = 'error'
        jobStatusMessage.value = 'An error has occurred with your request. Please try again or contact bCourses support.'
        clearInterval(exportTimer.value)
      }
    )
  }
}

const sectionString = (section: Section) => section.courseCode + ' ' + section.name

const getStagingEntryFocusTarget = () => {
  const firstLinkedSection = find(allSections.value, section => section.isCourseSection && section.stagedState !== 'delete')
  if (firstLinkedSection) {
    return `section-${firstLinkedSection.id}-unlink-btn`
  }
  return 'official-sections-header'
}

const stageAdd = (section: SectionEdit) => {
  if (!section.isCourseSection) {
    section.stagedState = 'add'
  } else {
    error.value = `Cannot link ${sectionString(section)} because it is already linked to the course site.`
  }
  return totalStagedCount.value
}

const stageDelete = (section: SectionEdit) => {
  if (section.isCourseSection) {
    availableSectionsPanel.value = union(availableSectionsPanel.value, [section.courseSlug])
    section.stagedState = 'delete'
  } else {
    error.value = `Cannot unlink ${sectionString(section)} because it is not linked to the course site.`
  }
  return totalStagedCount.value
}

const stageUpdate = (section: SectionEdit) => {
  if (section.isCourseSection) {
    availableSectionsPanel.value = union(availableSectionsPanel.value, [section.courseSlug])
    section.stagedState = 'update'
    alertScreenReader(`Updated ${sectionString(section)}.`)
  } else {
    error.value = `Cannot update ${sectionString(section)} because it is not linked to the course site.`
  }
}

const trackSectionUpdateJob = () => {
  exportTimer.value = setInterval(() => {
    courseProvisionJobStatus(backgroundJobId.value).then(
      data => {
        if (data.jobStatus !== jobStatus.value) {
          jobStatus.value = data.jobStatus
        } else {
          alertScreenReader(`Still ${includes(['sendingRequest', 'queued'], jobStatus.value) ? 'waiting' : 'processing'}`)
        }
        if (!(includes(['started', 'queued'], jobStatus.value))) {
          clearInterval(exportTimer.value)
          if (jobStatus.value === 'finished') {
            alertScreenReader('Success.', 'assertive')
            jobStatusMessage.value = 'The sections in this course site have been updated successfully.'
          } else {
            alertScreenReader('Error', 'assertive')
            jobStatusMessage.value = 'An error has occurred with your request. Please try again or contact bCourses support.'
          }
          fetchFeed()
        }
      }
    ).catch(
      () => {
        changeWorkflowStep('preview')
        alertScreenReader('Error.', 'assertive')
        jobStatus.value = 'error'
        jobStatusMessage.value = 'An error has occurred with your request. Please try again or contact bCourses support.'
        clearInterval(exportTimer.value)
      }
    )
  }, 4000)
}

const unstage = (section: SectionEdit) => {
  if (section.stagedState === 'add') {
    availableSectionsPanel.value = union(availableSectionsPanel.value, [section.courseSlug])
  } else if (section.stagedState === 'update') {
    alertScreenReader(`${sectionString(section)} will not be updated.`)
  }
  section.stagedState = undefined
  return totalStagedCount.value
}

const unstageAll = () => {
  return each(allSections.value, section => {
    unset(section, 'stagedState')
  })
}
</script>

<style scoped lang="scss">
.sections-course-title {
  font-size: 1.125rem !important;
  font-weight: 400 !important;
  line-height: 1.125rem !important;
}
:deep(.v-expansion-panel-text__wrapper) {
  padding: 8px 0 16px;
}
</style>
