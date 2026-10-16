"""Build the editable equipment and setup guide from the current audited basket.

Use the bundled workspace Python runtime with python-docx and Pillow installed.
This creates documentation only. It does not control or play audio hardware.
"""

from decimal import Decimal
from math import cos, pi
from pathlib import Path
import json

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/documents/2026-10-16"
ASSETS = OUT / "assets"
AUDIT = ROOT / "sources/Sound_Chain_Qualification_Audit_2026-10-16.json"
FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
SOURCES = [
    ("S1", "SONIC v1 methods", "https://doi.org/10.1101/2025.09.30.679683", "Saved PDF printed p 11 Sections 6.1 to 6.3; p 13 Section 6.6"),
    ("S2", "Earthworks M50 specifications", "https://earthworksaudio.com/measurement-microphones/m50/", "Bandwidth power load and individual calibration"),
    ("S3", "Earthworks serial calibration request", "https://earthworksaudio.com/support/ecf/", "Request the file for the delivered microphone"),
    ("S4", "Edifier MR3 specifications and delay FAQ", "https://www.edifier.com/global/p/studio-monitors/mr3", "Range inputs processing firmware and standby"),
    ("S5", "Edifier MR3 response illustration", "https://new-edifier-us-oss.edifier.com/files/20240904/9a364d5a62c02117cf79f7f52b4cc913.jpg", "Supports 32 kHz output under unspecified conditions"),
    ("S6", "Erin original MR3 measurements", "https://www.erinsaudiocorner.com/loudspeakers/edifier_mr3/", "Independent measurements end near 20 kHz"),
    ("S7", "Audient iD14 MKII specifications", "https://audient.com/products/audio-interfaces/id14/tech-specs/", "Inputs outputs power and frequency response"),
    ("S8", "Audient connections and phantom power", "https://audient.github.io/audient-documentation-site/id14/front-panel/", "Independent phantom switches and front DI behavior"),
    ("S9", "Audient output routing", "https://audient.github.io/audient-documentation-site/id14/system-panel-routing/", "DAW Thru and monitoring configuration"),
    ("S10", "REED R8090 specifications", "https://www.reedinstruments.com/pdfs/cache/www.reedinstruments.com/r8090/datasheet/r8090-datasheet.pdf", "Level accuracy frequency port and battery"),
    ("S11", "Python sounddevice playback and recording", "https://python-sounddevice.readthedocs.io/en/latest/api/convenience-functions.html", "Initial playrec checks and continuous streams"),
    ("S12", "Earthworks M50 user guide", "https://earthworksaudio.com/wp-content/uploads/2022/05/Earthworks_Audio_M50_may2022.pdf", "Included clip adapter and calibration information"),
    ("S13", "Dayton EMM-6 specifications", "https://www.parts-express.com/pedocs/manuals/390-801--dayton-audio-emm-6-quick-reference-guide.pdf", "18 Hz to 20 kHz and individual calibration file"),
    ("S14", "Edifier MR3 user manual", "https://new-edifier-us-oss.edifier.com/files/20240902/93517b14f597b1ec5b5814993aa9fca7.pdf", "Monitor mode and power rating with DRC on"),
    ("S15", "Audient iD4 MKII specifications", "https://audient.com/products/audio-interfaces/id4/tech-specs/", "Earlier one full band input comparison"),
    ("S16", "miniDSP UMIK-2 manual", "https://www.minidsp.com/images/documents/miniDSP%20UMIK-2-User%20Manual.pdf", "Printed page 17 supplied calibration ends at 20 kHz"),
    ("S17", "Earthworks M30 G2 manual", "https://earthworksaudio.com/wp-content/uploads/2025/11/Earthworks_Audio_M30_G2__11042025-1.pdf", "Pages 2 to 3 individual chart and bandwidth; supplied calibration endpoint unspecified"),
    ("S18", "Original Edifier MR4 specifications", "https://www.edifier.com/global/p/studio-monitors/mr4", "Original MR4 range ends at 20 kHz; distinct from MR4 MKII"),
    ("S19", "Edifier MR5 specifications and listed price", "https://us.edifier.com/products/mr5", "40 kHz nominal endpoint; official store displayed USD 349.99 on October 16"),
    ("S20", "Extech 407766 specifications and listed price", "https://prod.extech.com/products/407766/", "1 kHz reference and +/-0.5 dB at 94 dB; manufacturer displayed USD 519 on October 16"),
]

