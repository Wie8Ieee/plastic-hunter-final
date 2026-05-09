export default function Slide05Architecture() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 80% 50% at 50% 60%, rgba(6,182,212,0.05) 0%, transparent 70%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #06b6d4 60%, transparent)" }} />

      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        SYSTEM ARCHITECTURE
      </div>

      <div className="absolute top-[12vh] left-[6vw]">
        <h2 style={{ fontSize: "4vw", fontWeight: 800, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
          End-to-end detection pipeline
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#06b6d4", marginTop: "1.5vh", borderRadius: "2px" }} />
      </div>

      {/* Architecture flow — five nodes, compact height */}
      <div className="absolute left-[2vw] right-[2vw] flex items-stretch" style={{ top: "30vh", height: "30vh" }}>

        <div className="flex flex-col items-center justify-center" style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "12px 0 0 12px", padding: "2vh 1.2vw" }}>
          <div style={{ fontSize: "1.8vw", fontWeight: 700, color: "#06b6d4", marginBottom: "1vh", textAlign: "center" }}>Image Upload</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", textAlign: "center", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
            User uploads beach or ocean photo via drag-and-drop
          </div>
        </div>

        <div className="flex items-center justify-center" style={{ width: "3vw", background: "#050e1f", flexShrink: 0 }}>
          <div style={{ fontSize: "2.2vw", color: "#06b6d4", fontWeight: 700 }}>→</div>
        </div>

        <div className="flex flex-col items-center justify-center" style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", padding: "2vh 1.2vw" }}>
          <div style={{ fontSize: "1.8vw", fontWeight: 700, color: "#06b6d4", marginBottom: "1vh", textAlign: "center" }}>FastAPI Backend</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", textAlign: "center", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
            POST /detect receives the image, routes to the CV engine
          </div>
        </div>

        <div className="flex items-center justify-center" style={{ width: "3vw", background: "#050e1f", flexShrink: 0 }}>
          <div style={{ fontSize: "2.2vw", color: "#06b6d4", fontWeight: 700 }}>→</div>
        </div>

        <div className="flex flex-col items-center justify-center" style={{ flex: 1, background: "#0d1f38", border: "1px solid rgba(6,182,212,0.4)", padding: "2vh 1.2vw" }}>
          <div style={{ fontSize: "1.8vw", fontWeight: 700, color: "#10b981", marginBottom: "1vh", textAlign: "center" }}>CV Detection Engine</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", textAlign: "center", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
            Pillow + NumPy edge analysis, bounding boxes + confidence scores
          </div>
        </div>

        <div className="flex items-center justify-center" style={{ width: "3vw", background: "#050e1f", flexShrink: 0 }}>
          <div style={{ fontSize: "2.2vw", color: "#06b6d4", fontWeight: 700 }}>→</div>
        </div>

        <div className="flex flex-col items-center justify-center" style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", padding: "2vh 1.2vw" }}>
          <div style={{ fontSize: "1.8vw", fontWeight: 700, color: "#06b6d4", marginBottom: "1vh", textAlign: "center" }}>SQLite Database</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", textAlign: "center", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
            Stores count, confidence, severity, timestamp, geolocation
          </div>
        </div>

        <div className="flex items-center justify-center" style={{ width: "3vw", background: "#050e1f", flexShrink: 0 }}>
          <div style={{ fontSize: "2.2vw", color: "#06b6d4", fontWeight: 700 }}>→</div>
        </div>

        <div className="flex flex-col items-center justify-center" style={{ flex: 1, background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "0 12px 12px 0", padding: "2vh 1.2vw" }}>
          <div style={{ fontSize: "1.8vw", fontWeight: 700, color: "#06b6d4", marginBottom: "1vh", textAlign: "center" }}>Map + Dashboard</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", textAlign: "center", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
            Leaflet.js map, Chart.js trends, reduction banner in real time
          </div>
        </div>
      </div>

      {/* API endpoints strip */}
      <div className="absolute left-[2vw] right-[2vw] flex" style={{ top: "66vh", gap: "2vw" }}>
        <div style={{ flex: 1, background: "rgba(6,182,212,0.06)", border: "1px solid rgba(6,182,212,0.15)", borderRadius: "8px", padding: "1.5vh 1.5vw", textAlign: "center" }}>
          <div style={{ fontSize: "1.7vw", fontWeight: 700, color: "#06b6d4", fontFamily: "var(--font-body-family)" }}>POST /detect</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>Run detection on image</div>
        </div>
        <div style={{ flex: 1, background: "rgba(6,182,212,0.06)", border: "1px solid rgba(6,182,212,0.15)", borderRadius: "8px", padding: "1.5vh 1.5vw", textAlign: "center" }}>
          <div style={{ fontSize: "1.7vw", fontWeight: 700, color: "#06b6d4", fontFamily: "var(--font-body-family)" }}>GET /results</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>All past detections</div>
        </div>
        <div style={{ flex: 1, background: "rgba(6,182,212,0.06)", border: "1px solid rgba(6,182,212,0.15)", borderRadius: "8px", padding: "1.5vh 1.5vw", textAlign: "center" }}>
          <div style={{ fontSize: "1.7vw", fontWeight: 700, color: "#06b6d4", fontFamily: "var(--font-body-family)" }}>GET /stats</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>Summary statistics + trends</div>
        </div>
        <div style={{ flex: 1, background: "rgba(6,182,212,0.06)", border: "1px solid rgba(6,182,212,0.15)", borderRadius: "8px", padding: "1.5vh 1.5vw", textAlign: "center" }}>
          <div style={{ fontSize: "1.7vw", fontWeight: 700, color: "#06b6d4", fontFamily: "var(--font-body-family)" }}>GET /annotated</div>
          <div style={{ fontSize: "1.5vw", color: "#64748b", fontFamily: "var(--font-body-family)" }}>Annotated result images</div>
        </div>
      </div>

      <div className="absolute bottom-[3.5vh] left-0 right-0 text-center">
        <div style={{ fontSize: "1.5vw", color: "#475569", fontFamily: "var(--font-body-family)" }}>
          Image → CV engine → SQLite → frontend dashboard · Python 3.11 · Port 8000
        </div>
      </div>
    </div>
  );
}
