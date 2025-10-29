# app.py
# ShopImpact - Full-screen neon backgrounds, subtle transitions, full-screen pulse & floating icons
# Deploy on Streamlit Cloud (share.streamlit.io) from GitHub - no installs needed locally

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import date
import io, base64, random
from textwrap import shorten
import uuid

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

# different neon palettes per page (animated gradients)
NEON_THEMES = {
    "Add Purchase": {
        "name": "Magenta-Violet",
        "gradients": [
            ("#ff007f", "#7c4dff"),
            ("#ff5f7e", "#8a2be2"),
            ("#ff007f", "#00e5ff")
        ],
        "floating": ["#ff007f","#7c4dff","#00e5ff"]
    },
    "Dashboard": {
        "name": "Electric Green",
        "gradients": [
            ("#001f3f", "#004d7a"),
            ("#39ff14", "#0ff0fc"),
            ("#00ffaa", "#39ff14")
        ],
        "floating": ["#39ff14","#00ffaa","#0ff0fc"]
    },
    "History & Export": {
        "name": "Hot Neon",
        "gradients": [
            ("#2b0032", "#6a0572"),
            ("#ff073a", "#ff6ec7"),
            ("#ff9b00", "#ff073a")
        ],
        "floating": ["#ff073a","#ff6ec7","#ff9b00"]
    },
    "Settings & About": {
        "name": "Calm Neon",
        "gradients": [
            ("#011627", "#2f3c7e"),
            ("#ffd400", "#ff6b6b"),
            ("#7bffb2", "#ffd400")
        ],
        "floating": ["#ffd400","#ff6b6b","#7bffb2"]
    }
}

# ----------------------
# Session state
# ----------------------
if "purchases" not in st.session_state:
    st.session_state.purchases = []
if "last_pulse_id" not in st.session_state:
    st.session_state.last_pulse_id = None

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
# CSS: full-screen animated backgrounds, subtle fade-in transitions, full-screen pulse & floats
# ----------------------
def page_css(theme_name):
    theme = NEON_THEMES.get(theme_name, list(NEON_THEMES.values())[0])
    # create gradient sequence for CSS animation
    grads = theme['gradients']
    # prepare stops
    gradients_css = ", ".join([f"linear-gradient(120deg, {g[0]}, {g[1]})" for g in grads])
    # create keyframe steps using the colors
    kf = ""
    steps = len(grads)
    for i, g in enumerate(grads):
        pct = int((i/(steps-1))*100) if steps>1 else 100
        kf += f"{pct}% {{ background: linear-gradient(120deg, {g[0]}, {g[1]}); }}\n"
    css = f"""
    <style>
    /* make Streamlit main app full-bleed and remove default padding */
    .stApp {{
      padding: 0 !important;
      margin: 0 !important;
    }}
    /* top-level page container fills viewport */
    .page-wrap {{
      min-height: 100vh;
      width: 100%;
      position: relative;
      overflow: auto;
      display: flex;
      flex-direction: column;
      z-index: 1;
    }}
    /* animated neon background layer (full-screen) */
    .neon-bg {{
      position: fixed;
      inset: 0;
      z-index: 0;
      filter: contrast(1.05) saturate(1.2);
      background: linear-gradient(120deg, {grads[0][0]}, {grads[0][1]});
      background-size: 400% 400%;
      animation: neonBackground 18s linear infinite;
      opacity: 0.95;
      pointer-events: none;
    }}
    @keyframes neonBackground {{
      0% {{ background: linear-gradient(120deg, {grads[0][0]}, {grads[0][1]}); }}
      33% {{ background: linear-gradient(120deg, {grads[1%len(grads)][0]}, {grads[1%len(grads)][1]}); }}
      66% {{ background: linear-gradient(120deg, {grads[(2)%len(grads)][0]}, {grads[(2)%len(grads)][1]}); }}
      100% {{ background: linear-gradient(120deg, {grads[0][0]}, {grads[0][1]}); }}
    }}

    /* subtle fade-in when page loads */
    .page-content {{
      position: relative;
      z-index: 2;
      padding: 28px 40px;
      animation: pageFade 0.9s ease-in-out both;
    }}
    @keyframes pageFade {{
      0% {{ opacity: 0; transform: translateY(10px); filter: blur(3px); }}
      100% {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}

    /* full-screen pulse overlay used on add */
    .neon-pulse-full {{
      position: fixed;
      inset: 0;
      z-index: 3;
      display: none;
      pointer-events: none;
      mix-blend-mode: screen;
    }}
    .neon-pulse-full.active {{
      display: block;
      animation: fullPulse 1s ease-out 1;
      background: radial-gradient(circle at 50% 40%, rgba(255,255,255,0.06), rgba(255,255,255,0) 20%),
                  radial-gradient(circle at 10% 80%, rgba(255,255,255,0.02), rgba(255,255,255,0) 10%);
    }}
    @keyframes fullPulse {{
      0% {{ opacity: 0; filter: blur(0); transform: scale(1); }}
      30% {{ opacity: 1; filter: blur(6px); transform: scale(1.015); }}
      100% {{ opacity: 0; filter: blur(0); transform: scale(1); }}
    }}

    /* floating icons across full viewport */
    .float-layer {{
      position: fixed;
      inset: 0;
      z-index: 4;
      pointer-events: none;
      overflow: visible;
    }}
    .float-item {{
      position: absolute;
      font-size: 36px;
      text-shadow: 0 6px 18px rgba(0,0,0,0.6);
      animation: floatUpViewport 4.5s linear forwards;
      will-change: transform, opacity;
    }}
    @keyframes floatUpViewport {{
      0% {{ transform: translateY(40vh) scale(0.9); opacity: 1; }}
      100% {{ transform: translateY(-30vh) scale(1.1); opacity: 0; }}
    }}

    /* basic card styling on top content to keep text readable */
    .card {{
      background: rgba(0,0,0,0.22);
      border-radius: 12px;
      padding: 16px;
      border: 1px solid rgba(255,255,255,0.06);
      box-shadow: 0 8px 30px rgba(0,0,0,0.45);
      color: white;
    }}
    .title {{
      font-size: 40px;
      font-weight: 900;
      color: white;
      text-shadow: 0 0 14px rgba(255,255,255,0.06);
    }}
    .subtitle {{
      font-size: 16px;
      color: rgba(255,255,255,0.9);
      margin-bottom: 8px;
    }}
    .big-input {{ font-size:18px; padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.02); color: #fff; width:100%; }}
    .big-button {{ font-size:18px; padding:10px 18px; border-radius:10px; border:none; cursor:pointer; background: rgba(255,255,255,0.96); color: #111; font-weight:700; box-shadow: 0 10px 30px rgba(0,0,0,0.45); }}
    /* small responsive tweaks */
    @media (max-width: 800px) {{
      .page-content {{ padding: 18px 14px; }}
      .title {{ font-size: 32px; }}
      .float-item {{ font-size: 26px; }}
    }}
    </style>
    """
    return css

