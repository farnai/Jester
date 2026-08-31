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
  const session = (await supabase.auth.getSession()).data.session;
  const token = session?.access_token;

  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const url = `${CONFIG.API_BASE_URL}${path}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Session expired -> sign out to trigger redirect
      await supabase.auth.signOut();
    }

    let errorData: any = null;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: response.statusText };
    }

    const code = errorData?.error_code || `HTTP_${response.status}`;
    const msg = errorData?.message || errorData?.detail || response.statusText || "Request failed";

    throw new ApiClientError(response.status, code, msg);
  }

  // Check 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
