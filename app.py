# app.py
# ShopImpact - Vibrant multi-page Streamlit app with subtle transitions and neon themes
# Deploy on Streamlit Cloud (share.streamlit.io) from GitHub

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import date
import io, base64, random
from textwrap import shorten

st.set_page_config(page_title="ShopImpact", layout="wide", initial_sidebar_state="expanded")

# ----------------------
# Core configuration
# ----------------------
MULTIPLIERS = {
    "Clothing (Fast Fashion)": 0.12,
    "Clothing (Sustainable/Second-Hand)": 0.03,
    "Footwear (Leather)": 0.20,
    "Footwear (Synthetic)": 0.14,
    "Electronics": 0.35,
    "Groceries (Packaged)": 0.08,
    "Groceries (Fresh/Local)": 0.02,
    "Personal Care": 0.06,
    "Furniture": 0.25,
    "Beverages (Single-Use Bottle)": 0.09,
    "Books & Stationery": 0.02,
    "Home Appliances": 0.30,
    "Other": 0.10
}

SUGGESTIONS = {
    "Clothing (Fast Fashion)": ["Buy second-hand", "Choose organic cotton", "Rent for events"],
    "Clothing (Sustainable/Second-Hand)": ["Great choice! Try mending & care tips"],
    "Footwear (Leather)": ["Look for vegetable-tanned leather or recycled materials"],
    "Footwear (Synthetic)": ["Try locally made or recycled material brands"],
    "Electronics": ["Buy refurbed, repairable models"],
    "Groceries (Packaged)": ["Choose loose produce, bring reusable bags"],
    "Groceries (Fresh/Local)": ["Support local farmers markets"],
    "Personal Care": ["Refillable or solid bars (shampoo bars)"],
    "Furniture": ["Consider preloved or sustainably sourced wood"],
    "Beverages (Single-Use Bottle)": ["Use reusable bottle or buy bulk"],
    "Books & Stationery": ["Buy digital or second-hand books"],
    "Home Appliances": ["Choose energy star rated"],
    "Other": ["Search for lower-impact alternatives"]
}

QUOTES = [
    ("Avatar (2009)", "Everything is backwards now, like out there is the true world, and in here is the dream."),
    ("Greta Thunberg", "I want you to act as if the house is on fire, because it is."),
    ("Wall-E (2008)", "If you don't take care of the world, it won't be there for you to live in."),
    ("David Attenborough", "An understanding of the natural world is a source of great fulfillment."),
    ("Interstellar (2014)", "We used up the Earth's resources a long time ago."),
    ("Jane Goodall", "What you do makes a difference."),
    ("The Lorax (Dr. Seuss)", "Unless someone like you cares a whole awful lot, nothing is going to get better."),
    ("Leonardo DiCaprio", "Climate change is real. It is happening right now."),
    ("Wangari Maathai", "It's the little things citizens do that will make the difference."),
    ("Chief Seattle", "We do not inherit the Earth from our ancestors; we borrow it from our children."),
    ("Wendell Berry", "Wealth consists not in having great possessions, but in having few wants."),
    ("Ralph Waldo Emerson", "What lies behind us and what lies before us are tiny matters compared to what lies within us.")
]

NEON_THEMES = {
    "Add Purchase": {
        "bg1": "#0f0c29", "bg2": "#302b63", "accent": "#ff007f", "accent2": "#7c4dff", "floating": ["#ff007f","#7c4dff","#00e5ff"]
    },
    "Dashboard": {
        "bg1": "#001f3f", "bg2": "#004d7a", "accent": "#39ff14", "accent2": "#0ff0fc", "floating": ["#39ff14","#00ffaa","#0ff0fc"]
    },
    "History & Export": {
        "bg1": "#2b0032", "bg2": "#6a0572", "accent": "#ff073a", "accent2": "#ff6ec7", "floating": ["#ff073a","#ff6ec7","#ff9b00"]
    },
    "Settings & About": {
        "bg1": "#011627", "bg2": "#2f3c7e", "accent": "#ffd400", "accent2": "#ff6b6b", "floating": ["#ffd400","#ff6b6b","#7bffb2"]
    }
}

# ----------------------
# Session state
# ----------------------
if "purchases" not in st.session_state:
    st.session_state.purchases = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------
