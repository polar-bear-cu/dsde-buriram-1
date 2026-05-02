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

        total_parties_ds = ds["พรรค"].nunique()

        top_n_party_ds = st.number_input(
            f"จำนวนพรรคที่ต้องการแสดง (สูงสุด {total_parties_ds})",
            min_value=1,
            max_value=int(total_parties_ds),
            value=min(5, total_parties_ds),
            step=1,
            key="top_n_party_ds"
        )

        top_parties_ds = (
            ds.groupby("พรรค")["คะแนน"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n_party_ds)
            .index.tolist()
        )

        ds_filtered = ds[ds["พรรค"].isin(top_parties_ds)].copy()
        
        top_row = ds_filtered.groupby(["ชื่อผู้สมัคร", "พรรค"])["คะแนน"].sum().idxmax()
        total_units = ds_filtered["unit_key"].nunique() if "unit_key" in ds_filtered.columns else 0

        k1, k2, k3, k4 = st.columns([1, 1, 1, 3])
        k1.metric("คะแนนรวม", f"{int(ds_filtered['คะแนน'].sum()):,}")
        k2.metric("จำนวนหน่วย", f"{total_units:,}")
        k3.metric("จำนวนผู้สมัคร", str(ds_filtered["ชื่อผู้สมัคร"].nunique()))
        k4.metric("ผู้ชนะ", f"{top_row[0]} ({top_row[1]})")

        st.divider()

        # 1. คะแนนรวมแต่ละผู้สมัคร
        st.subheader("1. คะแนนรวมแต่ละผู้สมัคร")

        d1 = ds_filtered.groupby(["ชื่อผู้สมัคร", "พรรค"], as_index=False)["คะแนน"].sum()
        d1 = d1.sort_values("คะแนน", ascending=False).reset_index(drop=True)
        d1["% คะแนน"] = (d1["คะแนน"] / d1["คะแนน"].sum() * 100).round(2)
        d1["label"] = d1["ชื่อผู้สมัคร"] + " (" + d1["พรรค"] + ")"

        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(
                d1[["ชื่อผู้สมัคร", "พรรค", "คะแนน", "% คะแนน"]],
                use_container_width=True,
                hide_index=True
            )
        with c2:
            fig = px.bar(
                d1.sort_values("คะแนน"),
                x="คะแนน", y="label",
                orientation="h",
                color="พรรค",
                text="คะแนน"
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # 2. จำนวนหน่วยที่ชนะ
        st.subheader("2. จำนวนหน่วยที่ผู้สมัครแต่ละคนชนะ")

        if "unit_key" in ds_filtered.columns:
            uw = ds_filtered.loc[ds_filtered.groupby("unit_key")["คะแนน"].idxmax()]
            d2 = (uw.groupby(["ชื่อผู้สมัคร", "พรรค"])
                  .size()
                  .reset_index(name="หน่วยที่ชนะ")
                  .sort_values("หน่วยที่ชนะ", ascending=False))

            d2["label"] = d2["ชื่อผู้สมัคร"] + " (" + d2["พรรค"] + ")"

            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(d2, use_container_width=True, hide_index=True)
            with c2:
                fig2 = px.bar(
                    d2.sort_values("หน่วยที่ชนะ"),
                    x="หน่วยที่ชนะ", y="label",
                    orientation="h",
                    color="พรรค",
                    text="หน่วยที่ชนะ"
                )
                fig2.update_traces(textposition="outside")
                st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # 3. การกระจายคะแนน
        gcol = group_col()
        if gcol in ds_filtered.columns:
            st.subheader(f"3. การกระจายคะแนนแต่ละพรรคราย{gcol}")

            d3 = ds_filtered.groupby([gcol, "พรรค"], as_index=False)["คะแนน"].sum()

            c1, c2 = st.columns(2)
            with c1:
                fig3 = px.bar(d3, x=gcol, y="คะแนน", color="พรรค", barmode="group")
                st.plotly_chart(fig3, use_container_width=True)
            with c2:
                piv = d3.pivot_table(index=gcol, columns="พรรค", values="คะแนน", fill_value=0)
                piv_pct = (piv.div(piv.sum(axis=1), axis=0).reset_index()
                           .melt(id_vars=gcol, var_name="พรรค", value_name="สัดส่วน"))

                fig4 = px.density_heatmap(piv_pct, x="พรรค", y=gcol, z="สัดส่วน")
                st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # 4. พรรคที่ชนะ
        if gcol in ds_filtered.columns:
            st.subheader(f"4. พรรคที่ชนะในแต่ละ{gcol}")

            wt = ds_filtered.loc[
                ds_filtered.groupby(gcol)["คะแนน"].idxmax(),
                [gcol, "พรรค", "คะแนน"]
            ]

            st.dataframe(wt.reset_index(drop=True), use_container_width=True)

        st.divider()


        c1, c2 = st.columns(2)
        with c1:
            selected_party_ds = st.selectbox(
                "เลือกพรรค",
                options=["ทั้งหมด"] + sorted(ds_filtered["พรรค"].dropna().unique().tolist()),
                key="selected_party_ds"
            )
        with c2:
            TOP_UNIT_DS = st.number_input(
                f"จำนวนหน่วยที่แสดง (สูงสุด 20)",
                min_value=1, max_value=20, value=5,
                key="top_unit_ds"
            )

        # 5. ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา
        st.subheader("5. ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา")

        if "unit_key" in ds_filtered.columns:

            def calc_margin(group):
                g = group.sort_values("คะแนน", ascending=False).reset_index(drop=True)
                if len(g) < 2:
                    return pd.Series({
                        "winner": g.loc[0, "ชื่อผู้สมัคร"],
                        "พรรค": g.loc[0, "พรรค"],
                        "margin_pct": 1.0
                    })
                margin = g.loc[0, "คะแนน"] - g.loc[1, "คะแนน"]
                return pd.Series({
                    "winner": g.loc[0, "ชื่อผู้สมัคร"],
                    "พรรค": g.loc[0, "พรรค"],
                    "margin_pct": margin / g["คะแนน"].sum()
                })

            merge_cols = [c for c in ["unit_key", "หน่วย", "ตำบล"] if c in ds_filtered.columns]

            um = (ds_filtered.groupby("unit_key")
                  .apply(calc_margin, include_groups=False)
                  .reset_index()
                  .merge(ds_filtered[merge_cols].drop_duplicates(), on="unit_key"))

            parties = ds_filtered["พรรค"].dropna().unique().tolist()
            if selected_party_ds != "ทั้งหมด":
                parties = [selected_party_ds]

            for i, party in enumerate(parties):
                own = um[um["พรรค"] == party].sort_values("margin_pct", ascending=False).head(TOP_UNIT_DS)
                lost = um[um["พรรค"] != party].sort_values("margin_pct", ascending=False).head(TOP_UNIT_DS)

                if own.empty and lost.empty:
                    continue

                st.markdown(f"**พรรค {party}**")

                c1, c2 = st.columns(2)

                with c1:
                    fig_o = px.bar(own, x="margin_pct", y="หน่วย", orientation="h",
                                   title="ฐานเสียงแข็ง")
                    st.plotly_chart(fig_o, use_container_width=True, key=f"t1_s{i}")

                with c2:
                    fig_l = px.bar(lost, x="margin_pct", y="หน่วย", orientation="h",
                                   title="พื้นที่ต้องพัฒนา")
                    st.plotly_chart(fig_l, use_container_width=True, key=f"t1_l{i}")

with tab2:
    if pl.empty:
        st.info("ไม่มีข้อมูล กรุณาเลือกตำบลในแถบด้านซ้าย")
    else:
        tambon_label = selected_tambons[0] if is_single_tambon() else f"{selected_amphoe} ({len(selected_tambons)} ตำบล)"
        st.caption(f"แสดงข้อมูล: {tambon_label}")

        total_parties = pl["พรรค"].nunique()

        top_n_party = st.number_input(
            f"จำนวนพรรคที่ต้องการแสดง (สูงสุด {total_parties})",
            min_value=1,
            max_value=int(total_parties),
            value=min(5, total_parties),
            step=1
        )
            
        top_parties = (
            pl.groupby("พรรค")["คะแนน"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n_party)
            .index.tolist()
        )

        pl_filtered = pl[pl["พรรค"].isin(top_parties)].copy()

        top_pl_party = pl_filtered.groupby("พรรค")["คะแนน"].sum().idxmax()
        pl_units = pl_filtered["unit_key"].nunique() if "unit_key" in pl_filtered.columns else pl_filtered["หน่วย"].nunique()

        k1, k2, k3, k4 = st.columns([1, 1, 1, 3])
        k1.metric("คะแนนรวม", f"{int(pl_filtered['คะแนน'].sum()):,}")
        k2.metric("จำนวนหน่วย", f"{pl_units:,}")
        k3.metric("จำนวนพรรค", str(pl_filtered["พรรค"].nunique()))
        k4.metric("ผู้ชนะ", top_pl_party)

        st.divider()

        # 1. คะแนนรวมแต่ละพรรค
        st.subheader("1. คะแนนรวมแต่ละพรรค")
        p1 = pl_filtered.groupby("พรรค")["คะแนน"].sum().sort_values(ascending=False).reset_index()
        p1["% คะแนน"] = (p1["คะแนน"] / p1["คะแนน"].sum() * 100).round(2)

        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(p1, use_container_width=True, hide_index=True)
        with c2:
            fig7 = px.bar(p1.sort_values("คะแนน", ascending=False), x="คะแนน", y="พรรค", orientation="h",
                          color="พรรค", text="คะแนน")
            fig7.update_traces(texttemplate="%{text:,}", textposition="outside")
            st.plotly_chart(fig7, use_container_width=True)

        st.divider()

        # 2. จำนวนหน่วยที่ชนะ
        st.subheader("2. จำนวนหน่วยที่แต่ละพรรคชนะ")
        if "หน่วย" in pl_filtered.columns:
            wu = pl_filtered.loc[pl_filtered.groupby("หน่วย")["คะแนน"].idxmax()]
            wc = wu["พรรค"].value_counts().reset_index()
            wc.columns = ["พรรค", "จำนวนหน่วย"]

            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(wc, use_container_width=True, hide_index=True)
            with c2:
                fig8 = px.bar(wc.sort_values("จำนวนหน่วย", ascending=False), x="จำนวนหน่วย", y="พรรค",
                              orientation="h", color="พรรค", text="จำนวนหน่วย")
                fig8.update_traces(textposition="outside")
                st.plotly_chart(fig8, use_container_width=True)

        st.divider()

        # 3. พรรคที่ชนะราย (หน่วย หรือ ตำบล)
        gcol = group_col()
        if gcol in pl_filtered.columns:
            st.subheader(f"3. พรรคที่ชนะในแต่ละ{gcol}")
            wt = pl_filtered.loc[pl_filtered.groupby(gcol)["คะแนน"].idxmax(), [gcol, "พรรค", "คะแนน"]]
            st.dataframe(wt.reset_index(drop=True), use_container_width=True, hide_index=True)

        st.divider()

        # 4. การกระจายคะแนน
        if gcol in pl_filtered.columns:
            st.subheader(f"4. การกระจายคะแนนพรรคในแต่ละ{gcol}")
            p4 = pl_filtered.groupby([gcol, "พรรค"], as_index=False)["คะแนน"].sum()

            c1, c2 = st.columns(2)
            with c1:
                fig9 = px.bar(p4, x=gcol, y="คะแนน", color="พรรค", barmode="group")
                st.plotly_chart(fig9, use_container_width=True)
            with c2:
                piv = p4.pivot_table(index=gcol, columns="พรรค", values="คะแนน", fill_value=0)
                piv_pct = (piv.div(piv.sum(axis=1), axis=0).reset_index()
                           .melt(id_vars=gcol, var_name="พรรค", value_name="สัดส่วน"))
                fig10 = px.density_heatmap(piv_pct, x="พรรค", y=gcol, z="สัดส่วน")
                st.plotly_chart(fig10, use_container_width=True)

        st.divider()

        # 5. ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา
        c1, c2 = st.columns(2)
        with c1:
            selected_party_pl = st.selectbox(
                "เลือกพรรค",
                options=["ทั้งหมด"] + sorted(pl_filtered["พรรค"].dropna().unique().tolist())
            )
        with c2:
            TOP_UNIT = st.number_input(f"จำนวนหน่วยที่แสดง (สูงสุด 20)", 1, 20, 5)

        st.subheader(f"5. ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา")

        if "unit_key" in pl_filtered.columns:
            def calc_margin_pl(group):
                g = group.sort_values("คะแนน", ascending=False).reset_index(drop=True)
                if len(g) < 2:
                    return pd.Series({"winner": g.loc[0, "พรรค"], "margin_pct": 1.0})
                margin = g.loc[0, "คะแนน"] - g.loc[1, "คะแนน"]
                return pd.Series({"winner": g.loc[0, "พรรค"], "margin_pct": margin / g["คะแนน"].sum()})

            merge_cols = [c for c in ["unit_key", "หน่วย", "ตำบล"] if c in pl_filtered.columns]

            um = (pl_filtered.groupby("unit_key")
                .apply(calc_margin_pl, include_groups=False)
                .reset_index()
                .merge(pl_filtered[merge_cols].drop_duplicates(), on="unit_key"))

            parties = pl_filtered["พรรค"].dropna().unique().tolist()
            if selected_party_pl != "ทั้งหมด":
                parties = [selected_party_pl]

            for i, party in enumerate(parties):
                own = um[um["winner"] == party].sort_values("margin_pct", ascending=False).head(TOP_UNIT)
                lost = um[um["winner"] != party].sort_values("margin_pct", ascending=False).head(TOP_UNIT)
                if own.empty and lost.empty:
                    continue

                st.markdown(f"พรรค {party}")
                c1, c2 = st.columns(2)
                with c1:
                    fig_o = px.bar(own, x="margin_pct", y="หน่วย", orientation="h",
                                title="ฐานเสียงแข็ง")
                    st.plotly_chart(fig_o, use_container_width=True, key=f"t2_s{i}")
                with c2:
                    fig_l = px.bar(lost, x="margin_pct", y="หน่วย", orientation="h",
                                title="พื้นที่ต้องพัฒนา")
                    st.plotly_chart(fig_l, use_container_width=True, key=f"t2_l{i}")
                    
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