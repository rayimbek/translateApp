from docx import Document

doc = Document()
doc.add_paragraph("Hello")
doc.save("test.docx")