# Utilities
# ----------------------
def calculate_impact(price, multiplier):
    return round(price * multiplier, 2)

def add_purchase(entry):
    st.session_state.purchases.append(entry)

def purchases_df():
    if not st.session_state.purchases:
        return pd.DataFrame(columns=["date","product_type","product_name","brand","price","impact","eco_brand"])
    return pd.DataFrame(st.session_state.purchases)

def month_key(dt):
    return pd.to_datetime(dt).strftime("%Y-%m")

def summary_by_month(df):
    if df.empty:
        return pd.DataFrame(columns=["month","count","total_spend","total_impact"])
    df['month'] = pd.to_datetime(df['date']).apply(lambda d: d.strftime("%Y-%m"))
    grouped = df.groupby('month').agg(count=('product_name','count'), total_spend=('price','sum'), total_impact=('impact','sum')).reset_index()
    return grouped.sort_values('month')

def badge_for_month(impact):
    if impact <= 50:
        return ("Eco Saver — Neon Leaf", "Tiny footprint! Exceptional 🌿")
    if impact <= 150:
        return ("Green Shopper — Neon Bronze", "Very good! Keep going 🌱")
    if impact <= 300:
        return ("Conscious Shopper — Neon Silver", "Nice effort! You're making progress 🍃")
    return ("Eco Advocate — Neon Gold", "You're conscious — aim for smaller steps too 🌎")

def create_download_csv(df):
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f"data:file/csv;base64,{b64}"
    return href

def sample_quote():
    return random.choice(QUOTES)

# ----------------------
# CSS: neon + subtle fade-in + animations
# ----------------------
def neon_css_for(page_name):
    theme = NEON_THEMES.get(page_name, list(NEON_THEMES.values())[0])
    css = f"""
    <style>
    :root {{
      --bg1: {theme['bg1']};
      --bg2: {theme['bg2']};
      --accent1: {theme['accent']};
      --accent2: {theme['accent2']};
    }}
    .neon-page {{
      background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
      color: white;
      padding: 1.2rem;
      border-radius: 14px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }}
    .fade-in {{
      animation: fadeInSubtle 0.9s ease-in forwards;
      opacity: 0;
    }}
    @keyframes fadeInSubtle {{
      0% {{opacity: 0; transform: translateY(10px); filter: blur(3px);}}
      100% {{opacity: 1; transform: translateY(0); filter: blur(0);}}
    }}
    .neon-title {{
      font-size: 44px;
      font-weight: 900;
      letter-spacing: 1px;
      color: var(--accent1);
      text-shadow: 0 0 12px var(--accent1), 0 0 28px var(--accent2);
    }}
    .neon-sub {{
      font-size: 18px;
      color: #e6e6e6;
      margin-bottom: 10px;
    }}
    .neon-card {{
      background: rgba(255,255,255,0.03);
      padding: 1rem;
      border-radius: 12px;
      margin-bottom: 12px;
      border: 1px solid rgba(255,255,255,0.06);
    }}
    .neon-pulse {{
      position: relative;
      z-index: 10;
      width: 100%;
      height: 220px;
      border-radius: 14px;
      background: radial-gradient(circle at 20% 20%, rgba(255,255,255,0.02), transparent 20%),
                  radial-gradient(circle at 80% 80%, rgba(255,255,255,0.02), transparent 20%),
                  linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      overflow: hidden;
      box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }}
    .neon-pulse.active {{
      animation: neonGlowSubtle 1.2s ease-in-out 1;
    }}
    @keyframes neonGlowSubtle {{
      0% {{ box-shadow: 0 0 6px rgba(255,255,255,0); transform: scale(1); filter: saturate(1); }}
      30% {{ box-shadow: 0 0 36px var(--accent1); transform: scale(1.015); filter: saturate(1.25); }}
      70% {{ box-shadow: 0 0 56px var(--accent2); transform: scale(1.008); filter: saturate(1.35); }}
      100% {{ box-shadow: 0 0 6px rgba(255,255,255,0); transform: scale(1); filter: saturate(1); }}
    }}
    .float-area {{
      position: relative;
      height: 0;
      overflow: visible;
      pointer-events: none;
    }}
    .float-icon {{
      position: absolute;
      font-size: 28px;
      opacity: 0.95;
      text-shadow: 0 0 10px rgba(0,0,0,0.6);
      animation: floatUpSubtle 4s linear forwards;
      will-change: transform, opacity;
    }}
    @keyframes floatUpSubtle {{
      0% {{ transform: translateY(0) scale(1); opacity: 1; }}
      100% {{ transform: translateY(-260px) scale(1.15); opacity: 0; }}
    }}
    .big-input {{ font-size:18px; padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.02); color: #fff; }}
    .big-button {{ font-size:18px; padding:10px 18px; border-radius:10px; border:none; cursor:pointer; background: linear-gradient(90deg, var(--accent1), var(--accent2)); color: #001; font-weight:700; box-shadow: 0 8px 30px rgba(0,0,0,0.5); }}
    </style>
    """
    return css

