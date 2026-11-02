from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
root=Path(__file__).resolve().parent.parent
lines=(root/'AEGIS_User_Manual.md').read_text().splitlines()
doc=Document()
section=doc.sections[0]
section.top_margin=Inches(.8);section.bottom_margin=Inches(.75)
section.left_margin=Inches(.85);section.right_margin=Inches(.85)
styles=doc.styles
styles['Normal'].font.name='Calibri';styles['Normal'].font.size=Pt(10)
styles['Normal'].paragraph_format.space_after=Pt(7)
for name in ['Title','Heading 1','Heading 2','Heading 3']:
 styles[name].font.name='Calibri';styles[name].font.color.rgb=RGBColor.from_string('6242A6')
styles['Heading 1'].paragraph_format.space_before=Pt(18)
styles['Heading 1'].paragraph_format.keep_with_next=True
header=section.header.paragraphs[0]
header.text='AEGIS   /   PROTOTYPE USER MANUAL'
header.runs[0].font.size=Pt(8);header.runs[0].font.color.rgb=RGBColor.from_string('847590')
footer=section.footer.paragraphs[0]
footer.text='Independent prototype • Decision support only                                      Page '
footer.runs[0].font.size=Pt(8)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

def inline(par,text):
 for part in re.split(r'(\*\*.*?\*\*|`[^`]+`)',text):
  if not part: continue
  if part.startswith('**'):
   par.add_run(part[2:-2]).bold=True
  elif part.startswith('`'):
   r=par.add_run(part[1:-1]);r.font.name='Consolas';r.font.size=Pt(9)
  else: par.add_run(part)

i=0;code=False
while i<len(lines):
 line=lines[i]
 if line.startswith('```'):
  code=not code;i+=1;continue
 if code:
  p=doc.add_paragraph();p.paragraph_format.space_after=Pt(1)
  r=p.add_run(line or ' ');r.font.name='Consolas';r.font.size=Pt(8)
  shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F3F0F8');p._p.get_or_add_pPr().append(shade)
 elif line.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].startswith('|'):
   row=[s.strip() for s in lines[i].strip('|').split('|')]
   if not all(re.fullmatch(r':?-+:?',c) for c in row): rows.append(row)
   i+=1
  table=doc.add_table(rows=0,cols=len(rows[0]));table.style='Light Shading Accent 1'
  for n,row in enumerate(rows):
   cells=table.add_row().cells
   for c,text in zip(cells,row):
    inline(c.paragraphs[0],text)
    for run in c.paragraphs[0].runs: run.font.size=Pt(9)
    if n==0:
     for run in c.paragraphs[0].runs:run.bold=True
   if n==0:
    repeat=OxmlElement('w:tblHeader');table.rows[-1]._tr.get_or_add_trPr().append(repeat)
  doc.add_paragraph();continue
 elif line.startswith('# '): doc.add_paragraph(line[2:],style='Title')
 elif line.startswith('## '):
  p=doc.add_paragraph(line[3:],style='Heading 1')
 elif line.startswith('### '): doc.add_paragraph(line[4:],style='Heading 2')
 elif line.startswith('> '):
  p=doc.add_paragraph(style='Intense Quote');inline(p,line[2:])
 elif line=='---': pass
 elif line.startswith('- '): inline(doc.add_paragraph(style='List Bullet'),line[2:])
 elif re.match(r'^\d+\. ',line): inline(doc.add_paragraph(style='List Number'),re.sub(r'^\d+\. ','',line))
 elif line.strip(): inline(doc.add_paragraph(),line.strip())
 i+=1
# Accent theme table colors are kept calm; metadata documents scope explicitly.
doc.core_properties.title='AEGIS — Complete Prototype User & Administrator Manual'
doc.core_properties.subject='Version 1.0 | Synthetic demonstration prototype | 30 October 2026'
doc.core_properties.author='AEGIS Documentation'
doc.save(root/'AEGIS_User_Manual.docx')
print('Saved Word manual; words:',len((root/'AEGIS_User_Manual.md').read_text().split()))
