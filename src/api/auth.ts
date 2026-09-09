import utils from './api-utils'
import {RipleyConfig} from '@/stores/context'

export function becomeUser(canvasSiteId: number, uid: string) {
  return utils.post('/api/auth/become_user', {canvasSiteId, uid}, true)
}

export function devAuthLogIn(canvasSiteId: string, uid: string, password: string, canvasMasqueradingUserId?: string) {
  return utils.post('/api/auth/dev_auth', {canvasMasqueradingUserId, canvasSiteId, password, uid}, false)
}

export function getCasLoginURL() {
  return utils.get('/api/auth/cas_login_url', true)
}

export function getCasLogoutUrl() {
  return utils.get('/api/auth/logout', true)
}

export function logOut(): Promise<RipleyConfig> {
  return utils.get('/api/auth/logout', true)
}

export function updateUserSession(canvasSiteId: number, redirectOnError?: boolean) {
  return utils.post('/api/auth/update_user_session', {canvasSiteId}, redirectOnError)
}
