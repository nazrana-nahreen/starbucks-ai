import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

st.set_page_config(
    page_title="Starbucks AI Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

* {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}

h1 { font-family: 'Cormorant Garamond', serif !important; font-size: 36px !important; font-weight: 700 !important; color: #1E3932 !important; letter-spacing: -0.5px !important; }
h2 { font-family: 'Cormorant Garamond', serif !important; font-size: 26px !important; font-weight: 600 !important; color: #1E3932 !important; }
h3 { font-family: 'Cormorant Garamond', serif !important; font-size: 21px !important; font-weight: 600 !important; color: #1E3932 !important; }
h4 { font-family: 'Cormorant Garamond', serif !important; font-size: 17px !important; font-weight: 600 !important; }

.main { background-color: #F7F3EE !important; }
section[data-testid="stSidebar"] { background-color: #1E3932 !important; }
section[data-testid="stSidebar"] > div { background-color: #1E3932 !important; }

/* Sidebar all text white */
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebar"] p    { font-size: 15px !important; color: #D4E9E2 !important; }
[data-testid="stSidebar"] span { font-size: 15px !important; }

/* Navigate label */
[data-testid="stSidebar"] .stRadio > label {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: #9FD4BF !important;
    margin-bottom: 6px !important;
}

/* Nav items */
[data-testid="stSidebar"] .stRadio label {
    font-size: 16px !important;
    font-weight: 500 !important;
    color: #ffffff !important;
    padding: 8px 4px !important;
    letter-spacing: 0.2px !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #CBA258 !important; }

/* Sidebar divider */
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; margin: 16px 0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border-radius: 10px !important;
    padding: 16px !important;
    border: 1px solid #EDE9E4 !important;
}
[data-testid="metric-container"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #888 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 30px !important;
    font-weight: 700 !important;
    color: #1E3932 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 13px !important; }

/* Button */
.stButton > button {
    background-color: #1E3932 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 10px 24px !important;
    letter-spacing: 0.3px !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background-color: #00704A !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
    color: #666 !important;
}
.stTabs [aria-selected="true"] { color: #1E3932 !important; font-weight: 600 !important; }

/* Selectbox / inputs */
[data-testid="stSelectbox"] label { font-size: 13px !important; font-weight: 600 !important; letter-spacing: 0.5px !important; color: #555 !important; }
[data-testid="stSlider"] label    { font-size: 13px !important; font-weight: 600 !important; color: #555 !important; }

/* Finding cards */
.fc { border-radius: 10px; padding: 16px 18px; margin: 6px 0; }
.fc-green  { background: #00704A; }
.fc-red    { background: #B91C1C; }
.fc-dark   { background: #1E3932; border: 1px solid rgba(255,255,255,0.1); }
.fc-gold   { background: #92670A; }
.fc-gray   { background: #374151; }
.fc-title  { font-size: 14px !important; font-weight: 700 !important; color: #ffffff !important; margin-bottom: 5px; display: block; letter-spacing: 0.2px; }
.fc-text   { font-size: 13px !important; color: rgba(255,255,255,0.85) !important; line-height: 1.55; display: block; }
.fc-gold .fc-title, .fc-gold .fc-text { color: #ffffff !important; }

/* Segment cards */
.seg-card { border-radius: 10px; padding: 18px 20px; margin: 8px 0; }

/* Alert boxes */
[data-testid="stAlert"] { border-radius: 8px !important; }
[data-testid="stAlert"] div { font-size: 14px !important; }

/* Caption */
[data-testid="stCaptionContainer"] p { font-size: 13px !important; color: #888 !important; }
</style>
""", unsafe_allow_html=True)

CSV_PATH = "data/starbucks_customer_ordering_patterns.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M').dt.hour
        df['is_rewards_member_encoded'] = df['is_rewards_member'].astype(int)
        df['has_food_item_encoded']     = df['has_food_item'].astype(int)
        df['order_ahead_encoded']       = df['order_ahead'].astype(int)
        return df
    except FileNotFoundError:
        return None

df = load_data()

@st.cache_resource
def load_models():
    models = {}
    for f in ['spend_prediction_model.pkl', 'wait_time_model.pkl', 'kmeans_model.pkl',
              'label_encoders.pkl', 'cluster_scaler.pkl', 'spend_features.pkl',
              'wait_features.pkl', 'cluster_features.pkl', 'segment_names.pkl']:
        path = os.path.join('models', f)
        if os.path.exists(path):
            models[f.replace('.pkl', '')] = joblib.load(path)
    return models

models = load_models()

G = '#00704A'
D = '#1E3932'
GOLD = '#CBA258'
L = '#D4E9E2'

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 20px 0;">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/200px-Starbucks_Corporation_Logo_2011.svg.png"
             style="width:90px; height:90px; border-radius:50%; object-fit:cover;
                    box-shadow:0 0 0 3px rgba(255,255,255,0.15);" />
        <div style="margin-top:14px; font-family:'Cormorant Garamond',serif;
                    font-size:22px; font-weight:700; color:#ffffff; letter-spacing:0.3px;">
            Starbucks AI
        </div>
        <div style="font-size:10px; color:#9FD4BF; font-weight:600;
                    letter-spacing:3px; text-transform:uppercase; margin-top:3px;">
            Operations Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio("Navigate", [
        "📊 Overview",
        "🔍 Deep Insights",
        "🔮 Predictions",
        "👥 Segments",
    ])

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px; color:#9FD4BF; font-weight:600;
                letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
        Dataset
    </div>
    """, unsafe_allow_html=True)

    if df is not None:
        stats = [
            ("100,000", "Transactions"),
            ("14,988",  "Customers"),
            ("500",     "Stores"),
        ]
        for val, label in stats:
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="font-family:'Cormorant Garamond',serif; font-size:22px;
                            font-weight:700; color:#ffffff; line-height:1;">{val}</div>
                <div style="font-size:11px; color:#9FD4BF; margin-top:1px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("Starbucks AI Operations")
    st.caption("100,000 transactions · 500 stores · Jan 2024 – Dec 2025")

    if df is None:
        st.error("CSV not found. Update CSV_PATH.")
        st.stop()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue",       f"${df['total_spend'].sum():,.0f}")
    c2.metric("Avg Order",     f"${df['total_spend'].mean():.2f}")
    c3.metric("Mobile",        f"{(df['order_channel']=='Mobile App').mean()*100:.1f}%")
    c4.metric("Avg Wait",      f"{df['fulfillment_time_min'].mean():.1f} min")
    c5.metric("Satisfaction",  f"{df['customer_satisfaction'].mean():.2f}/5")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("### Key Findings")

    findings = [
        ("fc-green", "💰 Mobile App Revenue Gap",
         "Mobile App users spend <b>$18.08</b> avg vs <b>~$12.50</b> for all other channels — a <b>45% premium</b>."),
        ("fc-red",   "⏱️ Drive-Thru Bottleneck",
         "Drive-Thru has the <b>slowest wait (5.80 min)</b> AND <b>lowest satisfaction (3.44/5)</b>."),
        ("fc-dark",  "📱 Mobile Adoption Gap",
         "<b>55+ customers</b> placed only <b>981 mobile orders</b> vs <b>16,368 for 25-34</b>."),
        ("fc-gold",  "⭐ Rewards ROI",
         "Rewards members spend <b>$15.72 vs $14.09</b> — <b>$1.63 more per visit</b>."),
        ("fc-gray",  "🌅 Peak Hour Alert",
         "<b>7am is peak</b> with 10,208 orders. Ensure maximum staffing before morning rush."),
    ]

    col_a, col_b = st.columns(2)
    for i, (cls, title, text) in enumerate(findings):
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"""
            <div class="fc {cls}">
                <span class="fc-title">{title}</span>
                <span class="fc-text">{text}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        spend_data = df.groupby('order_channel')['total_spend'].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(spend_data, x='order_channel', y='total_spend',
                     color='order_channel',
                     color_discrete_sequence=[G, D, GOLD, L],
                     title="Avg Spend by Channel ($)", text='total_spend')
        fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)',
                          paper_bgcolor='rgba(0,0,0,0)', yaxis_title="",
                          title_font_size=14, margin=dict(t=40,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        wait_data = df.groupby('order_channel')['fulfillment_time_min'].mean().sort_values(ascending=False).reset_index()
        colors_w = [('#B91C1C' if v > 5 else G) for v in wait_data['fulfillment_time_min']]
        fig2 = px.bar(wait_data, x='order_channel', y='fulfillment_time_min',
                      color='order_channel', color_discrete_sequence=colors_w,
                      title="Avg Wait Time by Channel (min)", text='fulfillment_time_min')
        fig2.update_traces(texttemplate='%{text:.1f}m', textposition='outside')
        fig2.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)', yaxis_title="",
                           title_font_size=14, margin=dict(t=40,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        hourly = df.groupby('hour').size().reset_index(name='Orders')
        fig3 = px.area(hourly, x='hour', y='Orders', title="Orders by Hour of Day",
                       color_discrete_sequence=[G])
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           xaxis_title="Hour", yaxis_title="", title_font_size=14,
                           margin=dict(t=40,b=10))
        fig3.add_vline(x=7, line_dash="dash", line_color="#B91C1C", annotation_text="Peak 7am")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        age_mobile = df[df['order_channel']=='Mobile App']['customer_age_group'].value_counts()
        age_mobile = age_mobile.reindex(['18-24','25-34','35-44','45-54','55+']).reset_index()
        age_mobile.columns = ['Age Group', 'Orders']
        fig4 = px.bar(age_mobile, x='Age Group', y='Orders',
                      title="Mobile Orders by Age Group",
                      color='Orders', color_continuous_scale=[L, G])
        fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           yaxis_title="", title_font_size=14, margin=dict(t=40,b=10))
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2: DEEP INSIGHTS
# ══════════════════════════════════════════════════════════════
elif page == "🔍 Deep Insights":
    st.title("Deep Insights")
    if df is None:
        st.error("CSV not found.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["By Region", "By Drink", "Satisfaction"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            d = df.groupby('region')['total_spend'].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(d, x='region', y='total_spend', title="Avg Spend by Region",
                         color_discrete_sequence=[G])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              yaxis_title="", title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            rc = df.groupby(['region','order_channel']).size().unstack(fill_value=0)
            fig2 = px.bar(rc.reset_index(), x='region', y=rc.columns.tolist(),
                          title="Channel by Region", barmode='stack',
                          color_discrete_sequence=[G, D, GOLD, L])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               yaxis_title="", title_font_size=14)
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            d = df.groupby('drink_category')['total_spend'].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(d, x='drink_category', y='total_spend',
                         title="Avg Spend by Drink", color='total_spend',
                         color_continuous_scale=[L, G])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              yaxis_title="", title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            d2 = df.groupby('drink_category')['num_customizations'].mean().sort_values(ascending=False).reset_index()
            fig2 = px.bar(d2, x='drink_category', y='num_customizations',
                          title="Avg Customizations by Drink",
                          color_discrete_sequence=[GOLD])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               yaxis_title="", title_font_size=14)
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            d = df.groupby('order_channel')['customer_satisfaction'].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(d, x='order_channel', y='customer_satisfaction',
                         title="Satisfaction by Channel", color='customer_satisfaction',
                         color_continuous_scale=['#B91C1C', GOLD, G])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              yaxis_range=[0,5], yaxis_title="", title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            d2 = df.groupby('customer_age_group')['customer_satisfaction'].mean()\
                   .reindex(['18-24','25-34','35-44','45-54','55+']).reset_index()
            fig2 = px.line(d2, x='customer_age_group', y='customer_satisfaction',
                           title="Satisfaction by Age", markers=True,
                           color_discrete_sequence=[G])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               yaxis_range=[3,4], yaxis_title="", title_font_size=14)
            st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGE 3: PREDICTIONS
# ══════════════════════════════════════════════════════════════
elif page == "🔮 Predictions":
    st.title("AI Predictions")
    st.caption("Enter order details to get ML-powered predictions")

    if not models:
        st.error("Models not found. Run phase1_ml_models.py first.")
        st.stop()

    col_form, col_result = st.columns([1, 1])

    with col_form:
        st.markdown("#### Order Details")
        order_channel    = st.selectbox("Channel", ["Mobile App", "Drive-Thru", "In-Store Cashier", "Kiosk"])
        store_loc        = st.selectbox("Location Type", ["Urban", "Suburban", "Rural"])
        region           = st.selectbox("Region", ["Northeast", "Southeast", "Midwest", "West", "Southwest"])
        age_group        = st.selectbox("Age Group", ["18-24", "25-34", "35-44", "45-54", "55+"])
        day              = st.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        drink_cat        = st.selectbox("Drink", ["Espresso", "Frappuccino", "Refresher", "Tea", "Brewed Coffee", "Other"])
        cart_size        = st.slider("Cart Size", 1, 10, 3)
        num_custom       = st.slider("Customizations", 0, 8, 2)
        is_rewards       = st.toggle("Rewards Member?", value=True)
        has_food         = st.toggle("Has Food Item?", value=False)
        order_ahead_bool = st.toggle("Order Ahead?", value=False)
        predict_btn      = st.button("Run Prediction", use_container_width=True)

    with col_result:
        st.markdown("#### Results")
        if predict_btn:
            le = models.get('label_encoders', {})
            def enc(col, val):
                if col in le:
                    try: return int(le[col].transform([str(val)])[0])
                    except: return 0
                return 0

            data = {
                'order_channel': order_channel, 'store_location_type': store_loc,
                'region': region, 'customer_age_group': age_group,
                'day_of_week': day, 'drink_category': drink_cat,
                'cart_size': cart_size, 'num_customizations': num_custom,
                'is_rewards_member': is_rewards, 'has_food_item': has_food,
                'order_ahead': order_ahead_bool,
            }

            def build_vec(features):
                vec = []
                for f in features:
                    if f.endswith('_encoded'):
                        orig = f.replace('_encoded', '')
                        val  = data.get(orig)
                        vec.append(int(val) if isinstance(val, bool) else enc(orig, val))
                    else:
                        vec.append(data.get(f, 0))
                return vec

            spend_pred = float(models['spend_prediction_model'].predict([build_vec(models.get('spend_features', []))])[0])
            wait_pred  = float(models['wait_time_model'].predict([build_vec(models.get('wait_features', []))])[0])
            ch_avg = {"Mobile App":18.08,"Drive-Thru":12.48,"In-Store Cashier":12.51,"Kiosk":12.49}.get(order_channel,14.87)

            st.success("Predictions ready")
            st.metric("Predicted Spend", f"${spend_pred:.2f}", delta=f"${spend_pred-ch_avg:+.2f} vs channel avg")
            st.metric("Predicted Wait",  f"{wait_pred:.1f} min")

            if wait_pred < 3.5:   st.success("Fast service expected")
            elif wait_pred < 5.0: st.warning("Normal wait time")
            else:                  st.error("Slow — consider adding staff")

            if is_rewards:                    st.info("Rewards member — $1.63 more spend on average")
            if order_channel == "Mobile App": st.info("Mobile App — highest spend channel ($18.08 avg)")


# ══════════════════════════════════════════════════════════════
# PAGE 4: SEGMENTS
# ══════════════════════════════════════════════════════════════
elif page == "👥 Segments":
    st.title("Customer Segments")
    st.caption("AI-powered persona classification from K-Means clustering")

    if df is None:
        st.error("CSV not found.")
        st.stop()

    segments = [
        {"name": "Loyal High-Value",   "icon": "🏆", "color": G,       "tc": "#fff",
         "desc": "Frequent visitors, high spend, many customizations.",
         "action": "Exclusive early access to seasonal drinks. Priority loyalty rewards."},
        {"name": "Casual Regular",     "icon": "☕", "color": "#374151","tc": "#fff",
         "desc": "Average spend, simple orders, moderate frequency.",
         "action": "Send 'We miss you' coupons. Promote rewards program."},
        {"name": "Digital Power User", "icon": "📱", "color": "#92670A","tc": "#fff",
         "desc": "Heavy mobile app users, many customizations, tech-savvy.",
         "action": "Mobile-only deals. App-exclusive menu items."},
        {"name": "Quick Drive-Thru",   "icon": "🚗", "color": "#7F1D1D","tc": "#fff",
         "desc": "Speed-focused, simple orders, time-sensitive.",
         "action": "Drive-thru speed optimization. Bundle deals."},
    ]

    col1, col2 = st.columns(2)
    for i, seg in enumerate(segments):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="seg-card" style="background:{seg['color']};">
                <div style="font-size:24px; margin-bottom:8px;">{seg['icon']}</div>
                <div style="font-family:'Cormorant Garamond',serif; font-size:18px;
                            font-weight:700; color:{seg['tc']}; margin-bottom:6px;">{seg['name']}</div>
                <div style="font-size:13px; color:rgba(255,255,255,0.8); margin-bottom:10px;
                            line-height:1.5;">{seg['desc']}</div>
                <div style="font-size:12px; color:rgba(255,255,255,0.6); font-weight:600;
                            text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Action</div>
                <div style="font-size:13px; color:rgba(255,255,255,0.9);">{seg['action']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    fig = px.box(df, x='order_channel', y='total_spend', color='order_channel',
                 color_discrete_sequence=[G, D, GOLD, '#B91C1C'],
                 title="Spend Distribution by Channel")
    fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)', yaxis_title="", title_font_size=14)
    st.plotly_chart(fig, use_container_width=True)