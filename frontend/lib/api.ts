/**
 * API client for the Zomato AI backend.
 */

import type {
  RecommendationRequest,
  RecommendationResponse,
  MetaResponse,
  HealthResponse,
  ApiError,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async health(): Promise<HealthResponse> {
    const res = await fetch(`${this.baseUrl}/health`);
    if (!res.ok) throw new Error("Health check failed");
    return res.json();
  }

  async meta(): Promise<MetaResponse> {
    const res = await fetch(`${this.baseUrl}/api/v1/meta`);
    if (!res.ok) throw new Error("Failed to fetch metadata");
    return res.json();
  }

  async recommend(
    request: RecommendationRequest
  ): Promise<RecommendationResponse> {
    const res = await fetch(`${this.baseUrl}/api/v1/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });

    if (res.status === 422) {
      const error: ApiError = await res.json();
      throw new ValidationError(error);
    }

    if (res.status === 503) {
      throw new ServiceUnavailableError("AI service not configured");
    }

    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }

    return res.json();
  }
}

export class ValidationError extends Error {
  field?: string;
  suggestions?: string[];

  constructor(error: ApiError) {
    const detail = error.detail;
    if (typeof detail === "object") {
      super(detail.message);
      this.field = detail.field;
      this.suggestions = detail.suggestions;
    } else {
      super(detail || "Validation error");
    }
    this.name = "ValidationError";
  }
}

export class ServiceUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ServiceUnavailableError";
  }
}

export const api = new ApiClient(API_BASE);