# ----------------------
# Layout & navigation
# ----------------------
st.markdown("<style>body {margin: 0; padding: 0;}</style>", unsafe_allow_html=True)
st.sidebar.markdown("# 🔮 ShopImpact")
page = st.sidebar.radio("Navigate:", ["Add Purchase", "Dashboard", "History & Export", "Settings & About"])
q_src, q_text = sample_quote()
st.sidebar.markdown(f"**Quote:** _{shorten(q_text, width=100)}_ — *{q_src}*")

# header
st.markdown("<br/>", unsafe_allow_html=True)
hcol = st.columns([3,1])
with hcol[0]:
    st.markdown(f"<div style='display:flex;align-items:center;gap:18px'> <div style='font-size:28px;font-weight:900'>ShopImpact</div> <div style='color:#ddd'>— Conscious Shopping</div></div>", unsafe_allow_html=True)
with hcol[1]:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Emoji_u1f331.svg/512px-Emoji_u1f331.svg.png", width=56)
st.markdown("---")

# ----------------------
# Page: Add Purchase (big + neon + animations)
# ----------------------
if page == "Add Purchase":
    theme = NEON_THEMES['Add Purchase']
    st.markdown(neon_css_for("Add Purchase"), unsafe_allow_html=True)

    st.markdown("<div class='neon-page fade-in'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;justify-content:space-between;align-items:center'>"
                "<div><div class='neon-title'>Add Purchase — Big Stage</div>"
                "<div class='neon-sub'>Huge form, subtle neon pulse & floating icons. Brand is <b>required</b>.</div></div>"
                f"<div style='text-align:right'><div style='font-size:14px;color:#fff'>Neon Theme: Magenta & Violet</div></div></div>",
                unsafe_allow_html=True)

    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    with st.form("big_purchase_form", clear_on_submit=False):
        c1, c2 = st.columns([2,1])
        with c1:
            st.markdown("**Select Product Category**")
            product_type = st.selectbox("", options=list(MULTIPLIERS.keys()), key="ap_prod")
            st.markdown("**Product name**")
            product_name = st.text_input("", max_chars=80, key="ap_name", placeholder="e.g. Running Shoes / Cotton T-Shirt")
            st.markdown("**Brand (required)**")
            brand = st.text_input("", max_chars=60, key="ap_brand", placeholder="Type the brand name (required)")
            st.markdown("**Price**")
            price = st.number_input("", min_value=0.0, step=0.5, format="%.2f", key="ap_price")
            st.markdown("**Purchase date**")
            pd_date = st.date_input("", value=date.today(), key="ap_date")
            st.markdown("**Is this an eco / ethical brand?**")
            eco_brand = st.checkbox("Yes — eco / ethical brand", key="ap_eco")
        with c2:
            st.markdown("### Quick feelings & quotes")
            qlist = random.sample(QUOTES, k=3 if len(QUOTES)>=3 else len(QUOTES))
            for qsrc, qtxt in qlist:
                st.markdown(f"> _{shorten(qtxt, width=110)}_ — *{qsrc}*")
            st.markdown("---")
            st.markdown("### Suggestions")
            suggestions = SUGGESTIONS.get(product_type, ["Consider lower-impact choices"])
            for s in suggestions:
                st.markdown(f"- {s}")

        submit = st.form_submit_button("Add purchase ✨")

    if submit:
        if not brand or brand.strip() == "":
            st.error("Please enter the brand name — it is required for submission.")
        else:
            multiplier = MULTIPLIERS.get(product_type, MULTIPLIERS["Other"])
            impact = calculate_impact(price, multiplier)
            entry = {
                "date": pd_date.isoformat(),
                "product_type": product_type,
                "product_name": product_name if product_name else "—",
                "brand": brand.strip(),
                "price": float(price),
                "impact": float(impact),
                "eco_brand": bool(eco_brand)
            }
            add_purchase(entry)
            st.success(f"Added: {product_type} — estimated impact ≈ {impact} CO₂ units")
            st.info("Suggestion: " + " · ".join(SUGGESTIONS.get(product_type, ["Consider lower-impact choices"])))

            # subtle neon pulse
            st.markdown("<div class='neon-pulse active'></div>", unsafe_allow_html=True)

            # floating icons
            floats_html = "<div class='float-area' style='height:120px;margin-top:10px;'>"
            icons = ["🌱","💚","🌿","🌎","✨","💫","🪴"]
            colors = theme['floating']
            for i in range(14):
                ico = random.choice(icons)
                left = random.randint(4,92)
                delay = round(random.random()*1.0,2)
                dur = round(3.0 + random.random()*1.6,2)
                color = random.choice(colors)
                size = random.randint(22,36)
                floats_html += f"<div class='float-icon' style='left:{left}%; bottom:8px; animation-delay:{delay}s; animation-duration:{dur}s; color:{color}; font-size:{size}px'>{ico}</div>"
            floats_html += "</div>"
            st.markdown(floats_html, unsafe_allow_html=True)

            # small neon badge message
            if eco_brand or multiplier <= 0.03:
                st.markdown("<h3 style='color:var(--accent1);text-shadow:0 0 14px var(--accent1)'>NEON ECO BADGE 🌿</h3>", unsafe_allow_html=True)
            else:
                if impact < 10:
                    st.markdown("<h3 style='color:var(--accent2);text-shadow:0 0 12px var(--accent2)'>Small footprint — Nice!</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("<h3 style='color:var(--accent2);text-shadow:0 0 12px var(--accent2)'>Consider greener options ✨</h3>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------
# Page: Dashboard
# ----------------------
elif page == "Dashboard":
    st.markdown(neon_css_for("Dashboard"), unsafe_allow_html=True)
    st.markdown("<div class='neon-page fade-in'>", unsafe_allow_html=True)
    st.markdown("<div class='neon-title'>Dashboard — Electric Green</div>", unsafe_allow_html=True)
    st.markdown("<div class='neon-sub'>Monthly summaries, badges & colourful charts.</div>", unsafe_allow_html=True)

    df = purchases_df()
    if df.empty:
        st.warning("No purchases yet — go to Add Purchase and enter items to see neon charts.")
    else:
        total_spend = df['price'].sum()
        total_impact = df['impact'].sum()
        total_count = len(df)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total spend", f"{total_spend:.2f}")
        c2.metric("Total purchases", f"{total_count}")
        c3.metric("Total estimated CO₂", f"{total_impact:.2f}")
        c4.metric("Avg impact/item", f"{(total_impact/total_count if total_count else 0):.2f}")

        summary = summary_by_month(df)
        st.markdown("### Monthly summary")
        st.dataframe(summary, use_container_width=True)

        st.markdown("### Visualisations")
        fig1, ax1 = plt.subplots(figsize=(8,3))
        ax1.bar(summary['month'], summary['total_spend'], color="#39ff14")
        ax1.set_title("Monthly Spend")
        ax1.set_ylabel("Spend")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(8,3))
        ax2.plot(summary['month'], summary['total_impact'], marker='o', color="#0ff0fc")
        ax2.set_title("Monthly CO₂ Impact")
        ax2.set_ylabel("Estimated CO₂ units")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        latest = summary.iloc[-1] if not summary.empty else None
        if latest is not None:
            badge, msg = badge_for_month(latest['total_impact'])
            st.markdown(f"### Badge for {latest['month']}: **{badge}**")
            st.markdown(f"> {msg}")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------
