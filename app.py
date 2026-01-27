import io
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="数据分析与可视化", page_icon="📊", layout="wide")


@dataclass
class DataSummary:
    rows: int
    cols: int
    missing_total: int
    numeric_cols: List[str]
    categorical_cols: List[str]


def load_file(upload) -> Optional[pd.DataFrame]:
    if upload is None:
        return None

    name = upload.name.lower()
    data = upload.getvalue()

    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(data))
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(io.BytesIO(data))

    st.error("仅支持 CSV / XLSX / XLS 文件")
    return None


def summarize(df: pd.DataFrame) -> DataSummary:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    candidate_cols = df.columns.tolist()
    categorical_cols = []
    first_col = candidate_cols[0] if candidate_cols else None
    for col in candidate_cols:
        series = df[col]
        if str(col).lower().startswith("unnamed"):
            continue
        if series.dtype == "object" or str(series.dtype).startswith("category"):
            categorical_cols.append(col)
            continue
        unique_count = series.nunique(dropna=True)
        if unique_count <= min(50, max(2, len(series) // 20)):
            categorical_cols.append(col)
    if first_col and not str(first_col).lower().startswith("unnamed"):
        if first_col not in categorical_cols:
            categorical_cols.insert(0, first_col)
    return DataSummary(
        rows=len(df),
        cols=len(df.columns),
        missing_total=int(df.isna().sum().sum()),
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
    )


def render_overview(df: pd.DataFrame) -> None:
    summary = summarize(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("行数", summary.rows)
    c2.metric("列数", summary.cols)
    c3.metric("缺失值总数", summary.missing_total)
    c4.metric("数值列", len(summary.numeric_cols))

    st.subheader("数据预览")
    st.dataframe(df.head(st.session_state.get("preview_rows", 200)), use_container_width=True)


def safe_sample(df: pd.DataFrame, max_rows: int) -> pd.DataFrame:
    if len(df) <= max_rows:
        return df
    return df.sample(n=max_rows, random_state=42)


def ui_divider() -> None:
    st.markdown("---")


def detect_ftir_structure(df: pd.DataFrame) -> Optional[Dict[str, object]]:
    if df.shape[1] < 5:
        return None
    sample_col = df.columns[0]
    w_cols: List[str] = []
    w_values: List[float] = []
    for col in df.columns[1:]:
        try:
            w_val = float(col)
            w_cols.append(col)
            w_values.append(w_val)
        except (TypeError, ValueError):
            if pd.api.types.is_numeric_dtype(df[col]):
                w_cols.append(col)
                w_values.append(float(len(w_values)))
    if len(w_cols) < 20:
        return None
    order = np.argsort(w_values)[::-1]
    ordered_cols = [w_cols[i] for i in order]
    ordered_vals = [w_values[i] for i in order]
    return {
        "sample_col": sample_col,
        "w_cols": ordered_cols,
        "w_vals": ordered_vals,
    }


def build_long_spectra(df: pd.DataFrame, sample_col: str, w_cols: List[str], w_vals: List[float], samples: List[str]) -> pd.DataFrame:
    sub = df[df[sample_col].isin(samples)][[sample_col] + w_cols].copy()
    sub = sub.melt(id_vars=[sample_col], var_name="wavenumber", value_name="intensity")
    mapper = dict(zip(w_cols, w_vals))
    sub["wavenumber"] = sub["wavenumber"].map(mapper)
    return sub.sort_values("wavenumber", ascending=False)


def smooth_series(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values
    return pd.Series(values).rolling(window=window, center=True, min_periods=1).mean().to_numpy()


def detect_peaks(x: np.ndarray, y: np.ndarray, window: int, min_prom: float, top_n: int) -> pd.DataFrame:
    y_s = smooth_series(y, window)
    peaks: List[Tuple[float, float, float]] = []
    for i in range(1, len(y_s) - 1):
        if y_s[i] > y_s[i - 1] and y_s[i] > y_s[i + 1]:
            left = np.min(y_s[max(0, i - window) : i]) if i - window >= 0 else y_s[i - 1]
            right = np.min(y_s[i + 1 : i + window + 1]) if i + window + 1 <= len(y_s) else y_s[i + 1]
            prominence = y_s[i] - max(left, right)
            if prominence >= min_prom:
                peaks.append((x[i], y[i], y_s[i], prominence))
    if not peaks:
        return pd.DataFrame(columns=["峰值", "透过率", "平滑强度", "峰突出度"])
    peaks = sorted(peaks, key=lambda t: t[3], reverse=True)[:top_n]
    return pd.DataFrame(peaks, columns=["峰值", "透过率", "平滑强度", "峰突出度"])


def default_band_mapping() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"波段下限": 3600, "波段上限": 3200, "对应基团": "O-H 伸缩", "对应成分": "纤维素/半纤维素"},
            {"波段下限": 2970, "波段上限": 2840, "对应基团": "C-H 伸缩", "对应成分": "纤维素/木质素"},
            {"波段下限": 1745, "波段上限": 1710, "对应基团": "C=O 伸缩", "对应成分": "半纤维素"},
            {"波段下限": 1655, "波段上限": 1590, "对应基团": "芳香环 C=C", "对应成分": "木质素"},
            {"波段下限": 1515, "波段上限": 1500, "对应基团": "芳香环骨架", "对应成分": "木质素"},
            {"波段下限": 1470, "波段上限": 1410, "对应基团": "CH2 弯曲", "对应成分": "纤维素"},
            {"波段下限": 1375, "波段上限": 1360, "对应基团": "C-H 弯曲", "对应成分": "纤维素"},
            {"波段下限": 1335, "波段上限": 1310, "对应基团": "O-H 弯曲", "对应成分": "纤维素"},
            {"波段下限": 1275, "波段上限": 1230, "对应基团": "C-O 伸缩", "对应成分": "木质素/半纤维素"},
            {"波段下限": 1170, "波段上限": 1120, "对应基团": "C-O-C 伸缩", "对应成分": "纤维素"},
            {"波段下限": 1115, "波段上限": 1030, "对应基团": "C-O 伸缩", "对应成分": "纤维素/半纤维素"},
            {"波段下限": 900, "波段上限": 890, "对应基团": "β-糖苷键", "对应成分": "纤维素"},
        ]
    )


def map_peaks_to_bands(peaks_df: pd.DataFrame, band_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in peaks_df.iterrows():
        peak = float(row["峰值"])
        match = None
        for _, b in band_df.iterrows():
            low = float(b["波段下限"])
            high = float(b["波段上限"])
            band_min, band_max = min(low, high), max(low, high)
            if band_min <= peak <= band_max:
                match = b
                break
        if match is None:
            band = "未知"
            group = "未知"
            comp = "未知"
        else:
            band = f"{match['波段下限']}-{match['波段上限']}"
            group = match["对应基团"]
            comp = match["对应成分"]
        rows.append(
            {
                "波段": band,
                "峰值": peak,
                "对应基团": group,
                "对应成分": comp,
                "透过率": float(row["透过率"]),
            }
        )
    return pd.DataFrame(rows)


def parse_sample_code(name: str) -> Tuple[str, Optional[int], Optional[int]]:
    match = re.match(r"^([A-Za-z]+)(\d+)(?:-?(\d+))?$", str(name).strip())
    if not match:
        return str(name), None, None
    prefix = match.group(1).upper()
    series = int(match.group(2)) if match.group(2) else None
    replicate = int(match.group(3)) if match.group(3) else None
    return prefix, series, replicate


def load_sample_metadata(base_dir: str) -> Dict[str, object]:
    path = os.path.join(base_dir, "Sample.xlsx")
    if not os.path.exists(path):
        return {}
    df = pd.read_excel(path, sheet_name=0)
    meta: Dict[str, object] = {}
    if len(df.columns) > 1:
        meta["experiment_text"] = str(df.columns[1])

    sample_map: Dict[str, str] = {}
    if len(df.columns) >= 3:
        col_code = df.columns[1]
        col_desc = df.columns[2]
        for _, row in df.iterrows():
            code = str(row.get(col_code, "")).strip()
            desc = str(row.get(col_desc, "")).strip()
            if re.match(r"^[A-Za-z]{2}\d+", code) and desc:
                prefix = re.match(r"^([A-Za-z]{2})", code).group(1).upper()
                if prefix not in sample_map:
                    sample_map[prefix] = desc
    meta["sample_map"] = sample_map
    return meta


def compute_group_mean(df: pd.DataFrame, sample_col: str, w_cols: List[str], group_keys: List[str]) -> pd.DataFrame:
    grouped = df.groupby(group_keys)[w_cols].mean(numeric_only=True)
    grouped = grouped.reset_index()
    return grouped


st.title("📊 数据分析与可视化（内置 Pandas）")

with st.sidebar:
    st.header("导入数据")
    upload = st.file_uploader("选择 CSV 或 Excel 文件", type=["csv", "xlsx", "xls"])
    st.caption("建议先做基础清洗：空值、异常值、字段类型")

    ui_divider()
    st.header("性能与展示限制")
    preview_rows = st.number_input("预览行数上限", min_value=50, max_value=2000, value=200, step=50)
    chart_rows = st.number_input("图表最大行数", min_value=200, max_value=200000, value=20000, step=200)
    st.session_state["preview_rows"] = int(preview_rows)
    st.session_state["chart_rows"] = int(chart_rows)

    if st.button("使用示例数据"):
        sample = pd.DataFrame(
            {
                "日期": pd.date_range("2024-01-01", periods=60, freq="D"),
                "类别": ["A", "B", "C", "D"] * 15,
                "数量": [20, 35, 18, 50] * 15,
                "金额": [1200, 1800, 900, 2600] * 15,
            }
        )
        st.session_state["df"] = sample


if upload is not None:
    df = load_file(upload)
    if df is not None:
        st.session_state["df"] = df


df = st.session_state.get("df")

if df is None:
    st.info("请在左侧上传文件或使用示例数据。")
    st.stop()

render_overview(df)

ui_divider()

st.subheader("统计概览")
with st.expander("描述性统计（数值列）", expanded=True):
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) == 0:
        st.warning("没有可用的数值列")
    else:
        st.dataframe(df[numeric_cols].describe().T, use_container_width=True)

with st.expander("缺失值分布", expanded=False):
    missing = df.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if missing.empty:
        st.success("无缺失值")
    else:
        st.dataframe(missing.rename("缺失数量"), use_container_width=True)

ui_divider()

st.subheader("可视化")

chart_df = safe_sample(df, st.session_state.get("chart_rows", 20000))
if len(chart_df) < len(df):
    st.info(f"为避免浏览器过载，图表仅使用抽样数据：{len(chart_df)} 行 / 总计 {len(df)} 行。")

summary = summarize(df)

cols = st.columns(2)

with cols[0]:
    st.markdown("**数值列分布**")
    num_col = st.selectbox("选择数值列", df.select_dtypes(include="number").columns, key="num_col")
    if num_col:
        fig = px.histogram(chart_df, x=num_col, nbins=30, title=f"{num_col} 分布")
        st.plotly_chart(fig, use_container_width=True)

with cols[1]:
    st.markdown("**类别列对比**")
    cat_col = st.selectbox("选择类别列", summary.categorical_cols, key="cat_col")
    if cat_col:
        vc = chart_df[cat_col].value_counts().reset_index()
        vc.columns = [cat_col, "数量"]
        fig = px.bar(vc, x=cat_col, y="数量", title=f"{cat_col} 频数")
        st.plotly_chart(fig, use_container_width=True)

ui_divider()

st.subheader("分组汇总")

group_cols = st.multiselect("选择分组列", df.columns.tolist())
agg_col = st.selectbox("选择聚合列（数值）", df.select_dtypes(include="number").columns, key="agg_col")
agg_func = st.selectbox("聚合方式", ["sum", "mean", "median", "count", "min", "max"])

if group_cols and agg_col:
    grouped = chart_df.groupby(group_cols)[agg_col].agg(agg_func).reset_index()
    st.dataframe(grouped, use_container_width=True)

    if len(group_cols) == 1:
        fig = px.bar(grouped, x=group_cols[0], y=agg_col, title="分组汇总")
        st.plotly_chart(fig, use_container_width=True)

ui_divider()

st.subheader("相关性（数值列）")
num_df = chart_df.select_dtypes(include="number")
if num_df.shape[1] >= 2:
    corr = num_df.corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=True, title="相关矩阵")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("数值列不足，无法计算相关性。")

