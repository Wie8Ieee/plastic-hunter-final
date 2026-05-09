const base = import.meta.env.BASE_URL;

export default function Slide01Title() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      {/* Hero image with overlay */}
      <img
        src={`${base}hero-ocean.png`}
        crossOrigin="anonymous"
        alt="Ocean plastic pollution"
        className="absolute inset-0 w-full h-full object-cover"
        style={{ opacity: 0.35 }}
      />

      {/* Deep gradient overlay */}
      <div className="absolute inset-0" style={{ background: "linear-gradient(135deg, rgba(5,14,31,0.85) 0%, rgba(6,182,212,0.08) 100%)" }} />

      {/* Teal accent left bar */}
      <div className="absolute left-0 top-0 h-full" style={{ width: "0.5vw", background: "linear-gradient(180deg, #06b6d4 0%, #10b981 100%)" }} />

      {/* Hackathon badge top-right */}
      <div className="absolute top-[4vh] right-[4vw] text-right">
        <div style={{ fontSize: "1.5vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.06em", fontFamily: "var(--font-body-family)" }}>
          AESS SUSTAINABILITY HACKATHON 2026
        </div>
      </div>

      {/* Main content — left aligned */}
      <div className="absolute left-[7vw] bottom-[18vh]">
        <div style={{ fontSize: "1.6vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.12em", marginBottom: "1.5vh", fontFamily: "var(--font-body-family)" }}>
          MARINE PLASTIC DETECTION SYSTEM
        </div>
        <h1 style={{ fontSize: "7.5vw", fontWeight: 800, color: "#f1f5f9", lineHeight: 1.0, letterSpacing: "-0.03em", marginBottom: "2.5vh", textWrap: "balance" }}>
          Plastic Hunter
          <span style={{ color: "#06b6d4", display: "block" }}>AI</span>
        </h1>
        <div style={{ width: "8vw", height: "0.4vh", background: "linear-gradient(90deg,#06b6d4,#10b981)", marginBottom: "2.5vh", borderRadius: "2px" }} />
        <p style={{ fontSize: "2.2vw", fontWeight: 400, color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
          Computer vision-powered detection of marine plastic pollution
        </p>
      </div>

      {/* Team + year bottom bar */}
      <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between" style={{ padding: "2.2vh 7vw", background: "rgba(6,182,212,0.08)", borderTop: "1px solid rgba(6,182,212,0.2)" }}>
        <div style={{ fontSize: "1.8vw", fontWeight: 600, color: "#f1f5f9", fontFamily: "var(--font-body-family)" }}>
          Team Name
        </div>
        <div style={{ fontSize: "1.6vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>
          Phase 1 Submission · 2026
        </div>
      </div>
    </div>
  );
}
