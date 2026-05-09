export default function Slide04Solution() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 70% 60% at 50% 40%, rgba(6,182,212,0.07) 0%, transparent 70%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #06b6d4 60%, transparent)" }} />

      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        PROPOSED SOLUTION
      </div>

      {/* Title centered */}
      <div className="absolute top-[12vh] left-0 right-0 text-center" style={{ padding: "0 10vw" }}>
        <h2 style={{ fontSize: "4.2vw", fontWeight: 800, color: "#f1f5f9", lineHeight: 1.1, letterSpacing: "-0.02em", textWrap: "balance" }}>
          AI-powered image analysis — instant detection, global coverage
        </h2>
        <div style={{ width: "6vw", height: "0.35vh", background: "linear-gradient(90deg,#06b6d4,#10b981)", margin: "2vh auto 0", borderRadius: "2px" }} />
        <p style={{ fontSize: "2vw", color: "#94a3b8", marginTop: "2vh", fontFamily: "var(--font-body-family)" }}>
          Upload any beach or ocean image. Get AI analysis in seconds.
        </p>
      </div>

      {/* Three feature panels */}
      <div className="absolute left-[5vw] right-[5vw] flex" style={{ top: "40vh", gap: "2.5vw" }}>

        <div className="flex-1 flex flex-col" style={{ background: "linear-gradient(135deg,#0d1f38,#091929)", border: "1px solid rgba(6,182,212,0.25)", borderRadius: "14px", padding: "3.5vh 2.2vw" }}>
          <div style={{ fontSize: "3vw", fontWeight: 800, color: "#06b6d4", marginBottom: "1.2vh" }}>01</div>
          <div style={{ fontSize: "2.2vw", fontWeight: 700, color: "#f1f5f9", marginBottom: "1.5vh" }}>Detect</div>
          <p style={{ fontSize: "1.8vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.45, flex: 1 }}>
            Computer vision engine identifies plastic waste in uploaded images with colour-coded bounding boxes and confidence scores.
          </p>
        </div>

        <div className="flex-1 flex flex-col" style={{ background: "linear-gradient(135deg,#0d1f38,#091929)", border: "1px solid rgba(6,182,212,0.25)", borderRadius: "14px", padding: "3.5vh 2.2vw" }}>
          <div style={{ fontSize: "3vw", fontWeight: 800, color: "#06b6d4", marginBottom: "1.2vh" }}>02</div>
          <div style={{ fontSize: "2.2vw", fontWeight: 700, color: "#f1f5f9", marginBottom: "1.5vh" }}>Map</div>
          <p style={{ fontSize: "1.8vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.45, flex: 1 }}>
            Every detection event is stored with geolocation and plotted on an interactive Leaflet.js global pollution map.
          </p>
        </div>

        <div className="flex-1 flex flex-col" style={{ background: "linear-gradient(135deg,#0d1f38,#091929)", border: "1px solid rgba(6,182,212,0.25)", borderRadius: "14px", padding: "3.5vh 2.2vw" }}>
          <div style={{ fontSize: "3vw", fontWeight: 800, color: "#06b6d4", marginBottom: "1.2vh" }}>03</div>
          <div style={{ fontSize: "2.2vw", fontWeight: 700, color: "#f1f5f9", marginBottom: "1.5vh" }}>Analyse</div>
          <p style={{ fontSize: "1.8vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.45, flex: 1 }}>
            Dashboard tracks trends over time: detections per day, confidence distribution, severity breakdown, and AI vs baseline impact.
          </p>
        </div>
      </div>

      {/* Bottom accent */}
      <div className="absolute bottom-[5vh] left-0 right-0 text-center">
        <div style={{ fontSize: "1.8vw", color: "#475569", fontFamily: "var(--font-body-family)" }}>
          Fully operational · FastAPI backend · SQLite storage · Single-page frontend
        </div>
      </div>
    </div>
  );
}
