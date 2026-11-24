# -*- coding: utf-8 -*-
import io
import unicodedata
import numpy as np
import pandas as pd


def _norm(txt: str) -> str:
    if txt is None:
        return ""
    s = str(txt).strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _fmt_int(v) -> str:
    try:
        return f"{int(round(float(v))):,}".replace(",", ".")
    except Exception:
        return "0"


def _fmt_dec(v, dec: int = 2) -> str:
    try:
        s = f"{float(v):,.{dec}f}"
        return s.replace(",", "_").replace(".", ",").replace("_", ".")
    except Exception:
        return "0,00"


def _clasificar_ip4(ip4: float):
    if ip4 >= 1.50:
        return "Altamente concentrada", 3
    if ip4 >= 1.00:
        return "Concentrada", 2
    if ip4 >= 0.65:
        return "Dispersa", 1
    return "Muy dispersa", 0


def generar_pdf_imprimible_control5(
    region_sel: str,
    df_censo: pd.DataFrame,
    df_guttman: pd.DataFrame,
    df_aislamiento: pd.DataFrame,
    dimension_ot: str = "1. Servicios a la producción",
    fuente_censo: str = "",
) -> bytes:
    """Genera PDF Carta horizontal de 3 páginas: solo título + tabla/gráfico de cada indicador."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    c.setAuthor("")
    c.setTitle("")
    c.setSubject("")
    c.setCreator("")

    M_L, M_R, M_T, M_B = 28.0, 28.0, 26.0, 24.0
    usable_w = page_w - M_L - M_R

    C_TEXT = colors.HexColor("#111827")
    C_MUTED = colors.HexColor("#4B5563")
    C_LIGHT = colors.HexColor("#6B7280")
    C_GRID = colors.HexColor("#D1D5DB")
    C_BORDER = colors.HexColor("#9CA3AF")
    C_HDR = colors.HexColor("#E5E7EB")
    C_TOT = colors.HexColor("#F3F4F6")
    C_DIAG = colors.HexColor("#D1D5DB")
    C_BLUE = colors.HexColor("#2F5597")
    C_DARK = colors.HexColor("#1F2937")

    def draw_title(titulo: str) -> float:
        y = page_h - M_T
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica-Bold", 11.0)
        c.drawString(M_L, y - 10, titulo)
        c.setStrokeColor(C_TEXT)
        c.setLineWidth(0.9)
        c.line(M_L, y - 16, page_w - M_R, y - 16)
        return y - 24

    def trunc_text(txt: str, max_w: float, font_name: str, font_size: float) -> str:
        s = str(txt)
        if c.stringWidth(s, font_name, font_size) <= max_w:
            return s
        while len(s) > 2 and c.stringWidth(s + ".", font_name, font_size) > max_w:
            s = s[:-1]
        return s + "."

    def wrap_lines(txt: str, max_w: float, font_name: str, font_size: float, max_lines: int = 3):
        words = str(txt).split()
        lines, cur = [], ""
        for w in words:
            cand = (cur + " " + w).strip()
            if c.stringWidth(cand, font_name, font_size) <= max_w:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                cur = w
                if len(lines) >= max_lines - 1:
                    break
        if cur:
            lines.append(cur)
        if not lines:
            lines = [""]
        return [trunc_text(ln, max_w, font_name, font_size) for ln in lines[:max_lines]]

    def draw_table(
        x0, y_top, col_widths, headers, rows, row_h=13.0, hdr_h=20.0,
        font_size=7.4, aligns=None, bold_rows=None, fill_rows=None, cell_styles=None,
    ):
        n_cols = len(col_widths)
        aligns = aligns or ["L"] + ["R"] * (n_cols - 1)
        bold_rows = set(bold_rows or [])
        fill_rows = fill_rows or {}
        cell_styles = cell_styles or {}

        y_curr = y_top - hdr_h
        x = x0
        for hdr, cw in zip(headers, col_widths):
            c.setFillColor(C_HDR)
            c.setStrokeColor(C_BORDER)
            c.setLineWidth(0.5)
            c.rect(x, y_curr, cw, hdr_h, fill=1, stroke=1)
            c.setFillColor(C_TEXT)
            fs_h = max(font_size - 0.3, 6.2)
            lns = wrap_lines(hdr, cw - 4, "Helvetica-Bold", fs_h, max_lines=3)
            c.setFont("Helvetica-Bold", fs_h)
            line_step = fs_h + 1.4
            tot_h = len(lns) * line_step
            y_txt = y_curr + (hdr_h + tot_h) / 2.0 - fs_h + 1.0
            for ln in lns:
                c.drawCentredString(x + cw / 2.0, y_txt, ln)
                y_txt -= line_step
            x += cw

        for ri, rvals in enumerate(rows):
            y_curr -= row_h
            is_bold_r = ri in bold_rows
            bg_r = fill_rows.get(ri, None)
            x = x0
            for ci, (val, cw) in enumerate(zip(rvals, col_widths)):
                cs = cell_styles.get((ri, ci), {})
                bg = cs.get("bg", bg_r)
                fg = cs.get("fg", C_TEXT)
                is_b = cs.get("bold", is_bold_r)
                al = cs.get("align", aligns[ci])

                c.setStrokeColor(C_GRID)
                c.setLineWidth(0.4)
                if bg is not None:
                    c.setFillColor(bg)
                    c.rect(x, y_curr, cw, row_h, fill=1, stroke=1)
                else:
                    c.rect(x, y_curr, cw, row_h, fill=0, stroke=1)

                if val is not None and str(val) != "":
                    fn = "Helvetica-Bold" if is_b else "Helvetica"
                    c.setFont(fn, font_size)
                    c.setFillColor(fg)
                    s_val = trunc_text(str(val), cw - 4, fn, font_size)
                    ty = y_curr + (row_h - font_size) / 2.0 + 1.2
                    if al == "L":
                        c.drawString(x + 2.5, ty, s_val)
                    elif al == "C":
                        c.drawCentredString(x + cw / 2.0, ty, s_val)
                    else:
                        c.drawRightString(x + cw - 2.5, ty, s_val)
                x += cw
        return y_curr

    # --- DATOS BASE ---
    dfc = df_censo.copy()
    dfc["Censo_2017"] = pd.to_numeric(dfc["Censo_2017"], errors="coerce").fillna(0).astype(int)
    dfc["Censo_2024"] = pd.to_numeric(dfc["Censo_2024"], errors="coerce").fillna(0).astype(int)
    dfc = dfc.sort_values("Censo_2024", ascending=False).reset_index(drop=True)
    dfc["Rk17"] = dfc["Censo_2017"].rank(ascending=False, method="min").astype(int)
    dfc["Rk24"] = dfc["Censo_2024"].rank(ascending=False, method="min").astype(int)
    dfc["Cambio"] = dfc["Rk17"] - dfc["Rk24"]
    dfc["VarPct"] = np.where(
        dfc["Censo_2017"] > 0,
        ((dfc["Censo_2024"] / dfc["Censo_2017"]) - 1.0) * 100.0,
        0.0,
    )
    tot17 = int(dfc["Censo_2017"].sum())
    tot24 = int(dfc["Censo_2024"].sum())
    var_tot = ((tot24 / tot17) - 1.0) * 100.0 if tot17 > 0 else 0.0
    n_com = len(dfc)

    p24_desc = np.sort(dfc["Censo_2024"].values.astype(float))[::-1]
    p17_desc = np.sort(dfc["Censo_2017"].values.astype(float))[::-1]
    ip2_24 = p24_desc[0] / p24_desc[1] if len(p24_desc) >= 2 and p24_desc[1] > 0 else 0.0
    ip2_17 = p17_desc[0] / p17_desc[1] if len(p17_desc) >= 2 and p17_desc[1] > 0 else 0.0
    ip4_24 = p24_desc[0] / np.sum(p24_desc[1:4]) if len(p24_desc) >= 4 and np.sum(p24_desc[1:4]) > 0 else ip2_24
    ip4_17 = p17_desc[0] / np.sum(p17_desc[1:4]) if len(p17_desc) >= 4 and np.sum(p17_desc[1:4]) > 0 else ip2_17
    cat_ip4, cod_ip4 = _clasificar_ip4(ip4_24)
    cat_ip4_17, cod_ip4_17 = _clasificar_ip4(ip4_17)

    # === HOJA 1: PRIMACÍA Y RANKING ===
    y_body = draw_title(f"1. Índice de Primacía y Ranking de Asentamientos — {region_sel}")
    left_w = usable_w * 0.61
    right_x = M_L + left_w + 14.0
    right_w = page_w - M_R - right_x

    def _build_rk_list(sub_df):
        out = []
        for _, r in sub_df.iterrows():
            chg = int(r["Cambio"])
            c_txt = f"+{chg}" if chg > 0 else (str(chg) if chg < 0 else "0")
            out.append([
                str(r["Comuna"]),
                _fmt_int(r["Censo_2017"]),
                _fmt_int(r["Censo_2024"]),
                str(int(r["Rk17"])),
                str(int(r["Rk24"])),
                c_txt,
                f"{_fmt_dec(r['VarPct'], 1)}%",
            ])
        return out

    if n_com > 18:
        mitad = (n_com + 1) // 2
        gap_s = 7.0
        half_w = (left_w - gap_s) / 2.0
        cw_rk = [
            half_w * 0.34, half_w * 0.145, half_w * 0.145,
            half_w * 0.08, half_w * 0.08, half_w * 0.08, half_w * 0.13,
        ]
        rh = min(24.0, (y_body - M_B - 24.0) / max(mitad + 1, 1))
        rows_l = _build_rk_list(dfc.iloc[:mitad])
        rows_r = _build_rk_list(dfc.iloc[mitad:])
        rows_r.append([
            "Total", _fmt_int(tot17), _fmt_int(tot24), "-", "-", "-", f"{_fmt_dec(var_tot, 1)}%",
        ])

        draw_table(
            M_L, y_body, cw_rk,
            ["Comuna", "2017", "2024", "Rk17", "Rk24", "Dif.", "Var.%"],
            rows_l, row_h=rh, hdr_h=20.0, font_size=6.8,
            aligns=["L", "R", "R", "C", "C", "C", "R"],
        )
        draw_table(
            M_L + half_w + gap_s, y_body, cw_rk,
            ["Comuna", "2017", "2024", "Rk17", "Rk24", "Dif.", "Var.%"],
            rows_r, row_h=rh, hdr_h=20.0, font_size=6.8,
            aligns=["L", "R", "R", "C", "C", "C", "R"],
            bold_rows=[len(rows_r) - 1],
            fill_rows={len(rows_r) - 1: C_TOT},
        )
    else:
        cw_rk = [
            left_w * 0.34, left_w * 0.14, left_w * 0.14,
            left_w * 0.09, left_w * 0.09, left_w * 0.08, left_w * 0.12,
        ]
        rh = min(22.0, (y_body - M_B - 24.0) / max(n_com + 2, 1))
        rows_all = _build_rk_list(dfc)
        rows_all.append([
            "Total", _fmt_int(tot17), _fmt_int(tot24), "-", "-", "-", f"{_fmt_dec(var_tot, 1)}%",
        ])
        draw_table(
            M_L, y_body, cw_rk,
            ["Comuna", "Censo 2017", "Censo 2024", "Rk 17", "Rk 24", "Dif.", "Var.%"],
            rows_all, row_h=rh, hdr_h=22.0, font_size=7.6,
            aligns=["L", "R", "R", "C", "C", "C", "R"],
            bold_rows=[len(rows_all) - 1],
            fill_rows={len(rows_all) - 1: C_TOT},
        )

    cw_ip = [right_w * 0.54, right_w * 0.23, right_w * 0.23]
    y_after_ip = draw_table(
        right_x, y_body, cw_ip,
        ["Índice de Primacía", "2017", "2024"],
        [
            ["IP2 (P1 / P2)", _fmt_dec(ip2_17, 3), _fmt_dec(ip2_24, 3)],
            ["IP4 (P1 / [P2+P3+P4])", _fmt_dec(ip4_17, 3), _fmt_dec(ip4_24, 3)],
            ["Valor (0 a 3)", str(cod_ip4_17), str(cod_ip4)],
            ["Clasificación", cat_ip4_17, cat_ip4],
        ],
        row_h=15.0, hdr_h=20.0, font_size=7.4,
        aligns=["L", "C", "C"],
        bold_rows=[1],
        fill_rows={1: C_TOT},
    )

    # Gráfico de cruce Top 10
    box_top = y_after_ip - 10.0
    escala_h = 18.0 + 4 * 13.5
    box_bot = M_B + escala_h + 10.0
    box_h = max(145.0, box_top - box_bot)

    c.setStrokeColor(C_GRID)
    c.setLineWidth(0.6)
    c.rect(right_x, box_bot, right_w, box_h, fill=0, stroke=1)
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", 7.8)
    c.drawString(right_x + 7, box_top - 12, "Ranking Top 10 (2017–2024)")

    df_top = dfc.head(min(10, n_com)).copy().reset_index(drop=True)
    nt = len(df_top)
    if nt >= 2:
        rk17_o = df_top.sort_values("Censo_2017", ascending=False).reset_index(drop=True)
        rk24_o = df_top.sort_values("Censo_2024", ascending=False).reset_index(drop=True)
        p17_m = {str(r["Comuna"]): i for i, r in rk17_o.iterrows()}
        p24_m = {str(r["Comuna"]): i for i, r in rk24_o.iterrows()}

        xl_dot = right_x + right_w * 0.36
        xr_dot = right_x + right_w * 0.64
        yt_c = box_top - 34.0
        yb_c = box_bot + 14.0
        sy_c = (yt_c - yb_c) / max(nt - 1, 1)

        c.setFont("Helvetica-Bold", 7.3)
        c.setFillColor(C_MUTED)
        c.drawRightString(xl_dot + 4, box_top - 23, "2017")
        c.drawString(xr_dot - 4, box_top - 23, "2024")

        for _, r in df_top.iterrows():
            com = str(r["Comuna"])
            i1, i2 = p17_m[com], p24_m[com]
            y1, y2 = yt_c - i1 * sy_c, yt_c - i2 * sy_c
            chg = i1 - i2
            c.setStrokeColor(C_DARK if chg != 0 else C_GRID)
            c.setLineWidth(1.3 if chg != 0 else 0.8)
            if chg == 0:
                c.setDash(2, 2)
            else:
                c.setDash()
            c.line(xl_dot + 7, y1, xr_dot - 7, y2)
        c.setDash()

        for i, r in rk17_o.iterrows():
            com = str(r["Comuna"])
            yy = yt_c - i * sy_c
            lbl = trunc_text(com, xl_dot - right_x - 14, "Helvetica", 6.8)
            c.setFont("Helvetica", 6.8)
            c.setFillColor(C_TEXT)
            c.drawRightString(xl_dot - 9, yy - 2.3, lbl)
            c.setFillColor(colors.white)
            c.setStrokeColor(C_DARK)
            c.setLineWidth(0.8)
            c.circle(xl_dot, yy, 6.0, fill=1, stroke=1)
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(xl_dot, yy - 2.2, str(i + 1))

        for i, r in rk24_o.iterrows():
            com = str(r["Comuna"])
            yy = yt_c - i * sy_c
            chg = p17_m[com] - p24_m[com]
            tag = f" (+{chg})" if chg > 0 else (f" ({chg})" if chg < 0 else "")
            fn = "Helvetica-Bold" if chg != 0 else "Helvetica"
            lbl = trunc_text(com + tag, (right_x + right_w) - xr_dot - 12, fn, 6.8)
            c.setFillColor(C_DARK if chg != 0 else colors.white)
            c.setStrokeColor(C_DARK)
            c.setLineWidth(0.8)
            c.circle(xr_dot, yy, 6.0, fill=1, stroke=1)
            c.setFillColor(colors.white if chg != 0 else C_TEXT)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(xr_dot, yy - 2.2, str(i + 1))
            c.setFont(fn, 6.8)
            c.setFillColor(C_TEXT)
            c.drawString(xr_dot + 9, yy - 2.3, lbl)

    cw_esc = [right_w * 0.52, right_w * 0.28, right_w * 0.20]
    draw_table(
        right_x, box_bot - 8.0, cw_esc,
        ["Escala IP4", "Rango", "Valor"],
        [
            ["Altamente concentrada", ">= 1,50", "3"],
            ["Concentrada", "1,00 a 1,49", "2"],
            ["Dispersa", "0,65 a 0,99", "1"],
            ["Muy dispersa", "< 0,65", "0"],
        ],
        row_h=13.5, hdr_h=18.0, font_size=7.1,
        aligns=["L", "C", "C"],
    )
    c.showPage()

    # === HOJA 2: GUTTMAN / RONDINELLI ===
    mat_g = df_guttman.apply(pd.to_numeric, errors="coerce").fillna(0).clip(0, 1).astype(int)
    funcs = list(mat_g.columns)
    com_g = list(mat_g.index)
    n_g, n_f = len(com_g), len(funcs)
    frec = mat_g.sum(axis=0)
    pesos = frec.apply(lambda f: 100.0 / float(f) if f > 0 else 0.0)
    ic_ser = mat_g.multiply(pesos, axis=1).sum(axis=1)
    tot_f_ser = mat_g.sum(axis=1)
    pob_map = {_norm(r["Comuna"]): int(r["Censo_2024"]) for _, r in dfc.iterrows()}
    pobs_g = [pob_map.get(_norm(cm), 0) for cm in com_g]
    tot_pob_g = max(sum(pobs_g), 1)
    rk_rond = ic_ser.rank(ascending=False, method="min").astype(int).values

    dim_limpia = dimension_ot.split(".", 1)[1].strip() if "." in dimension_ot else dimension_ot
    if "(" in dim_limpia:
        dim_limpia = dim_limpia.split("(", 1)[0].strip()

    y_b2 = draw_title(f"2. Escala de Guttman y Matriz de Rondinelli — {dim_limpia} ({region_sel})")

    w_com, w_pob, w_pct, w_tot, w_ic, w_rk = 92.0, 52.0, 36.0, 38.0, 54.0, 30.0
    w_var = (usable_w - (w_com + w_pob + w_pct + w_tot + w_ic + w_rk)) / max(n_f, 1)
    cw_g = [w_com, w_pob, w_pct] + [w_var] * n_f + [w_tot, w_ic, w_rk]
    hdr_g = ["Comuna", "Pob. 2024", "% Pob."] + funcs + ["Total", "Rondinelli", "Rk"]

    rows_g, cstyles_g = [], {}
    for i, cm in enumerate(com_g):
        rvals = [cm, _fmt_int(pobs_g[i]), f"{_fmt_dec(pobs_g[i] / tot_pob_g * 100.0, 1)}%"]
        for j, f in enumerate(funcs):
            v = int(mat_g.loc[cm, f])
            rvals.append(str(v))
            cstyles_g[(i, 3 + j)] = {"bold": (v == 1), "fg": C_TEXT if v == 1 else C_LIGHT, "align": "C"}
        rvals.extend([str(int(tot_f_ser.iloc[i])), _fmt_dec(ic_ser.iloc[i], 2), str(int(rk_rond[i]))])
        cstyles_g[(i, 3 + n_f + 1)] = {"bold": True, "bg": C_TOT, "align": "R"}
        rows_g.append(rvals)

    rows_g.append(
        ["Suma (fk)", _fmt_int(tot_pob_g), "100,0%"]
        + [str(int(frec[f])) for f in funcs]
        + [str(int(tot_f_ser.sum())), _fmt_dec(ic_ser.sum(), 2), "-"]
    )
    rows_g.append(
        ["Ponderación (100/fk)", "-", "-"]
        + [_fmt_dec(pesos[f], 2) for f in funcs]
        + ["-", "-", "-"]
    )

    y_after_g = draw_table(
        M_L, y_b2, cw_g, hdr_g, rows_g,
        row_h=15.0, hdr_h=30.0, font_size=7.0,
        aligns=["L", "R", "R"] + ["C"] * n_f + ["C", "R", "C"],
        bold_rows=[n_g, n_g + 1],
        fill_rows={n_g: C_TOT, n_g + 1: colors.HexColor("#F9FAFB")},
        cell_styles=cstyles_g,
    )

    ch_top = y_after_g - 12.0
    ch_bot = M_B + 4.0
    ch_h = max(135.0, ch_top - ch_bot)
    c.setStrokeColor(C_GRID)
    c.setLineWidth(0.6)
    c.rect(M_L, ch_bot, usable_w, ch_h, fill=0, stroke=1)
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", 8.0)
    c.drawString(M_L + 10, ch_top - 13, "Complejidad Funcional vs. Población (2024)")

    px0, px1 = M_L + 52.0, page_w - M_R - 26.0
    py0, py1 = ch_bot + 26.0, ch_top - 26.0
    max_p = max(max(pobs_g) if pobs_g else 1000, 1000) * 1.12
    max_ic = max(float(ic_ser.max()) if len(ic_ser) else 20.0, 20.0) * 1.18

    def sx_p(p):
        return px0 + (float(p) / max_p) * (px1 - px0)

    def sy_p(ic):
        return py0 + (float(ic) / max_ic) * (py1 - py0)

    for k in range(5):
        yv = (max_ic / 4.0) * k
        yy = sy_p(yv)
        c.setStrokeColor(colors.HexColor("#E5E7EB"))
        c.setLineWidth(0.5)
        c.line(px0, yy, px1, yy)
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 7.0)
        c.drawRightString(px0 - 5, yy - 2.3, _fmt_dec(yv, 0))

        xv = (max_p / 4.0) * k
        xx = sx_p(xv)
        c.setStrokeColor(colors.HexColor("#F3F4F6"))
        c.line(xx, py0, xx, py1)
        c.drawCentredString(xx, py0 - 11, _fmt_int(xv))

    c.setStrokeColor(C_DARK)
    c.setLineWidth(0.9)
    c.line(px0, py0, px1, py0)
    c.line(px0, py0, px0, py1)
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawRightString(px1, ch_bot + 6, "Población (2024)")

    for i, cm in enumerate(com_g):
        cx, cy = sx_p(pobs_g[i]), sy_p(float(ic_ser.iloc[i]))
        c.setFillColor(C_BLUE)
        c.setStrokeColor(colors.white)
        c.setLineWidth(0.8)
        c.circle(cx, cy, 3.8, fill=1, stroke=1)
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica", 7.0)
        lbl = f"{trunc_text(cm, 82, 'Helvetica', 7.0)} ({_fmt_dec(ic_ser.iloc[i], 1)})"
        dy = 6.5 if (i % 2 == 0) else -10.5
        ly = max(py0 + 4, min(py1 - 5, cy + dy))
        if cx > px1 - 85:
            c.drawRightString(cx - 4, ly, lbl)
        elif cx < px0 + 55:
            c.drawString(cx + 4, ly, lbl)
        else:
            c.drawCentredString(cx, ly, lbl)

    c.showPage()

    # === HOJA 3: ÍNDICE DE AISLAMIENTO ===
    mat_a = df_aislamiento.apply(pd.to_numeric, errors="coerce").fillna(1).clip(0, 1).astype(int)
    locs = list(mat_a.index)
    n_l = len(locs)

    aisl_rows = []
    for i, loc in enumerate(locs):
        vals = [int(mat_a.iloc[i, j]) for j in range(n_l) if j != i]
        s1 = sum(vals)
        ia = (s1 / max(len(vals), 1)) * 100.0
        aisl_rows.append({"Comuna": str(loc), "Suma1": s1, "IA": ia, "Conex0": len(vals) - s1})
    df_aisl_res = pd.DataFrame(aisl_rows)
    df_aisl_res["Rk"] = df_aisl_res["IA"].rank(ascending=True, method="min").astype(int)

    y_b3 = draw_title(f"3. Índice de Aislamiento — {region_sel}")

    w_loc_a = 94.0 if n_l > 14 else 115.0
    w_s1, w_ia, w_c0, w_rka = 28.0, 34.0, 26.0, 22.0
    w_cell = (usable_w - (w_loc_a + w_s1 + w_ia + w_c0 + w_rka)) / max(n_l, 1)
    hdr_h_a = 74.0 if n_l > 14 else 22.0
    row_h_a = min(15.0, (y_b3 - M_B - hdr_h_a - 14.0) / max(n_l + 1, 1))
    fs_a = 6.2 if n_l > 22 else (7.0 if n_l > 14 else 8.0)

    y_hdr_bot = y_b3 - hdr_h_a
    c.setFillColor(C_HDR)
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.5)
    c.rect(M_L, y_hdr_bot, w_loc_a, hdr_h_a, fill=1, stroke=1)
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", fs_a + 0.6)
    c.drawString(M_L + 3, y_hdr_bot + 5, "Comuna")

    x = M_L + w_loc_a
    for loc in locs:
        c.setFillColor(C_HDR)
        c.setStrokeColor(C_BORDER)
        c.setLineWidth(0.45)
        c.rect(x, y_hdr_bot, w_cell, hdr_h_a, fill=1, stroke=1)
        c.setFillColor(C_TEXT)
        if n_l > 14:
            c.saveState()
            c.translate(x + w_cell / 2.0 + 2.0, y_hdr_bot + 3.5)
            c.rotate(90)
            c.setFont("Helvetica-Bold", fs_a)
            c.drawString(0, 0, trunc_text(loc, hdr_h_a - 6, "Helvetica-Bold", fs_a))
            c.restoreState()
        else:
            c.setFont("Helvetica-Bold", fs_a)
            c.drawCentredString(
                x + w_cell / 2.0,
                y_hdr_bot + (hdr_h_a - fs_a) / 2.0 + 1,
                trunc_text(loc, w_cell - 3, "Helvetica-Bold", fs_a),
            )
        x += w_cell

    for lbl_s, ws_s in [("Suma", w_s1), ("IA (%)", w_ia), ("Con.", w_c0), ("Rk", w_rka)]:
        c.setFillColor(C_HDR)
        c.setStrokeColor(C_BORDER)
        c.setLineWidth(0.5)
        c.rect(x, y_hdr_bot, ws_s, hdr_h_a, fill=1, stroke=1)
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica-Bold", fs_a + 0.3)
        c.drawCentredString(x + ws_s / 2.0, y_hdr_bot + 6, lbl_s)
        x += ws_s

    y_r = y_hdr_bot
    for i, loc in enumerate(locs):
        y_r -= row_h_a
        c.setStrokeColor(C_GRID)
        c.setLineWidth(0.35)
        c.rect(M_L, y_r, w_loc_a, row_h_a, fill=0, stroke=1)
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica-Bold", fs_a)
        ty = y_r + (row_h_a - fs_a) / 2.0 + 1.0
        c.drawString(M_L + 2.5, ty, trunc_text(loc, w_loc_a - 5, "Helvetica-Bold", fs_a))

        x = M_L + w_loc_a
        for j in range(n_l):
            if i == j:
                c.setFillColor(C_DIAG)
                c.setStrokeColor(C_GRID)
                c.rect(x, y_r, w_cell, row_h_a, fill=1, stroke=1)
            else:
                v = int(mat_a.iloc[i, j])
                if v == 0:
                    c.setFillColor(C_TOT)
                    c.setStrokeColor(C_GRID)
                    c.rect(x, y_r, w_cell, row_h_a, fill=1, stroke=1)
                    c.setFillColor(C_TEXT)
                    c.setFont("Helvetica-Bold", fs_a)
                else:
                    c.setStrokeColor(C_GRID)
                    c.rect(x, y_r, w_cell, row_h_a, fill=0, stroke=1)
                    c.setFillColor(C_LIGHT)
                    c.setFont("Helvetica", fs_a)
                c.drawCentredString(x + w_cell / 2.0, ty, str(v))
            x += w_cell

        r_st = df_aisl_res.iloc[i]
        for txt_s, ws_s, is_b, al_s in [
            (str(int(r_st["Suma1"])), w_s1, False, "R"),
            (f"{_fmt_dec(r_st['IA'], 1)}%", w_ia, True, "R"),
            (str(int(r_st["Conex0"])), w_c0, False, "C"),
            (str(int(r_st["Rk"])), w_rka, False, "C"),
        ]:
            c.setFillColor(C_TOT)
            c.setStrokeColor(C_GRID)
            c.rect(x, y_r, ws_s, row_h_a, fill=1, stroke=1)
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica-Bold" if is_b else "Helvetica", fs_a)
            if al_s == "R":
                c.drawRightString(x + ws_s - 2.5, ty, txt_s)
            else:
                c.drawCentredString(x + ws_s / 2.0, ty, txt_s)
            x += ws_s

    # Fila final única de promedio (estilo tabla Excel, sin párrafos extra)
    y_r -= row_h_a
    ty_p = y_r + (row_h_a - fs_a) / 2.0 + 1.0
    c.setFillColor(C_HDR)
    c.setStrokeColor(C_BORDER)
    c.rect(M_L, y_r, w_loc_a + n_l * w_cell, row_h_a, fill=1, stroke=1)
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", fs_a)
    c.drawString(M_L + 2.5, ty_p, "Promedio")

    x = M_L + w_loc_a + n_l * w_cell
    for txt_s, ws_s, al_s in [
        (_fmt_dec(df_aisl_res["Suma1"].mean(), 1), w_s1, "R"),
        (f"{_fmt_dec(df_aisl_res['IA'].mean(), 1)}%", w_ia, "R"),
        (_fmt_dec(df_aisl_res["Conex0"].mean(), 1), w_c0, "C"),
        ("-", w_rka, "C"),
    ]:
        c.setFillColor(C_HDR)
        c.setStrokeColor(C_BORDER)
        c.rect(x, y_r, ws_s, row_h_a, fill=1, stroke=1)
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica-Bold", fs_a)
        if al_s == "R":
            c.drawRightString(x + ws_s - 2.5, ty_p, txt_s)
        else:
            c.drawCentredString(x + ws_s / 2.0, ty_p, txt_s)
        x += ws_s

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()
