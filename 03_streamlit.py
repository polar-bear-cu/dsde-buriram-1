import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Election Dashboard", layout="wide")
st.title("Dashboard ผลการเลือกตั้งบุรีรัมย์ เขต 1")

BASE_DIR = os.path.dirname(__file__)
FLATTEN_DIR = os.path.join(BASE_DIR, "flatten_result")

@st.cache_data
def load_data():
    district_scores = pd.read_csv(os.path.join(FLATTEN_DIR, "district_scores.csv"),    index_col=0)
    district_summary = pd.read_csv(os.path.join(FLATTEN_DIR, "district_summary.csv"),   index_col=0)
    partylist_scores = pd.read_csv(os.path.join(FLATTEN_DIR, "partylist_scores.csv"),   index_col=0)
    partylist_summary = pd.read_csv(os.path.join(FLATTEN_DIR, "partylist_summary.csv"),  index_col=0)
    referendum_scores = pd.read_csv(os.path.join(FLATTEN_DIR, "referendum_scores.csv"),  index_col=0)
    referendum_summary = pd.read_csv(os.path.join(FLATTEN_DIR, "referendum_summary.csv"), index_col=0)

    for df, col in [(district_scores, "คะแนน"), (partylist_scores, "คะแนน"), (referendum_scores, "คะแนน")]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return (district_scores, district_summary,
            partylist_scores, partylist_summary,
            referendum_scores, referendum_summary)

district_scores, district_summary, partylist_scores, partylist_summary, referendum_scores, referendum_summary = load_data()

# == Sidebar ==
with st.sidebar:
    st.header("ตัวกรองข้อมูล")

    all_amphoes = sorted(set(
        district_scores["อำเภอ"].dropna().unique().tolist() +
        partylist_scores["อำเภอ"].dropna().unique().tolist() +
        referendum_scores[referendum_scores["ตำบล"] != "นอกเขต"]["อำเภอ"].dropna().unique().tolist()
    ))

    selected_amphoe = st.selectbox("เลือกอำเภอ", options=all_amphoes, index=0)

    def get_tambons_in_amphoe(amphoe):
        t1 = district_scores[district_scores["อำเภอ"] == amphoe]["ตำบล"].dropna().unique().tolist()
        t2 = partylist_scores[partylist_scores["อำเภอ"] == amphoe]["ตำบล"].dropna().unique().tolist()
        t3 = (referendum_scores[
                  (referendum_scores["อำเภอ"] == amphoe) & (referendum_scores["ตำบล"] != "นอกเขต")
              ]["ตำบล"].dropna().unique().tolist())
        return sorted(set(t1 + t2 + t3))

    tambons_in_amphoe = get_tambons_in_amphoe(selected_amphoe)

    selected_tambons = st.multiselect(
        "เลือกตำบล", options=tambons_in_amphoe,
        default=tambons_in_amphoe, key="selected_tambons",
    )

ds = district_scores[district_scores["ตำบล"].isin(selected_tambons)].copy()
pl = partylist_scores[partylist_scores["ตำบล"].isin(selected_tambons)].copy()
ref = referendum_scores[referendum_scores["ตำบล"].isin(selected_tambons)].copy()
ref_sum = referendum_summary[referendum_summary["ตำบล"].isin(selected_tambons)].copy()
ref_nok = referendum_scores[referendum_scores["ตำบล"] == "นอกเขต"].copy()
ref_sum_nok = referendum_summary[referendum_summary["ตำบล"] == "นอกเขต"].copy()

REF_COLORS = {
    "เห็นชอบ": "#2a9d8f",
    "ไม่เห็นชอบ": "#e63946",
    "ไม่แสดงความคิดเห็น": "#adb5bd",
}

# == Tabs ==
tab1, tab2, tab3 = st.tabs(["สส.เขต", "สส.บัญชีรายชื่อ", "ประชามติ"])

def is_single_tambon():
    return len(selected_tambons) == 1

def group_col():
    return "หน่วย" if is_single_tambon() else "ตำบล"

