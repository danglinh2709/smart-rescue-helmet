const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '')
export async function apiGet<T>(path: string): Promise<T> { const response = await fetch(`${baseUrl}${path}`); if (!response.ok) throw new Error(`API request failed (${response.status})`); return response.json() as Promise<T> }
