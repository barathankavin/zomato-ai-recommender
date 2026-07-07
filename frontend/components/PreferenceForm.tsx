"use client";

import { useState, useEffect } from "react";
import type { BudgetBand, RecommendationRequest, MetaResponse } from "@/types";
import { api } from "@/lib/api";

interface PreferenceFormProps {
  onSubmit: (request: RecommendationRequest) => void;
  isLoading: boolean;
}

export default function PreferenceForm({
  onSubmit,
  isLoading,
}: PreferenceFormProps) {
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [metaError, setMetaError] = useState<string | null>(null);
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState<BudgetBand | "">("");
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([]);
  const [minRating, setMinRating] = useState(0);
  const [additional, setAdditional] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    api
      .meta()
      .then(setMeta)
      .catch(() => setMetaError("Could not load restaurant data. Is the API running?"));
  }, []);

  const handleCuisineToggle = (cuisine: string) => {
    setSelectedCuisines((prev) =>
      prev.includes(cuisine)
        ? prev.filter((c) => c !== cuisine)
        : [...prev, cuisine]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!location) {
      setValidationError("Please select a location");
      return;
    }

    onSubmit({
      location,
      budget: budget || null,
      cuisines: selectedCuisines,
      min_rating: minRating,
      additional_preferences: additional,
    });
  };

  if (metaError) {
    return (
      <div className="rounded-2xl bg-red-500/10 border border-red-500/20 p-6 text-center">
        <p className="text-red-400 font-medium">⚠️ {metaError}</p>
        <p className="text-red-400/60 text-sm mt-2">
          Make sure the backend is running at{" "}
          <code className="bg-red-500/10 px-2 py-0.5 rounded">
            {process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}
          </code>
        </p>
      </div>
    );
  }

  if (!meta) {
    return (
      <div className="rounded-2xl bg-white/5 border border-white/10 p-8 text-center">
        <div className="animate-pulse flex flex-col gap-4">
          <div className="h-8 bg-white/10 rounded-lg w-1/3 mx-auto" />
          <div className="h-12 bg-white/10 rounded-lg" />
          <div className="h-12 bg-white/10 rounded-lg" />
          <div className="h-12 bg-white/10 rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6 md:p-8 space-y-6"
    >
      <h2 className="text-xl font-semibold text-white flex items-center gap-2">
        <span>🔍</span> Your Preferences
      </h2>

      {validationError && (
        <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
          {validationError}
        </div>
      )}

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          📍 Location
        </label>
        <select
          id="location-select"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all"
        >
          <option value="" className="bg-gray-900">Select a neighbourhood...</option>
          {meta.locations.map((loc) => (
            <option key={loc} value={loc} className="bg-gray-900">
              {loc}
            </option>
          ))}
        </select>
      </div>

      {/* Budget */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          💰 Budget
        </label>
        <div className="flex gap-2">
          {(["", "Low", "Medium", "High"] as const).map((b) => (
            <button
              key={b}
              type="button"
              onClick={() => setBudget(b as BudgetBand | "")}
              className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                budget === b
                  ? "bg-orange-500 text-white shadow-lg shadow-orange-500/25"
                  : "bg-white/5 text-white/60 hover:bg-white/10 border border-white/10"
              }`}
            >
              {b || "Any"}
            </button>
          ))}
        </div>
        <p className="text-xs text-white/30 mt-1.5">
          Low ≤ ₹400 · Medium ≤ ₹1000 · High &gt; ₹1000
        </p>
      </div>

      {/* Cuisines */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          🍳 Cuisines{" "}
          <span className="text-white/30 font-normal">(leave empty for all)</span>
        </label>
        <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto pr-2">
          {meta.cuisines.slice(0, 30).map((cuisine) => (
            <button
              key={cuisine}
              type="button"
              onClick={() => handleCuisineToggle(cuisine)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${
                selectedCuisines.includes(cuisine)
                  ? "bg-orange-500 text-white shadow-md shadow-orange-500/25"
                  : "bg-white/5 text-white/50 hover:bg-white/10 border border-white/10"
              }`}
            >
              {cuisine}
            </button>
          ))}
        </div>
      </div>

      {/* Min Rating */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          ⭐ Minimum Rating: {minRating.toFixed(1)}
        </label>
        <div className="flex gap-1.5">
          {[0, 1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setMinRating(star)}
              className={`flex-1 py-2 rounded-lg text-sm transition-all duration-200 ${
                minRating >= star && star > 0
                  ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                  : star === 0 && minRating === 0
                  ? "bg-orange-500 text-white"
                  : "bg-white/5 text-white/40 hover:bg-white/10 border border-white/10"
              }`}
            >
              {star === 0 ? "Any" : `${star}★`}
            </button>
          ))}
        </div>
      </div>

      {/* Additional Preferences */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          📝 Additional Preferences
        </label>
        <textarea
          id="additional-preferences"
          value={additional}
          onChange={(e) => setAdditional(e.target.value.slice(0, 500))}
          maxLength={500}
          rows={2}
          placeholder="E.g., 'cozy ambiance', 'good for groups', 'vegetarian-friendly'..."
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 resize-none transition-all"
        />
        <p className="text-xs text-white/30 mt-1 text-right">
          {additional.length}/500
        </p>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3.5 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Finding restaurants...
          </span>
        ) : (
          "🔎 Find Restaurants"
        )}
      </button>
    </form>
  );
}
