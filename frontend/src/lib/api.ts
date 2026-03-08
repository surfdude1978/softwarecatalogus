/**
 * API client voor de Softwarecatalogus backend.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T> {
    const { params, ...fetchOptions } = options;

    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(fetchOptions.headers as Record<string, string>),
    };

    // JWT token toevoegen indien aanwezig
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  get<T>(endpoint: string, options?: FetchOptions) {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  post<T>(endpoint: string, data?: unknown, options?: FetchOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  put<T>(endpoint: string, data?: unknown, options?: FetchOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  delete<T>(endpoint: string, options?: FetchOptions) {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: string
  ) {
    super(`API Error ${status}: ${body}`);
    this.name = "ApiError";
  }

  /**
   * Probeer de response-body als JSON te parsen.
   * Geeft `null` terug als de body geen geldig JSON is (bijv. HTML of plain text).
   * Werkt defensief: gooit nooit een exception.
   */
  parseBody(): Record<string, unknown> | null {
    if (!this.body || !this.body.trim()) return null;
    try {
      const parsed = JSON.parse(this.body);
      if (typeof parsed === "object" && parsed !== null && !Array.isArray(parsed)) {
        return parsed as Record<string, unknown>;
      }
      return null;
    } catch {
      return null;
    }
  }

  /**
   * Haal een gebruiksvriendelijk foutbericht op uit de response body.
   *
   * Probeert het `detail`-veld uit de JSON te lezen (DRF-conventie).
   * Valt terug op de opgegeven `fallback` als de body geen geldig JSON is,
   * geen `detail` bevat, of leeg is.
   *
   * @param fallback - Terugvalmelding als geen `detail` gevonden wordt.
   */
  getDetail(fallback = "Er is een fout opgetreden."): string {
    const parsed = this.parseBody();
    if (parsed && typeof parsed["detail"] === "string" && parsed["detail"]) {
      return parsed["detail"];
    }
    return fallback;
  }

  /**
   * Haal veldvalidatiefouten op uit de response body (DRF-formaat).
   * Geeft een dict terug van `{veldnaam: ["fout1", "fout2"]}`.
   * Geeft een leeg object terug als er geen veldfouten zijn.
   */
  getFieldErrors(): Record<string, string[]> {
    const parsed = this.parseBody();
    if (!parsed) return {};
    const errors: Record<string, string[]> = {};
    for (const [key, value] of Object.entries(parsed)) {
      if (key === "detail") continue;
      if (Array.isArray(value)) {
        errors[key] = value.map(String);
      } else if (typeof value === "string") {
        errors[key] = [value];
      }
    }
    return errors;
  }
}

export const api = new ApiClient(API_BASE_URL);
