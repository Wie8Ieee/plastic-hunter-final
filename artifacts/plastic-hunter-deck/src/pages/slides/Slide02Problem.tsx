export default function Slide02Problem() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      {/* Subtle bg texture */}
      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 70% 60% at 80% 50%, rgba(239,68,68,0.06) 0%, transparent 70%)" }} />

      {/* Top accent bar */}
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #ef4444, #f97316, transparent)" }} />

      {/* Slide label */}
      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#ef4444", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        THE PROBLEM
      </div>

      {/* Left column — text */}
      <div className="absolute left-[6vw] top-[15vh]" style={{ width: "52vw" }}>
        <h2 style={{ fontSize: "4.5vw", fontWeight: 800, color: "#f1f5f9", lineHeight: 1.1, letterSpacing: "-0.02em", marginBottom: "3vh", textWrap: "balance" }}>
          Marine plastic pollution kills faster than we can find it
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#ef4444", marginBottom: "3vh", borderRadius: "2px" }} />

        <div className="flex flex-col" style={{ gap: "2.2vh" }}>
          <div className="flex items-start" style={{ gap: "1.4vw" }}>
            <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#ef4444", borderRadius: "2px", marginTop: "0.4vh" }} />
            <p style={{ fontSize: "2vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
              Over <strong style={{ color: "#f1f5f9" }}>8 million tonnes</strong> of plastic enter the ocean every year
            </p>
          </div>
          <div className="flex items-start" style={{ gap: "1.4vw" }}>
            <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#ef4444", borderRadius: "2px", marginTop: "0.4vh" }} />
            <p style={{ fontSize: "2vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
              Traditional monitoring relies on <strong style={{ color: "#f1f5f9" }}>manual surveys</strong> — slow, expensive, and geographically limited
            </p>
          </div>
          <div className="flex items-start" style={{ gap: "1.4vw" }}>
            <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#ef4444", borderRadius: "2px", marginTop: "0.4vh" }} />
            <p style={{ fontSize: "2vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
              Early detection at <strong style={{ color: "#f1f5f9" }}>global scale</strong> is impossible without automation
            </p>
          </div>
        </div>
      </div>

      {/* Right column — big stat */}
      <div className="absolute right-[6vw] top-[18vh] flex flex-col items-center justify-center" style={{ width: "30vw" }}>
        <div style={{ fontSize: "13vw", fontWeight: 800, color: "#ef4444", lineHeight: 1, letterSpacing: "-0.04em" }}>8M</div>
        <div style={{ fontSize: "2vw", fontWeight: 600, color: "#94a3b8", textAlign: "center", marginTop: "1vh", fontFamily: "var(--font-body-family)" }}>
          tonnes of plastic
        </div>
        <div style={{ fontSize: "1.8vw", color: "#64748b", textAlign: "center", fontFamily: "var(--font-body-family)" }}>
          enter oceans annually
        </div>
        <div style={{ marginTop: "4vh", padding: "1.5vh 2vw", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: "10px", textAlign: "center" }}>
          <div style={{ fontSize: "3.5vw", fontWeight: 800, color: "#ef4444" }}>~26%</div>
          <div style={{ fontSize: "1.6vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>missed by manual methods</div>
        </div>
      </div>

      {/* Bottom divider */}
      <div className="absolute bottom-[4vh] left-[6vw] right-[6vw] flex items-center" style={{ gap: "1vw" }}>
        <div style={{ flex: 1, height: "1px", background: "rgba(100,116,139,0.25)" }} />
        <div style={{ fontSize: "1.5vw", color: "#475569", fontFamily: "var(--font-body-family)" }}>Problem Statement</div>
        <div style={{ flex: 1, height: "1px", background: "rgba(100,116,139,0.25)" }} />
      </div>
    </div>
  );
}
