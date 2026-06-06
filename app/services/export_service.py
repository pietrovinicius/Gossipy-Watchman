import csv
import io
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video


def generate_timeline_csv(
    db: Session,
    person_id: int | None = None,
    video_id: int | None = None,
) -> str:
    query = (
        db.query(Appearance, Person, Video)
        .join(Person, Appearance.person_id == Person.id)
        .join(Video, Appearance.video_id == Video.id)
    )

    if person_id is not None:
        query = query.filter(Appearance.person_id == person_id)
    if video_id is not None:
        query = query.filter(Appearance.video_id == video_id)

    rows = query.order_by(Appearance.video_id.asc(), Appearance.timestamp_start.asc()).all()

    count = len(rows)
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    output = io.StringIO()

    output.write(f"# Gossipy Watchman — Relatório de Presença\n")
    output.write(f"# Gerado em: {now_str}\n")
    output.write(f"# Total de registros: {count}\n")

    writer = csv.DictWriter(
        output,
        fieldnames=[
            "pessoa_id", "pessoa_nome", "pessoa_categoria",
            "video_id", "video_arquivo",
            "entrada_segundos", "saida_segundos", "duracao_segundos", "confianca",
        ],
        lineterminator="\n",
    )
    writer.writeheader()

    for appearance, person, video in rows:
        end = appearance.timestamp_end
        duracao = round(end - appearance.timestamp_start, 3) if end is not None else ""
        writer.writerow({
            "pessoa_id": person.id,
            "pessoa_nome": person.name,
            "pessoa_categoria": person.category or "Desconhecido",
            "video_id": video.id,
            "video_arquivo": video.file_name,
            "entrada_segundos": appearance.timestamp_start,
            "saida_segundos": end if end is not None else "",
            "duracao_segundos": duracao,
            "confianca": appearance.confidence,
        })

    return output.getvalue()