# ----------------------
# Helper to spawn full-screen floats and pulse HTML
# ----------------------
def render_fullscreen_effect(theme_name, intensity=14):
    theme = NEON_THEMES.get(theme_name)
    colors = theme['floating']
    # unique id to avoid caching issues
    uid = uuid.uuid4().hex[:8]
    floats_html = f"<div id='floatlayer_{uid}' class='float-layer'>"
    icons = ["🌱","💚","🌿","🌎","✨","💫","🪴","⚡","🌸"]
    for i in range(intensity):
        ico = random.choice(icons)
        left = random.randint(2,92)
        delay = round(random.random()*0.8,2)
        dur = round(3.6 + random.random()*1.6,2)
        color = random.choice(colors)
        size = random.randint(28,52)
        floats_html += f"<div class='float-item' style='left:{left}%; bottom:10vh; animation-delay:{delay}s; animation-duration:{dur}s; color:{color}; font-size:{size}px'>{ico}</div>"
    floats_html += "</div>"
    pulse_html = f"<div id='pulse_{uid}' class='neon-pulse-full active'></div>"
    st.markdown(floats_html + pulse_html, unsafe_allow_html=True)
    # store last pulse id so we can manage re-runs if needed
    st.session_state.last_pulse_id = uid

# ----------------------
# Layout & navigation
# ----------------------
st.markdown(page_css("Add Purchase"), unsafe_allow_html=True)  # inject CSS (themes will animate; CSS uses the gradients defined)
st.markdown("<div class='neon-bg'></div>", unsafe_allow_html=True)  # background layer (CSS animates)

# Sidebar & header
st.sidebar.markdown("# 🔮 ShopImpact")
page = st.sidebar.radio("Navigate:", ["Add Purchase", "Dashboard", "History & Export", "Settings & About"])
q_src, q_text = sample_quote()
st.sidebar.markdown(f"**Quote:** _{shorten(q_text, width=100)}_ — *{q_src}*")

# page wrapper
st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
st.markdown("<div class='page-content'>", unsafe_allow_html=True)

# header area
st.markdown("<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'>"
            "<div><div class='title'>ShopImpact</div><div class='subtitle'>Conscious shopping made colourful</div></div>"
            "<div style='text-align:right'><img src='https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Emoji_u1f331.svg/512px-Emoji_u1f331.svg.png' width='56' /></div>"
            "</div>", unsafe_allow_html=True)

