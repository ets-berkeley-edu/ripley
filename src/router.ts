import auth from '@/auth'
const Acheron = () => import('./views/Acheron.vue')
const BaseLTI = () => import('./layouts/lti/BaseLTI.vue')
const BaseStandalone = () => import('./layouts/standalone/BaseStandalone.vue')
const CanvasSiteSummary = () => import('./views/CanvasSiteSummary.vue')
const CourseAddUser = () => import('./views/CourseAddUser.vue')
const CourseGradeDistribution = () => import('./views/CourseGradeDistribution.vue')
const CourseGradeExport = () => import('./views/CourseGradeExport.vue')
const CreateCourseSite = () => import('./views/CreateCourseSite.vue')
const CreateProjectSite = () => import('./views/CreateProjectSite.vue')
const Error = () => import('./views/Error.vue')
const Login = () => import('./views/Login.vue')
const MailingListCreate = () => import('./views/MailingListCreate.vue')
const MailingListSelectCourse = () => import('./views/MailingListSelectCourse.vue')
const MailingListUpdate = () => import('./views/MailingListUpdate.vue')
const ManageOfficialSections = () => import('./views/ManageOfficialSections.vue')
const ManageSites = () => import('./views/ManageSites.vue')
const Profile = () => import('./views/Profile.vue')
const Roster = () => import('./views/Roster.vue')
const SendWelcomeEmail = () => import('./views/SendWelcomeEmail.vue')
const UserProvision = () => import('./views/UserProvision.vue')
const Welcome = () => import('@/views/Welcome.vue')
const WelcomeAdmin = () => import('@/views/WelcomeAdmin.vue')

import {capitalize} from 'lodash'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import {logOut} from '@/api/auth'
import {useContextStore} from '@/stores/context'

const isInIframe = window.parent.frames.length
const BaseView = () => import(isInIframe ? '@/layouts/lti/BaseLTI.vue' : '@/layouts/standalone/BaseStandalone.vue')

const routes:RouteRecordRaw[] = [
  {
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = useContextStore().currentUser
      currentUser.isAuthenticated ? next({path: currentUser.isAdmin ? '/admin' : '/welcome'}) : next()
    },
    children: [
      {
        component: Login,
        name: 'Login',
        path: '',
      }
    ],
    component: BaseStandalone,
    path: '/',
  },
  {
    beforeEnter: auth.requiresAuthenticated,
    component: BaseView,
    path: '/',
    children: [
      {
        component: Acheron,
        name: 'Acheron (LV-426)',
        path: '/Acheron'
      },
      {
        component: CanvasSiteSummary,
        meta: {
          announcer: {
            skip: true
          }
        },
        path: '/canvas_site/:id'
      },
      {
        component: CourseAddUser,
        name: 'Find a Person to Add',
        path: '/add_user'
      },
      {
        component: CourseGradeDistribution,
        name: 'Grade Distribution',
        path: '/grade_distribution'
      },
      {
        component: CourseGradeExport,
        name: 'E-Grade Export',
        path: '/export_grade'
      },
      {
        component: ManageOfficialSections,
        name: 'Manage Official Sections',
        path: '/official_sections/:canvasSiteId'
      },
      {
        component: Profile,
        name: 'Profile',
        path: '/profile/:uid'
      },
      {
        component: Roster,
        name: 'Roster Photos',
        path: '/roster'
      },
      {
        component: CreateCourseSite,
        name: 'Create a Course Site',
        path: '/create_course_site'
      },
      {
        component: CreateProjectSite,
        name: 'Create a Project Site',
        path: '/create_project_site'
      },
      {
        component: MailingListCreate,
        name: 'Create Mailing List',
        path: '/mailing_list/create/:canvasSiteId?'
      },
      {
        component: MailingListSelectCourse,
        name: 'Select Course Site',
        path: '/mailing_list/select_course'
      },
      {
        component: MailingListUpdate,
        name: 'Update Mailing List',
        path: '/mailing_list/update'
      },
      {
        component: ManageSites,
        name: 'Manage Sites',
        path: '/manage_sites'
      },
      {
        component: SendWelcomeEmail,
        name: 'Send Welcome Email',
        path: '/mailing_list/send_welcome_email'
      },
      {
        component: UserProvision,
        name: 'bCourses User Provision',
        path: '/provision_user'
      },
      {
        beforeEnter: (to: any, from: any, next: any) => {
          useContextStore().currentUser.isAdmin ? next({path: '/admin'}) : next()
        },
        component: Welcome,
        name: 'Welcome',
        meta: {
          isHome: true
        },
        path: '/welcome'
      },
      {
        beforeEnter: (to: any, from: any, next: any) => {
          const context = useContextStore()
          if (context.currentUser.isAdmin) {
            next()
          } else {
            next('/welcome')
          }
        },
        component: WelcomeAdmin,
        name: 'Admin',
        meta: {
          isHome: true
        },
        path: '/admin'
      }
    ]
  },
  {
    component: BaseLTI,
    path: '/',
    children: [
      {
        component: Error,
        path: '/error'
      },
      {
        component: Error,
        meta: {
          is404: true
        },
        path: '/:pathMatch(.*)'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  const context = useContextStore()
  const currentUser = context.currentUser
  context.resetApplicationState()
  if (currentUser.isAuthenticated && !isInIframe && !currentUser.canAccessStandaloneView) {
    return logOut().then(data => window.location.href = data.casLogoutUrl)
  } else {
    if (to.query.error && to.path !== '/error' && !to.meta.is404) {
      context.setApplicationState(500, to.query.error)
    }
    if (context.applicationState.status === 200) {
      next()
    } else {
      next({path: '/error'})
    }
  }
})

router.afterEach((to: any, from: any) => {
  const samePageLink = to.name === from.name && to.hash
  if (!samePageLink) {
    const context = useContextStore()
    context.resetApplicationState()
    context.loadingStart(to)
    const title = capitalize(to.name) || 'bCourses'
    document.title = `${title} | UC Berkeley`
  }
})

export default router