COMPARISONS = [
    {
        "chosen": "Earthworks M50",
        "alternatives": ["miniDSP UMIK-2", "Earthworks M30 G2"],
        "reason": "UMIK-2 factory calibration stops at 20 kHz; M30 G2 calibration at 32 kHz is unconfirmed. M50 offers a 50 kHz range and individual calibration with our Mac interface.",
        "source_ids": ["S2", "S3", "S16", "S17"],
    },
    {
        "chosen": "Audient iD14 MKII",
        "alternatives": ["Audient iD4 MKII"],
        "reason": "iD4 can do the basic sound checkout, but has one full-band mic/line input. iD14 gives two for recording the mic and electrical timing reference together.",
        "source_ids": ["S7", "S15"],
    },
    {
        "chosen": "Edifier MR3 powered pair",
        "alternatives": ["Original Edifier MR4", "Edifier MR5"],
        "reason": "Original MR4 stops at 20 kHz. MR5 ($349.99) also specifies 40 kHz. MR3 saves $200 and covers our target on paper; 10 ms acoustic tests are still required.",
        "source_ids": ["S4", "S5", "S18", "S19"],
    },
    {
        "chosen": "REED R8090",
        "alternatives": ["Extech 407766", "REED R8090-NIST"],
        "reason": "Extech 407766 ($519 listed) also provides a 1 kHz level check. R8090 costs less; both state +/-0.5 dB at 94 dB. R8090-NIST adds a certificate at extra cost.",
        "source_ids": ["S10", "S20"],
    },
    {
        "chosen": "Hosa HMIC-010",
        "alternatives": ["Equivalent XLR microphone cable"],
        "reason": "Connects M50 to the interface.",
        "source_ids": [],
    },
    {
        "chosen": "Hosa HSS-005",
        "alternatives": ["Equivalent balanced quarter-inch TRS cables"],
        "reason": "One cable to the speaker; one for the electrical reference.",
        "source_ids": [],
    },
    {
        "chosen": "Gator RI-MICTP-FBM",
        "alternatives": ["Existing stable boom microphone stand"],
        "reason": "Holds the microphone at the ear position.",
        "source_ids": [],
    },
]

PAPER_REFERENCE = {
    "version": "SONIC bioRxiv v1 posted 2025-10-02",
    "local_source": "sources/SONIC_2025_bioRxiv_v1.pdf",
    "locators": "Printed pages 7, 11 Sections 6.1 to 6.3, and 13 Section 6.6",
    "subjects": "Two awake, alert sheep; 421-channel Connexus recording from auditory cortex",
    "exploration_duration_ms": {"minimum": 4, "maximum": 24, "step": 2},
    "benchmark_pip_ms": 10,
    "ramp_each_end_ms": 2,
    "starting_phase": "zero",
    "neural_feature_bin_ms": 5,
    "sheep_C": {"frequency_count": 37, "described_range_khz": [1.4, 32], "described_step_octaves": "1/8"},
    "sheep_E_frequencies_khz": [2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8, 27],
    "order": "Uniformly random frequencies balanced within each block; no inter-tone silence",
    "pips_per_block": [8000, 15000],
    "minimum_blocks_per_session": 12,
    "silence_between_blocks_s": 1,
    "dac_sample_rate_hz": 192000,
    "playback_chain": ["NI USB-6361", "TDT SA1 amplifier", "TDT MF1 free-field speaker"],
    "reported_level": "Approximately 80 dB SPL at sheep-ear distance",
    "unreported_details": ["Exact 37-frequency numeric array", "Ramp shape"],
}


def font(size):
    return ImageFont.truetype(str(FONT), size)


