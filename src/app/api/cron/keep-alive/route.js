// app/api/cron/keep-alive/route.js
//
// Weekly ping to keep the Supabase project from auto-pausing due to
// inactivity (free-tier projects pause after a period with no activity).
// Triggered by Vercel Cron (see vercel.json) - this route itself does
// nothing on a schedule; Vercel's cron scheduler calls it on the cadence
// defined there.
//
// Secured with CRON_SECRET: Vercel automatically sends
// `Authorization: Bearer <CRON_SECRET>` when invoking a cron job, as long
// as CRON_SECRET is set as an environment variable on the project. Set
// one in Vercel's dashboard (Project -> Settings -> Environment Variables)
// before deploying - without it, this check always fails and the cron
// calls return 401.
//
// Adjust the two Supabase env var names below if your project uses
// different ones than NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY -
// this only needs read access, so the anon key is enough; no service role
// key required here.

import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export async function GET(request) {
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );

  // Trivial read - just enough to register as activity against the
  // project. Doesn't matter which table; `authors` is small and stable.
  const { error } = await supabase.from("authors").select("id").limit(1);

  if (error) {
    console.error("Keep-alive ping failed:", error);
    return NextResponse.json({ ok: false, error: error.message }, { status: 500 });
  }

  return NextResponse.json({ ok: true, pinged_at: new Date().toISOString() });
}