from pathlib import Path
svg = """<svg xmlns="http://www.w3.org/2000/svg" width="920" height="280" viewBox="0 0 920 280">
<rect width="920" height="280" fill="white"/>
<g font-family="sans-serif" font-size="17" text-anchor="middle">
<text x="460" y="30" font-size="20">RUN-ICPERF-caa0c1: build stopped before computation</text>
<rect x="25" y="80" width="240" height="95" rx="8" fill="#e6edf5" stroke="#385577"/>
<text x="145" y="118">Supervisor admitted</text><text x="145" y="146">frozen build trial</text>
<path d="M265 127H325" stroke="#385577" stroke-width="3"/><path d="M325 127l-10 -6v12z" fill="#385577"/>
<rect x="330" y="80" width="260" height="95" rx="8" fill="#fee8e5" stroke="#aa3b31"/>
<text x="460" y="118">Frozen crypto launcher</text><text x="460" y="146">absent; exit code 2</text>
<path d="M590 127H650" stroke="#aaa" stroke-width="3" stroke-dasharray="6 5"/>
<rect x="655" y="80" width="240" height="95" rx="8" fill="#f3f3f3" stroke="#aaa"/>
<text x="775" y="118">9 dependent trials</text><text x="775" y="146">not launched</text>
<text x="460" y="223" font-size="15">Observed execution path only. No scientific measurements or controls ran.</text>
<text x="460" y="249" font-size="13">Source: RUN-ICPERF-caa0c1/execution-receipt.json and raw-result.json</text>
</g></svg>"""
Path(__file__).with_name("pipeline.svg").write_text(svg)
