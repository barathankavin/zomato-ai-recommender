"""Streamlit demo app — single-process recommendation UI.

Imports milestone1 packages directly (no HTTP calls).
Secrets from st.secrets in Cloud, falls back to .env locally.
"""

from __future__ import annotations

import streamlit as st
from milestone1.phase0.settings import load_settings
from milestone1.phase1_ingestion.loader import load_restaurants
from milestone1.phase1_ingestion.models import BudgetBand
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase2_preferences.cities import allowed_cities_from_restaurants
from milestone1.phase4_llm.recommend import recommend
from milestone1.phase5_output.telemetry import emit_telemetry


def _get_api_key() -> str:
    """Read GROQ_API_KEY from Streamlit secrets or .env."""
    try:
        return st.secrets.get("GROQ_API_KEY", "") or load_settings().groq_api_key
    except Exception:
        return load_settings().groq_api_key


@st.cache_data(show_spinner="Loading restaurant data...")
def _load_corpus(limit: int = 5000):
    """Load and cache the restaurant corpus."""
    return load_restaurants(limit=limit)


def main():
    st.set_page_config(
        page_title="Zomato AI Recommendations",
        page_icon="🍽️",
        layout="centered",
    )

    st.title("🍽️ Zomato AI Restaurant Recommendations")
    st.caption("Powered by Groq LLM · Bangalore restaurants")

    # Load corpus
    try:
        corpus = _load_corpus()
    except Exception as e:
        st.error(f"Failed to load restaurant data: {e}")
        return

    # Build location and cuisine lists
    locations = sorted(allowed_cities_from_restaurants(corpus))
    all_cuisines = sorted({c for r in corpus for c in r.cuisines if c != "Unknown"})

    # --- Preference Form ---
    with st.form("preferences_form"):
        st.subheader("🔍 Your Preferences")

        col1, col2 = st.columns(2)

        with col1:
            location = st.selectbox(
                "📍 Location",
                options=locations,
                index=0,
                help="Select a neighbourhood in Bangalore",
            )

            budget = st.select_slider(
                "💰 Budget",
                options=["Any", "Low", "Medium", "High"],
                value="Any",
                help="Low ≤ ₹400 · Medium ≤ ₹1000 · High > ₹1000",
            )

        with col2:
            selected_cuisines = st.multiselect(
                "🍳 Cuisines",
                options=all_cuisines,
                default=[],
                help="Leave empty for all cuisines",
            )

            min_rating = st.slider(
                "⭐ Minimum Rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
            )

        additional = st.text_area(
            "📝 Additional Preferences",
            max_chars=500,
            placeholder="E.g., 'cozy ambiance', 'good for groups', 'vegetarian-friendly'...",
        )

        submitted = st.form_submit_button(
            "🔎 Find Restaurants",
            use_container_width=True,
        )

    # --- Results ---
    if submitted:
        # Map budget
        budget_val = None if budget == "Any" else BudgetBand(budget)

        prefs = UserPreferences(
            location=location,
            budget=budget_val,
            cuisines=selected_cuisines,
            min_rating=min_rating,
            additional_preferences=additional,
        )

        with st.spinner("🤖 AI is analyzing restaurants..."):
            result = recommend(corpus, prefs)

        # Emit telemetry
        emit_telemetry(result, corpus_size=len(corpus))

        # --- Display Results ---
        if not result.has_results:
            if result.empty_reason == "no_candidates":
                st.warning(
                    "😕 **No restaurants found**\n\n"
                    "No restaurants match your current filters. "
                    "Try broadening your search."
                )
            elif result.empty_reason == "llm_no_picks":
                st.info(
                    "🤔 **AI couldn't decide**\n\n"
                    "The AI reviewed candidates but couldn't pick the best matches. "
                    "Try broader filters or different preferences."
                )
            return

        # Source badge
        if result.source == "fallback":
            st.warning(
                "⚠️ AI ranking unavailable — showing top matches by rating."
            )

        st.subheader(f"🏆 Top {len(result.rankings)} Recommendations")

        for item in result.rankings:
            # Find the full restaurant info from corpus
            restaurant = next(
                (r for r in corpus if r.restaurant_id == item.restaurant_id),
                None,
            )

            st.markdown(f"**#{item.rank} {item.name}**")
            if restaurant:
                st.caption(
                    f"{', '.join(restaurant.cuisines)} · "
                    f"⭐ {restaurant.rating}/5 · "
                    f"₹{restaurant.cost_raw} for two · "
                    f"{restaurant.rest_type}"
                )
            st.info(item.explanation)
            st.divider()

        # Debug expander
        with st.expander("🔧 Debug Info"):
            st.json({
                "source": result.source,
                "latency_ms": result.latency_ms,
                "token_usage": result.token_usage,
                "result_count": len(result.rankings),
            })
