def list_primary(conn, waybill_id: str) -> list[dict]:
    """正式轴合成视图：原点字段不可变，eff_* 为「原点+有效覆盖」合成值。

    竖轴与投影只读 eff_*；origin 字段原样透出，供页面区分原点与覆盖后展示。
    """
    rows = conn.execute(
        """
        SELECT h.id, h.waybill_id, h.event_ts,
               h.location_code, h.event_code,
               COALESCE(o.new_location_code, h.location_code) AS eff_location_code,
               COALESCE(o.new_event_code, h.event_code) AS eff_event_code,
               o.id AS overlay_id, o.seq AS overlay_seq,
               o.reason AS overlay_reason, o.created_at AS overlay_at,
               h.seq, h.channel, h.retracted
        FROM hops h
        LEFT JOIN hop_overlays o ON o.hop_id = h.id AND o.status = 'effective'
        WHERE h.waybill_id=? AND h.channel='primary' AND h.retracted=0
        ORDER BY h.event_ts ASC, h.id ASC
        """,
        (waybill_id,),
    ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["corrected"] = d["overlay_id"] is not None
        out.append(d)
    return out
