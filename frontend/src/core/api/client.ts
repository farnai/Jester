import { CONFIG } from "../config";
import { supabase } from "../realtime/supabase";

export class ApiClientError extends Error {
  statusCode: number;
  errorCode: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiClientError";
    this.statusCode = status;
    this.errorCode = code;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  // Only resolve from Supabase if Authorization header was not explicitly supplied
  if (!headers.has("Authorization")) {
    try {
      const authResult = await Promise.race([
        supabase.auth.getSession(),
        new Promise<{ data: { session: null } }>((resolve) =>
          setTimeout(() => resolve({ data: { session: null } }), 1500)
        ),
      ]);
      const session = authResult?.data?.session;
      const token = session?.access_token;
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
    } catch {
      // Ignore auth failure for public or optional endpoints
    }
  }

  const url = `${CONFIG.API_BASE_URL}${path}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: any = null;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: response.statusText };
    }

    const code = errorData?.error?.code || errorData?.error_code || `HTTP_${response.status}`;
    const msg =
      errorData?.error?.message ||
      errorData?.message ||
      errorData?.detail ||
      response.statusText ||
      "Request failed";

    throw new ApiClientError(response.status, code, msg);
  }

  // Check 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
