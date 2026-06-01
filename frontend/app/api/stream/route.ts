import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get("job_id");

  if (!jobId) {
    return new Response(
      JSON.stringify({ error: "Missing required parameter 'job_id'." }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const backendUrl = `http://localhost:8000/api/stream/${jobId}`;

  try {
    const backendResponse = await fetch(backendUrl);

    if (!backendResponse.ok) {
      return new Response(
        JSON.stringify({ error: `Backend stream returned status: ${backendResponse.status}` }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    }

    // Set up a readable stream proxy
    const reader = backendResponse.body?.getReader();
    const encoder = new TextEncoder();

    const customStream = new ReadableStream({
      async start(controller) {
        if (!reader) {
          controller.close();
          return;
        }

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            controller.enqueue(value);
          }
        } catch (error) {
          console.error("Error reading proxy SSE stream:", error);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(customStream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error: any) {
    console.error("Proxy stream connection failed:", error);
    return new Response(
      JSON.stringify({ error: "Failed to connect to backend stream broker." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