def diagram():
    im = Image.new("RGB", (1800, 740), "white")
    d = ImageDraw.Draw(im)
    dark, blue = "#222222", "#245B87"

    def label(x, y, text, size=40):
        d.multiline_text((x, y), text, font=font(size), fill=dark,
                        anchor="mm", align="center", spacing=12)

    def box(rect, text):
        d.rectangle(rect, outline=dark, width=3)
        label((rect[0]+rect[2])/2, (rect[1]+rect[3])/2, text)

    def arrow(points):
        d.line(points, fill=blue, width=6)
        x, y = points[-1]
        px, py = points[-2]
        dx, dy = x-px, y-py
        length = (dx*dx+dy*dy)**0.5
        ux, uy = dx/length, dy/length
        d.polygon([(x,y), (x-23*ux+10*uy,y-23*uy-10*ux),
                   (x-23*ux-10*uy,y-23*uy+10*ux)], fill=blue)

    box((30,100,355,300), "Mac")
    box((650,60,1150,340), "iD14 MKII\nOutput 1 → speaker\nInput 1 ← microphone")
    box((1430,100,1770,300), "MR3\nspeaker")
    box((1430,510,1770,710), "M50\nat ear position")
    arrow([(355,200),(650,200)])
    arrow([(650,200),(355,200)])
    label(500,125,"USB\nplay + record",36)
    arrow([(1150,200),(1430,200)])
    label(1290,145,"TRS cable 1",36)
    arrow([(1600,300),(1600,510)])
    label(1690,405,"Sound",36)
    arrow([(1430,610),(1260,610),(1260,405),(900,405),(900,340)])
    label(1110,465,"XLR cable\nPhantom on",36)
    label(510,600,"Second TRS cable\nOutput 2 → rear line input 2\nPhantom off · duplicate reference",37)
    p = ASSETS / "sound_setup_connections.png"
    im.save(p, dpi=(300,300))
    return p


def envelope_figure():
    im = Image.new("RGB", (1800, 470), "white")
    d = ImageDraw.Draw(im)
    left, right, top, bottom = 170, 1700, 130, 350
    d.line((left,bottom,right,bottom), fill="#444444", width=3)
    points=[]
    for i in range(1001):
        ms=i/100
        value = 0.5-0.5*cos(pi*ms/2) if ms<2 else 1 if ms<=8 else 0.5-0.5*cos(pi*(10-ms)/2)
        points.append((left+(right-left)*ms/10,bottom-(bottom-top)*value))
    d.line(points,fill="#245B87",width=7)
    for ms in (0,2,8,10):
        x=left+(right-left)*ms/10
        d.line((x,bottom,x,bottom+12),fill="#444444",width=3)
        d.text((x,bottom+42),str(ms),font=font(29),fill="#222222",anchor="mm")
    for x,text in ((left+153,"2 ms rise\n192 samples"),(left+765,"6 ms plateau\n576 samples"),(right-153,"2 ms fall\n192 samples")):
        d.multiline_text((x,60),text,font=font(29),fill="#222222",anchor="mm",align="center",spacing=8)
    d.text((right,435),"Time in milliseconds",font=font(29),fill="#222222",anchor="rm")
    d.text((25,40),"Amplitude",font=font(28),fill="#222222")
    p=ASSETS / "ten_ms_envelope_schematic.png"
    im.save(p,dpi=(300,300))
    return p


def hyperlink(paragraph, text, url):
    part=paragraph.part
    rid=part.relate_to(url,"http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",is_external=True)
    link=OxmlElement("w:hyperlink")
    link.set(qn("r:id"),rid)
    run=OxmlElement("w:r")
    properties=OxmlElement("w:rPr")
    color=OxmlElement("w:color"); color.set(qn("w:val"),"245B87"); properties.append(color)
    under=OxmlElement("w:u"); under.set(qn("w:val"),"single"); properties.append(under)
    run.append(properties)
    value=OxmlElement("w:t"); value.text=text; run.append(value)
    link.append(run); paragraph._p.append(link)


def set_alt(run, title, description):
    for element in run._r.xpath(".//wp:docPr"):
        element.set("title",title); element.set("descr",description)


def paragraph(doc, text="", bold_lead=None, style=None):
    p=doc.add_paragraph(style=style)
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold=True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def heading(doc,text,level=1):
    return doc.add_heading(text,level)


