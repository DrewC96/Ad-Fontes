"""
Fill in NULL embeddings for existing passages using Gemini's
gemini-embedding-001 model, truncated to 768 dimensions (matches
passages.embedding vector(768) in schema.sql).
 
Uses the current `google-genai` SDK. The older `google-generativeai`
package (import google.generativeai as genai) is deprecated as of
March 2025 - do not reinstall that one if this ever needs rebuilding.
 
Batches multiple passages per API call to stay well under Gemini's
free-tier daily request limit - each request embeds a whole batch of
passages at once, not just one.
 
Resumable: only ever processes passages where embedding IS NULL, so
re-running on a new day picks up exactly where it left off. Stops
cleanly (not a crash) if the daily quota is hit mid-run.
 
Setup:
    pip install google-genai
 
Add to .env (alongside SUPABASE_URL / SUPABASE_KEY):
    GEMINI_API_KEY=your-key-here
 
Usage:
    python embed.py                 # run until done or quota hit
    python embed.py --limit 300     # cap how many passages to embed this run
"""
 
import os
import re
import time
import argparse
from dotenv import load_dotenv
from supabase import create_client
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
 
load_dotenv()
 
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
 
client = genai.Client(api_key=GEMINI_API_KEY)
 
EMBED_MODEL = "gemini-embedding-001"
OUTPUT_DIM = 768             # matches passages.embedding vector(768) - Matryoshka-truncated
BATCH_SIZE = 20              # passages embedded per single Gemini API call
DB_FETCH_SIZE = 200          # passages pulled from Supabase per round-trip
DAILY_REQUEST_BUFFER = 1400  # stop short of the real daily cap, leaving headroom
 
 
def fetch_unembedded_passages(supabase, limit):
    result = (
        supabase.table("passages")
        .select("id, chunk_text")
        .is_("embedding", "null")
        .order("id")
        .limit(limit)
        .execute()
    )
    return result.data
 
 
def embed_batch(texts):
    """One Gemini call embedding a whole batch of texts at once."""
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=OUTPUT_DIM,
        ),
    )
    return [emb.values for emb in response.embeddings]
 
 
def format_vector(vec):
    """pgvector expects a bracketed literal string, e.g. '[0.1,0.2,...]'."""
    return "[" + ",".join(str(x) for x in vec) + "]"
 
 
def extract_retry_delay(e, default=20) -> float:
    """Pull the server-suggested retry wait (e.g. 'retry in 19.5s') out of
    the error text if present, else fall back to a default wait."""
    match = re.search(r"retry in ([\d.]+)s", str(e))
    if match:
        return float(match.group(1)) + 2  # small buffer on top of what Google asks for
    return default
 
 
def embed_batch_with_retry(texts, max_retries=5):
    """Call Gemini for a batch, retrying on rate-limit (429) errors using
    the server's own suggested wait time instead of a blind guess."""
    for attempt in range(1, max_retries + 1):
        try:
            return embed_batch(texts)
        except Exception as e:
            print(f"    [attempt {attempt}/{max_retries}] error: {e}")
            if not is_quota_error(e):
                raise
            if attempt == max_retries:
                raise
            wait = extract_retry_delay(e)
            print(f"    Rate limit hit - waiting {wait:.0f}s before retrying...")
            time.sleep(wait)
 
 
def is_quota_error(e) -> bool:
    """Detect a rate-limit/quota error across genai SDK error shapes."""
    if isinstance(e, genai_errors.ClientError):
        code = getattr(e, "code", None) or getattr(e, "status_code", None)
        if code == 429:
            return True
    return "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e).upper()
 
 
def main(run_limit):
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
 
    total_embedded = 0
    requests_made = 0
 
    while True:
        if run_limit and total_embedded >= run_limit:
            print(f"\nReached this run's limit of {run_limit} passages.")
            break
 
        rows = fetch_unembedded_passages(supabase, DB_FETCH_SIZE)
        if not rows:
            print("\nNo passages left with NULL embeddings. Fully caught up.")
            break
 
        for i in range(0, len(rows), BATCH_SIZE):
            if run_limit and total_embedded >= run_limit:
                break
 
            if requests_made >= DAILY_REQUEST_BUFFER:
                print(f"\nApproaching daily request budget ({DAILY_REQUEST_BUFFER} requests). "
                      f"Stopping cleanly - re-run this script after quota resets to continue.")
                print(f"Embedded {total_embedded} passages this run ({requests_made} API requests used).")
                return
 
            batch = rows[i:i + BATCH_SIZE]
            texts = [r["chunk_text"] for r in batch]
 
            try:
                vectors = embed_batch_with_retry(texts)
                requests_made += 1
            except Exception as e:
                if is_quota_error(e):
                    print(f"\nRate limit/quota still blocking after retries "
                          f"({requests_made} successful requests so far). "
                          f"Stopping cleanly - re-run this script in a bit to continue.")
                    print(f"Embedded {total_embedded} passages this run.")
                    return
                print(f"\nUnexpected error on batch starting at passage id={batch[0]['id']}: {e}")
                print("Stopping here - re-run the script to retry from this point "
                      "(already-embedded passages won't be redone).")
                return
 
            for row, vec in zip(batch, vectors):
                supabase.table("passages").update(
                    {"embedding": format_vector(vec)}
                ).eq("id", row["id"]).execute()
                total_embedded += 1
 
            print(f"  Embedded passages id {batch[0]['id']}-{batch[-1]['id']} "
                  f"({total_embedded} total this run, {requests_made} API requests used)")
 
            time.sleep(0.7)  # ~85 req/min, under the confirmed 100 req/min free-tier cap
 
    print(f"\nFinished. {total_embedded} passages embedded this run "
          f"using {requests_made} API requests.")
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Max passages to embed this run (default: run until done or quota hit)"
    )
    args = parser.parse_args()
    main(args.limit)
 