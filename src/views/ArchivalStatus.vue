<template>
  <div v-if="!contextStore.isLoading" class="mx-10 my-5">
    <Header1 class="mb-4" text="View Course Retention Status" />
    <p class="my-4">
      The <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses/bcourses-course-retention-policy">bCourses Course Retention Policy</OutboundLink> applies to all users of bCourses. bCourses sites for academic courses are retained for seven years after the end of the Academic Year in which the course was offered. Project Sites are subject to removal from the system if they do not have user activity for three years.
      <b v-if="feed.length">The chart below displays which of your courses and project sites are scheduled for removal from bCourses in June 2028.</b>
      <b v-if="!feed.length" id="archival-status-no-courses">You have no courses or project sites currently scheduled for removal.</b>
    </p>
    <p class="my-4">
      The list is updated on a daily basis and may not display accurate information about exempted project sites with recent user activity.
    </p>
    <p class="my-4">
      To learn how to preserve your work and student records or request an opt-out, review the <OutboundLink href="https://berkeley.service-now.com/kb?id=kb_article_view&sysparm_article=KB0012071">bCourses data retention policy knowledge base articles</OutboundLink>.
    </p>
    <div aria-live="polite">
      <v-alert
        v-if="error"
        id="archival-status-error"
        class="my-3"
        density="compact"
        role="none"
        :text="error"
        type="warning"
      />
    </div>
    <table v-if="feed.length" id="archival-status-table" class="border-0 border-b-md border-t-md w-100">
      <caption class="sr-only">Course sites and their archival removal dates</caption>
      <thead class="bg-surface-light">
        <tr>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Course ID</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Course Code</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Course Name</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Role</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Term</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Removal Date</th>
          <th v-if="isMasquerading" class="font-weight-bold px-3 py-2 text-left" scope="col">Opted Out</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="item in feed"
          :id="`archival-status-row-${item.canvasSiteId}`"
          :key="item.canvasSiteId"
          class="border-0 border-t-sm"
        >
          <td class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Course ID:</span>
            <OutboundLink :id="`archival-status-site-id-${item.canvasSiteId}`" :href="item.url" no-wrap>{{ item.canvasSiteId }}</OutboundLink>
          </td>
          <td class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Course Code:</span>{{ item.courseCode }}
          </td>
          <td class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Course Name:</span>{{ item.name }}
          </td>
          <td :id="`archival-status-role-${item.canvasSiteId}`" class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Role:</span>{{ displayRole(item.currentUserRole) }}
          </td>
          <td class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Term:</span>{{ get(item, 'term.name') }}
          </td>
          <td :id="`archival-status-removal-date-${item.canvasSiteId}`" class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Removal Date:</span>{{ removalDate(item) }}
          </td>
          <td v-if="isMasquerading" class="align-middle px-3 py-2">
            <span aria-hidden="true" class="row-label">Opted Out:</span>
            <v-switch
              :id="`archival-status-opt-out-switch-${item.canvasSiteId}`"
              :aria-label="`${item.name}: ${get(item, 'archivalStatus.optedOut') ? 'Opted Out' : 'Not Opted Out'}`"
              color="primary"
              :disabled="pendingSiteIds.has(item.canvasSiteId)"
              density="compact"
              hide-details
              :model-value="get(item, 'archivalStatus.optedOut')"
              @update:model-value="value => toggleOptOut(item, !!value)"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {get, sortBy} from 'lodash'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink.vue'
import {getArchivalStatuses, updateArchivalStatusOptOut} from '@/api/canvas-site'
import {useContextStore} from '@/stores/context'
import {alertScreenReader} from '@/utils'

const contextStore = useContextStore()
const error = ref()
const feed = ref()
const pendingSiteIds = ref(new Set<number>())
// The opt-out toggle is an admin-only tool, reachable only when an admin narrows to a user's context via Canvas masquerade.
const isMasquerading = computed(() => !!contextStore.currentUser.canvasMasqueradingUserId)

onMounted(() => {
  getArchivalStatuses().then(
    data => {
      feed.value = sortBy(data, 'canvasSiteId')
    },
    e => {
      error.value = e
    }
  ).finally(() => contextStore.loadingComplete())
})

const roleDisplayMap: Record<string, string> = {
  'TaEnrollment': 'TA',
  'TeacherEnrollment': 'Teacher',
}

const displayRole = (role: string) => roleDisplayMap[role] || role

const removalDate = (item: any) => {
  // TODO: derive removal date from archivalTier once tier-to-date mapping is finalized
  return get(item, 'archivalStatus.optedOut') ? 'Exempt' : 'June 2028'
}

const toggleOptOut = (item: any, optedOut: boolean) => {
  pendingSiteIds.value.add(item.canvasSiteId)
  updateArchivalStatusOptOut(item.canvasSiteId, optedOut).then(
    (data: any) => {
      item.archivalStatus.optedOut = data.optedOut
      alertScreenReader(`${item.name} is now ${data.optedOut ? 'opted out of' : 'opted in to'} bCourses removal.`)
    },
    e => {
      error.value = e
    }
  ).finally(() => pendingSiteIds.value.delete(item.canvasSiteId))
}
</script>

<style scoped lang="scss">
.align-middle {
  vertical-align: middle;
}
.row-label {
  display: none;
}
@media screen and (max-width: 960px) {
  #archival-status-table {
    thead {
      border: 0;
      clip: rect(0 0 0 0);
      height: 1px;
      margin: -1px;
      overflow: hidden;
      padding: 0;
      position: absolute;
      width: 1px;
    }
    tbody tr {
      border: 0;
      border-bottom: 1pt solid rgba(var(--v-border-color), var(--v-border-opacity));
      display: block;
      padding-bottom: 8px;
      width: 100%;
    }
    tbody td {
      align-items: center;
      border: 0;
      display: flex;
      padding: 4px 12px;
      width: 100%;
    }
  }
  .row-label {
    display: inline-block;
    flex-shrink: 0;
    font-weight: bold;
    width: 40%;
  }
}
</style>
