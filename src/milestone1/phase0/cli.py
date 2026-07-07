import click
from milestone1.phase0.doctor import check_environment

@click.group()
def cli():
    """Zomato AI Recommendation System CLI."""
    pass

@cli.command()
def info():
    """Display information about the project."""
    click.echo("Zomato AI Restaurant Recommendation System")
    click.echo("Stack: Python 3.11, FastAPI, Next.js, Groq LLM")
    click.echo("Dataset: ManikaSaini/zomato-restaurant-recommendation")

@cli.command()
def doctor():
    """Check if the environment is configured correctly."""
    if check_environment():
        click.echo("Doctor check passed!")
    else:
        click.echo("Doctor check failed. Please resolve the issues above.")
        exit(1)


# ---------------------------------------------------------------------------
# Phase 1: Data ingestion
# ---------------------------------------------------------------------------

@cli.command(name="ingest-smoke")
@click.option("--limit", default=50, help="Number of rows to process")
def ingest_smoke(limit: int):
    """Smoke test: load and display a few restaurants."""
    from milestone1.phase1_ingestion.loader import load_restaurants

    click.echo(f"Loading up to {limit} rows...")
    restaurants = load_restaurants(limit=limit)
    click.echo(f"Loaded {len(restaurants)} restaurants after dedup.\n")

    for r in restaurants[:5]:
        click.echo(f"  {r.name} | {r.location} | {r.rating}/5 | ₹{r.cost_raw} | {', '.join(r.cuisines)}")

    if len(restaurants) > 5:
        click.echo(f"  ... and {len(restaurants) - 5} more")


# ---------------------------------------------------------------------------
# Phase 2: Preferences
# ---------------------------------------------------------------------------

@cli.command(name="prefs-parse")
@click.option("--location", required=True, help="Location/neighbourhood")
@click.option("--budget", default=None, help="Budget: Low, Medium, High")
@click.option("--cuisines", default="", help="Comma-separated cuisines")
@click.option("--min-rating", default=0.0, type=float, help="Minimum rating")
@click.option("--additional", default="", help="Free-text preferences")
def prefs_parse(location, budget, cuisines, min_rating, additional):
    """Parse and validate user preferences."""
    from milestone1.phase2_preferences.parser import parse_preferences
    from milestone1.phase2_preferences.models import PreferencesError

    raw = {
        "location": location,
        "budget": budget,
        "cuisines": [c.strip() for c in cuisines.split(",") if c.strip()] if cuisines else [],
        "min_rating": min_rating,
        "additional_preferences": additional,
    }

    try:
        prefs = parse_preferences(raw)
        click.echo("✅ Preferences parsed successfully:")
        click.echo(f"  Location: {prefs.location}")
        click.echo(f"  Budget: {prefs.budget}")
        click.echo(f"  Cuisines: {prefs.cuisines}")
        click.echo(f"  Min Rating: {prefs.min_rating}")
        click.echo(f"  Additional: {prefs.additional_preferences or '(none)'}")
    except PreferencesError as e:
        click.echo(f"❌ Validation error [{e.field}]: {e}")
        exit(1)


# ---------------------------------------------------------------------------
# Phase 3: Prompt build
# ---------------------------------------------------------------------------

@cli.command(name="prompt-build")
@click.option("--location", required=True, help="Location")
@click.option("--budget", default=None, help="Budget")
@click.option("--cuisines", default="", help="Comma-separated cuisines")
@click.option("--min-rating", default=0.0, type=float, help="Min rating")
@click.option("--limit", default=100, help="Dataset row limit")
def prompt_build(location, budget, cuisines, min_rating, limit):
    """Build the LLM prompt from preferences + corpus (no LLM call)."""
    from milestone1.phase1_ingestion.loader import load_restaurants
    from milestone1.phase2_preferences.models import UserPreferences
    from milestone1.phase3_integration.filter import filter_restaurants
    from milestone1.phase3_integration.prompt import build_prompt

    click.echo("Loading corpus...")
    restaurants = load_restaurants(limit=limit)

    prefs = UserPreferences(
        location=location,
        budget=budget,
        cuisines=[c.strip() for c in cuisines.split(",") if c.strip()] if cuisines else [],
        min_rating=min_rating,
    )

    candidates = filter_restaurants(restaurants, prefs)
    click.echo(f"Filtered to {len(candidates)} candidates")

    if not candidates:
        click.echo("⚠️  Zero candidates — LLM call would be skipped.")
        return

    prompt = build_prompt(prefs, candidates)
    click.echo(f"\n--- SYSTEM PROMPT ---\n{prompt['system'][:500]}...")
    click.echo(f"\n--- USER MESSAGE (truncated) ---\n{prompt['user'][:800]}...")


# ---------------------------------------------------------------------------
# Phase 4+5: End-to-end recommend
# ---------------------------------------------------------------------------

@cli.command(name="recommend")
@click.option("--location", required=True, help="Location")
@click.option("--budget", default=None, help="Budget: Low, Medium, High")
@click.option("--cuisines", default="", help="Comma-separated cuisines")
@click.option("--min-rating", default=0.0, type=float, help="Min rating")
@click.option("--additional", default="", help="Additional preferences")
@click.option("--limit", default=None, type=int, help="Dataset row limit")
def recommend_cmd(location, budget, cuisines, min_rating, additional, limit):
    """Run full recommendation pipeline (filter → LLM → output)."""
    from milestone1.phase1_ingestion.loader import load_restaurants
    from milestone1.phase2_preferences.models import UserPreferences
    from milestone1.phase4_llm.recommend import recommend
    from milestone1.phase5_output.renderer import render_plain
    from milestone1.phase5_output.telemetry import emit_telemetry

    click.echo("Loading corpus...")
    restaurants = load_restaurants(limit=limit)
    click.echo(f"Corpus: {len(restaurants)} restaurants\n")

    prefs = UserPreferences(
        location=location,
        budget=budget,
        cuisines=[c.strip() for c in cuisines.split(",") if c.strip()] if cuisines else [],
        min_rating=min_rating,
        additional_preferences=additional,
    )

    result = recommend(restaurants, prefs)

    # Emit telemetry
    emit_telemetry(result, corpus_size=len(restaurants))

    # Render output
    click.echo(render_plain(result))


if __name__ == "__main__":
    cli()
