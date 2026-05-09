export default function Slide03Baseline() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 60% 50% at 20% 80%, rgba(239,68,68,0.05) 0%, transparent 60%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #ef4444 30%, transparent)" }} />

      {/* Label */}
      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#ef4444", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        BASELINE SCENARIO
      </div>

      {/* Title */}
      <div className="absolute top-[12vh] left-[6vw] right-[6vw]">
        <h2 style={{ fontSize: "4vw", fontWeight: 800, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1.1, textWrap: "balance" }}>
          Without AI: manual detection misses critical pollution events
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#ef4444", marginTop: "2vh", borderRadius: "2px" }} />
      </div>

      {/* Three baseline problem cards */}
      <div className="absolute left-[6vw] right-[6vw] flex" style={{ top: "34vh", gap: "2.5vw" }}>

        {/* Card 1 */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid rgba(239,68,68,0.2)", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#ef4444", marginBottom: "1.5vh" }}>Slow</div>
          <div style={{ width: "3vw", height: "0.3vh", background: "rgba(239,68,68,0.4)", marginBottom: "1.8vh", borderRadius: "2px" }} />
          <p style={{ fontSize: "1.8vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.45 }}>
            Manual beach surveys take days to weeks. Pollution spreads faster than crews can survey it.
          </p>
        </div>

        {/* Card 2 */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid rgba(239,68,68,0.2)", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#ef4444", marginBottom: "1.5vh" }}>Costly</div>
          <div style={{ width: "3vw", height: "0.3vh", background: "rgba(239,68,68,0.4)", marginBottom: "1.8vh", borderRadius: "2px" }} />
          <p style={{ fontSize: "1.8vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.45 }}>
            Field teams, boats, and labs are resource-intensive. Continuous monitoring is economically unviable.
          </p>
        </div>

        {/* Card 3 */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid rgba(239,68,68,0.2)", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#ef4444", marginBottom: "1.5vh" }}>Incomplete</div>
          <div style={{ width: "3vw", height: "0.3vh", background: "rgba(239,68,68,0.4)", marginBottom: "1.8vh", borderRadius: "2px" }} />
          <p style={{ fontSize: "1.8vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.45 }}>
            Coverage is geographically sparse. An estimated 26% of plastic debris goes undetected.
          </p>
        </div>
      </div>

      {/* Bottom baseline comparison row */}
      <div className="absolute bottom-[6vh] left-[6vw] right-[6vw]" style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: "10px", padding: "2vh 2.5vw" }}>
        <div className="flex items-center justify-between">
          <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
            Baseline: <strong style={{ color: "#f1f5f9" }}>106 plastic items</strong> detected in simulated monitoring period
          </div>
          <div style={{ fontSize: "1.7vw", color: "#ef4444", fontFamily: "var(--font-body-family)", fontWeight: 600 }}>
            ~26% missed without AI assistance
          </div>
        </div>
      </div>
    </div>
  );
}