with tab1:
    if ds.empty:
        st.info("ไม่มีข้อมูล กรุณาเลือกตำบลในแถบด้านซ้าย")
    else:
        tambon_label = selected_tambons[0] if is_single_tambon() else f"{selected_amphoe} ({len(selected_tambons)} ตำบล)"
        st.caption(f"แสดงข้อมูล: {tambon_label}")

        top_row = ds.groupby(["ชื่อผู้สมัคร", "พรรค"])["คะแนน"].sum().idxmax()
        top_score = int(ds.groupby(["ชื่อผู้สมัคร", "พรรค"])["คะแนน"].sum().max())
        total_units = ds["unit_key"].nunique() if "unit_key" in ds.columns else 0

        k1, k2, k3, k4 = st.columns([1, 1, 1, 3])
        k1.metric("คะแนนรวม", f"{int(ds['คะแนน'].sum()):,}")
        k2.metric("จำนวนหน่วย", f"{total_units:,}")
        k3.metric("จำนวนผู้สมัคร", str(ds["ชื่อผู้สมัคร"].nunique()))
        k4.metric("ผู้ชนะ", f"{top_row[0]} ({top_row[1]})")

        st.divider()

        # 1. คะแนนรวมแต่ละผู้สมัคร
        st.subheader("1. คะแนนรวมแต่ละผู้สมัคร")
        d1 = ds.groupby(["ชื่อผู้สมัคร", "พรรค"], as_index=False)["คะแนน"].sum().sort_values("คะแนน", ascending=False).reset_index(drop=True)
        d1["% คะแนน"] = (d1["คะแนน"] / d1["คะแนน"].sum() * 100).round(2)
        d1["label"] = d1["ชื่อผู้สมัคร"] + " (" + d1["พรรค"] + ")"

        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(d1[["ชื่อผู้สมัคร", "พรรค", "คะแนน", "% คะแนน"]], use_container_width=True, hide_index=True,
                column_config={"คะแนน": st.column_config.NumberColumn(format="%d"),
                               "% คะแนน": st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100)})
        with c2:
            fig = px.bar(d1.sort_values("คะแนน"), x="คะแนน", y="label", orientation="h",
                         color="พรรค", text="คะแนน", title="คะแนนรวมทุกหน่วย", labels={"label": ""})
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(height=max(300, len(d1) * 45))
            st.plotly_chart(fig, use_container_width=True, key="t1_candidate_total")

        st.divider()

        # 2. จำนวนหน่วยที่ชนะ
        st.subheader("2. จำนวนหน่วยที่ผู้สมัครแต่ละคนชนะ")
        if "unit_key" in ds.columns:
            uw = ds.loc[ds.groupby("unit_key")["คะแนน"].idxmax(), ["unit_key", "ชื่อผู้สมัคร", "พรรค"]]
            d2 = (uw.groupby(["ชื่อผู้สมัคร", "พรรค"]).size().reset_index(name="หน่วยที่ชนะ")
                  .sort_values("หน่วยที่ชนะ", ascending=False).reset_index(drop=True))
            d2["label"] = d2["ชื่อผู้สมัคร"] + " (" + d2["พรรค"] + ")"
            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(d2[["ชื่อผู้สมัคร", "พรรค", "หน่วยที่ชนะ"]], use_container_width=True, hide_index=True)
            with c2:
                fig2 = px.bar(d2.sort_values("หน่วยที่ชนะ"), x="หน่วยที่ชนะ", y="label", orientation="h",
                              color="พรรค", text="หน่วยที่ชนะ", title="จำนวนหน่วยที่ชนะ", labels={"label": ""})
                fig2.update_traces(textposition="outside")
                fig2.update_layout(height=max(300, len(d2) * 45))
                st.plotly_chart(fig2, use_container_width=True, key="t1_unit_win")

        st.divider()

        # 3. การกระจายคะแนน
        gcol = group_col()
        if gcol in ds.columns:
            st.subheader(f"3. การกระจายคะแนนแต่ละพรรคราย{gcol}")
            d3 = ds.groupby([gcol, "พรรค"], as_index=False)["คะแนน"].sum()
            d3[gcol] = d3[gcol].astype(str)
            c1, c2 = st.columns(2)
            with c1:
                fig3 = px.bar(d3, x=gcol, y="คะแนน", color="พรรค", barmode="group",
                              title=f"คะแนนสส.เขตราย{gcol} (แยกพรรค)")
                fig3.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig3, use_container_width=True, key="t1_dist_bar")
            with c2:
                piv = d3.pivot_table(index=gcol, columns="พรรค", values="คะแนน", fill_value=0)
                piv_pct = (piv.div(piv.sum(axis=1), axis=0).reset_index()
                           .melt(id_vars=gcol, var_name="พรรค", value_name="สัดส่วน"))
                fig4 = px.density_heatmap(piv_pct, x="พรรค", y=gcol, z="สัดส่วน",
                                          color_continuous_scale="Blues", title=f"Heatmap พรรค x {gcol} (%)")
                st.plotly_chart(fig4, use_container_width=True, key="t1_dist_heat")

        st.divider()

        # 4. พรรคที่ชนะ
        if gcol in ds.columns:
            st.subheader(f"4. พรรคที่ชนะในแต่ละ{gcol}")
            tv = ds.groupby(gcol)["คะแนน"].sum().reset_index(name="total")
            pv = ds.groupby([gcol, "พรรค"])["คะแนน"].sum().reset_index()
            m  = pv.merge(tv, on=gcol)
            m["สัดส่วน"] = m["คะแนน"] / m["total"]
            m[gcol] = m[gcol].astype(str)
            top4 = m.sort_values("สัดส่วน", ascending=False).drop_duplicates(gcol)
            fig5 = px.bar(top4, x=gcol, y="สัดส่วน", color="พรรค", text="พรรค",
                          title=f"พรรคที่ได้คะแนนสูงสุดในแต่ละ{gcol}",
                          labels={"สัดส่วน": "สัดส่วนคะแนน"})
            fig5.update_traces(textposition="outside")
            fig5.update_layout(xaxis_tickangle=-45, yaxis_tickformat=".0%")
            st.plotly_chart(fig5, use_container_width=True, key="t1_winner")

        st.divider()

        # 5. ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา
        if "unit_key" in ds.columns:
            st.subheader("5. ฐานเสียงแข็ง และพื้นที่ที่ต้องพัฒนาของแต่ละพรรค")

            def calc_margin(group):
                g = group.sort_values("คะแนน", ascending=False).reset_index(drop=True)
                if len(g) < 2:
                    return pd.Series({"winner": g.loc[0, "ชื่อผู้สมัคร"], "พรรค": g.loc[0, "พรรค"],
                                      "winner_score": g.loc[0, "คะแนน"], "margin": g.loc[0, "คะแนน"], "margin_pct": 1.0})
                margin = g.loc[0, "คะแนน"] - g.loc[1, "คะแนน"]
                return pd.Series({"winner": g.loc[0, "ชื่อผู้สมัคร"], "พรรค": g.loc[0, "พรรค"],
                                  "winner_score": g.loc[0, "คะแนน"], "margin": margin,
                                  "margin_pct": margin / g["คะแนน"].sum()})

            merge_cols = [c for c in ["unit_key", "หน่วย", "ตำบล", "อำเภอ"] if c in ds.columns]
            um = (ds.groupby("unit_key").apply(calc_margin, include_groups=False).reset_index()
                  .merge(ds[merge_cols].drop_duplicates(), on="unit_key"))

            TOP_UNIT = 5
            for i, party in enumerate(ds["พรรค"].dropna().unique().tolist()):
                own  = um[um["พรรค"] == party].sort_values("margin_pct", ascending=False).head(TOP_UNIT)
                lost = um[um["พรรค"] != party].sort_values("margin_pct", ascending=False).head(TOP_UNIT)
                if own.empty and lost.empty:
                    continue
                st.markdown(f"**พรรค {party}**")
                c1, c2 = st.columns(2)
                with c1:
                    if not own.empty:
                        own = own.dropna(subset=["หน่วย"]).copy()
                        own["label"] = own["ตำบล"].astype(str) + " หน่วย " + own["หน่วย"].astype(str) if not is_single_tambon() else "หน่วย " + own["หน่วย"].astype(str)
                        fig_o = px.bar(own.sort_values("margin_pct"), x="margin_pct", y="label",
                                       orientation="h", title=f"Top {TOP_UNIT} ฐานเสียงแข็ง",
                                       labels={"margin_pct": "Margin", "label": ""},
                                       color_discrete_sequence=["#457b9d"])
                        fig_o.update_traces(texttemplate="%{x:.1%}", textposition="outside")
                        fig_o.update_layout(xaxis_tickformat=".0%", height=300)
                        st.plotly_chart(fig_o, use_container_width=True, key=f"t1_strong_{i}")
                with c2:
                    if not lost.empty:
                        lost = lost.dropna(subset=["หน่วย"]).copy()
                        lost["label"] = lost["ตำบล"].astype(str) + " หน่วย " + lost["หน่วย"].astype(str) if not is_single_tambon() else "หน่วย " + lost["หน่วย"].astype(str)
                        fig_l = px.bar(lost.sort_values("margin_pct"), x="margin_pct", y="label",
                                       orientation="h", title=f"Top {TOP_UNIT} พื้นที่แพ้ห่างที่สุด",
                                       labels={"margin_pct": "Margin", "label": ""},
                                       color_discrete_sequence=["#e63946"])
                        fig_l.update_traces(texttemplate="%{x:.1%}", textposition="outside")
                        fig_l.update_layout(xaxis_tickformat=".0%", height=300)
                        st.plotly_chart(fig_l, use_container_width=True, key=f"t1_weak_{i}")