# ----------------------
# PAGE: Add Purchase (big full-screen neon page)
# ----------------------
if page == "Add Purchase":
    # Add Purchase uses its own theme - re-inject CSS so neon-bg uses Add Purchase palette
    st.markdown(page_css("Add Purchase"), unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='margin-bottom:20px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                f"<div style='font-size:28px;font-weight:800'>Add Purchase — Big Stage</div>"
                f"<div style='font-size:14px;color:rgba(255,255,255,0.85)'>Theme: {NEON_THEMES['Add Purchase']['name']}</div>"
                f"</div></div>", unsafe_allow_html=True)

    with st.form("big_purchase_form", clear_on_submit=False):
        c1, c2 = st.columns([2,1])
        with c1:
            product_type = st.selectbox("Product category", options=list(MULTIPLIERS.keys()), key="ap_prod")
            product_name = st.text_input("Product name", max_chars=80, key="ap_name", placeholder="e.g. Running Shoes / Cotton T-Shirt")
            brand = st.text_input("Brand (required)", max_chars=60, key="ap_brand", placeholder="Type the brand name (required)")
            price = st.number_input("Price", min_value=0.0, step=0.5, format="%.2f", key="ap_price")
            pd_date = st.date_input("Purchase date", value=date.today(), key="ap_date")
            eco_brand = st.checkbox("Eco / ethical brand", key="ap_eco")
        with c2:
            st.markdown("### Inspirations & Quotes")
            qlist = random.sample(QUOTES, k=4 if len(QUOTES)>=4 else len(QUOTES))
            for qsrc, qtxt in qlist:
                st.markdown(f"> _{shorten(qtxt, width=110)}_ — *{qsrc}*")
            st.markdown("---")
            st.markdown("### Suggestions")
            for s in SUGGESTIONS.get(product_type, ["Consider lower-impact choices"]):
                st.markdown(f"- {s}")
        submitted = st.form_submit_button("Add purchase ✨")

    if submitted:
        if not brand or brand.strip() == "":
            st.error("Brand is required. Please type the brand name to add your purchase.")
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
            # render full screen pulse + floats
            render_fullscreen_effect("Add Purchase", intensity=18)
            # show badge text
            if eco_brand or multiplier <= 0.03:
                st.markdown("<h3 style='color:#fff'>NEON ECO BADGE 🌿 — Great choice!</h3>", unsafe_allow_html=True)
            else:
                if impact < 10:
                    st.markdown("<h3 style='color:#fff'>Small footprint — Nice!</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("<h3 style='color:#fff'>Consider greener options ✨</h3>", unsafe_allow_html=True)

# ----------------------
# PAGE: Dashboard
# ----------------------
elif page == "Dashboard":
    st.markdown(page_css("Dashboard"), unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='margin-bottom:14px'><div style='font-size:24px;font-weight:800'>Dashboard — {NEON_THEMES['Dashboard']['name']}</div>"
                f"<div style='font-size:13px;color:rgba(255,255,255,0.85)'>Monthly summaries, badges & charts</div></div>", unsafe_allow_html=True)
    df = purchases_df()
    if df.empty:
        st.warning("No purchases yet — use Add Purchase to start logging items.")
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
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(8,3))
        ax2.plot(summary['month'], summary['total_impact'], marker='o', color="#0ff0fc")
        ax2.set_title("Monthly CO₂ Impact")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        latest = summary.iloc[-1] if not summary.empty else None
        if latest is not None:
            badge, msg = badge_for_month(latest['total_impact'])
            st.markdown(f"### Badge for {latest['month']}: **{badge}**")
            st.markdown(f"> {msg}")

# ----------------------
# PAGE: History & Export
# ----------------------
elif page == "History & Export":
    st.markdown(page_css("History & Export"), unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='margin-bottom:14px'><div style='font-size:24px;font-weight:800'>History & Export — {NEON_THEMES['History & Export']['name']}</div>"
                f"<div style='font-size:13px;color:rgba(255,255,255,0.85)'>Filter, download CSV, and quick reports</div></div>", unsafe_allow_html=True)
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

# ----------------------
# PAGE: Settings & About
# ----------------------
elif page == "Settings & About":
    st.markdown(page_css("Settings & About"), unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='margin-bottom:14px'><div style='font-size:24px;font-weight:800'>Settings & About — {NEON_THEMES['Settings & About']['name']}</div>"
                f"<div style='font-size:13px;color:rgba(255,255,255,0.85)'>Edit multipliers and learn how the app works</div></div>", unsafe_allow_html=True)
    st.markdown("""
    **What is ShopImpact?**  
    A colourful, immersive app that estimates environmental impact of purchases and encourages greener choices.

    **How to use**  
    1. Add purchases on the big Add Purchase page (brand is required).  
    2. Explore Dashboard & History for charts and exports.  
    3. Deploy to Streamlit Cloud and include the live link in your submission.
    """, unsafe_allow_html=True)

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

# close wrappers
st.markdown("</div>", unsafe_allow_html=True)  # page-content
st.markdown("</div>", unsafe_allow_html=True)  # page-wrap

# If a pulse id exists (recent), add a small invisible element to keep it stable (no action)
if st.session_state.get("last_pulse_id"):
    pass

# footer
st.markdown("<div style='text-align:center;color:rgba(255,255,255,0.85);padding:18px 0'>Made with neon love 💖 — ask me if you want auto screenshots or PDF report next.</div>", unsafe_allow_html=True)
