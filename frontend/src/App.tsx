import { useQuery } from "@tanstack/react-query";
import "./App.css";

type Health = { status: string };

async function fetchHealth(): Promise<Health> {
  const response = await fetch("/api/health");
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

function App() {
  // The whole point of this component: prove a request reaches the API and comes back.
  const { data, isPending, isError, error } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: false,
  });

  return (
    <main className="app">
      <h1>Counterfactual Atlas</h1>
      <p className="tagline">
        A virtual museum of world history with AI-driven counterfactual timelines.
      </p>

      <section className="status" aria-live="polite">
        <h2>API status</h2>
        {isPending && <p className="pending">checking…</p>}
        {isError && <p className="error">unreachable — {error.message}</p>}
        {data && <p className="ok">{data.status}</p>}
      </section>
    </main>
  );
}

export default App;