ui_divider()

st.subheader("FTIR 专用分析")
ftir = detect_ftir_structure(df)
meta = load_sample_metadata(os.path.dirname(__file__))
if not ftir:
    st.info("未检测到典型 FTIR 结构（首列样本名 + 大量波数列）。")
else:
    sample_col = ftir["sample_col"]
    w_cols = ftir["w_cols"]
    w_vals = ftir["w_vals"]

    df_ftir = df.copy()
    df_ftir[sample_col] = df_ftir[sample_col].astype(str)
    df_ftir["_prefix"], df_ftir["_series"], df_ftir["_replicate"] = zip(
        *df_ftir[sample_col].map(parse_sample_code)
    )
    all_samples = df_ftir[sample_col].dropna().unique().tolist()
    default_samples = all_samples[: min(5, len(all_samples))]

    if meta.get("experiment_text"):
        with st.expander("实验说明（来自 Sample.xlsx）", expanded=False):
            st.write(meta["experiment_text"])

    with st.expander("FTIR 波段-基团映射", expanded=False):
        if "band_map" not in st.session_state:
            st.session_state["band_map"] = default_band_mapping()
        band_df = st.data_editor(
            st.session_state["band_map"],
            num_rows="dynamic",
            use_container_width=True,
        )
        st.session_state["band_map"] = band_df

    with st.expander("谱线绘制（单样本/多样本）", expanded=True):
        pick_samples = st.multiselect("选择样本", all_samples, default=default_samples, key="ftir_samples")
        step = st.number_input("每隔 N 个波数取点", min_value=1, max_value=20, value=1, step=1)
        if pick_samples:
            w_cols_step = w_cols[:: int(step)]
            w_vals_step = w_vals[:: int(step)]
            long_df = build_long_spectra(df_ftir, sample_col, w_cols_step, w_vals_step, pick_samples)
            fig = px.line(long_df, x="wavenumber", y="intensity", color=sample_col, title="样本谱线")
            fig.update_xaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请至少选择一个样本")

    with st.expander("平均谱", expanded=False):
        avg_samples = st.multiselect("选择用于平均的样本", all_samples, default=default_samples, key="ftir_avg_samples")
        if avg_samples:
            sub = df_ftir[df_ftir[sample_col].isin(avg_samples)][w_cols].copy()
            avg = sub.mean(axis=0, skipna=True).to_numpy()
            avg_df = pd.DataFrame({"wavenumber": w_vals, "intensity": avg}).sort_values("wavenumber", ascending=False)
            fig = px.line(avg_df, x="wavenumber", y="intensity", title="平均谱")
            fig.update_xaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请至少选择一个样本")

    with st.expander("差异谱（样本 - 参考）", expanded=False):
        ref_sample = st.selectbox("参考样本", all_samples, index=0, key="ftir_ref")
        diff_samples = st.multiselect("对比样本", all_samples, default=default_samples, key="ftir_diff_samples")
        if ref_sample and diff_samples:
            ref_row = df_ftir[df_ftir[sample_col] == ref_sample][w_cols].iloc[0].to_numpy()
            rows = []
            for s in diff_samples:
                target = df_ftir[df_ftir[sample_col] == s][w_cols].iloc[0].to_numpy()
                diff = target - ref_row
                rows.append(pd.DataFrame({"wavenumber": w_vals, "intensity": diff, "样本": s}))
            diff_df = pd.concat(rows, ignore_index=True).sort_values("wavenumber", ascending=False)
            fig = px.line(diff_df, x="wavenumber", y="intensity", color="样本", title="差异谱")
            fig.update_xaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请选择参考样本和至少一个对比样本")

    with st.expander("峰位检测", expanded=False):
        peak_mode = st.selectbox("峰位来源", ["单一样本", "平均谱"], index=0)
        peak_sample = st.selectbox("选择样本", all_samples, index=0, key="ftir_peak_sample")
        smooth_window = st.number_input("平滑窗口", min_value=1, max_value=31, value=5, step=2)
        if peak_mode == "平均谱":
            avg_samples = st.multiselect("选择用于平均的样本", all_samples, default=default_samples, key="ftir_peak_avg")
            if avg_samples:
                y_vals = df_ftir[df_ftir[sample_col].isin(avg_samples)][w_cols].mean(axis=0, skipna=True).to_numpy()
            else:
                y_vals = df_ftir[df_ftir[sample_col] == peak_sample][w_cols].iloc[0].to_numpy()
        else:
            y_vals = df_ftir[df_ftir[sample_col] == peak_sample][w_cols].iloc[0].to_numpy()
        prom_max = float(np.nanmax(y_vals) - np.nanmin(y_vals))
        prom_max = prom_max if prom_max > 0 else 0.01
        min_prom = st.slider("最小峰突出度", min_value=0.0, max_value=prom_max, value=min(0.001, prom_max), step=0.001)
        top_n = st.number_input("返回峰数量", min_value=5, max_value=50, value=15, step=1)
        peaks_df = detect_peaks(np.array(w_vals), y_vals, int(smooth_window), float(min_prom), int(top_n))
        st.dataframe(peaks_df, use_container_width=True)

        band_df = st.session_state.get("band_map", default_band_mapping())
        result_df = map_peaks_to_bands(peaks_df, band_df)
        st.markdown("**FTIR 峰表（波段 / 峰值 / 基团 / 成分 / 透过率）**")
        st.dataframe(result_df, use_container_width=True)
        st.download_button(
            "下载峰表 CSV",
            data=result_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="ftir_peaks.csv",
            mime="text/csv",
        )

    with st.expander("分组平均谱与差异", expanded=False):
        group_mode = st.selectbox("分组方式", ["样本前缀 (LB/LD/SS/SR)", "系列编号 (1/2/3/4)"], index=0)
        if group_mode.startswith("样本前缀"):
            group_key = "_prefix"
        else:
            group_key = "_series"
        grouped = compute_group_mean(df_ftir, sample_col, w_cols, [group_key])
        group_vals = grouped[group_key].dropna().astype(str).tolist()
        selected_groups = st.multiselect("选择对比组", group_vals, default=group_vals[: min(4, len(group_vals))])
        if selected_groups:
            rows = []
            for g in selected_groups:
                row = grouped[grouped[group_key].astype(str) == str(g)][w_cols].iloc[0].to_numpy()
                rows.append(pd.DataFrame({"wavenumber": w_vals, "intensity": row, "组别": str(g)}))
            gdf = pd.concat(rows, ignore_index=True).sort_values("wavenumber", ascending=False)
            fig = px.line(gdf, x="wavenumber", y="intensity", color="组别", title="分组平均谱")
            fig.update_xaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            if len(selected_groups) >= 2:
                base = selected_groups[0]
                base_row = grouped[grouped[group_key].astype(str) == str(base)][w_cols].iloc[0].to_numpy()
                diff_rows = []
                for g in selected_groups[1:]:
                    row = grouped[grouped[group_key].astype(str) == str(g)][w_cols].iloc[0].to_numpy()
                    diff_rows.append(pd.DataFrame({"wavenumber": w_vals, "intensity": row - base_row, "组别": f"{g}-vs-{base}"}))
                diff_df = pd.concat(diff_rows, ignore_index=True).sort_values("wavenumber", ascending=False)
                fig = px.line(diff_df, x="wavenumber", y="intensity", color="组别", title="组间差异谱")
                fig.update_xaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请选择至少一个组")

