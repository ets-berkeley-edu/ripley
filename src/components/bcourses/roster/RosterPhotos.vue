<template>
  <ul class="align-content-start page-roster-photos-list ml-3 pt-3">
    <li v-for="student in students" :key="student.student_id" class="list-item pb-3 text-center">
      <div v-if="student.profile_url">
        <a
          :id="`student-profile-url-${student.student_id}`"
          :href="student.profile_url"
          target="_top"
        >
          <RosterPhoto :student="student" />
        </a>
      </div>
      <div v-if="!student.profile_url">
        <a
          :id="`student-profile-url-${student.student_id}`"
          :href="`/${context}/${courseId}/profile/${student.login_id}`"
          target="_top"
        >
          <RosterPhoto :student="student" />
        </a>
      </div>
      <div v-if="!student.email" :id="`student-without-email-${student.student_id}`">
        <div class="page-roster-student-name">{{ student.first_name }}</div>
        <div class="page-roster-student-name font-weight-bolder">{{ student.last_name }}</div>
      </div>
      <div v-if="student.email" class="pt-2">
        <OutboundLink :id="`student-email-${student.student_id}`" :href="`mailto:${student.email}`">
          <div class="sr-only">Email</div>
          <div class="page-roster-student-name">{{ student.first_name }}</div>
          <div class="page-roster-student-name font-weight-bolder">{{ student.last_name }}</div>
        </OutboundLink>
      </div>
      <div :id="`student-id-${student.student_id}`" class="print-hide">
        <span class="sr-only">Student ID: </span>
        {{ student.student_id }}
      </div>
      <div
        v-if="student.terms_in_attendance"
        :id="`student-terms-in-attendance-${student.student_id}`"
        class="page-roster-student-terms print-hide"
      >
        Terms: {{ student.terms_in_attendance }}
      </div>
      <div
        v-if="student.majors"
        :id="`student-majors-${student.student_id}`"
        class="page-roster-student-majors print-hide"
      >
        {{ $_.truncate(student.majors.join(', '), {length: 50}) }}
      </div>
    </li>
  </ul>
</template>

<script>
import OutboundLink from '@/components/utils/OutboundLink'
import RosterPhoto from '@/components/bcourses/roster/RosterPhoto'

export default {
  name: 'RosterPhotos',
  components: {OutboundLink, RosterPhoto},
  props: {
    courseId: {
      required: true,
      type: Number
    },
    students: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    context: 'canvas'
  })
}
</script>

<style scoped lang="scss">
.page-roster-student-name {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-roster-photos-list {
  display: block;
  overflow: hidden;
  width: 100%;
  li {
    display: block;
    float: left;
    height: auto;
    padding: 5px;
    width: 173px;
  }
}

@media print {
  a[href]::after {
    content: none;
  }

  .page-roster-student-name {
    font-size: 18px;
    overflow: visible;
    text-overflow: string;
    white-space: normal;
  }

  .page-roster-photos-list {
    li {
      height: auto;
      margin-top: 15px;
      page-break-inside: avoid;
      width: 220px;
    }
  }
}
</style>
