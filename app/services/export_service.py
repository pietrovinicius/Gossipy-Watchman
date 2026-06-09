import csv
import io
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appearance import Appearance
from app.models.person import Person
from app.models.video import Video

_DELIMITER = ";"


def _fmt_ss(seconds: float | None) -> str:
    """Converte segundos float → MM:SS (ex.: 125.3 → '02:05')."""
    if seconds is None:
        return ""
    total = int(round(seconds))
    m, s = divmod(abs(total), 60)
    return f"{m:02d}:{s:02d}"


def _fmt_dt(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y %H:%M:%S")


def generate_timeline_csv(
    db: Session,
    person_id: int | None = None,
    video_id: int | None = None,
) -> str:
    # Subquery: agrega métricas por (pessoa, vídeo)
    agg_sub = (
        db.query(
            Appearance.person_id.label("agg_person_id"),
            Appearance.video_id.label("agg_video_id"),
            func.min(Appearance.timestamp_start).label("first_seen"),
            func.max(
                func.coalesce(Appearance.timestamp_end, Appearance.timestamp_start)
            ).label("last_seen"),
            func.count(Appearance.id).label("total_aprs"),
            func.sum(
                func.coalesce(Appearance.timestamp_end, Appearance.timestamp_start)
                - Appearance.timestamp_start
            ).label("total_secs"),
        )
        .group_by(Appearance.person_id, Appearance.video_id)
        .subquery()
    )

    query = (
        db.query(
            Appearance,
            Person,
            Video,
            agg_sub.c.first_seen,
            agg_sub.c.last_seen,
            agg_sub.c.total_aprs,
            agg_sub.c.total_secs,
        )
        .join(Person, Appearance.person_id == Person.id)
        .join(Video, Appearance.video_id == Video.id)
        .join(
            agg_sub,
            (agg_sub.c.agg_person_id == Appearance.person_id)
            & (agg_sub.c.agg_video_id == Appearance.video_id),
        )
    )

    if person_id is not None:
        query = query.filter(Appearance.person_id == person_id)
    if video_id is not None:
        query = query.filter(Appearance.video_id == video_id)

    rows = query.order_by(
        Appearance.video_id.asc(),
        Appearance.person_id.asc(),
        Appearance.timestamp_start.asc(),
    ).all()

    count = len(rows)
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    output = io.StringIO()
    output.write("# Gossipy Watchman — Relatório de Presença\n")
    output.write(f"# Gerado em: {now_str}\n")
    output.write(f"# Total de registros: {count}\n")

    fieldnames = [
        "pessoa_id",
        "pessoa_nome",
        "pessoa_categoria",
        "aparicao_num",
        "inicio_s",
        "inicio_formatado",
        "fim_s",
        "fim_formatado",
        "presente_por_s",
        "presente_por_formatado",
        "primeira_vez_s",
        "primeira_vez_formatado",
        "ultima_vez_s",
        "ultima_vez_formatado",
        "total_aparicoes_no_video",
        "total_presente_no_video_s",
        "confianca",
        "video_id",
        "video_arquivo",
        "video_data_upload",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=_DELIMITER,
        lineterminator="\n",
    )
    writer.writeheader()

    # Contador de aparição por (pessoa, vídeo)
    apricao_counter: dict[tuple[int, int], int] = {}

    for appearance, person, video, first_seen, last_seen, total_aprs, total_secs in rows:
        key = (person.id, video.id)
        apricao_counter[key] = apricao_counter.get(key, 0) + 1
        apricao_num = apricao_counter[key]

        end = appearance.timestamp_end
        duracao = round(end - appearance.timestamp_start, 3) if end is not None else None

        first_seen_val = float(first_seen) if first_seen is not None else None
        last_seen_val = float(last_seen) if last_seen is not None else None
        total_secs_val = round(float(total_secs), 3) if total_secs is not None else 0.0

        writer.writerow({
            "pessoa_id": person.id,
            "pessoa_nome": person.name,
            "pessoa_categoria": person.category or "Desconhecido",
            "aparicao_num": apricao_num,
            "inicio_s": round(appearance.timestamp_start, 3),
            "inicio_formatado": _fmt_ss(appearance.timestamp_start),
            "fim_s": round(end, 3) if end is not None else "",
            "fim_formatado": _fmt_ss(end),
            "presente_por_s": duracao if duracao is not None else "",
            "presente_por_formatado": _fmt_ss(duracao),
            "primeira_vez_s": round(first_seen_val, 3) if first_seen_val is not None else "",
            "primeira_vez_formatado": _fmt_ss(first_seen_val),
            "ultima_vez_s": round(last_seen_val, 3) if last_seen_val is not None else "",
            "ultima_vez_formatado": _fmt_ss(last_seen_val),
            "total_aparicoes_no_video": total_aprs,
            "total_presente_no_video_s": total_secs_val,
            "confianca": round(appearance.confidence, 4),
            "video_id": video.id,
            "video_arquivo": video.file_name,
            "video_data_upload": _fmt_dt(video.uploaded_at),
        })

    return output.getvalue()
