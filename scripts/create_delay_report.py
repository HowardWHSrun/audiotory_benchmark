"""Reproduce the initial PDF; the current requested report is authored in LaTeX.

Current source: output/pdf/2026-10-23/Audient_Delay_Report/main.tex.
This historical generator preserves the first report's provenance.

Requires reportlab. Reads sanitized verification JSON, never raw room audio.
"""
from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/verification/2026-10-23_Audient_Playback_Microphone_Delay.json"
OUTPUT = ROOT / "output/pdf/2026-10-23/Audient_Playback_Microphone_Delay_Report.pdf"
REPO_URL = "https://github.com/HowardWHSrun/audiotory_benchmark/blob/main/"
BLUE = colors.HexColor("#17384d")
GREEN = colors.HexColor("#15715a")
GRAY = colors.HexColor("#52616b")


def build():
    record = json.loads(RECORD.read_text())
    runs = record["runs"]
    trials = [trial for run in runs for trial in run["trials"] if trial["accepted"]]
    delays = [trial["delay_ms"] for trial in trials]
    if len(runs) != 2 or len(trials) != 40:
        raise ValueError("This dated report requires the two verified 20-probe runs")
    medians = [run["summary"]["median_delay_ms"] for run in runs]
    if medians != [38.25, 38.375] or min(delays) != 3671 / 96 or max(delays) != 3684 / 96:
        raise ValueError("The dated record differs from this report's reviewed values")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=(8.5 * inch, 11 * inch),
                            leftMargin=43, rightMargin=43, topMargin=37, bottomMargin=36,
                            title="Playback-to-microphone delay | Bench verification | 2026-10-23",
                            author="SONIC Auditory Benchmarking")
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=8.2, leading=11, textColor=GRAY)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=9.6, leading=13.2,
                          textColor=BLUE, spaceAfter=8, alignment=TA_LEFT)
    heading = ParagraphStyle("section", parent=body, fontName="Helvetica-Bold",
                             fontSize=10, spaceBefore=7, spaceAfter=5)
    title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=23,
                           leading=27, textColor=BLUE, spaceAfter=10)
    result = ParagraphStyle("result", fontName="Helvetica-Bold", fontSize=32,
                            leading=36, textColor=GREEN, spaceAfter=3)
    story = [Paragraph("SONIC AUDITORY BENCHMARKING  |  BENCH VERIFICATION  |  23 OCTOBER 2026", small),
             Spacer(1, 12), Paragraph("Playback-to-microphone delay", title),
             Paragraph("Approximately 38.3 ms", result),
             Paragraph("Measured native-application playback-to-recording waveform roundtrip", small),
             Spacer(1, 13),
             Paragraph("<b>Established:</b> the wired speaker can play sound while the Earthworks microphone records it, "
                       "with repeatable waveform delay in the tested program and configuration. "
                       "All 40 sweeps were detected across two separately opened audio streams.", body)]
    table_data = [["Test", "Accepted", "Median delay", "Observed range"]]
    for index, run in enumerate(runs, 1):
        s = run["summary"]
        table_data.append([f"Run {index}", f"{s['accepted_trials']} / {s['total_trials']}",
                           f"{s['median_delay_ms']:.3f} ms",
                           f"{s['min_delay_ms']:.3f} - {s['max_delay_ms']:.3f} ms"])
    table = Table(table_data, colWidths=[70, 78, 117, 161], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.3),
        ("TEXTCOLOR", (0, 0), (-1, -1), BLUE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eff2")),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#c8d3d9")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [table, Spacer(1, 8),
              Paragraph("Across both runs: <b>38.240 - 38.375 ms</b> (0.135 ms total observed span). "
                        "Run medians differed by 0.125 ms. There were no clipped samples, callback status warnings, "
                        "or rejected probes. This observed repeatability is not an absolute accuracy bound.", body),
              Paragraph("Setup and method", heading),
              Paragraph("Computer / native Core Audio program &gt; Audient iD14 &gt; wired Edifier speaker "
                        "&gt; air &gt; Earthworks M50 &gt; Audient input 1 &gt; program.", body),
              Paragraph("One full-duplex stream at 96 kHz; twenty 100 ms, 100 Hz-20 kHz sweeps per run, "
                        "500 ms apart, at -24 dBFS digital peak. Cross-correlation matched the exact submitted "
                        "source array with the recorded microphone waveform. Weak, ambiguous, clipped, boundary, "
                        "and invalid-transport results were screened out. The operator reported 10 cm separation; "
                        "it was not remeasured or subtracted from the delay.", body),
              Paragraph("What this establishes", heading),
              Paragraph("The approximately 38.3 ms result includes playback and recording buffering, interface "
                        "conversion, loudspeaker, sound propagation, and microphone path. It applies to these two "
                        "short runs in this program, with the current settings. Other programs, buffer settings, "
                        "routes, or geometry can produce a different delay.", body),
              Paragraph("This does not isolate speaker latency, measure UI-click-to-sound timing, or establish "
                        "exact acoustic onset. The correlation peak was roughly 1.5 ms wide; 10.4 microsecond "
                        "sample spacing is a search increment, not calibrated accuracy. No calibrated SPL, full "
                        "frequency response, animal readiness, or SONIC neural/intrinsic latency is established.", body),
              Paragraph("SONIC stimulus", heading),
              Paragraph("A separate Sheep E reconstruction was played and recorded: 14 published frequencies from 2 to 27 kHz, "
                        "consecutive 10 ms sine pips with 2 ms end ramps, 8,400 pips in one 84-second block. "
                        "The local order and raised-cosine ramp shape are declared choices; the original waveform "
                        "was unavailable. Our output is 96 kHz; the paper used 192 kHz. Acoustic level and high-frequency "
                        "coverage remain unqualified. These tones were not used to infer the delay above.", body),
              Spacer(1, 4),
              Paragraph('Evidence: <link href="' + REPO_URL + str(RECORD.relative_to(ROOT)) + '">dated measurement record</link> '
                        '| <link href="' + REPO_URL + 'latency/roundtrip.py">measurement code</link> '
                        '| <link href="https://github.com/PortAudio/portaudio/blob/master/qa/loopback/src/paqa.c">PortAudio roundtrip QA precedent</link>. '
                        'Raw source/capture hashes are recorded; room audio stays local.', small)]

    def footer(canvas, document):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(43, 21, "Measured bench data | Current configuration only | Revision 1")
        canvas.drawRightString(569, 21, str(document.page))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