with tab2:
    if pl.empty:
        st.info("ไม่มีข้อมูล กรุณาเลือกตำบลในแถบด้านซ้าย")
    else:
        tambon_label = selected_tambons[0] if is_single_tambon() else f"{selected_amphoe} ({len(selected_tambons)} ตำบล)"
        st.caption(f"แสดงข้อมูล: {tambon_label}")

        top_pl_party = pl.groupby("พรรค")["คะแนน"].sum().idxmax()
        top_pl_score = int(pl.groupby("พรรค")["คะแนน"].sum().max())
        pl_units = pl["unit_key"].nunique() if "unit_key" in pl.columns else pl["หน่วย"].nunique()

        k1, k2, k3, k4 = st.columns([1, 1, 1, 3])
        k1.metric("คะแนนรวม", f"{int(pl['คะแนน'].sum()):,}")
        k2.metric("จำนวนหน่วย", f"{pl_units:,}")
        k3.metric("จำนวนพรรค", str(pl["พรรค"].nunique()))
        k4.metric("ผู้ชนะ", top_pl_party)

        st.divider()

        # 1. คะแนนรวมแต่ละพรรค
        st.subheader("1. คะแนนรวมแต่ละพรรค")
        p1 = pl.groupby("พรรค")["คะแนน"].sum().sort_values(ascending=False).reset_index()
        p1["% คะแนน"] = (p1["คะแนน"] / p1["คะแนน"].sum() * 100).round(2)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(p1, use_container_width=True, hide_index=True,
                column_config={"คะแนน": st.column_config.NumberColumn(format="%d"),
                               "% คะแนน": st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100)})
        with c2:
            fig7 = px.bar(p1.sort_values("คะแนน"), x="คะแนน", y="พรรค", orientation="h",
                          color="พรรค", text="คะแนน", title="คะแนนรวมแต่ละพรรค (บัญชีรายชื่อ)", labels={"พรรค": ""})
            fig7.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig7.update_layout(showlegend=False, height=max(300, len(p1) * 40))
            st.plotly_chart(fig7, use_container_width=True, key="t2_party_total")

        st.divider()

        # 2. จำนวนหน่วยที่ชนะ
        st.subheader("2. จำนวนหน่วยที่แต่ละพรรคชนะ")
        if "หน่วย" in pl.columns:
            wu = pl.loc[pl.groupby("หน่วย")["คะแนน"].idxmax()]
            wc = wu["พรรค"].value_counts().reset_index()
            wc.columns = ["พรรค", "จำนวนหน่วย"]
            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(wc, use_container_width=True, hide_index=True)
            with c2:
                fig8 = px.bar(wc.sort_values("จำนวนหน่วย"), x="จำนวนหน่วย", y="พรรค", orientation="h",
                              color="พรรค", text="จำนวนหน่วย", title="จำนวนหน่วยที่แต่ละพรรคชนะ", labels={"พรรค": ""})
                fig8.update_traces(textposition="outside")
                fig8.update_layout(showlegend=False, height=max(300, len(wc) * 40))
                st.plotly_chart(fig8, use_container_width=True, key="t2_unit_win")

        st.divider()

        # 3. พรรคที่ชนะราย (หน่วย หรือ ตำบล)
        gcol = group_col()
        if gcol in pl.columns:
            st.subheader(f"3. พรรคที่ชนะในแต่ละ{gcol}")
            wt = pl.loc[pl.groupby(gcol)["คะแนน"].idxmax(), [gcol, "พรรค", "คะแนน"]].sort_values(gcol)
            wt[gcol] = wt[gcol].astype(str)
            st.dataframe(wt.reset_index(drop=True), use_container_width=True, hide_index=True)

        st.divider()

        # 4. การกระจายคะแนน
        if gcol in pl.columns:
            st.subheader(f"4. การกระจายคะแนนพรรคในแต่ละ{gcol}")
            p4 = pl.groupby([gcol, "พรรค"], as_index=False)["คะแนน"].sum()
            p4[gcol] = p4[gcol].astype(str)
            c1, c2 = st.columns(2)
            with c1:
                fig9 = px.bar(p4, x=gcol, y="คะแนน", color="พรรค", barmode="group",
                              title=f"คะแนนบัญชีรายชื่อราย{gcol}")
                fig9.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig9, use_container_width=True, key="t2_dist_bar")
            with c2:
                piv_pl = p4.pivot_table(index=gcol, columns="พรรค", values="คะแนน", fill_value=0)
                piv_pl_pct = (piv_pl.div(piv_pl.sum(axis=1), axis=0).reset_index()
                              .melt(id_vars=gcol, var_name="พรรค", value_name="สัดส่วน"))
                fig10 = px.density_heatmap(piv_pl_pct, x="พรรค", y=gcol, z="สัดส่วน",
                                           color_continuous_scale="Reds", title=f"Heatmap พรรค x {gcol} (%)")
                st.plotly_chart(fig10, use_container_width=True, key="t2_dist_heat")

        st.divider()

        # 5. ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา
        if "unit_key" in pl.columns:
            st.subheader("5. ฐานเสียงแข็ง และพื้นที่ที่ต้องพัฒนาของแต่ละพรรค (บัญชีรายชื่อ)")

            def calc_margin_pl(group):
                g = group.sort_values("คะแนน", ascending=False).reset_index(drop=True)
                if len(g) < 2:
                    return pd.Series({"winner": g.loc[0, "พรรค"], "winner_score": g.loc[0, "คะแนน"],
                                      "margin": g.loc[0, "คะแนน"], "margin_pct": 1.0})
                margin = g.loc[0, "คะแนน"] - g.loc[1, "คะแนน"]
                return pd.Series({"winner": g.loc[0, "พรรค"], "winner_score": g.loc[0, "คะแนน"],
                                  "margin": margin, "margin_pct": margin / g["คะแนน"].sum()})

            merge_cols_pl = [c for c in ["unit_key", "หน่วย", "ตำบล", "อำเภอ"] if c in pl.columns]
            um_pl = (pl.groupby("unit_key").apply(calc_margin_pl, include_groups=False).reset_index()
                     .merge(pl[merge_cols_pl].drop_duplicates(), on="unit_key"))

            TOP_UNIT = 5
            for i, party in enumerate(pl["พรรค"].dropna().unique().tolist()):
                own  = um_pl[um_pl["winner"] == party].sort_values("margin_pct", ascending=False).head(TOP_UNIT)
                lost = um_pl[um_pl["winner"] != party].sort_values("margin_pct", ascending=False).head(TOP_UNIT)
                if own.empty and lost.empty:
                    continue
                st.markdown(f"**พรรค {party}**")
                c1, c2 = st.columns(2)
                with c1:
                    if not own.empty:
                        own = own.dropna(subset=["หน่วย"]).copy()
                        own["label"] = own["ตำบล"].astype(str) + " หน่วย " + own["หน่วย"].astype(str) if not is_single_tambon() else "หน่วย " + own["หน่วย"].astype(str)
                        fig_o = px.bar(own.sort_values("margin_pct"), x="margin_pct", y="label",
                                       orientation="h", title=f"Top {TOP_UNIT} ฐานเสียงแข็ง",
                                       labels={"margin_pct": "Margin", "label": ""},
                                       color_discrete_sequence=["#457b9d"])
                        fig_o.update_traces(texttemplate="%{x:.1%}", textposition="outside")
                        fig_o.update_layout(xaxis_tickformat=".0%", height=300)
                        st.plotly_chart(fig_o, use_container_width=True, key=f"t2_strong_{i}")
                with c2:
                    if not lost.empty:
                        lost = lost.dropna(subset=["หน่วย"]).copy()
                        lost["label"] = lost["ตำบล"].astype(str) + " หน่วย " + lost["หน่วย"].astype(str) if not is_single_tambon() else "หน่วย " + lost["หน่วย"].astype(str)
                        fig_l = px.bar(lost.sort_values("margin_pct"), x="margin_pct", y="label",
                                       orientation="h", title=f"Top {TOP_UNIT} พื้นที่แพ้ห่างที่สุด",
                                       labels={"margin_pct": "Margin", "label": ""},
                                       color_discrete_sequence=["#e63946"])
                        fig_l.update_traces(texttemplate="%{x:.1%}", textposition="outside")
                        fig_l.update_layout(xaxis_tickformat=".0%", height=300)
                        st.plotly_chart(fig_l, use_container_width=True, key=f"t2_weak_{i}")


