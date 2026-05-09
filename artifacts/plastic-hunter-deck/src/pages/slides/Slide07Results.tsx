export default function Slide07Results() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 70% 60% at 50% 40%, rgba(16,185,129,0.08) 0%, transparent 70%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #10b981 60%, transparent)" }} />

      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        RESULTS
      </div>

      {/* Left — big stat */}
      <div className="absolute left-[6vw] top-[13vh]" style={{ width: "40vw" }}>
        <h2 style={{ fontSize: "3.8vw", fontWeight: 800, color: "#f1f5f9", lineHeight: 1.1, letterSpacing: "-0.02em", marginBottom: "2.5vh", textWrap: "balance" }}>
          Baseline vs AI-Optimised comparison
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#10b981", marginBottom: "4vh", borderRadius: "2px" }} />

        {/* Reduction hero number */}
        <div style={{ fontSize: "13vw", fontWeight: 800, color: "#10b981", lineHeight: 1, letterSpacing: "-0.05em" }}>25.5%</div>
        <div style={{ fontSize: "2.2vw", fontWeight: 600, color: "#94a3b8", marginTop: "0.5vh", fontFamily: "var(--font-body-family)" }}>
          estimated plastic detection improvement
        </div>
        <div style={{ fontSize: "1.7vw", color: "#475569", marginTop: "1vh", fontFamily: "var(--font-body-family)" }}>
          Simulated estimate — assumptions documented
        </div>
      </div>

      {/* Right — comparison bars */}
      <div className="absolute right-[5vw] top-[13vh]" style={{ width: "42vw" }}>

        {/* Baseline bar */}
        <div style={{ marginBottom: "4vh" }}>
          <div className="flex items-center justify-between" style={{ marginBottom: "1.2vh" }}>
            <div style={{ fontSize: "2vw", fontWeight: 700, color: "#ef4444", fontFamily: "var(--font-body-family)" }}>Baseline (manual)</div>
            <div style={{ fontSize: "2.2vw", fontWeight: 800, color: "#ef4444" }}>106</div>
          </div>
          <div style={{ height: "4vh", background: "#0d1f38", borderRadius: "6px", overflow: "hidden", border: "1px solid #1e3a5f" }}>
            <div style={{ width: "100%", height: "100%", background: "linear-gradient(90deg,#ef4444,#dc2626)", borderRadius: "6px" }} />
          </div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", marginTop: "0.8vh", fontFamily: "var(--font-body-family)" }}>
            Plastic items in simulated monitoring period
          </div>
        </div>

        {/* AI Optimised bar */}
        <div style={{ marginBottom: "5vh" }}>
          <div className="flex items-center justify-between" style={{ marginBottom: "1.2vh" }}>
            <div style={{ fontSize: "2vw", fontWeight: 700, color: "#10b981", fontFamily: "var(--font-body-family)" }}>AI-Optimised</div>
            <div style={{ fontSize: "2.2vw", fontWeight: 800, color: "#10b981" }}>79</div>
          </div>
          <div style={{ height: "4vh", background: "#0d1f38", borderRadius: "6px", overflow: "hidden", border: "1px solid #1e3a5f" }}>
            <div style={{ width: "74.5%", height: "100%", background: "linear-gradient(90deg,#10b981,#059669)", borderRadius: "6px" }} />
          </div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", marginTop: "0.8vh", fontFamily: "var(--font-body-family)" }}>
            Items when AI-assisted detection applied
          </div>
        </div>

        {/* KPI row */}
        <div className="flex" style={{ gap: "2vw" }}>
          <div style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "10px", padding: "2vh 1.5vw", textAlign: "center" }}>
            <div style={{ fontSize: "3.5vw", fontWeight: 800, color: "#06b6d4" }}>12</div>
            <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>scans across 12 global coastal sites</div>
          </div>
          <div style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "10px", padding: "2vh 1.5vw", textAlign: "center" }}>
            <div style={{ fontSize: "3.5vw", fontWeight: 800, color: "#06b6d4" }}>75%</div>
            <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>average detection confidence</div>
          </div>
          <div style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "10px", padding: "2vh 1.5vw", textAlign: "center" }}>
            <div style={{ fontSize: "3.5vw", fontWeight: 800, color: "#06b6d4" }}>&lt;2s</div>
            <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>average processing time per image</div>
          </div>
        </div>
      </div>
    </div>
  );
}
