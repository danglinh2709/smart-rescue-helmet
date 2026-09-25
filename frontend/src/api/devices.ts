import { apiGet } from './client'; import type { ApiDevicesResponse } from '../types/dashboard'; export const getDevices = () => apiGet<ApiDevicesResponse>('/api/v1/devices')
