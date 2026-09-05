import { useState } from "react";
import "./App.css";
import type { CelesteState } from "./visualizers/types";
import { getVisualizer } from "./visualizers/registry";

type DebugEvent = {
  id: number;
  type: "system" | "state";
  message: string;
};

const stateLabels: Record<CelesteState, string> = {
  idle: "IDLE",
  listening: "LISTENING",
  thinking: "THINKING",
  speaking: "SPEAKING",
};

function App() {
  const [celesteState] = useState<CelesteState>("idle");
  const visualizer = getVisualizer("crystal");
  const ActiveVisualizer = visualizer.component;
  const [debugOpen, setDebugOpen] = useState(false);

  const debugEvents: DebugEvent[] = [
    {
      id: 1,
      type: "system",
      message: "Celeste Desktop initialized",
    },
    {
      id: 2,
      type: "state",
      message: stateLabels[celesteState],
    },
  ];

  return (
    <main className={`celeste-app ${debugOpen ? "debug-open" : ""}`}>
      <section className="celeste-stage">
        <div className="ambient ambient-one" />
        <div className="ambient ambient-two" />

        <div className="celeste-presence">
          <span className="celeste-name">CELESTE</span>

          <div className="visualizer-container">
            <ActiveVisualizer
              state={celesteState}
              audioLevel={0}
              accentColor="#ff7a18"
            />
          </div>

          <div className="state-indicator">
            <span className="state-dot" />
            <span>{stateLabels[celesteState]}</span>
          </div>
        </div>

        <button
          className="settings-button"
          type="button"
          aria-label="Ajustes"
          title="Ajustes — próximamente"
        >
          ⚙
        </button>

        {!debugOpen && (
          <button
            className="debug-trigger"
            type="button"
            onClick={() => setDebugOpen(true)}
          >
            <span>DEBUG</span>
            <span className="debug-arrow">‹</span>
          </button>
        )}
      </section>

      <aside className={`debug-panel ${debugOpen ? "open" : ""}`}>
        <header className="debug-header">
          <div>
            <span className="debug-eyebrow">CELESTE</span>
            <h2>Development</h2>
          </div>

          <button
            className="debug-close"
            type="button"
            onClick={() => setDebugOpen(false)}
            aria-label="Cerrar panel"
          >
            ×
          </button>
        </header>

        <nav className="debug-tabs" aria-label="Debug">
          <button className="active" type="button">
            ALL
          </button>
          <button type="button">CHAT</button>
          <button type="button">EVENTS</button>
          <button type="button">SYSTEM</button>
        </nav>

        <div className="debug-content">
          {debugEvents.map((event) => (
            <article className="debug-event" key={event.id}>
              <span className={`event-type ${event.type}`}>
                {event.type}
              </span>
              <p>{event.message}</p>
            </article>
          ))}
        </div>

        <footer className="debug-footer">
          <span className="connection-dot" />
          <span>LOCAL DEVELOPMENT</span>
        </footer>
      </aside>
    </main>
  );
}

export default App;