# Page: History & Export
# ----------------------
elif page == "History & Export":
    st.markdown(neon_css_for("History & Export"), unsafe_allow_html=True)
    st.markdown("<div class='neon-page fade-in'>", unsafe_allow_html=True)
    st.markdown("<div class='neon-title'>History & Export — Hot Neon</div>", unsafe_allow_html=True)
    st.markdown("<div class='neon-sub'>See everything, filter, and download CSV or a quick report image.</div>", unsafe_allow_html=True)

    df = purchases_df()
    if df.empty:
        st.info("No purchases yet.")
    else:
        st.dataframe(df, use_container_width=True)
        months = sorted(list({month_key(r['date']) for r in st.session_state.purchases}), reverse=True)
        sel_month = st.selectbox("Select month (or 'All')", options=["All"] + months)
        sel_cat = st.selectbox("Select category (or 'All')", options=["All"] + list(MULTIPLIERS.keys()))
        filtered = df.copy()
        if sel_month != "All":
            filtered = filtered[filtered['date'].apply(lambda d: month_key(d)==sel_month)]
        if sel_cat != "All":
            filtered = filtered[filtered['product_type']==sel_cat]
        st.dataframe(filtered, use_container_width=True)

        csv = filtered.to_csv(index=False).encode()
        st.download_button("Download filtered CSV", data=csv, file_name="shopimpact_history.csv", mime="text/csv")
        href = create_download_csv(filtered)
        st.markdown(f"[Direct CSV export]({href})")

        st.markdown("#### Create Quick Visual Report")
        if st.button("Create Report Image"):
            fig, ax = plt.subplots(figsize=(8,6))
            ax.axis('off')
            text = f"ShopImpact Quick Report\\n\\nTotal items: {len(filtered)}\\nTotal spend: {filtered['price'].sum():.2f}\\nTotal impact: {filtered['impact'].sum():.2f}\\n\\nTop categories:\\n"
            topcats = filtered.groupby('product_type').agg(total_impact=('impact','sum')).reset_index().sort_values('total_impact', ascending=False).head(3)
            for i,row in topcats.iterrows():
                text += f" - {row['product_type']}: {row['total_impact']:.2f}\\n"
            ax.text(0,0.9, text, fontsize=12, family='monospace')
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches='tight')
            buf.seek(0)
            st.image(buf)
            st.download_button("Download report image", data=buf, file_name="shopimpact_report.png")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------
