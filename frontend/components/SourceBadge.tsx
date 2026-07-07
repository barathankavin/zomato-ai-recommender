interface SourceBadgeProps {
  source: "llm" | "fallback";
}

export default function SourceBadge({ source }: SourceBadgeProps) {
  if (source === "llm") {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
        AI Ranked
      </span>
    );
  }

  return (
    <div className="rounded-xl bg-yellow-500/10 border border-yellow-500/20 px-4 py-3 text-sm text-yellow-300">
      ⚠️ AI ranking unavailable — showing top matches by rating.
    </div>
  );
}
