"""
Instagram DM Lead Manager
A simple CRM for small businesses tracking leads from Instagram DMs.
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

DB_PATH = "leads.db"

def get_connection():
    """Return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the leads table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                username    TEXT    NOT NULL,
                phone       TEXT,
                inquiry     TEXT,
                status      TEXT    DEFAULT 'New',
                notes       TEXT,
                date_added  TEXT    NOT NULL,
                followup_date TEXT
            )
        """)
        conn.commit()


# ─────────────────────────────────────────────
# CRUD OPERATIONS
# ─────────────────────────────────────────────

def add_lead(name, username, phone, inquiry, status, notes, followup_date):
    """Insert a new lead into the database."""
    today = date.today().isoformat()
    followup_str = followup_date.isoformat() if followup_date else None
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO leads (name, username, phone, inquiry, status, notes, date_added, followup_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, username, phone, inquiry, status, notes, today, followup_str))
        conn.commit()


def get_all_leads():
    """Return all leads as a DataFrame."""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM leads ORDER BY date_added DESC", conn)
    return df


def get_lead_by_id(lead_id):
    """Return a single lead dict by ID."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    return dict(row) if row else None


def update_lead(lead_id, status, notes, followup_date):
    """Update status, notes, and follow-up date for a lead."""
    followup_str = followup_date.isoformat() if followup_date else None
    with get_connection() as conn:
        conn.execute("""
            UPDATE leads SET status = ?, notes = ?, followup_date = ?
            WHERE id = ?
        """, (status, notes, followup_str, lead_id))
        conn.commit()


def delete_lead(lead_id):
    """Delete a lead by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()


def insert_demo_data():
    """Insert sample demo leads so new users can explore the app."""
    today = date.today()
    samples = [
        ("Aisha Mehta",    "@aisha.mehta",    "9876543210", "Interested in custom embroidery hoodies",      "Interested",      "Wants 5 pieces in navy blue. Waiting for size chart.", (today + timedelta(days=2)).isoformat()),
        ("Rohan Kapoor",   "@rohankapoor_",   "",           "Asked for pricing on logo tote bags",           "Follow-up",       "Sent price list. No reply yet.",                      (today - timedelta(days=1)).isoformat()),
        ("Sneha D",        "@sneha.deshpande", "9123456789","Wants birthday gift hamper, budget ₹1500",      "New",             "",                                                    None),
        ("Vikram Nair",    "@vikram_nair22",  "",           "Bulk order inquiry — 50 custom mugs for office","Closed",          "Order confirmed. Payment received.",                  None),
        ("Priya Sharma",   "@priyasharma_art","8800001234", "Wants to know if we ship to Pune",             "Not Interested",  "Said shipping cost was too high.",                    None),
        ("Kabir Hussain",  "@kabirhussain",   "",           "Custom phone case with photo print",            "Interested",      "Shared 3 reference images. Awaiting final approval.", (today + timedelta(days=5)).isoformat()),
        ("Meera Joshi",    "@meeraj_99",      "9988776655", "Wedding return gifts — 100 qty, personalised", "Follow-up",       "Big potential order. Call scheduled.",                (today).isoformat()),
    ]
    with get_connection() as conn:
        for s in samples:
            conn.execute("""
                INSERT INTO leads (name, username, phone, inquiry, status, notes, date_added, followup_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (*s[:6], (today - timedelta(days=len(samples))).isoformat(), s[6]))
        conn.commit()


