"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { 
  Bell, 
  User, 
  Utensils, 
  PartyPopper, 
  MapPin, 
  Sparkles, 
  Heart 
} from "lucide-react";
import type { RecommendationRequest, RecommendationResponse, MetaResponse, BudgetBand } from "@/types";
import { api, ValidationError, ServiceUnavailableError } from "@/lib/api";

export default function Home() {
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [metaError, setMetaError] = useState<string | null>(null);
  
  // Form State
  const [location, setLocation] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [vibe, setVibe] = useState("");
  const [taste, setTaste] = useState("");
  const [budgetVal, setBudgetVal] = useState(150);
  const [minRating, setMinRating] = useState(4.0);

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const resultsRef = useRef<HTMLElement>(null);

  useEffect(() => {
    api
      .meta()
      .then(setMeta)
      .catch(() => setMetaError("Could not load restaurant data. Is the API running?"));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null);
    setError(null);

    if (!location) {
      setError("Please select a location first.");
      setIsLoading(false);
      return;
    }

    // Map budget slider to API categories
    let mappedBudget: BudgetBand | null = null;
    if (budgetVal <= 1000) mappedBudget = "Low";
    else if (budgetVal <= 2500) mappedBudget = "Medium";
    else mappedBudget = "High";

    // Combine vibe and free-form taste for the AI prompt
    let combinedPreferences = "";
    if (vibe) combinedPreferences += `Vibe: ${vibe}. `;
    if (taste) combinedPreferences += `Specific taste/request: ${taste}`;

    const request: RecommendationRequest = {
      location,
      cuisines: cuisine ? [cuisine] : [],
      budget: mappedBudget,
      min_rating: minRating,
      additional_preferences: combinedPreferences.trim(),
    };

    try {
      const response = await api.recommend(request);
      setResult(response);
      
      // Smooth scroll down to results after a short delay to allow rendering
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);

    } catch (err) {
      if (err instanceof ValidationError) {
        const suffix = err.suggestions
          ? ` Did you mean: ${err.suggestions.join(", ")}?`
          : "";
        setError(`${err.message}${suffix}`);
      } else if (err instanceof ServiceUnavailableError) {
        setError("AI service is not configured. The backend needs a GROQ_API_KEY.");
      } else {
        setError(err instanceof Error ? err.message : "An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col pt-24 pb-24">
      {/* TopNavBar */}
      <nav className="fixed top-0 w-full z-50 bg-glass-surface backdrop-blur-md shadow-sm border-b border-glass-border">
        <div className="flex justify-between items-center px-margin-mobile md:px-margin-desktop py-4 max-w-[1440px] mx-auto hidden md:flex relative z-10">
          <div className="flex items-center gap-3 font-display-xl text-[28px] font-bold tracking-tight">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Zomato_logo.png/600px-Zomato_logo.png" alt="Zomato Logo" className="h-6 w-auto" />
            <span className="text-white">AI</span>
          </div>
          <div className="flex gap-8 items-center font-body-md text-body-md">
            <a className="text-primary font-bold border-b-2 border-primary pb-1" href="#">AI Recommender</a>
          </div>
          <div className="flex gap-4 text-primary">
            <button className="hover:scale-105 transition-transform duration-200">
              <Bell size={20} />
            </button>
            <button className="hover:scale-105 transition-transform duration-200">
              <User size={20} />
            </button>
          </div>
        </div>
      </nav>

      <main className="flex-grow max-w-[1440px] mx-auto w-full px-margin-mobile md:px-margin-desktop flex flex-col gap-16 mt-8">
        
        {/* Hero Section */}
        <motion.header 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center flex flex-col items-center gap-6" 
          id="hero-section"
        >
          <h1 className="font-display-xl text-[64px] md:text-[80px] leading-tight text-on-surface max-w-4xl bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 relative z-10">
            Discover Your Next <br /> <span className="text-primary">Favorite Meal</span>
          </h1>
          <p className="font-body-lg text-[18px] text-on-surface-variant max-w-2xl">
            Let Zomato AI curate the perfect dining experience tailored to your exact cravings, budget, and vibe.
          </p>
        </motion.header>

        {/* Preference Form */}
        <motion.section 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
          className="glass-panel rounded-xl p-8 max-w-4xl w-full mx-auto" 
          id="preference-form"
        >
          {metaError && (
            <div className="mb-6 rounded-lg bg-error-container/20 border border-error/50 p-4 text-center">
              <p className="text-error font-medium">⚠️ {metaError}</p>
            </div>
          )}

          <form className="flex flex-col gap-8" onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Location Select */}
              <div className="flex flex-col gap-2">
                <label className="font-label-md text-[14px] text-on-surface">Location</label>
                <div className="relative">
                  <MapPin size={20} className="absolute left-3 top-3 text-on-surface-variant" />
                  <select 
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="glass-input w-full rounded-lg py-3 pl-10 pr-4 font-body-md text-[16px] text-on-surface appearance-none"
                    disabled={!meta}
                  >
                    <option value="" disabled className="bg-[#111827]">Select Area</option>
                    {meta?.locations.map((loc) => (
                      <option key={loc} value={loc} className="bg-[#111827]">{loc}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label className="font-label-md text-[14px] text-on-surface">Cuisine Craving</label>
                <div className="relative">
                  <Utensils size={20} className="absolute left-3 top-3 text-on-surface-variant" />
                  <input 
                    type="text"
                    value={cuisine}
                    onChange={(e) => setCuisine(e.target.value)}
                    className="glass-input w-full rounded-lg py-3 pl-10 pr-4 font-body-md text-[16px] text-on-surface placeholder-on-surface-variant/50" 
                    placeholder="e.g. Japanese, Vegan..." 
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label className="font-label-md text-[14px] text-on-surface">Vibe / Occasion</label>
                <div className="relative">
                  <PartyPopper size={20} className="absolute left-3 top-3 text-on-surface-variant" />
                  <select 
                    value={vibe}
                    onChange={(e) => setVibe(e.target.value)}
                    className="glass-input w-full rounded-lg py-3 pl-10 pr-4 font-body-md text-[16px] text-on-surface appearance-none"
                  >
                    <option value="" disabled className="bg-[#111827]">Select Vibe</option>
                    <option value="romantic date night" className="bg-[#111827]">Romantic Date Night</option>
                    <option value="casual catchup" className="bg-[#111827]">Casual Catchup</option>
                    <option value="business dinner" className="bg-[#111827]">Business Dinner</option>
                    <option value="lively group dinner" className="bg-[#111827]">Lively Group Dinner</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
              <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center">
                  <label className="font-label-md text-[14px] text-on-surface">Max Budget for Two</label>
                  <span className="font-body-md text-primary">₹{budgetVal}</span>
                </div>
                <input 
                  type="range" 
                  min="500" max="4000" step="100" 
                  value={budgetVal}
                  onChange={(e) => setBudgetVal(Number(e.target.value))}
                />
              </div>

              <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center">
                  <label className="font-label-md text-[14px] text-on-surface">Minimum Rating</label>
                  <span className="font-body-md text-primary flex items-center gap-1">
                    {minRating.toFixed(1)} ★
                  </span>
                </div>
                <input 
                  type="range" 
                  min="3" max="5" step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(Number(e.target.value))}
                />
              </div>
            </div>

            {/* Custom Taste Text Box */}
            <div className="flex flex-col gap-3 mt-4 relative z-10 bg-surface-container-low/30 p-6 rounded-xl border border-glass-border">
              <label className="font-display-xl text-[24px] text-on-surface bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-red-400">
                ✨ Describe Your Perfect Taste
              </label>
              <p className="font-body-md text-on-surface-variant text-[14px]">
                Tell Zomato AI exactly what you're craving (e.g. "Spicy garlic noodles with a great view", "Authentic wood-fired pizza")
              </p>
              <textarea 
                value={taste}
                onChange={(e) => setTaste(e.target.value)}
                className="glass-input w-full rounded-lg py-4 px-4 font-body-md text-[16px] text-on-surface placeholder-on-surface-variant/50 min-h-[100px] resize-y" 
                placeholder="Type your cravings here..." 
              />
            </div>

            {error && (
              <div className="text-error font-body-md text-center">{error}</div>
            )}

            <button 
              type="submit"
              disabled={isLoading || !meta}
              className="mt-4 bg-[#E23744] hover:bg-[#bb162c] text-white font-label-md text-[14px] py-4 rounded-lg flex justify-center items-center gap-2 transition-all duration-200 hover:scale-[1.02] shadow-[0_0_15px_rgba(226,55,68,0.3)] disabled:opacity-50 disabled:hover:scale-100"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <Sparkles size={20} className="animate-pulse" /> Generating Insights...
                </span>
              ) : (
                <>
                  <Sparkles size={20} /> Generate AI Recommendations
                </>
              )}
            </button>
          </form>
        </motion.section>

        {/* Results Grid */}
        {result && (
          <section className="mt-8" id="results-section" ref={resultsRef}>
            <div className="flex justify-between items-end mb-8">
              <h2 className="font-headline-lg text-[40px] text-on-surface">Top Matches for You</h2>
              <span className="font-label-md text-[14px] text-on-surface-variant">
                {result.rankings.length === 0 ? "No matches found" : `Found ${result.rankings.length} exceptional venues`}
              </span>
            </div>

            {result.source === "fallback" && (
              <div className="mb-6 p-4 border border-outline/30 rounded-lg bg-surface-container-low text-on-surface-variant flex gap-2">
                ⚠️ AI ranking unavailable — showing top matches by rating.
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {result.rankings.map((item, index) => (
                <motion.article 
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.15 * index, ease: "easeOut" }}
                  key={item.restaurant_id}
                  className="glass-panel rounded-xl overflow-hidden flex flex-col group transition-all duration-300"
                >
                  <div className="relative h-48 w-full bg-[#1c1b1b]">
                    {/* Placeholder image since backend doesn't return one */}
                    <div 
                      className="bg-cover bg-center w-full h-full absolute inset-0 opacity-80 mix-blend-overlay"
                      style={{ backgroundImage: "url('https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=800&auto=format&fit=crop')" }}
                    ></div>
                    <div className="absolute inset-0 bg-gradient-to-t from-[#131313] to-transparent"></div>
                    <div className="absolute top-4 left-4 bg-[#353534] text-[#e5e2e1] font-label-md text-[12px] px-3 py-1 rounded-full flex items-center gap-1 border border-glass-border">
                      <span className="text-white">#{item.rank}</span> Match
                    </div>
                    <button className="absolute top-4 right-4 text-white/70 hover:text-[#E23744] transition-colors">
                      <Heart size={20} />
                    </button>
                  </div>
                  
                  <div className="p-6 flex flex-col gap-4 flex-grow bg-[#1c1b1b]/50 backdrop-blur-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-headline-md text-[28px] text-[#e5e2e1] truncate pr-2" title={item.name}>{item.name}</h3>
                      </div>
                    </div>
                    
                    <div className="mt-auto bg-[#1a1314] border border-[#312729] rounded-lg p-4">
                      <h4 className="font-label-sm text-[#ffb3b1] flex items-center gap-1 mb-2">
                        <Sparkles size={16} /> AI Insight
                      </h4>
                      <p className="font-body-md text-[14px] leading-relaxed text-[#e4bebc]">
                        {item.explanation}
                      </p>
                    </div>
                  </div>
                </motion.article>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
