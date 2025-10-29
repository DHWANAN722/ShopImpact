# app.py
# ShopImpact - Vibrant Conscious Shopping Dashboard
# Designed for Streamlit
# Paste this file into your project root and run: streamlit run app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, date
import io
import base64
import random
from textwrap import shorten

st.set_page_config(
    page_title="ShopImpact — Conscious Shopping Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------
# Helper / configuration
# ----------------------
# Product categories and CO2 multipliers (example multipliers; intuitive mapping)
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

# Greener suggestions per product type
SUGGESTIONS = {
    "Clothing (Fast Fashion)": ["Buy second-hand", "Choose organic cotton brands", "Rent for events"],
    "Clothing (Sustainable/Second-Hand)": ["Great choice! Try mending & care tips"],
    "Footwear (Leather)": ["Look for vegetable-tanned leather or recycled materials"],
    "Footwear (Synthetic)": ["Try locally made or recycled material brands"],
    "Electronics": ["Buy refurbed, repairable models, choose energy efficient ones"],
    "Groceries (Packaged)": ["Choose loose produce, bring reusable bags"],
    "Groceries (Fresh/Local)": ["Support local farmers markets"],
    "Personal Care": ["Refillable or solid bars (shampoo bars)"],
    "Furniture": ["Consider preloved or sustainably sourced wood"],
    "Beverages (Single-Use Bottle)": ["Use reusable bottle or buy bulk"],
    "Books & Stationery": ["Buy digital or second-hand books"],
    "Home Appliances": ["Choose energy star rated"],
    "Other": ["Search for lower-impact alternatives"]
}

# Quotes - films & famous people (environmental / inspirational)
QUOTES = [
    ("From the movie 'Avatar'", "Everything is backwards now, like out there is the true world, and in here is the dream."),
    ("Greta Thunberg", "I want you to act as if the house is on fire, because it is."),
    ("From the movie 'Wall-E'", "If you don't take care of the world, it won't be there for you to live in."),
    ("David Attenborough", "An understanding of the natural world and what's in it is a source of not only a great curiosity but great fulfillment."),
    ("From the movie 'Erin Brockovich'", "I can't go into that house and live with the creature."),
    ("Leonardo DiCaprio", "Climate change is real. It is happening right now."),
    ("From the movie 'Interstellar'", "We used up the Earth's resources a long time ago."),
    ("Jane Goodall", "What you do makes a difference, and you have to decide what kind of difference you want to make."),
    ("From the movie 'The Lorax'", "Unless someone like you cares a whole awful lot, nothing is going to get better. It's not."),
    ("Wangari Maathai", "It's the little things citizens do. That's what will make the difference.")
]

# Colors & theme
APP_BG = "#F7FFF7"  # soft mint
ACCENT = "#2E8B57"  # sea green
SECOND_ACCENT = "#FFC857"  # warm yellow
TEXT_COLOR = "#013220"  # dark green

# ----------------------
# Session state setup
# ----------------------
if "purchases" not in st.session_state:
    st.session_state.purchases = []  # list of dicts
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------
# Utility functions
# ----------------------
def calculate_impact(price, multiplier):
    # Impact (a simple estimate): price * multiplier => convert to "CO2 units"
    # Round to two decimals
    return round(price * multiplier, 2)

def add_purchase(entry):
    st.session_state.purchases.append(entry)

def purchases_df():
    if not st.session_state.purchases:
        return pd.DataFrame(columns=["date","product_type","product_name","brand","price","impact","eco_brand"])
    return pd.DataFrame(st.session_state.purchases)

def month_key(dt: date):
    return dt.strftime("%Y-%m")

def summary_by_month(df):
    if df.empty:
        return pd.DataFrame(columns=["month","count","total_spend","total_impact"])
    df['month'] = df['date'].apply(lambda d: month_key(pd.to_datetime(d)))
    grouped = df.groupby('month').agg(
        count=('product_name','count'),
        total_spend=('price','sum'),
        total_impact=('impact','sum')
    ).reset_index()
    return grouped.sort_values('month')

def badge_for_month(impact):
    # fun rules for badges (you can tune thresholds)
    if impact <= 50:
        return ("Eco Saver — Leaf Crown", "Amazing! Tiny footprint 🌿")
    if impact <= 150:
        return ("Green Shopper — Bronze Leaf", "Very good! Keep choosing greener options 🌱")
    if impact <= 300:
        return ("Conscious Shopper — Silver Leaf", "Nice effort! You're making progress 🍃")
    return ("Eco Advocate — Golden Leaf", "You're conscious — aim for smaller steps too 🌎")

def create_download_csv(df):
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f"data:file/csv;base64,{b64}"
    return href

def draw_leaf_badge(figsize=(2,2)):
    # Create a small matplotlib leaf icon
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis('off')
    # leaf body
    leaf = patches.Ellipse((0.5,0.5), 0.7, 0.4, angle=-30, facecolor=ACCENT, edgecolor='darkgreen', lw=2)
    ax.add_patch(leaf)
    # vein
    ax.plot([0.5, 0.9], [0.5, 0.9], color='white', lw=2)
    ax.plot([0.5, 0.75], [0.5, 0.6], color='white', lw=1.5)
    plt.tight_layout()
    return fig

def draw_footprint(figsize=(2,2)):
    # small footprint-like shapes
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis('off')
    # big pad
    pad = patches.Circle((0.5,0.4), 0.25, facecolor='#5EAD8A', edgecolor='darkgreen', lw=2)
    ax.add_patch(pad)
    # toes
    positions = [(0.68,0.68),(0.5,0.78),(0.32,0.68)]
    for x,y in positions:
        t = patches.Circle((x,y), 0.06, facecolor='#5EAD8A', edgecolor='darkgreen', lw=1.5)
        ax.add_patch(t)
    plt.tight_layout()
    return fig

def draw_medal(figsize=(2,2)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis('off')
    circle = patches.Circle((0.5,0.6), 0.28, facecolor=SECOND_ACCENT, edgecolor='gold', lw=2)
    ax.add_patch(circle)
    star = patches.RegularPolygon((0.5,0.6), 5, 0.12, color=ACCENT)
    ax.add_patch(star)
    plt.tight_layout()
    return fig

def sample_quote():
    return random.choice(QUOTES)

# ----------------------
# Layout & Navigation
# ----------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, {APP_BG} 0%, #FFFDF2 100%);
        color: {TEXT_COLOR};
    }}
    .big-title {{
        font-size:42px; 
        font-weight:800;
        color: {ACCENT};
    }}
    .subtitle {{
        font-size:18px; 
        font-weight:600; 
        color: {TEXT_COLOR};
    }}
    .card {{
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    }}
    </style>
    """, unsafe_allow_html=True
)

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.markdown('<div class="big-title">ShopImpact</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Turn every purchase into a mindful step — colourful, playful, and data-friendly.</div>', unsafe_allow_html=True)
with col2:
    _,_, logo_col = st.columns([1,1,4])
    with logo_col:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Emoji_u1f331.svg/512px-Emoji_u1f331.svg.png", width=72)

st.markdown("---")

# Sidebar for navigation
st.sidebar.header("Navigate ShopImpact")
page = st.sidebar.radio("Go to:", ["Add Purchase", "Dashboard", "History & Export", "Settings & About"])

# small card: quote
q_src, q_text = sample_quote()
st.sidebar.markdown(f"**Quote 🎬 / 🌍**\n\n> _{q_text}_\n\n— *{q_src}*")

# ----------------------
# Page: Add Purchase
# ----------------------
if page == "Add Purchase":
    st.subheader("Add a new purchase 🛒")
    with st.form("purchase_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2,2,2])
        with c1:
            product_type = st.selectbox("Product category", options=list(MULTIPLIERS.keys()))
            product_name = st.text_input("Product name (optional)", max_chars=60)
        with c2:
            brand = st.text_input("Brand (optional)", max_chars=60)
            price = st.number_input("Price (in your currency)", min_value=0.0, step=0.5, format="%.2f")
        with c3:
            dt = st.date_input("Purchase date", value=date.today())
            eco_brand = st.checkbox("Is this an eco / ethical brand? (tick if yes)")
        submitted = st.form_submit_button("Add purchase ✨")

    if submitted:
        multiplier = MULTIPLIERS.get(product_type, MULTIPLIERS["Other"])
        impact = calculate_impact(price, multiplier)
        entry = {
            "date": dt.isoformat(),
            "product_type": product_type,
            "product_name": product_name if product_name else "—",
            "brand": brand if brand else "—",
            "price": float(price),
            "impact": float(impact),
            "eco_brand": bool(eco_brand)
        }
        add_purchase(entry)
        st.success(f"Added: {product_type} — impact ≈ {impact} CO₂ units")
        # show suggestion for greener alternatives
        suggestion_list = SUGGESTIONS.get(product_type, ["Consider lower-impact choices"])
        st.info("Suggestion: " + " · ".join(suggestion_list))
        # show a fun graphic for eco choices
        if eco_brand or (multiplier <= 0.03):
            st.markdown("### Great choice! Here's a tiny badge for you 🎖️")
            fig = draw_leaf_badge(figsize=(2.5,2.5))
            st.pyplot(fig)
        else:
            # show footprint graphic sometimes
            if impact < 10:
                st.markdown("### Small footprint — Nice!")
                fig = draw_footprint(figsize=(2.5,2.5))
                st.pyplot(fig)
            else:
                st.markdown("### Keep exploring greener options!")
                fig = draw_footprint(figsize=(2.5,2.5))
                st.pyplot(fig)

        # show a random quote
        q_src, q_text = sample_quote()
        st.caption(f"“{shorten(q_text, width=120)}” — {q_src}")

# ----------------------
# Page: Dashboard
# ----------------------
elif page == "Dashboard":
    st.subheader("Monthly Dashboard 📊 — colourful & clear")

    df = purchases_df()
    if df.empty:
        st.info("No purchases yet. Go to 'Add Purchase' to start adding items.")
    else:
        # quick KPIs
        total_spend = df['price'].sum()
        total_impact = df['impact'].sum()
        total_count = len(df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total spend", f"{total_spend:.2f}")
        col2.metric("Total purchases", f"{total_count}")
        col3.metric("Total estimated CO₂", f"{total_impact:.2f}")
        col4.metric("Average impact/item", f"{(total_impact/total_count if total_count else 0):.2f}")

        # monthly summary
        summary = summary_by_month(df)
        st.markdown("### Monthly summary")
        st.dataframe(summary, use_container_width=True)

        # charts
        st.markdown("### Visualisations")
        fig1, ax1 = plt.subplots(figsize=(8,3))
        ax1.bar(summary['month'], summary['total_spend'])
        ax1.set_title("Monthly Spend")
        ax1.set_ylabel("Spend")
        ax1.set_xlabel("Month")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(8,3))
        ax2.plot(summary['month'], summary['total_impact'], marker='o')
        ax2.set_title("Monthly CO₂ Impact")
        ax2.set_ylabel("Estimated CO₂ units")
        ax2.set_xlabel("Month")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        # badge awarding for the most recent month
        latest_month = summary.iloc[-1] if not summary.empty else None
        if latest_month is not None:
            month = latest_month['month']
            impact_val = latest_month['total_impact']
            badge_name, badge_msg = badge_for_month(impact_val)
            st.markdown(f"### Badge for {month}: **{badge_name}**")
            st.markdown(f"> {badge_msg}")
            # draw badge
            figb = draw_medal(figsize=(3,3))
            st.pyplot(figb)

        # eco breakdown by category
        st.markdown("### Impact by Product Category")
        cat = df.groupby('product_type').agg(total_impact=('impact','sum'), total_spend=('price','sum')).reset_index()
        fig3, ax3 = plt.subplots(figsize=(8,3))
        ax3.barh(cat['product_type'], cat['total_impact'])
        ax3.set_xlabel("Estimated CO₂ units")
        ax3.set_ylabel("Product type")
        ax3.set_title("Impact by Category")
        st.pyplot(fig3)

# ----------------------
# Page: History & Export
# ----------------------
elif page == "History & Export":
    st.subheader("All purchases history & export")
    df = purchases_df()
    if df.empty:
        st.info("No purchases yet.")
    else:
        # show table
        st.dataframe(df, use_container_width=True)

        # filters
        st.markdown("#### Filter history")
        months = sorted(list({month_key(pd.to_datetime(r['date'])) for r in st.session_state.purchases}), reverse=True)
        sel_month = st.selectbox("Select month (or 'All')", options=["All"] + months)
        sel_cat = st.selectbox("Select category (or 'All')", options=["All"] + list(MULTIPLIERS.keys()))
        filtered = df.copy()
        if sel_month != "All":
            filtered = filtered[filtered['date'].apply(lambda d: month_key(pd.to_datetime(d))==sel_month)]
        if sel_cat != "All":
            filtered = filtered[filtered['product_type']==sel_cat]
        st.dataframe(filtered, use_container_width=True)

        # download CSV
        csv = filtered.to_csv(index=False).encode()
        st.download_button("Download filtered CSV", data=csv, file_name="shopimpact_history.csv", mime="text/csv")

        # quick CSV link alternative
        href = create_download_csv(filtered)
        st.markdown(f"[Direct CSV export]({href})")

        # lightweight printable report (as PNG)
        st.markdown("#### Generate a quick visual report")
        if st.button("Create Report Image"):
            # simple image-like report using matplotlib
            fig, ax = plt.subplots(figsize=(8,6))
            ax.axis('off')
            text = f"ShopImpact Quick Report\n\nTotal items: {len(filtered)}\nTotal spend: {filtered['price'].sum():.2f}\nTotal impact: {filtered['impact'].sum():.2f}\n\nTop 3 categories:\n"
            topcats = filtered.groupby('product_type').agg(total_impact=('impact','sum')).reset_index().sort_values('total_impact', ascending=False).head(3)
            for i,row in topcats.iterrows():
                text += f" - {row['product_type']}: {row['total_impact']:.2f}\n"
            ax.text(0,0.9, text, fontsize=12, family='monospace')
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches='tight')
            buf.seek(0)
            st.image(buf)
            st.download_button("Download report image", data=buf, file_name="shopimpact_report.png")

# ----------------------
# Page: Settings & About
# ----------------------
elif page == "Settings & About":
    st.subheader("Settings & About ShopImpact 💚")
    st.markdown(
        """
        **What is this app?**  
        ShopImpact is a playful, educational app that helps you estimate the environmental impact of everyday purchases.  
        It uses simple multipliers (price × category multiplier) to estimate a CO₂-like score so you can compare and make choices.

        **Design notes:**  
        - Colourful, large text and friendly charts.  
        - Suggestions & badges to encourage greener choices.  
        - Export your history for assignment submission.

        **How to use for your assignment:**  
        1. Add 10-15 purchases across categories (try both high and low impact).  
        2. Visit Dashboard to see charts & badges.  
        3. Export CSV and include it in your GitHub repo.

        **Credits:** Built for your class assignment with love. 💖
        """
    )

    st.markdown("### Tweak multipliers (advanced)")
    with st.form("multipliers_form"):
        edited = {}
        cols = st.columns(2)
        i = 0
        for k, v in MULTIPLIERS.items():
            with cols[i % 2]:
                new_val = st.number_input(f"{k}", min_value=0.0, value=float(v), step=0.01, key=f"mult_{k}")
                edited[k] = new_val
            i += 1
        if st.form_submit_button("Save multipliers"):
            MULTIPLIERS.update(edited)
            st.success("Multipliers updated for this session (won't persist across reload).")

    st.markdown("---")
    st.markdown("### Quick tips to make your app look grand (for the submission README)")
    st.markdown("""
    - Add screenshots of the Dashboard and Badge.  
    - Mention how many test purchases you entered and the resulting badges.  
    - Describe UI colors, fonts and why they support accessibility.  
    """)

# ----------------------
# Footer with small help
# ----------------------
st.markdown("---")
st.markdown("Made with ❤️ — Add colourful purchases and watch your eco-story grow. Need help? Ask me what each part does and I'll explain like you're 4!")
