import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from tempfile import NamedTemporaryFile
from pathlib import Path
import uuid
import asyncio
import pprint as pp
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks

from docx_utils import read_docx_to_blocks, write_blocks_to_docx
from translator import translate_text_block, TranslationError

app = FastAPI(title="Docx Translator API (API2)")


@app.post("/translate/docx", summary="Загрузите .docx — получите переведённый .docx")
async def translate_docx(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Можно загружать только .docx")

    with NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
        tmp_in.write(await file.read())
        tmp_in_path: Path = Path(tmp_in.name)

    pp.pprint(file)

    try:
        blocks = read_docx_to_blocks(tmp_in_path)
    except Exception as exc:
        tmp_in_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Файл не читается: {exc}")

    pp.pprint(blocks)
    try:
        translated_blocks = await asyncio.gather(
            *[translate_text_block(b) for b in blocks], return_exceptions=True
        )
    except TranslationError as exc:
        tmp_in_path.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=str(exc))

    pp.pprint(translated_blocks)

    output_blocks: list[str] = []
    for original, translated in zip(blocks, translated_blocks):
        if isinstance(translated, Exception):
            output_blocks.append(original)           # falls back to original
        else:
            output_blocks.append(translated)


    tmp_out_path = tmp_in_path.with_name(f"{uuid.uuid4()}.docx")
    write_blocks_to_docx(tmp_in_path, tmp_out_path, output_blocks)

    def cleanup_files():
        tmp_in_path.unlink(missing_ok=True)
        tmp_out_path.unlink(missing_ok=True)

    background_tasks.add_task(cleanup_files)

    # Отдаём файл через FileResponse с правильным именем
    return FileResponse(
        path=tmp_out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"translated_{file.filename}",
        background=background_tasks
    )

@app.get("/", summary = 'main api', tags=['main apis'])
async def home():
    return {"message": "Hello World"}

@app.get("/users", summary = 'second api', tags=['main apis'])
async def get_users():
    return [{"id": 1, "name": "Ivan"}]


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True , host='0.0.0.0', port=8000)


