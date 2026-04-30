import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import os

matplotlib.rcParams['font.family'] = 'Tahoma'
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Election Dashboard", layout="wide")

st.title("Dashboard วิเคราะห์ผลการเลือกตั้ง")

BASE_DIR = os.path.dirname(__file__)
FLATTEN_DIR = os.path.join(BASE_DIR, "flatten_result")

district_scores = None
district_summary = None
partylist_scores = None
partylist_summary = None

@st.cache_data
def load_data():
    district_scores = pd.read_csv(os.path.join(FLATTEN_DIR, "district_scores.csv"), index_col=0)
    district_summary = pd.read_csv(os.path.join(FLATTEN_DIR, "district_summary.csv"), index_col=0)
    partylist_scores = pd.read_csv(os.path.join(FLATTEN_DIR, "partylist_scores.csv"), index_col=0)
    partylist_summary = pd.read_csv(os.path.join(FLATTEN_DIR, "partylist_summary.csv"), index_col=0)
    return district_scores, district_summary, partylist_scores, partylist_summary

district_scores, district_summary, partylist_scores, partylist_summary = load_data()

with st.sidebar:
    st.header("Filter")
    district_parties  = sorted(district_scores["พรรค"].dropna().unique().tolist())
    partylist_parties = sorted(partylist_scores["พรรค"].dropna().unique().tolist())

    st.subheader("สส.เขต")
    st.subheader("สส.เขต")
    selected_district_parties = st.multiselect(
        "เลือกพรรค (สส.เขต)",
        options=district_parties,
        default=district_parties,
        key="district_parties",)
 
    st.divider()

    top10_partylist = (
        partylist_scores.groupby("พรรค")["คะแนน"].sum()
        .nlargest(10).index.tolist()
    )

    st.subheader("สส.บัญชีรายชื่อ")
    selected_partylist_parties = st.multiselect(
        "เลือกพรรค (บัญชีรายชื่อ)",
        options=partylist_parties,
        default=top10_partylist,
        key="partylist_parties",
    )

ds = district_scores[district_scores["พรรค"].isin(selected_district_parties)].copy()
pl = partylist_scores[partylist_scores["พรรค"].isin(selected_partylist_parties)].copy()

tab1, tab2 = st.tabs(["สส.เขต", "สส.บัญชีรายชื่อ"])

