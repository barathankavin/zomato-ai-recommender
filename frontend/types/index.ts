/**
 * Shared TypeScript types for the Zomato AI recommendation frontend.
 */

export type BudgetBand = "Low" | "Medium" | "High";

export interface RecommendationRequest {
  location: string;
  budget?: BudgetBand | null;
  cuisines: string[];
  min_rating: number;
  additional_preferences: string;
}

export interface RankedItem {
  restaurant_id: number;
  rank: number;
  name: string;
  explanation: string;
}

export interface RecommendationResponse {
  rankings: RankedItem[];
  source: "llm" | "fallback";
  has_results: boolean;
  empty_reason: "no_candidates" | "llm_no_picks" | null;
  candidate_count: number;
  latency_ms: number | null;
}

export interface HealthResponse {
  status: string;
  groq_configured: boolean;
  corpus_size: number;
}

export interface MetaResponse {
  locations: string[];
  cuisines: string[];
  total_restaurants: number;
}

export interface ApiError {
  detail:
    | string
    | {
        field: string;
        message: string;
        suggestions?: string[];
      };
}
