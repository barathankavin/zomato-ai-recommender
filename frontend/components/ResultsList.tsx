import type { RecommendationResponse } from "@/types";
import ResultCard from "./ResultCard";
import SourceBadge from "./SourceBadge";
import EmptyState from "./EmptyState";

interface ResultsListProps {
  result: RecommendationResponse;
}

export default function ResultsList({ result }: ResultsListProps) {
  // Empty states
  if (!result.has_results) {
    return <EmptyState reason={result.empty_reason} />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <span>🏆</span> Top {result.rankings.length} Recommendations
        </h2>
        <SourceBadge source={result.source} />
      </div>

      {/* Fallback banner */}
      {result.source === "fallback" && (
        <SourceBadge source="fallback" />
      )}

      {/* Result cards */}
      <div className="space-y-3">
        {result.rankings.map((item) => (
          <ResultCard key={item.restaurant_id} item={item} />
        ))}
      </div>

      {/* Latency footer */}
      {result.latency_ms !== null && (
        <p className="text-center text-white/20 text-xs mt-4">
          Response time: {Math.round(result.latency_ms)}ms
        </p>
      )}
    </div>
  );
}