with tab1:
    if ds.empty:
        st.info("ไม่มีข้อมูล กรุณาเลือกพรรคในแถบด้านซ้าย")
    else:
        # == Section 1: คะแนนรวมแต่ละผู้สมัคร ==
        st.subheader("1. คะแนนรวมแต่ละผู้สมัคร")
        d1 = (
            ds.groupby(["ชื่อผู้สมัคร", "พรรค"], as_index=False)["คะแนน"]
            .sum()
            .sort_values("คะแนน", ascending=False)
            .reset_index(drop=True)
        )
        d1.index += 1
        d1["% คะแนน"] = (d1["คะแนน"] / d1["คะแนน"].sum() * 100).round(2)

        col_t, col_c = st.columns([1, 2])
        with col_t:
            st.dataframe(d1, use_container_width=True)
        with col_c:
            fig, ax = plt.subplots(figsize=(8, max(3, len(d1) * 0.45)))
            colors = ["#e63946" if i == 0 else "#457b9d" for i in range(len(d1))]
            ax.barh(d1["ชื่อผู้สมัคร"] + " (" + d1["พรรค"] + ")", d1["คะแนน"], color=colors)
            ax.set_xlabel("คะแนน")
            ax.set_title("คะแนนรวมทุกหน่วย")
            ax.invert_yaxis()
            for i, v in enumerate(d1["คะแนน"]):
                ax.text(v + 10, i, f"{v:,}", va="center", fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        st.divider()

        # == Section 2: จำนวนหน่วยที่ชนะ ==
        st.subheader("2. จำนวนหน่วยที่ผู้สมัครแต่ละคนชนะ")
        if "unit_key" in ds.columns:
            unit_winner = ds.loc[
                ds.groupby("unit_key")["คะแนน"].idxmax(),
                ["unit_key", "ชื่อผู้สมัคร", "พรรค"],
            ]
            d2 = (
                unit_winner.groupby(["ชื่อผู้สมัคร", "พรรค"])
                .size()
                .reset_index(name="หน่วยที่ชนะ")
                .sort_values("หน่วยที่ชนะ", ascending=False)
                .reset_index(drop=True)
            )
            d2.index += 1

            col_t2, col_c2 = st.columns([1, 2])
            with col_t2:
                st.dataframe(d2, use_container_width=True)
            with col_c2:
                fig2, ax2 = plt.subplots(figsize=(8, max(3, len(d2) * 0.45)))
                colors2 = ["#e63946" if i == 0 else "#457b9d" for i in range(len(d2))]
                ax2.barh(d2["ชื่อผู้สมัคร"] + " (" + d2["พรรค"] + ")", d2["หน่วยที่ชนะ"], color=colors2)
                ax2.set_xlabel("จำนวนหน่วย")
                ax2.set_title("จำนวนหน่วยที่ชนะ")
                ax2.invert_yaxis()
                for i, v in enumerate(d2["หน่วยที่ชนะ"]):
                    ax2.text(v + 0.2, i, str(v), va="center", fontsize=8)
                plt.tight_layout()
                st.pyplot(fig2)
                plt.close(fig2)
        else:
            st.warning("ไม่พบคอลัมน์ unit_key ในข้อมูล")

        st.divider()

        # == Section 3: การกระจายคะแนนรายตำบล ==
        if "ตำบล" in ds.columns:
            st.subheader("3. การกระจายคะแนนแต่ละพรรครายตำบล")
            d4 = ds.groupby(["ตำบล", "พรรค"], as_index=False)["คะแนน"].sum()
            d4_pivot = d4.pivot_table(index="ตำบล", columns="พรรค", values="คะแนน", fill_value=0)

            col_h1, col_h2 = st.columns(2)
            with col_h1:
                fig3, ax3 = plt.subplots(figsize=(10, 5))
                d4_pivot.plot(kind="bar", ax=ax3)
                ax3.set_title("คะแนนสส.เขตรายตำบล (แยกพรรค)")
                ax3.set_ylabel("คะแนน")
                ax3.set_xlabel("ตำบล")
                plt.xticks(rotation=45, ha="right")
                ax3.legend(title="พรรค", bbox_to_anchor=(1.05, 1), loc="upper left")
                plt.tight_layout()
                st.pyplot(fig3)
                plt.close(fig3)

            with col_h2:
                pivot_pct = d4_pivot.div(d4_pivot.sum(axis=1), axis=0)
                fig4, ax4 = plt.subplots(figsize=(10, 5))
                sns.heatmap(pivot_pct, cmap="Blues", ax=ax4)
                ax4.set_title("Heatmap พรรค × ตำบล (%)")
                plt.tight_layout()
                st.pyplot(fig4)
                plt.close(fig4)

        st.divider()

        # == Section 4: พรรคที่ชนะรายตำบล ==
        if "ตำบล" in ds.columns:
            st.subheader("4. พรรคที่ชนะในแต่ละตำบล")
            total_v  = ds.groupby("ตำบล")["คะแนน"].sum().reset_index(name="total_votes")
            party_v  = ds.groupby(["ตำบล", "พรรค"])["คะแนน"].sum().reset_index()
            merged   = party_v.merge(total_v, on="ตำบล")
            merged["สัดส่วนคะแนน"] = merged["คะแนน"] / merged["total_votes"]
            top_party = (
                merged.sort_values("สัดส่วนคะแนน", ascending=False)
                .drop_duplicates("ตำบล")
            )
            party_colors = {
                p: c
                for p, c in zip(
                    ds["พรรค"].unique(),
                    plt.cm.tab10.colors,
                )
            }
            colors_bar = top_party["พรรค"].map(party_colors)

            fig5, ax5 = plt.subplots(figsize=(12, 5))
            ax5.bar(range(len(top_party)), top_party["สัดส่วนคะแนน"], color=list(colors_bar))
            for i, v in enumerate(top_party["สัดส่วนคะแนน"]):
                ax5.text(i, v + 0.005, f"{v*100:.1f}%", ha="center", va="bottom", fontsize=8)
            ax5.set_xticks(range(len(top_party)))
            ax5.set_xticklabels(top_party["ตำบล"].tolist(), rotation=45, ha="right")
            ax5.set_title("พรรคที่ได้คะแนนสูงสุดในแต่ละตำบล")
            ax5.set_xlabel("ตำบล")
            ax5.set_ylabel("สัดส่วนคะแนน")
            handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in party_colors.values()]
            ax5.legend(handles, party_colors.keys(), title="พรรค")
            plt.tight_layout()
            st.pyplot(fig5)
            plt.close(fig5)

        st.divider()

        # == Section 5: ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา ==
        if "unit_key" in ds.columns and "ตำบล" in ds.columns:
            st.subheader("5. ฐานเสียงแข็ง และพื้นที่ที่ต้องพัฒนาของแต่ละพรรค")

            def calc_margin(group):
                group = group.sort_values("คะแนน", ascending=False).reset_index(drop=True)
                if len(group) < 2:
                    return pd.Series({"winner": group.loc[0, "ชื่อผู้สมัคร"], "พรรค": group.loc[0, "พรรค"],
                                        "winner_score": group.loc[0, "คะแนน"], "margin": group.loc[0, "คะแนน"], "margin_pct": 1.0})
                margin = group.loc[0, "คะแนน"] - group.loc[1, "คะแนน"]
                total  = group["คะแนน"].sum()
                return pd.Series({"winner": group.loc[0, "ชื่อผู้สมัคร"], "พรรค": group.loc[0, "พรรค"],
                                    "winner_score": group.loc[0, "คะแนน"], "margin": margin, "margin_pct": margin / total})

            unit_margin = (
                ds.groupby("unit_key")
                .apply(calc_margin, include_groups=False)
                .reset_index()
            )
            unit_margin = unit_margin.merge(
                ds[["unit_key", "หน่วย", "ตำบล", "อำเภอ"]].drop_duplicates(), on="unit_key"
            )

            TOP_UNIT = 5
            for party in selected_district_parties:
                own  = unit_margin[unit_margin["พรรค"] == party].sort_values("margin_pct", ascending=False).head(TOP_UNIT).reset_index(drop=True)
                lost = unit_margin[unit_margin["พรรค"] != party].sort_values("margin_pct", ascending=False).head(TOP_UNIT).reset_index(drop=True)

                if own.empty and lost.empty:
                    continue

                st.markdown(f"**พรรค {party}**")
                fig6, axes6 = plt.subplots(1, 2, figsize=(12, max(3, TOP_UNIT * 1.2)))
                fig6.suptitle(f"พรรค {party}", fontweight="bold")

                if not own.empty:
                    own = own.dropna(subset=["ตำบล", "หน่วย"]).reset_index(drop=True)
                    vals = own["margin_pct"] * 100
                    axes6[0].barh(own["ตำบล"] + " หน่วย " + own["หน่วย"].astype(str), vals, color="#457b9d")
                    axes6[0].set_xlim(0, vals.max() * 1.2 if len(vals) else 1)
                axes6[0].set_xlabel("Margin (%)")
                axes6[0].set_title(f"Top {TOP_UNIT} ฐานเสียงแข็ง")

                if not lost.empty:
                    lost = lost.dropna(subset=["ตำบล", "หน่วย"]).reset_index(drop=True)
                    vals2 = lost["margin_pct"] * 100
                    axes6[1].barh(lost["ตำบล"] + " หน่วย " + lost["หน่วย"].astype(str), vals2, color="#e63946")
                    axes6[1].set_xlim(0, vals2.max() * 1.2 if len(vals2) else 1)
                axes6[1].set_xlabel("Margin (%)")
                axes6[1].set_title(f"Top {TOP_UNIT} พื้นที่แพ้ห่างที่สุด")

                plt.tight_layout()
                st.pyplot(fig6)
                plt.close(fig6)