# Page: Settings & About
# ----------------------
elif page == "Settings & About":
    st.markdown(neon_css_for("Settings & About"), unsafe_allow_html=True)
    st.markdown("<div class='neon-page fade-in'>", unsafe_allow_html=True)
    st.markdown("<div class='neon-title'>Settings & About — Calm Neon</div>", unsafe_allow_html=True)
    st.markdown("<div class='neon-sub'>Change multipliers, read about the app, and export guidelines for your assignment.</div>", unsafe_allow_html=True)

    st.markdown("""
    **What is ShopImpact?**  
    A colourful, encouraging app that estimates the environmental impact of purchases and nudges users toward greener choices.

    **How to use for your assignment**  
    1. Add many purchases (10–15) across categories using the big Add Purchase page.  
    2. Visit Dashboard and History for charts & export.  
    3. Push this repo to GitHub and deploy to Streamlit Cloud to get a live link.

    **Design notes**  
    - Each page uses a unique neon palette so the app feels multi-stage.  
    - Brand is required on the Add page for better data quality.  
    """)

    st.markdown("### Edit multipliers (session-only)")
    with st.form("mult_form"):
        edited = {}
        cols = st.columns(2)
        i = 0
        for k,v in MULTIPLIERS.items():
            with cols[i % 2]:
                newv = st.number_input(f"{k}", min_value=0.0, value=float(v), step=0.01, key=f"m_{k}")
                edited[k] = newv
            i += 1
        if st.form_submit_button("Save multipliers"):
            MULTIPLIERS.update(edited)
            st.success("Saved multipliers for this session (reload resets).")

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<br/><hr/><div style='text-align:center;color:#ddd'>Made with neon love 💖 — ask me to push to GitHub or deploy to Streamlit Cloud and I'll give exact click-by-click instructions.</div>", unsafe_allow_html=True)
