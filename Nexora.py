import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
st.set_page_config(
    page_title="Nexora.ai • E-Commerce Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown("### 📂 DATA SOURCE")
uploaded_file = st.sidebar.file_uploader(
    "Upload your E-Commerce CSV file",
    type=["csv"],
    help="Choose a CSV file from your computer."
)
if uploaded_file is None:
    st.markdown("""
    <div style="margin-top:25px;padding:35px;border:1px dashed #28d7ff;
                border-radius:18px;background:#061523;text-align:center;">
        <div style="font-size:34px;">📂</div>
        <div style="font-size:20px;font-weight:800;color:#28d7ff;">
            Upload your dataset to start Nexora.ai
        </div>
        <div style="color:#7894a8;margin-top:8px;">
            Use the <b>Upload E-Commerce CSV file</b> button in the sidebar.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
@st.cache_data
def load_uploaded_data(file_bytes):
    from io import BytesIO
    d = pd.read_csv(BytesIO(file_bytes))
    d["Order_Date"] = pd.to_datetime(d["Order_Date"], errors="coerce")
    for c in d.columns:
        if c not in ["Order_ID","Order_Date","Customer_ID","Gender","City","State",
                     "Product_Category","Product","Payment_Method","Return_Status",
                     "Return_Reason","Marketing_Channel","Customer_Segment","Order_Status"]:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d
try:
    df = load_uploaded_data(uploaded_file.getvalue())
    st.sidebar.success(f"✅ {uploaded_file.name} loaded")
except Exception as e:
    st.error("❌ Unable to read the uploaded CSV file.")
    st.exception(e)
    st.stop()
def avg(c):
    return float(data[c].mean()) if len(data) else np.nan
def total(c):
    return float(data[c].sum()) if len(data) else 0
def money(x):
    if pd.isna(x): return "—"
    if abs(x)>=1e7: return f"₹{x/1e7:.2f}Cr"
    if abs(x)>=1e5: return f"₹{x/1e5:.2f}L"
    return f"₹{x:,.0f}"
def num(x):
    return "—" if pd.isna(x) else f"{x:,.0f}"
def fig_dark(figsize=(7,3.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#071827"); ax.set_facecolor("#071827")
    for s in ax.spines.values(): s.set_color("#16374e")
    ax.tick_params(colors="#7894a8",labelsize=8)
    ax.grid(alpha=.10,color="#9fb8c7")
    return fig, ax
def recommendation_rows():
    rec=[]
    ret=(data["Return_Status"]=="Returned").mean()*100
    margin=total("Profit")/max(total("Revenue"),1)*100
    topcat=data.groupby("Product_Category")["Profit"].sum().sort_values(ascending=False)
    topcity=data.groupby("City")["Revenue"].sum().sort_values(ascending=False)
    if ret>10: rec.append(("red","🔄 HIGH RETURN RISK",f"Overall return rate is {ret:.1f}%. Review product quality, sizing and delivery issues."))
    else: rec.append(("green","🟢 RETURN PERFORMANCE",f"Return rate is {ret:.1f}%, within a manageable range."))
    if len(topcat): rec.append(("purple","💰 PROFIT LEADER",f"{topcat.index[0]} is the strongest category by total profit."))
    if len(topcity): rec.append(("cyan","📍 TOP MARKET",f"{topcity.index[0]} currently generates the highest revenue."))
    if margin<20: rec.append(("yellow","⚠️ MARGIN WATCH",f"Overall profit margin is {margin:.1f}%. Review discounts, cost and shipping."))
    else: rec.append(("green","📈 MARGIN HEALTH",f"Overall profit margin is {margin:.1f}%, showing healthy profitability."))
    channel=data.groupby("Marketing_Channel")["Revenue"].sum().sort_values(ascending=False)
    if len(channel): rec.append(("purple","🎯 MARKETING OPPORTUNITY",f"{channel.index[0]} is the leading revenue channel; evaluate scaling efficiency."))
    return rec
st.sidebar.markdown("""
<div class="brand">
<b>🛒 E-COMMERCE<br>INTELLIGENCE CENTER</b>
<small>NEXORA.AI BUSINESS ANALYTICS</small>
</div>
""", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigation",
    ["Command Center","Sales Intelligence","Customer Intelligence",
     "Product Intelligence","Marketing Intelligence","Delivery & Returns",
     "AI Business Advisor","Data Explorer"],
    label_visibility="collapsed"
)
st.sidebar.markdown("### 🎛️ FILTERS")
city = st.sidebar.selectbox("City", ["All"] + sorted(df["City"].dropna().unique().tolist()))
category = st.sidebar.selectbox("Category", ["All"] + sorted(df["Product_Category"].dropna().unique().tolist()))
channel = st.sidebar.selectbox("Marketing Channel", ["All"] + sorted(df["Marketing_Channel"].dropna().unique().tolist()))
min_date = pd.Timestamp("2000-01-01").date()
max_date = pd.Timestamp("2026-12-31").date()
dates = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
available_years = list(range(2000, 2027))
selected_year = st.sidebar.selectbox(
    "📆 Select Year",
    ["All Years"] + available_years
)
data = df.copy()
if city != "All":
    data = data[data["City"] == city]
if category != "All":
    data = data[data["Product_Category"] == category]
if channel != "All":
    data = data[data["Marketing_Channel"] == channel]
if selected_year != "All Years":
    data = data[data["Order_Date"].dt.year == int(selected_year)]
if isinstance(dates, (tuple, list)) and len(dates) == 2:
    start_date, end_date = dates
    data = data[
        (data["Order_Date"] >= pd.Timestamp(start_date)) &
        (data["Order_Date"] <= pd.Timestamp(end_date))
    ]
st.markdown(f"""
<div class="top">
<div><div class="title">🛒 NEXORA.AI • E-COMMERCE INTELLIGENCE</div>
<div class="sub">NEXORA.AI • DATA-DRIVEN BUSINESS DECISION SUPPORT</div></div>
<div style="text-align:right"><div class="live">● LIVE ANALYTICS</div>
<div class="sub">{len(data):,} records loaded</div></div>
</div>
""", unsafe_allow_html=True)
revenue=total("Revenue"); profit=total("Profit"); orders=data["Order_ID"].nunique()
unique_customers=data["Customer_ID"].nunique()
conv=avg("Conversion_Rate_pct")
ret=(data["Return_Status"]=="Returned").mean()*100 if len(data) else 0
kpis=[
("💰","TOTAL REVENUE",money(revenue),"green"),
("📈","TOTAL PROFIT",money(profit),"cyan"),
("🛍️","TOTAL ORDERS",num(orders),"purple"),
("👥","CUSTOMERS",num(unique_customers),"cyan"),
("🎯","CONVERSION RATE",f"{conv:.2f}%","green"),
("🔄","RETURN RATE",f"{ret:.2f}%","red" if ret>10 else "yellow"),
]
cols=st.columns(6)
for c,(i,l,v,cl) in zip(cols,kpis):
    c.markdown(f'<div class="card"><div class="label">{i} {l}</div><div class="value {cl}">{v}</div><div class="muted">Filtered business performance</div></div>',unsafe_allow_html=True)
def command():
    st.markdown('<div class="section">📡 COMMAND CENTER • EXECUTIVE OVERVIEW</div>',unsafe_allow_html=True)
    left,mid,right=st.columns([1.8,1.25,1])
    daily=data.groupby("Order_Date").agg(Revenue=("Revenue","sum"),Profit=("Profit","sum")).reset_index()
    with left:
        fig,ax=fig_dark((8,3.7))
        ax.plot(daily.Order_Date,daily.Revenue,label="Revenue",linewidth=2)
        ax.plot(daily.Order_Date,daily.Profit,label="Profit",linewidth=2)
        ax.set_title("Revenue & Profit Trend",color="#dff8ff",loc="left")
        ax.legend(frameon=False,labelcolor="#dff8ff")
        st.pyplot(fig,use_container_width=True);plt.close(fig)
    with mid:
        cat = (
            data.groupby("Product_Category")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )
        cat = cat[cat > 0]
        fig, ax = fig_dark((5, 3.7))
        if len(cat) > 0:
            ax.pie(
                cat.values,
                labels=cat.index,
                autopct="%1.0f%%",
                textprops={"color": "white", "fontsize": 7},
                wedgeprops={"width": .42}
            )
        else:
            ax.text(
                0.5,
                0.5,
                "No revenue data\\nfor selected filters",
                ha="center",
                va="center",
                color="white",
                fontsize=11
            )
        ax.set_title("Revenue by Category", color="#dff8ff", loc="left")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with right:
        st.markdown("#### 🚨 INTELLIGENCE ALERTS")
        for typ,title,text in recommendation_rows()[:4]:
            st.markdown(f'<div class="alert {typ}"><b>{title}</b><p>{text}</p></div>',unsafe_allow_html=True)
    a,b,c,d,e=st.columns(5)
    metrics=[
        ("Average Order Value",money(avg("Revenue"))),
        ("Average Delivery",f"{avg('Delivery_Days'):.1f} days"),
        ("Average Rating",f"{avg('Customer_Rating'):.2f}/5"),
        ("Shipping Cost",money(avg("Shipping_Cost"))),
        ("Profit Margin",f"{profit/max(revenue,1)*100:.2f}%")
    ]
    for col,(l,v) in zip([a,b,c,d,e],metrics):
        col.metric(l,v)
    a,b,c=st.columns(3)
    with a:
        top=data.groupby("Product")["Revenue"].sum().sort_values(ascending=False).head(7)
        st.markdown("#### 🏆 TOP PRODUCTS")
        st.dataframe(top.rename("Revenue").map(money),use_container_width=True)
    with b:
        seg=data.groupby("Customer_Segment")["Revenue"].sum().sort_values(ascending=False)
        st.markdown("#### 👥 CUSTOMER SEGMENTS")
        st.dataframe(seg.rename("Revenue").map(money),use_container_width=True)
    with c:
        ch=data.groupby("Marketing_Channel")["Revenue"].sum().sort_values(ascending=False)
        fig,ax=fig_dark((5,3))
        ax.bar(ch.index,ch.values)
        ax.set_title("Revenue by Marketing Channel",color="#dff8ff",loc="left")
        ax.tick_params(axis="x",rotation=45)
        st.pyplot(fig,use_container_width=True);plt.close(fig)
def sales():
    st.markdown('<div class="section">📈 SALES INTELLIGENCE</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Revenue",money(revenue));b.metric("Profit",money(profit));c.metric("Margin",f"{profit/max(revenue,1)*100:.2f}%")
    daily=data.groupby("Order_Date")[["Revenue","Profit"]].sum()
    fig,ax=fig_dark((12,4));daily.plot(ax=ax,linewidth=2);ax.set_title("Daily Revenue & Profit",color="#dff8ff",loc="left");ax.legend(frameon=False)
    st.pyplot(fig,use_container_width=True);plt.close(fig)
    st.dataframe(data.groupby("Product_Category").agg(Orders=("Order_ID","nunique"),Revenue=("Revenue","sum"),Profit=("Profit","sum"),Margin=("Profit_Margin_pct","mean")).sort_values("Revenue",ascending=False).round(2),use_container_width=True)
def customers():
    st.markdown('<div class="section">👥 CUSTOMER INTELLIGENCE</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Unique Customers",f"{unique_customers:,}")
    b.metric("Avg Customer Value",money(avg("Customer_Lifetime_Value")))
    c.metric("Avg Value Score",f"{avg('Customer_Value_Score'):.1f}/100")
    seg=data.groupby("Customer_Segment").agg(Customers=("Customer_ID","nunique"),Revenue=("Revenue","sum"),CLV=("Customer_Lifetime_Value","mean"),Score=("Customer_Value_Score","mean")).sort_values("Revenue",ascending=False)
    st.dataframe(seg.round(2),use_container_width=True)
    fig,ax=fig_dark((10,4)); ax.scatter(data.Customer_Age,data.Customer_Lifetime_Value,alpha=.18); ax.set_title("Age vs Customer Lifetime Value",color="#dff8ff",loc="left");st.pyplot(fig,use_container_width=True);plt.close(fig)
def products():
    st.markdown('<div class="section">📦 PRODUCT INTELLIGENCE</div>',unsafe_allow_html=True)
    p=data.groupby(["Product_Category","Product"]).agg(Orders=("Order_ID","nunique"),Units=("Quantity","sum"),Revenue=("Revenue","sum"),Profit=("Profit","sum"),Return_Rate=("Return_Status",lambda s:(s=="Returned").mean()*100)).reset_index()
    st.dataframe(p.sort_values("Profit",ascending=False).head(20).round(2),use_container_width=True)
    cat = p.groupby("Product_Category")[["Revenue", "Profit"]].sum().sort_values("Profit", ascending=False)
    fig, ax = fig_dark((10, 4))
    if len(cat) > 0:
        cat.plot(kind="bar", ax=ax)
    else:
        ax.text(0.5, 0.5, "No product data for selected filters",
                ha="center", va="center", color="white", fontsize=11)
    ax.set_title("Category Revenue vs Profit", color="#dff8ff", loc="left")
    ax.tick_params(axis="x", rotation=20)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
def marketing():
    st.markdown('<div class="section">🎯 MARKETING INTELLIGENCE</div>',unsafe_allow_html=True)
    m=data.groupby("Marketing_Channel").agg(Orders=("Order_ID","nunique"),Revenue=("Revenue","sum"),Profit=("Profit","sum"),Visits=("Website_Visits","sum"),Conversion=("Conversion_Rate_pct","mean")).sort_values("Revenue",ascending=False)
    st.dataframe(m.round(2),use_container_width=True)
    fig,ax=fig_dark((10,4));m.Revenue.plot(kind="bar",ax=ax);ax.set_title("Revenue by Marketing Channel",color="#dff8ff",loc="left");ax.tick_params(axis="x",rotation=30);st.pyplot(fig,use_container_width=True);plt.close(fig)
def delivery():
    st.markdown('<div class="section">🚚 DELIVERY & RETURNS</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Avg Delivery",f"{avg('Delivery_Days'):.2f} days")
    b.metric("Returned Orders",f"{(data.Return_Status=='Returned').sum():,}")
    c.metric("Return Rate",f"{ret:.2f}%")
    r=data.groupby("Return_Reason").size().sort_values(ascending=False)
    st.markdown("#### 🔄 Return Reasons")
    st.dataframe(r.rename("Orders"),use_container_width=True)
    fig,ax=fig_dark((9,4));data.groupby("Delivery_Days")["Return_Risk_Score"].mean().plot(kind="bar",ax=ax);ax.set_title("Delivery Days vs Average Return Risk",color="#dff8ff",loc="left");st.pyplot(fig,use_container_width=True);plt.close(fig)
def advisor():
    st.markdown('<div class="section">🧠 AI BUSINESS ADVISOR</div>',unsafe_allow_html=True)
    st.info("The recommendation layer uses rule-based analytical scoring from the selected dataset. It is an educational decision-support module, not a predictive ML model.")
    for typ,title,text in recommendation_rows():
        st.markdown(f'<div class="alert {typ}"><b>{title}</b><p>{text}</p></div>',unsafe_allow_html=True)
    st.markdown("#### 🔍 High-Risk Products")
    risk=data.groupby("Product").agg(Return_Risk=("Return_Risk_Score","mean"),Return_Rate=("Return_Status",lambda s:(s=="Returned").mean()*100),Profit=("Profit","sum")).sort_values("Return_Risk",ascending=False).head(10)
    st.dataframe(risk.round(2),use_container_width=True)
def explorer():
    st.markdown('<div class="section">🔎 DATA EXPLORER</div>',unsafe_allow_html=True)
    search=st.text_input("Search by Order ID, Customer ID, Product, City or Category")
    x=data.copy()
    if search:
        mask=np.zeros(len(x),dtype=bool)
        for col in ["Order_ID","Customer_ID","Product","City","Product_Category"]:
            mask |= x[col].astype(str).str.contains(search,case=False,na=False).to_numpy()
        x=x[mask]
    st.write(f"Showing **{len(x):,}** rows × **{len(x.columns)}** columns")
    st.dataframe(x.sort_values("Order_Date",ascending=False),height=530,use_container_width=True)
    st.download_button("⬇️ DOWNLOAD FILTERED CSV",x.to_csv(index=False).encode(),"ecommerce_filtered.csv","text/csv")
if page=="Command Center": command()
elif page=="Sales Intelligence": sales()
elif page=="Customer Intelligence": customers()
elif page=="Product Intelligence": products()
elif page=="Marketing Intelligence": marketing()
elif page=="Delivery & Returns": delivery()
elif page=="AI Business Advisor": advisor()
else: explorer()
st.markdown('<div class="footer">NEXORA.AI • E-COMMERCE INTELLIGENCE • TANMAY BAGADE • Pandas • NumPy • Matplotlib • Streamlit</div>',unsafe_allow_html=True)