with tab2:
    if pl.empty:
        st.info("ไม่มีข้อมูล กรุณาเลือกพรรคในแถบด้านซ้าย")
    else:
        # == Section 1: คะแนนรวมแต่ละพรรค ==
        st.subheader("1. คะแนนรวมแต่ละพรรค")
        p1 = (
            pl.groupby("พรรค")["คะแนน"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        p1.index += 1
        p1["% คะแนน"] = (p1["คะแนน"] / p1["คะแนน"].sum() * 100).round(2)

        col_p1t, col_p1c = st.columns([1, 2])
        with col_p1t:
            st.dataframe(p1, use_container_width=True)
        with col_p1c:
            fig7, ax7 = plt.subplots(figsize=(10, 5))
            ax7.bar(p1["พรรค"], p1["คะแนน"], color="#2a9d8f")
            ax7.set_title("คะแนนรวมแต่ละพรรค (บัญชีรายชื่อ)")
            ax7.set_ylabel("คะแนน")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig7)
            plt.close(fig7)

        st.divider()

        # == Section 2: จำนวนหน่วยที่ชนะ ==
        st.subheader("2. จำนวนหน่วยที่แต่ละพรรคชนะ")
        if "หน่วย" in pl.columns:
            winner_unit = pl.loc[pl.groupby("หน่วย")["คะแนน"].idxmax()]
            win_count   = winner_unit["พรรค"].value_counts().reset_index()
            win_count.columns = ["พรรค", "จำนวนหน่วย"]

            col_p2t, col_p2c = st.columns([1, 2])
            with col_p2t:
                st.dataframe(win_count, use_container_width=True)
            with col_p2c:
                fig8, ax8 = plt.subplots(figsize=(10, 5))
                ax8.barh(win_count["พรรค"], win_count["จำนวนหน่วย"], color="#e9c46a")
                ax8.set_xlabel("จำนวนหน่วย")
                ax8.set_title("จำนวนหน่วยที่แต่ละพรรคชนะ")
                ax8.invert_yaxis()
                plt.tight_layout()
                st.pyplot(fig8)
                plt.close(fig8)

        st.divider()

        # == Section 3: พรรคที่ชนะรายตำบล ==
        if "ตำบล" in pl.columns:
            st.subheader("3. พรรคที่ชนะในแต่ละตำบล")
            winner_tambon = pl.loc[
                pl.groupby("ตำบล")["คะแนน"].idxmax(),
                ["ตำบล", "พรรค", "คะแนน"],
            ].sort_values("ตำบล")
            st.dataframe(winner_tambon.reset_index(drop=True), use_container_width=True)

        st.divider()

        # == Section 4: การกระจายคะแนนรายตำบล ==
        if "ตำบล" in pl.columns:
            st.subheader("4. การกระจายคะแนนพรรคในแต่ละตำบล")
            pivot_pl = pl.pivot_table(index="ตำบล", columns="พรรค", values="คะแนน", aggfunc="sum", fill_value=0)

            col_pl1, col_pl2 = st.columns(2)
            with col_pl1:
                fig9, ax9 = plt.subplots(figsize=(10, 5))
                pivot_pl.plot(kind="bar", ax=ax9)
                ax9.set_title("คะแนนบัญชีรายชื่อรายตำบล")
                ax9.set_ylabel("คะแนน")
                plt.xticks(rotation=45, ha="right")
                ax9.legend(title="พรรค", bbox_to_anchor=(1.05, 1), loc="upper left")
                plt.tight_layout()
                st.pyplot(fig9)
                plt.close(fig9)

            with col_pl2:
                pivot_pct_pl = pivot_pl.div(pivot_pl.sum(axis=1), axis=0)
                fig10, ax10 = plt.subplots(figsize=(10, 5))
                sns.heatmap(pivot_pct_pl, cmap="Reds", ax=ax10)
                ax10.set_title("Heatmap พรรค × ตำบล (%)")
                plt.tight_layout()
                st.pyplot(fig10)
                plt.close(fig10)

        st.divider()

        # == Section 5: ฐานเสียงแข็ง / พื้นที่ต้องพัฒนา ==
        if "unit_key" in pl.columns and "ตำบล" in pl.columns:
            st.subheader("5. ฐานเสียงแข็ง และพื้นที่ที่ต้องพัฒนาของแต่ละพรรค (บัญชีรายชื่อ)")

            def calc_margin_pl(group):
                group = group.sort_values("คะแนน", ascending=False).reset_index(drop=True)
                if len(group) < 2:
                    return pd.Series({"winner": group.loc[0, "พรรค"], "winner_score": group.loc[0, "คะแนน"],
                                        "margin": group.loc[0, "คะแนน"], "margin_pct": 1.0})
                margin = group.loc[0, "คะแนน"] - group.loc[1, "คะแนน"]
                total  = group["คะแนน"].sum()
                return pd.Series({"winner": group.loc[0, "พรรค"], "winner_score": group.loc[0, "คะแนน"],
                                    "margin": margin, "margin_pct": margin / total})

            unit_margin_pl = (
                pl.groupby("unit_key")
                .apply(calc_margin_pl, include_groups=False)
                .reset_index()
            )
            unit_margin_pl = unit_margin_pl.merge(
                pl[["unit_key", "หน่วย", "ตำบล", "อำเภอ"]].drop_duplicates(), on="unit_key"
            )

            TOP_UNIT = 5
            for party in selected_partylist_parties:
                own  = unit_margin_pl[unit_margin_pl["winner"] == party].sort_values("margin_pct", ascending=False).head(TOP_UNIT).reset_index(drop=True)
                lost = unit_margin_pl[unit_margin_pl["winner"] != party].sort_values("margin_pct", ascending=False).head(TOP_UNIT).reset_index(drop=True)

                if own.empty and lost.empty:
                    continue

                st.markdown(f"**พรรค {party}**")
                fig11, axes11 = plt.subplots(1, 2, figsize=(12, max(3, TOP_UNIT * 1.2)))
                fig11.suptitle(f"พรรค {party}", fontweight="bold")

                if not own.empty:
                    own = own.dropna(subset=["ตำบล", "หน่วย"]).reset_index(drop=True)
                    vals = own["margin_pct"] * 100
                    axes11[0].barh(own["ตำบล"] + " หน่วย " + own["หน่วย"].astype(str), vals, color="#457b9d")
                    axes11[0].set_xlim(0, vals.max() * 1.2 if len(vals) else 1)
                axes11[0].set_xlabel("Margin (%)")
                axes11[0].set_title(f"Top {TOP_UNIT} ฐานเสียงแข็ง")

                if not lost.empty:
                    lost = lost.dropna(subset=["ตำบล", "หน่วย"]).reset_index(drop=True)
                    vals2 = lost["margin_pct"] * 100
                    axes11[1].barh(lost["ตำบล"] + " หน่วย " + lost["หน่วย"].astype(str), vals2, color="#e63946")
                    axes11[1].set_xlim(0, vals2.max() * 1.2 if len(vals2) else 1)
                axes11[1].set_xlabel("Margin (%)")
                axes11[1].set_title(f"Top {TOP_UNIT} พื้นที่แพ้ห่างที่สุด")

                plt.tight_layout()
                st.pyplot(fig11)
                plt.close(fig11)
