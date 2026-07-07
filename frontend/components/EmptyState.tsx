interface EmptyStateProps {
  reason: "no_candidates" | "llm_no_picks" | null;
}

export default function EmptyState({ reason }: EmptyStateProps) {
  if (reason === "no_candidates") {
    return (
      <div className="rounded-2xl bg-white/5 border border-white/10 p-8 text-center">
        <div className="text-5xl mb-4">😕</div>
        <h3 className="text-xl font-semibold text-white mb-2">
          No restaurants found
        </h3>
        <p className="text-white/50 text-sm max-w-md mx-auto">
          No restaurants match your current filters. Try broadening your search:
        </p>
        <ul className="text-white/40 text-sm mt-3 space-y-1">
          <li>• Choose a different location</li>
          <li>• Lower your minimum rating</li>
          <li>• Select a different budget range</li>
          <li>• Remove cuisine filters</li>
        </ul>
      </div>
    );
  }

  if (reason === "llm_no_picks") {
    return (
      <div className="rounded-2xl bg-white/5 border border-white/10 p-8 text-center">
        <div className="text-5xl mb-4">🤔</div>
        <h3 className="text-xl font-semibold text-white mb-2">
          AI couldn&apos;t decide
        </h3>
        <p className="text-white/50 text-sm max-w-md mx-auto">
          The AI model reviewed the candidates but couldn&apos;t pick the best
          matches. This can happen with very specific preferences.
        </p>
        <p className="text-orange-400 text-sm mt-3">
          Try: Broaden your filters or adjust your additional preferences.
        </p>
      </div>
    );
  }

  return null;
}