def new_numbering(doc):
    numbering=doc.part.numbering_part.element
    base_id=doc.styles["List Number"].element.pPr.numPr.numId.val
    base=next(n for n in numbering.findall(qn("w:num")) if n.get(qn("w:numId"))==str(base_id))
    abstract_id=base.find(qn("w:abstractNumId")).get(qn("w:val"))
    new_id=max(int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num")))+1
    num=OxmlElement("w:num"); num.set(qn("w:numId"),str(new_id))
    abstract=OxmlElement("w:abstractNumId"); abstract.set(qn("w:val"),abstract_id); num.append(abstract)
    override=OxmlElement("w:lvlOverride"); override.set(qn("w:ilvl"),"0")
    start=OxmlElement("w:startOverride"); start.set(qn("w:val"),"1"); override.append(start); num.append(override)
    numbering.append(num)
    return new_id


def numbered_paragraph(doc,text,num_id):
    p=paragraph(doc,text,style="List Number")
    props=p._p.get_or_add_pPr().get_or_add_numPr()
    level=OxmlElement("w:ilvl"); level.set(qn("w:val"),"0"); props.append(level)
    identifier=OxmlElement("w:numId"); identifier.set(qn("w:val"),str(num_id)); props.append(identifier)
    return p


def page(doc,title):
    p=heading(doc,title)
    p.paragraph_format.page_break_before=True


def table(doc, headers, rows, widths, links=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    for cell,width in zip(t.columns,widths): cell.width=Inches(width)
    props=t._tbl.tblPr
    borders=OxmlElement("w:tblBorders")
    for side in ("top","left","bottom","right","insideH","insideV"):
        el=OxmlElement("w:"+side); el.set(qn("w:val"),"single"); el.set(qn("w:sz"),"5"); el.set(qn("w:color"),"D9D9D9"); borders.append(el)
    props.append(borders)
    margins=OxmlElement("w:tblCellMar")
    for side,value in (("top",85),("bottom",85),("left",100),("right",100)):
        el=OxmlElement("w:"+side); el.set(qn("w:w"),str(value)); el.set(qn("w:type"),"dxa"); margins.append(el)
    props.append(margins)
    for j,value in enumerate(headers): t.rows[0].cells[j].text=value
    repeat=OxmlElement("w:tblHeader"); repeat.set(qn("w:val"),"true"); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for i,row in enumerate(rows):
        cells=t.add_row().cells
        for j,value in enumerate(row):
            cells[j].text=str(value)
            if links and j==0 and i<len(links) and links[i]:
                cells[j].paragraphs[0].clear(); hyperlink(cells[j].paragraphs[0],str(value),links[i])
    for i,row in enumerate(t.rows):
        cant=OxmlElement("w:cantSplit"); row._tr.get_or_add_trPr().append(cant)
        for j,(cell,width) in enumerate(zip(row.cells,widths)):
            cell.width=Inches(width); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            shade=OxmlElement("w:shd"); shade.set(qn("w:fill"),"30343A" if i==0 else "FFFFFF" if i%2 else "F3F4F5"); cell._tc.get_or_add_tcPr().append(shade)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(1); p.paragraph_format.space_before=Pt(1)
                p.paragraph_format.line_spacing=1.05
                if j>0 and len(str(row.cells[j].text))<22: p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size=Pt(11)
                    if i==0: run.bold=True; run.font.color.rgb=RGBColor(255,255,255)
    paragraph(doc,"").paragraph_format.space_after=Pt(0)
    return t


def picture(doc,path,width,caption,alt):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=p.add_run(); run.add_picture(str(path),width=Inches(width)); set_alt(run,caption,alt)
    p.paragraph_format.space_after=Pt(3)
    cp=paragraph(doc,caption); cp.style=doc.styles["Caption"]


def build():
    OUT.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(exist_ok=True)
    audit=json.loads(AUDIT.read_text())
    parts=audit["revised_recommendation"]["parts"]
    subtotal=sum(Decimal(str(p["unit_usd"]))*p["quantity"] for p in parts)
    assert subtotal==Decimal("2099.87")
    doc=Document(); section=doc.sections[0]
    section.page_width=Inches(8.5); section.page_height=Inches(11)
    section.top_margin=section.bottom_margin=Inches(.65)
    section.left_margin=section.right_margin=Inches(.65)
    section.footer_distance=Inches(.25)
    for name in ("Normal","Title","Subtitle","Heading 1","Heading 2","Caption"):
        s=doc.styles[name]; s.font.name="Arial"; s.font.color.rgb=RGBColor(0,0,0)
        s._element.get_or_add_rPr().rFonts.set(qn("w:ascii"),"Arial")
        s._element.rPr.rFonts.set(qn("w:hAnsi"),"Arial")
    normal=doc.styles["Normal"]; normal.font.size=Pt(11)
    normal.paragraph_format.line_spacing=1.08; normal.paragraph_format.space_after=Pt(6)
    doc.styles["Title"].font.size=Pt(24)
    doc.styles["Title"].paragraph_format.space_after=Pt(5)
    doc.styles["Subtitle"].font.size=Pt(11)
    doc.styles["Heading 1"].font.size=Pt(17)
    doc.styles["Heading 1"].paragraph_format.space_before=Pt(0)
    doc.styles["Heading 1"].paragraph_format.space_after=Pt(9)
    doc.styles["Heading 2"].font.size=Pt(12)
    doc.styles["Heading 2"].paragraph_format.space_before=Pt(8)
    doc.styles["Heading 2"].paragraph_format.space_after=Pt(4)
    doc.styles["Caption"].font.size=Pt(9)
    doc.styles["Caption"].font.bold=False
    doc.styles["Caption"].font.italic=False
    doc.styles["Caption"].paragraph_format.space_after=Pt(6)
    for style in doc.styles:
        for border in style.element.xpath(".//w:pBdr"):
            border.getparent().remove(border)
    footer=section.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run("M50 sound setup  |  ").font.size=Pt(9)
    field=OxmlElement("w:fldSimple"); field.set(qn("w:instr"),"PAGE"); footer._p.append(field)
    doc.core_properties.title="M50 auditory sound setup"
    doc.core_properties.subject="Equipment rationale wiring software calibration and qualification"
    doc.core_properties.author="Howard Wang"

    # Page 1
    doc.add_paragraph("Our sound setup",style="Title")
    doc.add_paragraph("Parts and setup  |  16 October 2026",style="Subtitle")
    paragraph(doc,"Goal: play and measure approximately 1.4–32 kHz tones, changing every 10 ms. Check the sound setup on the mouse rig first, then recalibrate for sheep.",bold_lead="Goal:")
    heading(doc,"What to get",2)
    names=["Earthworks M50", "Audient iD14 MKII", "Edifier MR3 powered pair",
           "REED R8090", "Hosa HMIC-010 XLR\n10 ft", "Hosa HSS-005 TRS\n5 ft",
           "Gator RI-MICTP-FBM\nboom mic stand"]
    reasons=[item["reason"] for item in COMPARISONS]
    rows=[]
    for name,reason,item in zip(names,reasons,parts):
        cost=Decimal(str(item["unit_usd"]))*item["quantity"]
        rows.append([name,reason,item["quantity"],f"${cost:,.2f}"])
    table(doc,["Part and buying link","Other options and why this fits","Qty","Cost"],rows,
          [2.1,3.65,.4,1.05],links=[p["buy_url"] for p in parts])

    heading(doc,"SONIC paper experiment",2)
    p=paragraph(doc,"Two awake, alert sheep heard tones while a 421-channel Connexus implant recorded auditory cortex. A decoder predicted the tone frequency.")
    p.paragraph_format.space_after=Pt(3)
    for lead,body in [
        ("Benchmark stimuli: ", "10 ms sine pips (100/s), zero starting phase, 2 ms ramps at both ends, and no silence between pips. Neural features used 5 ms bins."),
        ("Frequencies: ", "Sheep C used 37 frequencies over about 1.4–32 kHz in 1/8-octave steps. Sheep E used 2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8 and 27 kHz."),
        ("Blocks: ", "Uniformly random frequencies, balanced within each block. 8,000–15,000 pips per block; at least 12 blocks per session; 1 s silence between blocks."),
        ("Playback: ", "Precomputed waveform at 192 kHz: NI USB-6361 → TDT SA1 amplifier → MF1 speaker; about 80 dB SPL at the sheep’s ears."),
    ]:
        p=paragraph(doc,lead+body,bold_lead=lead)
        p.paragraph_format.space_after=Pt(3)
    p=doc.add_paragraph(); p.style=doc.styles["Caption"]
    hyperlink(p,"SONIC v1",SOURCES[0][2])
    p.add_run(" — pp. 7, 11 (§6.1–6.3), 13 (§6.6). Exact 37-frequency array and ramp shape are not listed.")

    # Page 2
    page(doc,"Put it together")
    picture(doc,diagram(),7.05,"Connections for sound playback and recording",
            "Mac connects to iD14 by USB. Output one feeds MR3 by TRS. M50 measures the sound at the ear position and connects to input one by XLR with phantom on. Output two returns to rear line input two with phantom off through the second TRS cable as a duplicate electrical reference.")
    sequence_id=new_numbering(doc)
    steps=[
        ("Connect and position. ", "Connect as shown. Turn input monitoring off to prevent feedback; leave the front instrument input empty. Put the M50 tip at the ear/reference position and record distance and angle."),
        ("Program the sequence. ", "Python builds one continuous waveform at 96 kHz: 960 samples per 10 ms pip, including a 2 ms ramp at each end. Send it to output 1 and a copy to output 2. Save the tone schedule and random seed."),
        ("Calibrate. ", "Use the calibration file for that M50, checking coverage through 32 kHz. Use the R8090 at 94 dB to set the recording scale, then keep mic gain fixed. Remove the calibrator and adjust each tone’s level using recordings at the ear position."),
        ("Check the actual sound. ", "Record the microphone and electrical reference simultaneously during the actual 10 ms sequence. Check level at every frequency, short-tone transitions, ringing and stability through a full run. Check the reference channel’s relative delay too. Repeat calibration when moving to sheep."),
    ]
    for lead,body in steps:
        p=numbered_paragraph(doc,"",sequence_id)
        p.add_run(lead).bold=True
        p.add_run(body)
        p.paragraph_format.space_after=Pt(9)
    paragraph(doc,"Before testing: the lab chooses distance, sound level and pass tolerances. The paper’s approximately 80 dB sheep level is not automatically the mouse setting. Physical sound checks and later neural synchronization are still pending.",bold_lead="Before testing:")
    p=doc.add_paragraph(); p.style=doc.styles["Caption"]
    p.add_run("Specifications: ")
    for i,key in enumerate(("S2","S7","S4","S10")):
        if i: p.add_run("  ·  ")
        _,title,url,_=next(item for item in SOURCES if item[0]==key)
        hyperlink(p,{"S2":"M50","S7":"iD14","S4":"MR3","S10":"R8090"}[key],url)
    p=doc.add_paragraph(); p.style=doc.styles["Caption"]
    p.add_run("Alternatives: ")
    for i,(key,label) in enumerate((("S16","UMIK-2"),("S17","M30 G2"),("S15","iD4"),
                                  ("S18","original MR4"),("S19","MR5"),("S20","Extech 407766"))):
        if i: p.add_run("  ·  ")
        _,_,url,_=next(item for item in SOURCES if item[0]==key)
        hyperlink(p,label,url)
    dest=OUT/"M50_Sound_Setup_Guide.docx"
    doc.save(dest)
    manifest={
        "date":"2026-10-16","document":str(dest.relative_to(ROOT)),
        "source_audit":str(AUDIT.relative_to(ROOT)),"intended_pages":2,
        "parts_total_usd":str(subtotal),"working_budget_usd":"2349.87",
        "revision":"two-page guide with equipment choices and a separate SONIC stimulus reference",
        "visible_source_ids":["S1","S2","S7","S4","S10","S16","S17","S15","S18","S19","S20"],
        "comparisons":COMPARISONS,
        "paper_reference":PAPER_REFERENCE,
        "comparison_checked_date":"2026-10-16",
        "speaker_price_comparison":{
            "MR3_official_store_usd":"149.99",
            "MR5_official_store_usd":"349.99",
            "difference_usd":"200.00",
            "source":"https://us.edifier.com/products/mr5",
            "scope":"Dated official store observations; neither model physically qualified for this sequence",
        },
        "calibrator_price_comparison":{
            "REED_R8090_usd":"219.00",
            "REED_source":"https://www.globaltestsupply.com/product/reed-r8090-sound-level-calibrator",
            "Extech_407766_manufacturer_display_usd":"519.00",
            "Extech_source":"https://prod.extech.com/products/407766/",
            "scope":"Dated seller/manufacturer observations, not a market-wide lowest-price comparison or delivered quote",
        },
        "source_references":[dict(id=k,title=t,url=u,scope=s) for k,t,u,s in SOURCES],
        "scientific_scope":"Documentation and setup plan only; physical qualification pending; initial mouse checkout then independently calibrated sheep geometry",
        "software_scope":"Architecture and workflow described; no stimulus control implementation or audio playback performed",
    }
    (ROOT/"sources/M50_Sound_Setup_Guide_2026-10-16.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(dest)


if __name__=="__main__":
    build()
