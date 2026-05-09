"""
Commonwealth Perpetua — Portfolio Intelligence
Upload a fund document. See what you actually own.
"""

import streamlit as st
import anthropic
import json
import pandas as pd
import plotly.express as px
import PyPDF2
import io

st.set_page_config(
    page_title="Commonwealth Perpetua",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
    html, body, [class*="css"] { font-family: 'EB Garamond', Georgia, serif; }
    .main { background-color: #FAFAF7; }
    .cp-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        border-bottom: 2px solid #8B6914;
        margin-bottom: 2rem;
    }
    .cp-title {
        font-size: 2.4rem;
        font-weight: 600;
        color: #1A3C2A;
        letter-spacing: 0.12em;
        margin: 0;
    }
    .cp-tagline {
        font-size: 1rem;
        color: #8B6914;
        font-style: italic;
        margin: 0.3rem 0 0 0;
    }
    .metric-card {
        background: white;
        border: 1px solid #E0E0D8;
        border-top: 3px solid #1A3C2A;
        padding: 1.2rem;
        border-radius: 2px;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        color: #1A3C2A;
    }
    .metric-sub { font-size: 0.85rem; color: #666; font-style: italic; }
    .flag-card {
        background: #FFF8E8;
        border-left: 4px solid #8B6914;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #444;
    }
    .insight-card {
        background: #EEF4F0;
        border-left: 4px solid #1A3C2A;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        color: #222;
        font-style: italic;
    }
    .section-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #1A3C2A;
        font-weight: 600;
        border-bottom: 1px solid #E0E0D8;
        padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }
    .stButton button {
        background-color: #1A3C2A;
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        font-family: 'EB Garamond', Georgia, serif;
        font-size: 1rem;
        letter-spacing: 0.06em;
        border-radius: 2px;
        width: 100%;
    }
    .stButton button:hover { background-color: #2D5A3D; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="cp-header">
    <p class="cp-title">COMMONWEALTH PERPETUA</p>
    <p class="cp-tagline">Legacy & Institutional Investor Portfolio Intelligence</p>
</div>
""", unsafe_allow_html=True)

def extract_pdf_text(uploaded_file):
    reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_portfolio_intelligence(pdf_text):
    client = anthropic.Anthropic()
    prompt = f"""You are analyzing a fund document on behalf of an institutional investor (pension fund, endowment, or similar).

Your job is portfolio intelligence — not tax analysis. Extract what the investor actually owns, where returns are coming from, and what risks are concentrated in the portfolio.

Return ONLY valid JSON, no other text:

{{
  "fund_name": "fund name — if real fund name present, replace with generic description like 'Infrastructure Fund IV'",
  "fund_manager": "manager name — if real firm name present, replace with generic like 'Infrastructure Capital Manager'",
  "tax_year": "year",
  "lp_name": "investor name — if real institution name present, replace with generic like 'Regional Pension Trust'",
  "lp_commitment": "capital commitment as string",
  "lp_ownership_pct": "ownership percentage",
  "lp_capital_account": "ending capital account value",
  "total_net_income": "total net income attributed to LP",
  "portfolio_companies": [
    {{
      "name": "company name — generalize if needed",
      "state": "state abbreviation",
      "industry": "industry sector",
      "activity_status": "Operating / New Investment / Disposition / Exited",
      "lp_income": numeric dollar value,
      "lp_income_formatted": "formatted string",
      "pct_of_total": numeric percentage
    }}
  ],
  "intelligence_flags": [
    "plain English observation about concentration, risk, or notable pattern"
  ],
  "plain_english_summary": "2-3 sentence plain English summary of what this investor actually owns and where returns came from. No tax language. Write for a pension board member."
}}

Document:
{pdf_text}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

# Main UI
col_upload, col_info = st.columns([1, 1])

with col_upload:
    st.markdown('<div class="section-header">Upload Fund Document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Annual filing, capital notice, or fund document (PDF)",
        type="pdf",
        help="Upload any fund document to extract portfolio intelligence"
    )
    if uploaded:
        if st.button("Generate Portfolio Intelligence"):
            with st.spinner("Extracting portfolio intelligence..."):
                try:
                    pdf_text = extract_pdf_text(uploaded)
                    data = extract_portfolio_intelligence(pdf_text)
                    st.session_state['data'] = data
                except Exception as e:
                    st.error(f"Extraction error: {e}")

with col_info:
    st.markdown('<div class="section-header">What This Does</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="insight-card">
Your investment office receives thousands of documents annually — fund filings, capital notices, communications, agreements. Most of it never gets synthesized into a unified picture of what your capital is actually doing. Commonwealth Perpetua changes that. Upload a document, see what you own.
</div>
""", unsafe_allow_html=True)

# Dashboard
if 'data' in st.session_state:
    d = st.session_state['data']
    portcos = d.get('portfolio_companies', [])

    if portcos:
        df = pd.DataFrame(portcos)
        df_positive = df[df['lp_income'] > 0].sort_values('lp_income', ascending=False)

        st.markdown("---")

        # Fund header
        st.markdown(f"""
<div style="text-align:center; margin-bottom:1.5rem;">
    <div style="font-size:1.5rem; font-weight:600; color:#1A3C2A;">{d.get('fund_name','')}</div>
    <div style="font-size:0.9rem; color:#8B6914; font-style:italic;">
        {d.get('lp_name','')} &nbsp;·&nbsp; Tax Year {d.get('tax_year','')} &nbsp;·&nbsp; {d.get('lp_ownership_pct','')} ownership
    </div>
</div>
""", unsafe_allow_html=True)

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        top1 = df_positive.iloc[0] if len(df_positive) > 0 else None
        top3_pct = df_positive.head(3)['pct_of_total'].sum() if len(df_positive) >= 3 else df_positive['pct_of_total'].sum()
        new_investments = len(df[df['activity_status'].str.contains('New', na=False)])

        with m1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Total LP Return</div>
                <div class="metric-value">{d.get('total_net_income','—')}</div>
                <div class="metric-sub">Net attributed income</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Underlying Companies</div>
                <div class="metric-value">{len(portcos)}</div>
                <div class="metric-sub">{new_investments} new this year</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            top1_pct = f"{top1['pct_of_total']:.1f}%" if top1 is not None else "—"
            top1_name = top1['name'][:28] + '...' if top1 is not None and len(top1['name']) > 28 else (top1['name'] if top1 is not None else '—')
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Top Company Concentration</div>
                <div class="metric-value">{top1_pct}</div>
                <div class="metric-sub">{top1_name}</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Top 3 Concentration</div>
                <div class="metric-value">{top3_pct:.1f}%</div>
                <div class="metric-sub">of positive returns</div>
            </div>""", unsafe_allow_html=True)

        # Summary
        st.markdown('<div class="section-header">Portfolio Intelligence Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-card">{d.get("plain_english_summary","")}</div>', unsafe_allow_html=True)

        # Flags
        flags = d.get('intelligence_flags', [])
        if flags:
            st.markdown('<div class="section-header">Intelligence Flags</div>', unsafe_allow_html=True)
            for flag in flags:
                st.markdown(f'<div class="flag-card">⚑ {flag}</div>', unsafe_allow_html=True)

        # Charts
        st.markdown('<div class="section-header">Return Attribution by Underlying Company</div>', unsafe_allow_html=True)
        chart_col, table_col = st.columns([1.2, 1])

        with chart_col:
            if len(df_positive) > 0:
                fig = px.bar(
                    df_positive,
                    x='lp_income', y='name', orientation='h',
                    color='pct_of_total',
                    color_continuous_scale=[[0, '#EEF4F0'], [0.5, '#2D5A3D'], [1, '#1A3C2A']],
                    labels={'lp_income': 'LP Income ($)', 'name': '', 'pct_of_total': '% of Return'},
                )
                fig.update_layout(
                    plot_bgcolor='white', paper_bgcolor='white',
                    font_family='Georgia', height=max(300, len(df_positive) * 35 + 100),
                    margin=dict(l=10, r=10, t=20, b=10),
                    coloraxis_showscale=False,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with table_col:
            display_df = df[['name', 'industry', 'activity_status', 'lp_income_formatted', 'pct_of_total']].copy()
            display_df.columns = ['Company', 'Industry', 'Status', 'LP Income', '% Total']
            display_df['% Total'] = display_df['% Total'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)

        # Sector breakdown
        if 'industry' in df.columns:
            ind_df = df[df['lp_income'] > 0].groupby('industry')['lp_income'].sum().reset_index()
            st.markdown('<div class="section-header">Sector Exposure</div>', unsafe_allow_html=True)
            fig3 = px.pie(
                ind_df, values='lp_income', names='industry',
                color_discrete_sequence=px.colors.sequential.Greens_r,
            )
            fig3.update_layout(
                font_family='Georgia', height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")
        st.markdown("""
<div style="text-align:center; font-size:0.75rem; color:#999; font-style:italic; padding:1rem 0;">
    COMMONWEALTH PERPETUA &nbsp;·&nbsp; Confidential &nbsp;·&nbsp; For institutional use only
</div>
""", unsafe_allow_html=True)

else:
    st.markdown("""
<div style="text-align:center; padding:4rem 2rem; color:#888;">
    <div style="font-size:3rem; margin-bottom:1rem;">⚖️</div>
    <div style="font-size:1.1rem; font-style:italic;">Upload a fund document to generate portfolio intelligence</div>
</div>
""", unsafe_allow_html=True)