with tab3:
    if ref.empty:
        st.info("ไม่มีข้อมูล กรุณาเลือกตำบลในแถบด้านซ้าย")
    else:
        tambon_label = selected_tambons[0] if is_single_tambon() else f"{selected_amphoe} ({len(selected_tambons)} ตำบล)"
        st.caption(f"แสดงข้อมูล: {tambon_label}")

        total_eligible = int(ref_sum["ผู้มีสิทธิ"].sum())
        total_turnout  = int(ref_sum["ผู้มาใช้สิทธิ"].sum())
        total_invalid  = int(ref_sum["บัตรเสีย"].sum())
        score_by_type  = ref.groupby("รายการ")["คะแนน"].sum()
        agree_score    = int(score_by_type.get("เห็นชอบ", 0))
        disagree_score = int(score_by_type.get("ไม่เห็นชอบ", 0))
        abstain_score  = int(score_by_type.get("ไม่แสดงความคิดเห็น", 0))

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("ผู้มีสิทธิ", f"{total_eligible:,}")
        k2.metric("ผู้มาใช้สิทธิ", f"{total_turnout:,}")
        k3.metric("บัตรเสีย", f"{total_invalid:,}")
        k4.metric("เห็นชอบ", f"{agree_score:,}")
        k5.metric("ไม่เห็นชอบ", f"{disagree_score:,}")
        k6.metric("ไม่แสดงความคิดเห็น", f"{abstain_score:,}")

        st.divider()

        # 1. สัดส่วนผลโดยรวม
        st.subheader("1. สัดส่วนผลประชามติโดยรวม")
        pie_df = pd.DataFrame({
            "รายการ": ["เห็นชอบ", "ไม่เห็นชอบ", "ไม่แสดงความคิดเห็น"],
            "คะแนน":  [agree_score, disagree_score, abstain_score],
        })
        pie_df["% คะแนน"] = (pie_df["คะแนน"] / pie_df["คะแนน"].sum() * 100).round(2)

        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(pie_df, use_container_width=True, hide_index=True,
                column_config={"คะแนน": st.column_config.NumberColumn(format="%d"),
                               "% คะแนน": st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100)})
        with c2:
            fig_pie = px.pie(pie_df, names="รายการ", values="คะแนน",
                             color="รายการ", color_discrete_map=REF_COLORS,
                             title="สัดส่วนผลประชามติ", hole=0.4)
            fig_pie.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True, key="t3_pie")

        st.divider()

        # 2. ผลราย (หน่วย หรือ ตำบล)
        gcol = group_col()
        if gcol in ref.columns:
            st.subheader(f"2. ผลประชามติราย{gcol}")
            
            ref_grp = ref.groupby([gcol, "รายการ"], as_index=False)["คะแนน"].sum()
            piv_t = ref_grp.pivot_table(index=gcol, columns="รายการ", values="คะแนน", fill_value=0)
            tbl = piv_t.copy().reset_index()
            for col in ["เห็นชอบ", "ไม่เห็นชอบ", "ไม่แสดงความคิดเห็น"]:
                if col not in tbl.columns:
                    tbl[col] = 0

            tbl["รวม"] = tbl["เห็นชอบ"] + tbl["ไม่เห็นชอบ"] + tbl["ไม่แสดงความคิดเห็น"]
            tbl["% เห็นชอบ"] = (tbl["เห็นชอบ"] / tbl["รวม"] * 100).round(2)
            tbl["ผล"] = (tbl["เห็นชอบ"] > tbl["ไม่เห็นชอบ"]).map({True: "เห็นชอบ", False: "ไม่เห็นชอบ"})
            tbl[gcol] = tbl[gcol].astype(str)

            st.dataframe(
                tbl[[gcol, "เห็นชอบ", "ไม่เห็นชอบ", "ไม่แสดงความคิดเห็น", "รวม", "% เห็นชอบ", "ผล"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "เห็นชอบ": st.column_config.NumberColumn(format="%d"),
                    "ไม่เห็นชอบ": st.column_config.NumberColumn(format="%d"),
                    "ไม่แสดงความคิดเห็น": st.column_config.NumberColumn(format="%d"),
                    "รวม": st.column_config.NumberColumn(format="%d"),
                    "% เห็นชอบ": st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100),
                },
            )
            
            ref_grp[gcol] = ref_grp[gcol].astype(str)
            fig_t = px.bar(ref_grp, x=gcol, y="คะแนน", color="รายการ",
                           color_discrete_map=REF_COLORS, barmode="stack",
                           title=f"ผลประชามติราย{gcol} (จำนวนคะแนน)")
            fig_t.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_t, use_container_width=True, key="t3_ref_bar")

            piv_t_pct = (piv_t.div(piv_t.sum(axis=1), axis=0).reset_index()
                         .melt(id_vars=gcol, var_name="รายการ", value_name="สัดส่วน"))
            fig_t_pct = px.bar(piv_t_pct, x=gcol, y="สัดส่วน", color="รายการ",
                               color_discrete_map=REF_COLORS, barmode="stack",
                               title=f"ผลประชามติราย{gcol} (สัดส่วน %)")
            fig_t_pct.update_layout(xaxis_tickangle=-45, yaxis_tickformat=".0%")
            st.plotly_chart(fig_t_pct, use_container_width=True, key="t3_ref_pct")

        st.divider()

        # 3. Turnout
        if gcol in ref_sum.columns:
            st.subheader(f"3. อัตราการใช้สิทธิราย{gcol}")
            td = ref_sum.groupby(gcol)[["ผู้มีสิทธิ", "ผู้มาใช้สิทธิ", "บัตรเสีย"]].sum().reset_index()
            td[gcol] = td[gcol].astype(str)
            td["turnout_%"] = (td["ผู้มาใช้สิทธิ"] / td["ผู้มีสิทธิ"] * 100).round(2)
            td["invalid_%"] = (td["บัตรเสีย"] / td["ผู้มีสิทธิ"] * 100).round(2)

            c1, c2 = st.columns(2)
            with c1:
                fig_to = px.bar(td.sort_values("turnout_%", ascending=False),
                                x=gcol, y="turnout_%", text="turnout_%",
                                title=f"อัตราการใช้สิทธิ (%) ราย{gcol}",
                                labels={"turnout_%": "Turnout (%)"},
                                color="turnout_%", color_continuous_scale="Teal")
                fig_to.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_to.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig_to, use_container_width=True, key="t3_turnout")
            with c2:
                fig_inv = px.bar(td.sort_values("invalid_%", ascending=False),
                                 x=gcol, y="invalid_%", text="invalid_%",
                                 title=f"อัตราบัตรเสีย (%) ราย{gcol}",
                                 labels={"invalid_%": "บัตรเสีย (%)"},
                                 color="invalid_%", color_continuous_scale="Oranges")
                fig_inv.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
                fig_inv.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig_inv, use_container_width=True, key="t3_invalid")

        st.divider()

        # 4. นอกเขต vs ในเขต 
        st.subheader("4. เปรียบเทียบ นอกเขต vs ในเขต")
        ref_in_zone = ref.copy()
        ref_in_zone["ประเภท"] = "ในเขต"
        ref_nok["ประเภท"] = "นอกเขต"
        cmp_df = pd.concat([ref_in_zone, ref_nok])
        cmp = cmp_df.groupby(["ประเภท", "รายการ"])["คะแนน"].sum().reset_index()
        fig_cmp = px.bar(cmp, x="ประเภท", y="คะแนน", color="รายการ",
                         color_discrete_map=REF_COLORS, barmode="group",
                         title="เปรียบเทียบผลประชามติ นอกเขต vs ในเขต", text="คะแนน")
        fig_cmp.update_traces(texttemplate="%{text:,}", textposition="outside")
        st.plotly_chart(fig_cmp, use_container_width=True, key="t3_cmp")