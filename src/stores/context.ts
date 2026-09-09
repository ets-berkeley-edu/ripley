import mitt from 'mitt'
import {defineStore} from 'pinia'
import {nextTick} from 'vue'
import type {ScreenReaderAlert} from '@/lib/types'
import {alertScreenReader, putFocusNextTick} from '@/utils'

export type RipleyConfig = {
  canvasApiUrl: string,
  casLogoutUrl: string,
  devAuthEnabled: boolean,
  hypersleep: any,
  newtInformationBlock: string,
  newtShowOtherGender: boolean,
  terms: {
    current: {
      name: string
    },
    next: {
      name: string
    }
  }
}

export type RipleyUser = {
  canAccessStandaloneView: boolean,
  canvasMasqueradingUserId: number | undefined,
  canvasSiteId: number,
  canvasSiteName: string | undefined,
  inDemoMode: boolean,
  isAdmin: boolean,
  isAuthenticated: boolean,
  isCanvasAdmin: boolean,
  uid: string | undefined
}

const $_getDefaultApplicationState = () => ({
  message: undefined,
  stacktrace: undefined,
  status: 200
})

const ANONYMOUS_USER: RipleyUser = {
  canAccessStandaloneView: false,
  canvasMasqueradingUserId: undefined,
  canvasSiteId: NaN,
  canvasSiteName: undefined,
  inDemoMode: false,
  isAdmin: false,
  isAuthenticated: false,
  isCanvasAdmin: false,
  uid: undefined
}

export const useContextStore = defineStore('context', {
  state: () => ({
    applicationState: $_getDefaultApplicationState(),
    config: {} as RipleyConfig,
    currentUser: ANONYMOUS_USER as RipleyUser,
    eventHub: mitt(),
    isLoading: false,
    screenReaderAlert: {
      message: '',
      politeness: 'polite'
    }
  }),
  actions: {
    loadingComplete(focusTarget?: string) {
      this.isLoading = false
      nextTick(() => {
        setTimeout(() => putFocusNextTick(focusTarget || 'page-title'), 150)
      })
    },
    loadingStart() {
      this.isLoading = true
      alertScreenReader('Loading')
    },
    resetApplicationState() {
      this.applicationState = $_getDefaultApplicationState()
    },
    setConfig(config: any) {
      this.config = config
    },
    setApplicationState(status: number, message?: any, stacktrace?: any) {
      this.applicationState = {message, stacktrace, status}
    },
    setCurrentUser(user: any) {
      this.currentUser = user
      this.eventHub.emit('current-user-update')
    },
    setHypersleep(hypersleep: any) {
      this.config.hypersleep = hypersleep
    },
    setScreenReaderAlert(screenReaderAlert: ScreenReaderAlert) {
      this.screenReaderAlert = {
        message: screenReaderAlert.message,
        politeness: screenReaderAlert.politeness || 'polite'
      }
    },
  }
})
