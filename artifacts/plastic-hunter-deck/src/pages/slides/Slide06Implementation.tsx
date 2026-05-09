export default function Slide06Implementation() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 60% 50% at 30% 70%, rgba(16,185,129,0.05) 0%, transparent 60%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #10b981 60%, transparent)" }} />

      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        IMPLEMENTATION METHOD
      </div>

      <div className="absolute top-[12vh] left-[6vw]">
        <h2 style={{ fontSize: "4vw", fontWeight: 800, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
          Built and tested — fully functional on Replit
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#10b981", marginTop: "1.5vh", borderRadius: "2px" }} />
      </div>

      {/* Three columns */}
      <div className="absolute left-[5vw] right-[5vw] flex" style={{ top: "30vh", gap: "2.5vw" }}>

        {/* Backend */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "1.3vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.08em", marginBottom: "1.5vh", fontFamily: "var(--font-body-family)" }}>
            BACKEND
          </div>
          <div style={{ fontSize: "2.5vw", fontWeight: 700, color: "#f1f5f9", marginBottom: "2vh" }}>Python + FastAPI</div>

          <div className="flex flex-col" style={{ gap: "1.5vh" }}>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>FastAPI</span> — REST endpoints for detection, results, stats
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>Uvicorn</span> — ASGI server, serves static frontend
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>SQLite</span> — seeded with 12 real coastal demo locations
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>Pillow</span> — annotated JPEG output with bounding boxes
            </div>
          </div>
        </div>

        {/* Detection */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid rgba(6,182,212,0.35)", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "1.3vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.08em", marginBottom: "1.5vh", fontFamily: "var(--font-body-family)" }}>
            DETECTION ENGINE
          </div>
          <div style={{ fontSize: "2.5vw", fontWeight: 700, color: "#f1f5f9", marginBottom: "2vh" }}>CV Simulation</div>

          <div className="flex flex-col" style={{ gap: "1.5vh" }}>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#06b6d4", fontWeight: 600 }}>NumPy</span> — image edge density analysis via 4×4 grid
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#06b6d4", fontWeight: 600 }}>FIND_EDGES</span> — Pillow filter guides bounding box placement
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#06b6d4", fontWeight: 600 }}>14 plastic types</span> — bottles, bags, nets, foam, utensils
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#06b6d4", fontWeight: 600 }}>Same contract</span> as YOLOv8 — identical JSON response format
            </div>
          </div>
        </div>

        {/* Frontend */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "1.3vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.08em", marginBottom: "1.5vh", fontFamily: "var(--font-body-family)" }}>
            FRONTEND
          </div>
          <div style={{ fontSize: "2.5vw", fontWeight: 700, color: "#f1f5f9", marginBottom: "2vh" }}>Single-page HTML</div>

          <div className="flex flex-col" style={{ gap: "1.5vh" }}>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>Canvas API</span> — draws bounding boxes over uploaded image
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>Leaflet.js</span> — dark-mode interactive global pollution map
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>Chart.js</span> — bar chart (daily) + doughnut (confidence)
            </div>
            <div style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
              <span style={{ color: "#10b981", fontWeight: 600 }}>4 tabs</span> — Detect, Map, Dashboard, History
            </div>
          </div>
        </div>
      </div>

      {/* Note about YOLOv8 decision */}
      <div className="absolute bottom-[5vh] left-[5vw] right-[5vw]" style={{ background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: "8px", padding: "1.8vh 2vw" }}>
        <div className="flex items-center" style={{ gap: "1.5vw" }}>
          <div style={{ fontSize: "1.6vw", color: "#10b981", fontWeight: 600, fontFamily: "var(--font-body-family)", whiteSpace: "nowrap" }}>Design decision</div>
          <div style={{ width: "1px", height: "3vh", background: "rgba(16,185,129,0.3)" }} />
          <p style={{ fontSize: "1.6vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
            YOLOv8 was excluded: Ultralytics pulls 400 MB+ of CUDA packages exceeding Replit's free-tier disk quota. The CV simulation delivers identical API contract with zero model download.
          </p>
        </div>
      </div>
    </div>
  );
}
