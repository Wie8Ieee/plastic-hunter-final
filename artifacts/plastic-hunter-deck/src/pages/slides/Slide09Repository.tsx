export default function Slide09Repository() {
  return (
    <div className="relative w-screen h-screen overflow-hidden" style={{ background: "#050e1f", fontFamily: "var(--font-display-family)" }}>

      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse 60% 50% at 30% 60%, rgba(6,182,212,0.05) 0%, transparent 60%)" }} />
      <div className="absolute top-0 left-0 right-0" style={{ height: "0.5vh", background: "linear-gradient(90deg, #06b6d4 60%, transparent)" }} />

      <div className="absolute top-[5vh] left-[6vw]" style={{ fontSize: "1.3vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.1em", fontFamily: "var(--font-body-family)" }}>
        REPOSITORY AND REPRODUCIBILITY
      </div>

      <div className="absolute top-[12vh] left-[6vw]">
        <h2 style={{ fontSize: "4vw", fontWeight: 800, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1.1 }}>
          Every result is reproducible from submitted files
        </h2>
        <div style={{ width: "5vw", height: "0.35vh", background: "#06b6d4", marginTop: "1.5vh", borderRadius: "2px" }} />
      </div>

      {/* Two columns */}
      <div className="absolute left-[6vw] right-[6vw] flex" style={{ top: "30vh", gap: "4vw" }}>

        {/* File structure */}
        <div className="flex-1" style={{ background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "12px", padding: "3vh 2vw" }}>
          <div style={{ fontSize: "1.5vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.08em", marginBottom: "2.5vh", fontFamily: "var(--font-body-family)" }}>
            REPOSITORY STRUCTURE
          </div>
          <div className="flex flex-col" style={{ gap: "1.5vh", fontFamily: "var(--font-body-family)" }}>
            <div className="flex items-center" style={{ gap: "1.5vw" }}>
              <div style={{ fontSize: "1.8vw", color: "#06b6d4", fontWeight: 700, minWidth: "12vw" }}>main.py</div>
              <div style={{ fontSize: "1.6vw", color: "#64748b" }}>FastAPI app — /detect, /results, /stats</div>
            </div>
            <div style={{ height: "1px", background: "rgba(100,116,139,0.15)" }} />
            <div className="flex items-center" style={{ gap: "1.5vw" }}>
              <div style={{ fontSize: "1.8vw", color: "#06b6d4", fontWeight: 700, minWidth: "12vw" }}>detector.py</div>
              <div style={{ fontSize: "1.6vw", color: "#64748b" }}>CV simulation engine + Pillow annotation</div>
            </div>
            <div style={{ height: "1px", background: "rgba(100,116,139,0.15)" }} />
            <div className="flex items-center" style={{ gap: "1.5vw" }}>
              <div style={{ fontSize: "1.8vw", color: "#06b6d4", fontWeight: 700, minWidth: "12vw" }}>database.py</div>
              <div style={{ fontSize: "1.6vw", color: "#64748b" }}>SQLite schema, CRUD, 12 demo records</div>
            </div>
            <div style={{ height: "1px", background: "rgba(100,116,139,0.15)" }} />
            <div className="flex items-center" style={{ gap: "1.5vw" }}>
              <div style={{ fontSize: "1.8vw", color: "#10b981", fontWeight: 700, minWidth: "12vw" }}>static/index.html</div>
              <div style={{ fontSize: "1.6vw", color: "#64748b" }}>Complete single-page frontend</div>
            </div>
            <div style={{ height: "1px", background: "rgba(100,116,139,0.15)" }} />
            <div className="flex items-center" style={{ gap: "1.5vw" }}>
              <div style={{ fontSize: "1.8vw", color: "#06b6d4", fontWeight: 700, minWidth: "12vw" }}>results/</div>
              <div style={{ fontSize: "1.6vw", color: "#64748b" }}>Annotated detection images (JPEG)</div>
            </div>
            <div style={{ height: "1px", background: "rgba(100,116,139,0.15)" }} />
            <div className="flex items-center" style={{ gap: "1.5vw" }}>
              <div style={{ fontSize: "1.8vw", color: "#06b6d4", fontWeight: 700, minWidth: "12vw" }}>requirements.txt</div>
              <div style={{ fontSize: "1.6vw", color: "#64748b" }}>fastapi, uvicorn, pillow, numpy, python-multipart</div>
            </div>
          </div>
        </div>

        {/* How to run + checklist */}
        <div className="flex-1 flex flex-col" style={{ gap: "2.5vh" }}>
          <div style={{ background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "12px", padding: "2.5vh 2vw" }}>
            <div style={{ fontSize: "1.5vw", fontWeight: 600, color: "#06b6d4", letterSpacing: "0.08em", marginBottom: "1.5vh", fontFamily: "var(--font-body-family)" }}>
              HOW TO RUN
            </div>
            <div style={{ background: "#050e1f", borderRadius: "8px", padding: "1.5vh 1.5vw", fontFamily: "monospace" }}>
              <div style={{ fontSize: "1.7vw", color: "#94a3b8" }}>pip install -r requirements.txt</div>
              <div style={{ fontSize: "1.7vw", color: "#10b981", marginTop: "0.8vh" }}>uvicorn main:app --host 0.0.0.0 --port 8000</div>
            </div>
          </div>

          <div style={{ background: "#0d1f38", border: "1px solid #1e3a5f", borderRadius: "12px", padding: "2.5vh 2vw", flex: 1 }}>
            <div style={{ fontSize: "1.5vw", fontWeight: 600, color: "#10b981", letterSpacing: "0.08em", marginBottom: "1.8vh", fontFamily: "var(--font-body-family)" }}>
              SUBMISSION CHECKLIST
            </div>
            <div className="flex flex-col" style={{ gap: "1.4vh", fontFamily: "var(--font-body-family)" }}>
              <div className="flex items-center" style={{ gap: "1vw" }}>
                <div style={{ width: "1.2vw", height: "1.2vw", background: "#10b981", borderRadius: "3px", flexShrink: 0 }} />
                <div style={{ fontSize: "1.7vw", color: "#94a3b8" }}>README with run instructions</div>
              </div>
              <div className="flex items-center" style={{ gap: "1vw" }}>
                <div style={{ width: "1.2vw", height: "1.2vw", background: "#10b981", borderRadius: "3px", flexShrink: 0 }} />
                <div style={{ fontSize: "1.7vw", color: "#94a3b8" }}>Reproducible baseline vs optimised results</div>
              </div>
              <div className="flex items-center" style={{ gap: "1vw" }}>
                <div style={{ width: "1.2vw", height: "1.2vw", background: "#10b981", borderRadius: "3px", flexShrink: 0 }} />
                <div style={{ fontSize: "1.7vw", color: "#94a3b8" }}>All assumptions clearly stated</div>
              </div>
              <div className="flex items-center" style={{ gap: "1vw" }}>
                <div style={{ width: "1.2vw", height: "1.2vw", background: "#10b981", borderRadius: "3px", flexShrink: 0 }} />
                <div style={{ fontSize: "1.7vw", color: "#94a3b8" }}>AI usage disclosed in README</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
