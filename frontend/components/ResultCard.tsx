import type { RankedItem } from "@/types";

interface ResultCardProps {
  item: RankedItem;
}

export default function ResultCard({ item }: ResultCardProps) {
  return (
    <div className="group rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 p-5 hover:bg-white/[0.08] hover:border-orange-500/30 transition-all duration-300">
      <div className="flex items-start gap-4">
        {/* Rank Badge */}
        <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-orange-500/20">
          {item.rank}
        </div>

        <div className="flex-1 min-w-0">
          {/* Name */}
          <h3 className="text-lg font-semibold text-white group-hover:text-orange-400 transition-colors">
            {item.name}
          </h3>

          {/* AI Explanation */}
          {item.explanation && (
            <p className="mt-2 text-sm text-white/50 leading-relaxed">
              💡 {item.explanation}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