ui_divider()

st.subheader("自动分析摘要")
if ftir:
    summary_lines = []
    summary_lines.append(f"检测到 FTIR 结构：样本列为 {ftir['sample_col']}，波数列约 {len(ftir['w_cols'])} 个。")

    if meta.get("sample_map"):
        maps = meta["sample_map"]
        mapped = ", ".join([f"{k}: {v}" for k, v in maps.items()])
        summary_lines.append(f"样本前缀含义：{mapped}。")

    if meta.get("experiment_text"):
        summary_lines.append("实验采用超声波辅助碱浸出处理，变量包括时间、液固比、NaOH 浓度与温度。")

    if "ftir_samples" in st.session_state and st.session_state["ftir_samples"]:
        used_samples = st.session_state["ftir_samples"]
        summary_lines.append(f"已选择 {len(used_samples)} 个样本用于谱线展示：{', '.join(used_samples[:5])}{'…' if len(used_samples)>5 else ''}。")

    if "ftir_avg_samples" in st.session_state and st.session_state["ftir_avg_samples"]:
        avg_samples = st.session_state["ftir_avg_samples"]
        summary_lines.append(f"平均谱基于 {len(avg_samples)} 个样本。")

    if "ftir_peak_sample" in st.session_state:
        peak_sample = st.session_state["ftir_peak_sample"]
        y_vals = df_ftir[df_ftir[ftir["sample_col"]] == peak_sample][ftir["w_cols"]].iloc[0].to_numpy()
        peaks_df = detect_peaks(np.array(ftir["w_vals"]), y_vals, 5, 0.001, 10)
        if not peaks_df.empty:
            top_peaks = ", ".join([f"{row['峰值']:.1f}" for _, row in peaks_df.head(5).iterrows()])
            summary_lines.append(f"样本 {peak_sample} 的主要峰位（前 5）：{top_peaks}。")

    # Variability across all samples
    matrix = df_ftir[ftir["w_cols"]].to_numpy(dtype=float)
    variance = np.nanvar(matrix, axis=0)
    top_var_idx = np.argsort(variance)[-8:][::-1]
    var_points = ", ".join([f"{ftir['w_vals'][i]:.1f}" for i in top_var_idx])
    summary_lines.append(f"全样本变化较大的波数点（前 8）：{var_points}。")

    # Group differences by prefix
    grouped = compute_group_mean(df_ftir, ftir["sample_col"], ftir["w_cols"], ["_prefix"])
    if len(grouped) >= 2:
        group_names = grouped["_prefix"].astype(str).tolist()
        distances = []
        for i in range(len(group_names)):
            for j in range(i + 1, len(group_names)):
                a = grouped.iloc[i][ftir["w_cols"]].to_numpy(dtype=float)
                b = grouped.iloc[j][ftir["w_cols"]].to_numpy(dtype=float)
                dist = float(np.nanmean(np.abs(a - b)))
                distances.append((group_names[i], group_names[j], dist))
        distances.sort(key=lambda t: t[2], reverse=True)
        g1, g2, dist = distances[0]
        summary_lines.append(f"组间平均谱差异最大：{g1} vs {g2}（平均绝对差 {dist:.4g}）。")
        summary_lines.append("推测：这些组别在化学组成或杂质去除程度上可能存在差异，需结合工艺参数验证。")

    st.write("\n".join([f"• {line}" for line in summary_lines]) if summary_lines else "暂无可总结的结果。")
else:
    st.info("当前数据不满足 FTIR 结构，无法自动总结。")
