const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = 5000;

type ApiErrorPayload = {
  detail?: string;
  error?: { message?: string };
};

export function isApiConfigured() {
  return Boolean(API_URL);
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
  fallbackMessage = 'Sunucu isteği tamamlanamadı.'
): Promise<T> {
  if (!API_URL) throw new Error('Mobil API adresi tanımlı değil.');

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const headers = new Headers(init?.headers);
  if (!headers.has('Accept')) headers.set('Accept', 'application/json');
  if (init?.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers,
      signal: controller.signal,
    });
    const text = await response.text();
    let payload: unknown = null;
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch {
        payload = text;
      }
    }

    if (!response.ok) {
      const errorPayload = payload as ApiErrorPayload | null;
      throw new Error(errorPayload?.error?.message ?? errorPayload?.detail ?? fallbackMessage);
    }
    return payload as T;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Sunucu yanıt vermedi. Bağlantını kontrol edip tekrar dene.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
