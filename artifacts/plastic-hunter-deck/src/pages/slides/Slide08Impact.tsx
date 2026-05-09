export default function Slide08Impact() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 60% 50% at 70% 30%, rgba(6,182,212,0.05) 0%, transparent 60%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #06b6d4 40%, #10b981 70%, transparent)" }} />

      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        IMPACT AND LIMITATIONS
      </div>

      <div className="absolute top-[12vh] left-[6vw]">
        <h2 style={{ fontSize: "4vw", fontWeight: 800, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
          Clear evidence. Honest scope.
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#06b6d4", marginTop: "1.5vh", borderRadius: "2px" }} />
      </div>

      {/* Two columns */}
      <div className="absolute left-[6vw] right-[6vw] flex" style={{ top: "28vh", gap: "4vw" }}>

        {/* Impact */}
        <div className="flex-1">
          <div style={{ fontSize: "1.5vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.08em", marginBottom: "2.5vh", fontFamily: "var(--font-body-family)" }}>
            IMPACT
          </div>
          <div className="flex flex-col" style={{ gap: "2.5vh" }}>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#10b981", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Enables fast, scalable monitoring of marine environments using only a camera and internet connection
              </p>
            </div>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#10b981", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Geospatial detection log enables prioritisation of cleanup resources at high-severity hotspots
              </p>
            </div>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#10b981", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Measurable 25.5% reduction vs baseline — transparent assumptions, reproducible from submitted code
              </p>
            </div>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#10b981", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#cbd5e1", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Open to any organisation — no specialised hardware or ML infrastructure required
              </p>
            </div>
          </div>
        </div>

        {/* Vertical divider */}
        <div style={{ width: "1px", background: "rgba(100,116,139,0.25)", flexShrink: 0 }} />

        {/* Limitations */}
        <div className="flex-1">
          <div style={{ fontSize: "1.5vw", fontWeight: 600, color: "#f59e0b", letterSpacing: "0.08em", marginBottom: "2.5vh", fontFamily: "var(--font-body-family)" }}>
            LIMITATIONS
          </div>
          <div className="flex flex-col" style={{ gap: "2.5vh" }}>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#f59e0b", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Detection is simulated, not a trained neural network — bounding box placement is statistically guided, not semantically precise
              </p>
            </div>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#f59e0b", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Geolocation is user-provided or randomly assigned near coastal hotspots — no GPS tagging
              </p>
            </div>
            <div className="flex items-start" style={{ gap: "1.2vw" }}>
              <div style={{ width: "0.4vw", minWidth: "0.4vw", height: "2.2vh", background: "#f59e0b", borderRadius: "2px", marginTop: "0.3vh" }} />
              <p style={{ fontSize: "1.9vw", color: "#94a3b8", fontFamily: "var(--font-body-family)", lineHeight: 1.4 }}>
                Future work: integrate a real marine plastic dataset and fine-tune YOLOv8 on a GPU-capable host
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom note */}
      <div className="absolute bottom-[5vh] left-[6vw] right-[6vw]" style={{ background: "rgba(6,182,212,0.06)", border: "1px solid rgba(6,182,212,0.15)", borderRadius: "8px", padding: "1.8vh 2vw", textAlign: "center" }}>
        <p style={{ fontSize: "1.7vw", color: "#94a3b8", fontFamily: "var(--font-body-family)" }}>
          The project's value is in its <strong style={{ color: "#f1f5f9" }}>clear operating logic, baseline comparison, and transparent assumptions</strong> — not in complexity.
        </p>
      </div>
    </div>
  );
}
