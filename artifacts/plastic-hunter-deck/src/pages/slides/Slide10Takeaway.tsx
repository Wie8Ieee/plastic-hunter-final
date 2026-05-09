const base = import.meta.env.BASE_URL;

export default function Slide10Takeaway() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      {/* Hero image — same as title for bookend effect */}
      <img
        src={`${base}hero-ocean.png`}
        crossOrigin="anonymous"
        alt="Ocean"
        className="absolute inset-0 w-full h-full object-cover"
        style={{ opacity: 0.2 }}
      />

      <div className="absolute inset-0" style={{ background: "linear-gradient(135deg, rgba(5,14,31,0.92) 0%, rgba(6,182,212,0.06) 100%)" }} />

      {/* Teal accent left bar */}
      <div className="absolute left-0 top-0 h-full" style={{ width: "0.5vw", background: "linear-gradient(180deg, #10b981 0%, #06b6d4 100%)" }} />

      {/* Hackathon badge */}
      <div className="absolute top-[4vh] right-[5vw]" style={{ fontSize: "1.5vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.06em", fontFamily: "var(--font-body-family)" }}>
        AESS SUSTAINABILITY HACKATHON 2026
      </div>

      {/* Main content */}
      <div className="absolute left-[8vw]" style={{ top: "18vh", maxWidth: "60vw" }}>
        <div style={{ fontSize: "1.6vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.1em", marginBottom: "2vh", fontFamily: "var(--font-body-family)" }}>
          FINAL TAKEAWAY
        </div>
        <h2 style={{ fontSize: "5vw", fontWeight: 800, color: "#f1f5f9", lineHeight: 1.05, letterSpacing: "-0.03em", marginBottom: "3vh", textWrap: "balance" }}>
          Simple technology.
          <span style={{ color: "#06b6d4", display: "block" }}>Measurable impact.</span>
          <span style={{ color: "#10b981", display: "block" }}>Transparent evidence.</span>
        </h2>
        <div style={{ width: "6vw", height: "0.4vh", background: "linear-gradient(90deg,#10b981,#06b6d4)", marginBottom: "3.5vh", borderRadius: "2px" }} />
        <p style={{ fontSize: "2vw", color: "#94a3b8", lineHeight: 1.5, fontFamily: "var(--font-body-family)" }}>
          Plastic Hunter AI proves that accessible tools — Python, Pillow, SQLite, and a browser — are enough to build a working marine pollution detection system with a 25.5% improvement over baseline.
        </p>
      </div>

      {/* Three bottom stats */}
      <div className="absolute left-[8vw] right-[5vw] flex" style={{ bottom: "12vh", gap: "3vw" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#06b6d4" }}>25.5%</div>
          <div style={{ fontSize: "1.6vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>reduction vs baseline</div>
        </div>
        <div style={{ width: "1px", background: "rgba(100,116,139,0.25)" }} />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#06b6d4" }}>12</div>
          <div style={{ fontSize: "1.6vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>global coastal sites monitored</div>
        </div>
        <div style={{ width: "1px", background: "rgba(100,116,139,0.25)" }} />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#06b6d4" }}>4</div>
          <div style={{ fontSize: "1.6vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>fully functional product tabs</div>
        </div>
        <div style={{ width: "1px", background: "rgba(100,116,139,0.25)" }} />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "4vw", fontWeight: 800, color: "#06b6d4" }}>0</div>
          <div style={{ fontSize: "1.6vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>external API dependencies</div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between" style={{ padding: "2.2vh 8vw", background: "rgba(6,182,212,0.07)", borderTop: "1px solid rgba(6,182,212,0.15)" }}>
        <div style={{ fontSize: "2vw", fontWeight: 700, color: "#f1f5f9", fontFamily: "var(--font-body-family)" }}>
          Plastic Hunter AI
        </div>
        <div style={{ fontSize: "1.6vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>
          Team Name · AESS Sustainability Hackathon 2026
        </div>
      </div>
    </div>
  );
}