# ─────────────────────────────────────────────
# CUSTOM CSS — clean, modern, minimal
# ─────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0f0f0f;
    }
    [data-testid="stSidebar"] * {
        color: #f0f0f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 15px;
        font-weight: 500;
        padding: 6px 0;
        cursor: pointer;
    }

    /* Main background */
    .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #f8f8f8;
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        padding: 14px 18px;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-new           { background: #dbeafe; color: #1d4ed8; }
    .badge-interested    { background: #dcfce7; color: #166534; }
    .badge-not-interested{ background: #fee2e2; color: #991b1b; }
    .badge-follow-up     { background: #fef9c3; color: #854d0e; }
    .badge-closed        { background: #f3f4f6; color: #374151; }

    /* Overdue highlight */
    .overdue-row {
        background: #fff1f1;
        border-left: 3px solid #ef4444;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .due-today-row {
        background: #fffbeb;
        border-left: 3px solid #f59e0b;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .upcoming-row {
        background: #f0fdf4;
        border-left: 3px solid #22c55e;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }

    /* Section headings */
    h2 { font-weight: 600; letter-spacing: -0.5px; }
    h3 { font-weight: 500; color: #333; }

    /* Subtle divider */
    hr { border: none; border-top: 1px solid #ececec; margin: 1.5rem 0; }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border-color: #e0e0e0 !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #0f0f0f;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 22px;
        font-weight: 500;
        font-family: 'DM Sans', sans-serif;
    }
    .stButton > button[kind="primary"]:hover {
        background: #333;
    }

    /* Secondary button */
    .stButton > button {
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
    }

    /* Success/warning/error messages */
    .stSuccess, .stWarning, .stError {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STATUS CONFIG
# ─────────────────────────────────────────────

STATUSES = ["New", "Interested", "Not Interested", "Follow-up", "Closed"]

STATUS_BADGE = {
    "New":           "badge-new",
    "Interested":    "badge-interested",
    "Not Interested":"badge-not-interested",
    "Follow-up":     "badge-follow-up",
    "Closed":        "badge-closed",
}

STATUS_EMOJI = {
    "New":           "🔵",
    "Interested":    "🟢",
    "Not Interested":"🔴",
    "Follow-up":     "🟡",
    "Closed":        "⚪",
}


def badge_html(status):
    cls = STATUS_BADGE.get(status, "badge-new")
    return f'<span class="badge {cls}">{status}</span>'


# ─────────────────────────────────────────────
# PAGE: ADD LEAD
# ─────────────────────────────────────────────

def page_add_lead():
    st.markdown("## ➕ Add New Lead")
    st.markdown("Fill in the details from the Instagram DM conversation.")
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.form("add_lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name *", placeholder="e.g. Aisha Mehta")
        with col2:
            username = st.text_input("Instagram Username *", placeholder="e.g. @aisha.mehta")

        col3, col4 = st.columns(2)
        with col3:
            phone = st.text_input("Phone Number", placeholder="Optional")
        with col4:
            status = st.selectbox("Lead Status", STATUSES)

        inquiry = st.text_area("What did they ask? (Inquiry)", placeholder="e.g. Interested in custom hoodies, wants 5 pieces in navy blue", height=100)
        notes   = st.text_area("Notes", placeholder="Any additional context or follow-up points", height=80)
        followup_date = st.date_input("Follow-up Date (optional)", value=None)

        submitted = st.form_submit_button("Save Lead", type="primary", use_container_width=True)

    if submitted:
        if not name.strip() or not username.strip():
            st.error("Customer Name and Instagram Username are required.")
        else:
            add_lead(name.strip(), username.strip(), phone.strip(),
                     inquiry.strip(), status, notes.strip(), followup_date)
            st.success(f"✅ Lead **{name}** added successfully!")
            st.balloons()


# ─────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────

def page_dashboard():
    st.markdown("## 📋 Lead Dashboard")

    df = get_all_leads()

    if df.empty:
        st.info("No leads yet. Add your first lead from the sidebar, or load demo data below.")
        if st.button("Load Demo Data"):
            insert_demo_data()
            st.success("Demo leads added!")
            st.rerun()
        return

    # ── Metrics row ──
    total      = len(df)
    new_count  = len(df[df["status"] == "New"])
    interested = len(df[df["status"] == "Interested"])
    followup   = len(df[df["status"] == "Follow-up"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Leads",  total)
    m2.metric("New",          new_count)
    m3.metric("Interested",   interested)
    m4.metric("Follow-ups",   followup)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Filters ──
    fc1, fc2 = st.columns([2, 3])
    with fc1:
        status_filter = st.selectbox("Filter by Status", ["All"] + STATUSES)
    with fc2:
        search = st.text_input("Search by Name or Username", placeholder="Type to search…")

    filtered = df.copy()
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if search.strip():
        q = search.strip().lower()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(q) |
            filtered["username"].str.lower().str.contains(q)
        ]

    st.markdown(f"**{len(filtered)} lead(s) found**")
    st.markdown("<hr>", unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No leads match your filters.")
        return

    # ── Lead cards / table ──
    for _, row in filtered.iterrows():
        with st.expander(f"{STATUS_EMOJI.get(row['status'], '')}  {row['name']}  ·  {row['username']}  ·  Added {row['date_added']}"):
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**Inquiry:** {row['inquiry'] or '—'}")
                st.markdown(f"**Notes:** {row['notes'] or '—'}")
                st.markdown(f"**Phone:** {row['phone'] or '—'}")
                st.markdown(f"**Follow-up date:** {row['followup_date'] or '—'}")
            with c2:
                st.markdown(f"**Status:** {badge_html(row['status'])}", unsafe_allow_html=True)

            st.markdown("")
            # ── Inline update form ──
            with st.form(f"update_{row['id']}"):
                new_status = st.selectbox("Update Status", STATUSES,
                                          index=STATUSES.index(row["status"]),
                                          key=f"s_{row['id']}")
                new_notes  = st.text_area("Notes", value=row["notes"] or "",
                                          key=f"n_{row['id']}", height=70)
                current_fu = datetime.strptime(row["followup_date"], "%Y-%m-%d").date() \
                             if row["followup_date"] else None
                new_fu     = st.date_input("Follow-up Date", value=current_fu,
                                           key=f"f_{row['id']}")

                ucol1, ucol2 = st.columns([1, 1])
                with ucol1:
                    save = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with ucol2:
                    delete = st.form_submit_button("🗑 Delete Lead", use_container_width=True)

            if save:
                update_lead(row["id"], new_status, new_notes, new_fu)
                st.success("Updated!")
                st.rerun()
            if delete:
                delete_lead(row["id"])
                st.warning("Lead deleted.")
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Load Demo Data (adds sample leads)"):
        insert_demo_data()
        st.success("Demo leads added!")
        st.rerun()


# ─────────────────────────────────────────────
# PAGE: FOLLOW-UPS
# ─────────────────────────────────────────────

def page_followups():
    st.markdown("## 🔔 Follow-up Tracker")
    st.markdown("Leads that need your attention based on follow-up dates.")
    st.markdown("<hr>", unsafe_allow_html=True)

    df = get_all_leads()

    # Only leads with a follow-up date
    fu_df = df[df["followup_date"].notna() & (df["followup_date"] != "")].copy()

    if fu_df.empty:
        st.info("No follow-up dates set yet. Add one while editing a lead in the Dashboard.")
        return

    today = date.today()
    fu_df["followup_date_parsed"] = pd.to_datetime(fu_df["followup_date"]).dt.date
    fu_df["days_diff"] = fu_df["followup_date_parsed"].apply(lambda d: (d - today).days)
    fu_df = fu_df.sort_values("days_diff")

    overdue   = fu_df[fu_df["days_diff"] < 0]
    due_today = fu_df[fu_df["days_diff"] == 0]
    upcoming  = fu_df[fu_df["days_diff"] > 0]

    def render_card(row, css_class, label):
        days = int(row["days_diff"])
        if days < 0:
            time_label = f"**{abs(days)} day(s) overdue**"
        elif days == 0:
            time_label = "**Due today**"
        else:
            time_label = f"In {days} day(s)"

        st.markdown(f"""
        <div class="{css_class}">
            <strong>{row['name']}</strong> &nbsp; <span style="color:#888">{row['username']}</span><br>
            <span style="font-size:13px; color:#555">
                📅 {row['followup_date']} &nbsp;|&nbsp; {time_label} &nbsp;|&nbsp;
                {badge_html(row['status'])}
            </span><br>
            <span style="font-size:13px; margin-top:4px; display:block; color:#444">
                💬 {row['inquiry'] or '—'}
            </span>
            {f'<span style="font-size:12px; color:#666; margin-top:4px; display:block;">📝 {row["notes"]}</span>' if row["notes"] else ''}
        </div>
        """, unsafe_allow_html=True)

    if not overdue.empty:
        st.markdown(f"### 🔴 Overdue ({len(overdue)})")
        for _, row in overdue.iterrows():
            render_card(row, "overdue-row", "overdue")

    if not due_today.empty:
        st.markdown(f"### 🟡 Due Today ({len(due_today)})")
        for _, row in due_today.iterrows():
            render_card(row, "due-today-row", "today")

    if not upcoming.empty:
        st.markdown(f"### 🟢 Upcoming ({len(upcoming)})")
        for _, row in upcoming.iterrows():
            render_card(row, "upcoming-row", "upcoming")

    if overdue.empty and due_today.empty and upcoming.empty:
        st.success("You're all caught up! No pending follow-ups.")


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="InstaLeads — DM CRM",
        page_icon="📩",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()
    init_db()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("## 📩 InstaLeads")
        st.markdown("*Your Instagram DM CRM*")
        st.markdown("---")

        page = st.radio(
            "Navigate",
            ["➕ Add Lead", "📋 Dashboard", "🔔 Follow-ups"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Quick stats in sidebar
        df = get_all_leads()
        if not df.empty:
            st.markdown("**Quick Stats**")
            for s in STATUSES:
                cnt = len(df[df["status"] == s])
                if cnt > 0:
                    st.markdown(f"{STATUS_EMOJI[s]} {s}: **{cnt}**")

        st.markdown("---")
        st.markdown(
            "<span style='font-size:11px; color:#888'>Built for small business owners.<br>Track every DM. Miss no customer.</span>",
            unsafe_allow_html=True
        )

    # ── Page routing ──
    if page == "➕ Add Lead":
        page_add_lead()
    elif page == "📋 Dashboard":
        page_dashboard()
    elif page == "🔔 Follow-ups":
        page_followups()


if __name__ == "__main__":
    main()
