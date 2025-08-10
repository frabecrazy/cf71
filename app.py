import streamlit as st
import pandas as pd
import random
import plotly.express as px
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Digital Carbon Footprint Calculator", layout="wide")

# Init session state
if "page" not in st.session_state or st.session_state.page not in ["intro", "main", "guess", "results", "virtues"]:
    st.session_state.page = "intro"
if "role" not in st.session_state:
    st.session_state.role = ""
if "device_inputs" not in st.session_state:
    st.session_state.device_inputs = {}
if "results" not in st.session_state:
    st.session_state.results = {}
if "archetype_guess" not in st.session_state:
    st.session_state.archetype_ = None

activity_factors = {
    "Student": {
        "MS Office (e.g. Excel, Word, PPT…)": 0.00901,
        "Technical softwares (e.g. Matlab, Python…)": 0.00901,
        "Web browsing": 0.0264,
        "Watching lecture recordings": 0.0439,
        "Online classes streaming or video call": 0.112,
        "Reading study materials on your computer (e.g. slides, articles, digital textbooks)": 0.00901
    },
    "Professor": {
        "MS Office (e.g. Excel, Word, PPT…)": 0.00901,
        "Web browsing": 0.0264,
        "Videocall (e.g. Zoom, Teams…)": 0.112,
        "Online classes streaming": 0.112,
        "Reading materials on your computer (e.g. slides, articles, digital textbooks)": 0.00901,
        "Technical softwares (e.g. Matlab, Python…)": 0.00901
    },
    "Staff Member": {
        "MS Office (e.g. Excel, Word, PPT…)": 0.00901,
        "Management software (e.g. SAP)": 0.00901,
        "Web browsing": 0.0264,
        "Videocall (e.g. Zoom, Teams…)": 0.112,
        "Reading materials on your computer (e.g. documents)": 0.00901
    }
}

ai_factors = {
    "Summarize texts or articles": 0.000711936,
    "Translate sentences or texts": 0.000363008,
    "Explain a concept": 0.000310784,
    "Generate quizzes or questions": 0.000539136,
    "Write formal emails or messages": 0.000107776,
    "Correct grammar or style": 0.000107776,
    "Analyze long PDF documents": 0.001412608,
    "Write or test code": 0.002337024,
    "Generate images": 0.00206,
    "Brainstorm for thesis or projects": 0.000310784,
    "Explain code step-by-step": 0.003542528,
    "Prepare lessons or presentations": 0.000539136
}

device_ef = {
    "Desktop Computer": 296,
    "Laptop Computer": 170,
    "Smartphone": 38.4,
    "Tablet": 87.1,
    "External Monitor": 235,
    "Headphones": 12.17,
    "Printer": 62.3,
    "Router/Modem": 106
}

eol_modifier = {
    "I bring it to a certified e-waste collection center": -0.224,
    "I throw it away in general waste": 0.611,
    "I return it to manufacturer for recycling or reuse": -0.3665,
    "I sell or donate it to someone else": -0.445,
    "I store it at home, unused": 0.402
}

DAYS = 250  # Typical number of work/study days per year


emails = {
    "-- Select option --": 0,
    "1–10": 5,
    "11–20": 15,
    "21–30": 25,
    "31–40": 35,
    "> 40": 50,
}
cloud_gb = {
    "-- Select option --": 0,
    "<5GB": 2.5,
    "5–20GB": 12.5,
    "20–50GB": 35,
    "50–100GB": 75,
}

ARCHETYPES = [
    {
        "key": "Devices",
        "name": "Lord of the Latest Gadgets",
        "category": "Devices",
        "image": "lord_of_the_latest_gadgets.png",   # file nella stessa cartella di app.py
    },
    {
        "key": "ai",
        "name": "Prompt Pirate, Ruler of the Queries",
        "category": "Artificial Intelligence",
        "image": "prompt_pirate.png",
    },
    {
        "key": "weee",
        "name": "Guardian of the Eternal E-Waste Pile",
        "category": "E-Waste",
        "image": "guardian_ewaste.png",
    },
    {
        "key": "activities",
        "name": "Master of Endless Streams",
        "category": "Digital Activities",
        "image": "master_endless_streams.png",
    },
]

AVERAGE_CO2_BY_ROLE = {
    "Student": 300,        # <-- metti i tuoi numeri
    "Professor": 300,
    "Staff member": 300,
}

# INTRO PAGE 

def show_intro():
    # --- STILE GLOBALE ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4 {
            color: #1d3557;
        }

        .intro-box {
            background: linear-gradient(to right, #d8f3dc, #a8dadc);
            padding: 40px 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 18px rgba(0,0,0,0.06);
            margin-bottom: 30px;
        }

        .selectbox-container {
            background-color: #f1faee;
            border-left: 5px solid #52b788;
            border-radius: 10px;
            padding: 20px;
            margin-top: 25px;
        }

        .start-button {
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HERO INTUITIVO ---
    st.markdown("""
        <div class="intro-box">
            <h1 style="font-size: 2.6em;">📱 Digital Carbon Footprint Calculator</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- TESTO DESCRITTIVO ---
    st.markdown("""
Welcome to the **Digital Carbon Footprint Calculator**, a tool developed within the *Green DiLT* project to raise awareness about the hidden environmental impact of digital habits in academia.

This calculator is tailored for **university students, professors, and staff members**, helping you estimate your CO₂e emissions from everyday digital activities, often overlooked, but increasingly relevant.

---

👉 Please enter your details to begin:
""")

    # --- SELECTBOX ---
    with st.container():
        st.session_state.role = st.selectbox(
            "What is your role in academia?",
            ["", "Student", "Professor", "Staff Member"]
        )

    # --- INPUT NOME ---
    st.session_state.name = st.text_input("What is your name")

    # --- BOTTONE START ---
    st.markdown('<div class="start-button">', unsafe_allow_html=True)
    if st.button("➡️ Start Calculation"):
        if st.session_state.role and st.session_state.name.strip():
            st.session_state.page = "main"
            st.rerun()
        else:
            st.warning("⚠️ Please enter your name and select your role before continuing.")
    st.markdown('</div>', unsafe_allow_html=True)


# MAIN PAGE
def show_main():
    st.markdown("""
        <style>
            .device-box {
                padding: 10px 15px 15px 10px;
                border-radius: 12px;
                margin-top: 15px;
                margin-bottom: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .device-header { font-size: 1.4em; font-weight: 600; color: #1d3557; margin-bottom: 10px; }
            .stMarkdown { margin-bottom: 2px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background: linear-gradient(to right, #d8f3dc, #a8dadc);
        padding: 25px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        text-align: center;
        margin-bottom: 20px;
    ">
        <h1 style="font-size: 2.2em; color:#1d3557; margin-bottom: 0;">
            Hello <b>{st.session_state.name}</b>, it’s time to uncover the impact of your digital world! 🚀
        </h1>
    </div>
""", unsafe_allow_html=True)


    st.markdown(f"""
        <p style="font-size: 1em; color: #6c757d; margin-top: -8px;">
            First, we’ll ask you a few quick questions about your studying/working habits. This will take less than <b>5 minutes</b>.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h3 style="margin-top: 25px; color:#1d3557;">💻 Devices & E-Waste</h3>
        <p>Choose the digital devices you currently use, and for each one, provide a few details about how you use it and what you do when it's no longer needed.</p>
    """, unsafe_allow_html=True)

    # --- STATE INIT ---
    if "device_list" not in st.session_state:
        st.session_state.device_list = []
    if "device_expanders" not in st.session_state:
        st.session_state.device_expanders = {}
    if "device_inputs" not in st.session_state:
        st.session_state.device_inputs = {}
    # NEW: token per expander per forzare re-mount alla conferma
    if "expander_tokens" not in st.session_state:
        st.session_state.expander_tokens = {}

    device_to_add = st.selectbox("Select a device and click 'Add Device', repeat for all the devices you own", ["-- Select --"] + list(device_ef.keys()))
    if st.button("➕ Add Device"):
        if device_to_add == "-- Select --":
            st.warning("Please select a valid device before adding.")
        else:
            count = sum(d.startswith(device_to_add) for d in st.session_state.device_list)
            new_id = f"{device_to_add}_{count}"
            st.session_state.device_list.insert(0, new_id)
            st.session_state.device_inputs[new_id] = {"years": 1.0, "used": "-- Select --", "shared": "-- Select --", "eol": "-- Select --"}
            st.session_state.device_expanders[new_id] = True       # aggiungo aperto
            st.session_state.expander_tokens[new_id] = 0            # NEW

    total_prod, total_eol = 0, 0

    for device_id in st.session_state.device_list:
        base_device = device_id.rsplit("_", 1)[0]
        prev = st.session_state.device_inputs[device_id]
        is_open = st.session_state.device_expanders.get(device_id, True)
        token = st.session_state.expander_tokens.get(device_id, 0)

        # Cambiamo l’etichetta SOLO quando vogliamo forzare la chiusura
        suffix = "" if is_open else ("\u200B" * (token + 1))
        label = f"{base_device}{suffix}"

        with st.expander(label, expanded=is_open):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                    <div style='margin-bottom:-20px'>
                        <strong>Ownership</strong><br/>
                        <span style='font-size:12px; color:gray'>Is this device used only by you or shared?</span>
                    </div>
                """, unsafe_allow_html=True)
                shared_options = ["-- Select --", "Personal", "Shared"]
                shared_index = shared_options.index(prev["shared"]) if prev["shared"] in shared_options else 0
                shared = st.selectbox("", shared_options, index=shared_index, key=f"{device_id}_shared")

            with col2:
                st.markdown("""
                    <div style='margin-bottom:-20px'>
                        <strong>Condition</strong><br/>
                        <span style='font-size:12px; color:gray'>Was the device new or used when you got it?</span>
                    </div>
                """, unsafe_allow_html=True)
                used_options = ["-- Select --", "New", "Used"]
                used_index = used_options.index(prev["used"]) if prev["used"] in used_options else 0
                used = st.selectbox("", used_options, index=used_index, key=f"{device_id}_used")

            with col3:
                st.markdown("""
                    <div style='margin-bottom:-20px'>
                        <strong>Device's lifespan</strong><br/>
                        <span style='font-size:12px; color:gray'>How many years you plan to use the device in total</span>
                    </div>
                """, unsafe_allow_html=True)
                years = st.number_input("", 0.5, 20.0, step=0.5, format="%.1f", key=f"{device_id}_years")

            with col4:
                st.markdown("""
                    <div style='margin-bottom:-20px'>
                        <strong>End-of-life behavior</strong><br/>
                        <span style='font-size:12px; color:gray'>What do you usually do when the device reaches its end of life?</span>
                    </div>
                """, unsafe_allow_html=True)
                eol_options = ["-- Select --"] + list(eol_modifier.keys())
                eol_index = eol_options.index(prev["eol"]) if prev["eol"] in eol_options else 0
                eol = st.selectbox("", eol_options, index=eol_index, key=f"{device_id}_eol")

            # --- calcoli (immutati) ---
            impact = device_ef.get(base_device, 0)
            if used == "New" and shared == "Personal":
                adj_years = years
            elif used == "Used" and shared == "Personal":
                adj_years = years + (years / 2)
            elif used == "New" and shared == "Shared":
                adj_years = years * 3
            elif used == "Used" and shared == "Shared":
                adj_years = years * 4.5
            else:
                adj_years = years

            eol_mod = eol_modifier.get(eol, 0)
            prod_per_year = impact / adj_years if adj_years else 0
            eol_impact = (impact * eol_mod) / adj_years if adj_years else 0
            total_prod += prod_per_year
            total_eol += eol_impact

            col_remove, _, col_confirm = st.columns([1, 8, 1])

            with col_remove:
                if st.button(f"🗑 Remove", key=f"remove_{device_id}"):
                    st.session_state.device_list.remove(device_id)
                    st.session_state.device_inputs.pop(device_id, None)
                    st.session_state.device_expanders.pop(device_id, None)
                    st.session_state.expander_tokens.pop(device_id, None)  # NEW
                    st.rerun()

            with col_confirm:
                confirm_key = f"confirm_{device_id}"
                if st.button("✅ Confirm", key=confirm_key):
                    if "-- Select --" in [used, shared, eol]:
                        st.warning("Please complete all fields before confirming.")
                    else:
                        st.session_state.device_inputs[device_id] = {
                            "years": years, "used": used, "shared": shared, "eol": eol
                        }
                        # Forza CHIUSURA e RE-MOUNT alla prossima esecuzione
                        st.session_state.device_expanders[device_id] = False
                        st.session_state.expander_tokens[device_id] = st.session_state.expander_tokens.get(device_id, 0) + 1
                        st.rerun()



    # === DIGITAL ACTIVITIES ===

    st.markdown("""
        <h3 style="margin-top: 25px; color:#1d3557;">🔌 Digital Activities</h3>
        <p>
            Estimate how many hours per day you spend on each activity during a typical 8-hour study or work day.
            <br>
            <b style="color: #40916c;">You may exceed 8 hours if multitasking</b> 
            <span style="color: #495057;">(e.g., watching a lecture while writing notes).</span>
        </p>
    """, unsafe_allow_html=True)

    role = st.session_state.role
    ore_dict = {}
    hours_total = 0
    col1, col2 = st.columns(2)

    # Sliders con -- Select --
    for i, (act, ef) in enumerate(activity_factors[role].items()):
        with (col1 if i % 2 == 0 else col2):
            ore = st.slider(
                f"{act} (h/day)",
                min_value=0.0,
                max_value=8.0,
                value=0.0,
                step=0.5,
                key=f"slider_{act}"
            )
            ore_dict[act] = ore

    total_hours_raw = sum(ore_dict.values())
    warn_color = "#B58900"  # giallo scuro
    color = "#6EA8FE" if total_hours_raw <= 8 else warn_color

    # Riga totale ore (con colore condizionale)
    st.markdown(
        f"<div style='text-align:right; font-size:0.9rem; color:{color}; margin-top:-6px;'>"
        f"Total: <b>{total_hours_raw:.1f}</b> h/day</div>",
        unsafe_allow_html=True
    )

    # Nota esplicativa se supera 8h
    if total_hours_raw > 8:
        st.markdown(
            "<div style='text-align:right; font-size:0.85rem; color:#B58900; margin-top:-8px;'>"
            "Overlapping activities can push the total above 8 hours.</div>",
            unsafe_allow_html=True
        )


    
    for act, ore in ore_dict.items():
        hours_total += ore * activity_factors[role][act] * DAYS
    
    # Parte 2: Email, cloud, printing, connectivity
    st.markdown("""
        <hr style="margin-top: 30px; margin-bottom: 20px;">
        <p style="font-size: 17px; line-height: 1.5;">
            Now tell us more about your habits related to <b style="color: #40916c;">email, cloud, printing and connectivity</b>.
        </p>
        <p style="font-size: 13px; color: gray; margin-top: 8px;">
            How many study or work emails do you send or receive in a typical 8-hour day? 
            Please do not count spam messages.
        </p>
    """, unsafe_allow_html=True)

    email_opts = ["-- Select option --", "1–10", "11–20", "21–30", "31–40", "> 40"]
    cloud_opts = ["-- Select option --", "<5GB", "5–20GB", "20–50GB", "50–100GB"]


    email_col1, email_col2 = st.columns(2)

    with email_col1:
        email_plain = st.selectbox("Emails (no attachments)", email_opts, index=0, key="email_plain")

    with email_col2:
        email_attach = st.selectbox("Emails (with attachments)", email_opts, index=0, key="email_attach")

    cloud = st.selectbox("Cloud storage you currently use for academic or work-related files (e.g., on iCloud, Google Drive, OneDrive)", cloud_opts, index=0, key="cloud")

    wifi = st.slider("Estimate your daily Wi-Fi connection time during a typical 8-hour study or work day, including hours when you're not actively using your device (e.g., background apps, idle mode)", 0.0, 8.0, 4.0, 0.5, key="wifi")
    pages = st.number_input("Printed pages per day", 0, 100, 0, key="pages")

    idle = st.radio("When you're not using your computer...", ["I turn it off", "I leave it on (idle mode)", "I don’t have a computer"],
    key="idle")


# --- CALCOLI 
    em_plain  = emails.get(st.session_state.get("email_plain"), 0)
    em_attach = emails.get(st.session_state.get("email_attach"), 0)
    cld = cloud_gb.get(st.session_state.get("cloud"), 0)

    mail_total = (em_plain * 0.004 + em_attach * 0.035 + cld * 0.01) * DAYS
    wifi_total  = st.session_state.get("wifi", 4.0) * 0.00584 * DAYS
    print_total = st.session_state.get("pages", 0) * 0.0045 * DAYS

    idle_val = st.session_state.get("idle")
    if idle_val == "I leave it on (idle mode)":
        idle_total = DAYS * 0.0104 * 16
    elif idle_val == "I turn it off":
        idle_total = DAYS * 0.0005204 * 16
    else:
        idle_total = 0

    digital_total = hours_total + mail_total + wifi_total + print_total + idle_total


    # === AI TOOLS ===
    st.markdown("""
    <h3 style="margin-top: 25px; color:#1d3557;">🦾 AI Tools</h3>
    <p>
        Estimate how many queries you make for each AI-powered task on a typical 8-hour study/working day.
        As a reference, users submit approximately 15 to 20 queries during a half-hour interaction with an AI assistant.
    </p>
    """, unsafe_allow_html=True)

    ai_total = 0
    ai_queries_count = 0
    cols = st.columns(4)

    for i, (task, ef) in enumerate(ai_factors.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style='margin-bottom: 12px;'>
                <div style='
                    font-weight: 600;
                    font-size: 15px;
                    color: #1d3557;
                    margin-bottom: 6px;
                '>
                    {task}
                </div>
            """, unsafe_allow_html=True)

            q = st.number_input(
                label="",
                min_value=0,
                max_value=10000,
                value=0,
                step=5,
                key=task,
                label_visibility="collapsed"
            )
            ai_total += q * ef * DAYS
            ai_queries_count += int(q)

            st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.ai_total_queries = ai_queries_count


    # === FINAL BUTTONS (BACK + NEXT) ===
    col_back, col_space, col_next = st.columns([1, 4, 1])

    with col_back:
        if st.button("⬅️ Back", key="main_back_btn", use_container_width=True):
            st.session_state.page = "intro"  # Oppure "main" se serve tornare a una sottosezione
            st.rerun()

    with col_next:
        next_clicked = st.button(
            f"Next ➡️",
            key="main_next_btn",
            use_container_width=True
        )

    # --- LOGICA DEL NEXT ---
    if next_clicked:
        unconfirmed_devices = [
            key for key in st.session_state.get("device_expanders", {})
            if st.session_state.device_expanders[key]
        ]

        missing_activities = (
            st.session_state.get("email_plain", "-- Select option --") == "-- Select option --"
            or st.session_state.get("email_attach", "-- Select option --") == "-- Select option --"
            or st.session_state.get("cloud", "-- Select option --") == "-- Select option --"
        )

        # Mostra eventuali warning
        if unconfirmed_devices:
            st.warning("⚠️ You have devices not yet confirmed. Please click 'Confirm' in each box to proceed.")
        if missing_activities:
            st.warning("⚠️ Please complete all digital activity fields before continuing.")

        # Procedi solo se tutto è OK
        if not unconfirmed_devices and not missing_activities:
            st.session_state.results = {
                "Devices": total_prod,
                "E-Waste": total_eol,
                "Digital Activities": digital_total,
                "AI Tools": ai_total
            }
            st.session_state.page = "guess"
            st.rerun()

def show_guess():
    if "archetype_guess" not in st.session_state:
        st.session_state.archetype_guess = None

    # ---- Stili ---- (aggiunta intro-box, senza rimuovere il resto)
    st.markdown("""
        <style>
        .intro-box {
            background: linear-gradient(to right, #d8f3dc, #a8dadc);
            padding: 40px 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 18px rgba(0,0,0,0.06);
            margin-bottom: 30px;
        }
        .arc-card h4{
            margin: 6px 0 10px; text-align:center; color:#1d3557;
            font-weight:800; font-size:1.05rem;
        }
        .arc-badge{
            display:inline-block; margin:10px auto 12px; padding:6px 12px;
            border:1px solid #e9ecef; border-radius:999px; background:#fff;
            color:#1b4332; font-weight:700; font-size:.9rem;
        }
        .picked { box-shadow: 0 0 0 3px #52b788 inset; border-radius: 12px; }
        div[data-testid="stVerticalBlockBorderWrapper"] > div:empty { display:none; }
        </style>
    """, unsafe_allow_html=True)

    # --- Box identico a intro ---
    st.markdown(f"""
        <div class="intro-box">
            <h2 style="margin:.2rem 0;">{st.session_state.get('name','')}, before you discover your full Digital Carbon Footprint, take a guess!</h2>
            <p style="margin:.2rem 0; color:#1b4332;">
                Based on the area where you think you have the biggest impact, which digital archetype matches you best?
            </p>
        </div>
    """, unsafe_allow_html=True)


    cols = st.columns(4)
    for i, arc in enumerate(ARCHETYPES):
        with cols[i]:
            # contenitore unico con bordo (titolo+img+badge+bottone)
            cont = st.container(border=True)
            with cont:
                # aggiungo una classe 'picked' al contenitore se selezionato
                if st.session_state.get("archetype_guess") == arc["key"]:
                    st.markdown('<div class="picked">', unsafe_allow_html=True)

                st.markdown(f"<div class='arc-card'><h4>{arc['name']}</h4></div>", unsafe_allow_html=True)
                st.image(arc["image"], use_container_width=True)
                st.markdown(f"<div style='text-align:center;'><span class='arc-badge'>{arc['category']}</span></div>",
                            unsafe_allow_html=True)

                if st.button("Choose", key=f"choose_{arc['key']}", use_container_width=True):
                    st.session_state.archetype_guess = arc["key"]
                    st.rerun()

                if st.session_state.get("archetype_guess") == arc["key"]:
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ")
    left, _, right = st.columns([1, 4, 1])
    with left:
        if st.button("⬅️ Back", key="guess_back_btn", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
    with right:
        if st.button("Discover your Carbon Footprint➡️",
                     key="guess_continue_btn",
                     use_container_width=True,
                     disabled=st.session_state.get("archetype_guess") is None):
            st.session_state.page = "results"
            st.rerun()


# RESULTS PAGE

def show_results():

    # --- STILE GLOBALE ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4 {
            color: #1d3557;
        }

        .tip-card {
            background-color: #e3fced;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }

        .equiv-card {
            background-color: white;
            border-left: 6px solid #52b788;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
        }

        .equiv-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }

        footer {
            text-align: center;
            font-size: 0.8em;
            color: #999;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HERO SECTION ---
    st.markdown("""
        <div style="
            background: linear-gradient(to right, #d8f3dc, #a8dadc);
            padding: 40px 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        ">
            <h1 style="font-size: 2.8em; margin-bottom: 0.1em;">🌍 Your Digital Carbon Footprint</h1>
            <p style="font-size: 1.2em; color: #1b4332;">Discover your impact — and what to do about it.</p>
        </div>
    """, unsafe_allow_html=True)

    res = st.session_state.results
    total = sum(res.values())

    # --- CARICAMENTO ---
    with st.spinner("🔍 Calculating your footprint..."):
        time.sleep(1.2)

    # --- RISULTATO TOTALE ---
    # --- CONFRONTO  vs CATEGORIA REALE + TOTALE AFFIANCATI ---

    # mappa valori per categoria e top
    cat_by_value = {
        "Devices": res.get("Devices", 0),
        "E-Waste": res.get("E-Waste", 0),
        "Digital Activities": res.get("Digital Activities", 0),
        "Artificial Intelligence": res.get("AI Tools", 0),
    }
    actual_top = max(cat_by_value, key=cat_by_value.get)

    # mappe derivate dagli ARCHETYPES (no hardcode)
    key_to_category = {a["key"]: a["category"] for a in ARCHETYPES}
    category_to_arc = {a["category"]: a for a in ARCHETYPES}

    # guess scelto dall'utente
    guessed_key = st.session_state.get("archetype_guess")
    guessed = next((a for a in ARCHETYPES if a["key"] == guessed_key), None)

    # archetipo reale in base alla categoria più impattante
    actual = category_to_arc.get(actual_top)

    # ha indovinato?
    guessed_right = bool(guessed) and (key_to_category.get(guessed["key"]) == actual_top)

    # --- 3 CARD: Total, Comparison, Archetype ---

    # Precompute confronto con media
    role_label = st.session_state.get("role", "")
    avg = AVERAGE_CO2_BY_ROLE.get(role_label)
    msg, comp_color = None, "#6EA8FE"
    if isinstance(avg, (int, float)) and avg > 0:
        diff_pct = ((total - avg) / avg) * 100
        abs_pct = abs(diff_pct)
        if abs_pct < 1:
            msg = f"You're roughly in line with the average {role_label.lower()}."
            comp_color = "#6EA8FE"
        elif diff_pct > 0:
            msg = f"You emit ~{abs_pct:.0f}% more than the average {role_label.lower()}."
            comp_color = "#e63946"  # rosso per > media
        else:
            msg = f"You emit ~{abs_pct:.0f}% less than the average {role_label.lower()}."
            comp_color = "#2b8a3e"

    c1, c2, c3 = st.columns(3)
 
    CARD_STYLE = """
        display: flex;
        flex-direction: column;
        justify-content: center;  /* centratura verticale */
        align-items: center;      /* centratura orizzontale */
        min-height: 220px;        /* altezza minima uguale per tutte */
        text-align: center;
    """

    # Card 1 — Total
    with c1:
        card = st.container(border=True)
        with card:
            st.markdown(
                f"<div style='{CARD_STYLE}'>"
                f"<div style='font-size:2rem; color:#1b4332; font-weight:800; margin-bottom:.5rem;'>"
                f"{st.session_state.get('name','')}, your total CO₂e is…</div>"
                f"<div style='font-size:clamp(2.6rem,6vw,3.6rem); line-height:1; font-weight:900; "
                f"color:#ff7f0e; letter-spacing:-0.5px;'>{total:.0f} kg/year</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Card 2 — Comparison vs average
    with c2:
        card = st.container(border=True)
        with card:
            if msg:
                st.markdown(
                    f"<div style='{CARD_STYLE}'>"
                    f"<div style='font-size:1.3rem; font-weight:800; color:#1b4332; margin-bottom:.6rem;'>Your footprint vs average</div>"
                    f"<div style='font-size:2rem; font-weight:800; color:{comp_color}; line-height:1.2; margin-bottom:.4rem;'>{msg}</div>"
                    f"<div style='font-size:1.05rem; color:#1b4332;'>Average {role_label.lower()} emissions: <b>{avg:.0f} kg/year</b></div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='{CARD_STYLE}'>No average available for your role.</div>",
                    unsafe_allow_html=True
                )


    # --- Card 3 • Archetype (usa i file immagine definiti in ARCHETYPES) ---
    from pathlib import Path

    # Fallback nel caso 'actual' non fosse valorizzato (dovrebbe esserlo)
    if actual is None and actual_top in category_to_arc:
        actual = category_to_arc[actual_top]

    # scegli cosa mostrare: se ha indovinato e c'è guessed → guessed, altrimenti actual
    show_arc = guessed if (guessed_right and guessed) else (actual or {})
    arc_name = show_arc.get("name", "")
    arc_img_rel = show_arc.get("image")  # es. 'lord_of_the_latest_gadgets.png'

    # Costruisci path assoluto per evitare MediaFileStorageError sul cloud
    arc_img = None
    if arc_img_rel:
        p = (Path(__file__).parent / arc_img_rel).resolve()
        if p.exists():
            arc_img = str(p)
        else:
            # fallback: prova comunque la stringa relativa (se il working dir combacia)
            arc_img = arc_img_rel

    color = "#1b4332" if guessed_right else "#e63946"
    title = "Great job, you guessed it! Your match is" if guessed_right else "Nice try, but your match is"

    # --- Card 3 • Render: titolo, poi riga con NOME + IMMAGINE affiancati, poi sottotitolo ---
    with c3:
        card = st.container(border=True)
        with card:
            # Titolo (riga intera)
            st.markdown(
                f"<div style='font-size:1.2rem; font-weight:800; margin-bottom:.6rem; color:{color};'>{title}</div>",
                unsafe_allow_html=True
            )

            # Riga: NOME (sx) + IMMAGINE (dx)
            row_l, row_r = st.columns([5, 3])  # aumenta il 2 -> 3 per rendere l'immagine ancora più grande
            with row_l:
                st.markdown(
                    f"<div style='display:flex; align-items:center; min-height:220px; text-align:left;'>"
                    f"<div style='font-weight:800; font-size:2rem; line-height:1.1; color:#ff7f0e;'>{arc_name}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with row_r:
                st.markdown(
                    "<div style='display:flex; align-items:center; justify-content:flex-end; min-height:220px;'>",
                    unsafe_allow_html=True
                )
                if arc_img:
                    st.image(arc_img, width=160)  # 160–180 se la vuoi ancora più grande
                st.markdown("</div>", unsafe_allow_html=True)

            # Sottotitolo (riga intera)
            st.markdown(
                f"<div style='margin-top:.45rem; font-size:1.05rem; color:#1b4332;'>"
                f"Your biggest footprint comes from <b>{actual_top}</b></div>",
                unsafe_allow_html=True
            )


    # --- METRICHE IN GRIGLIA ---
    st.markdown("<br><h4>Breakdown by source:</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
            <div class="tip-card" style="text-align:center;">
                <div style="font-size: 2em;">💻</div>
                <div style="font-size: 1.2em;"><b>{res['Devices']:.2f} kg</b></div>
                <div style="color: #555;">Devices</div>
            </div>
            <div class="tip-card" style="text-align:center;">
                <div style="font-size: 2em;">🗑️</div>
                <div style="font-size: 1.2em;"><b>{res['E-Waste']:.2f} kg</b></div>
                <div style="color: #555;">E-Waste</div>
            </div>
            <div class="tip-card" style="text-align:center;">
                <div style="font-size: 2em;">🔌</div>
                <div style="font-size: 1.2em;"><b>{res['Digital Activities']:.2f} kg</b></div>
                <div style="color: #555;">Digital Activities</div>
            </div>
            <div class="tip-card" style="text-align:center;">
                <div style="font-size: 2em;">🦾</div>
                <div style="font-size: 1.2em;"><b>{res['AI Tools']:.2f} kg</b></div>
                <div style="color: #555;">AI Tools</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- GRAFICO ---
    st.subheader("Breakdown by Category")
    df_plot = pd.DataFrame({
        "Category": ["Devices", "Digital Activities", "Artificial Intelligence", "E-Waste"],
        "CO₂e (kg)": [res["Devices"], res["Digital Activities"], res["AI Tools"], res["E-Waste"]]
    })

    fig = px.bar(df_plot,
                 x="CO₂e (kg)",
                 y="Category",
                 orientation="h",
                 color="Category",
                 color_discrete_sequence=["#95d5b2", "#74c69d", "#52b788", "#1b4332"],
                 height=400)

    fig.update_layout(showlegend=False, 
                      plot_bgcolor="#f1faee", 
                      paper_bgcolor="#f1faee",
                      font_family="Inter")

    fig.update_traces(marker=dict(line=dict(width=1.5, color='white')))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- EQUIVALENZE VISUALI ---
    st.markdown("### With the same emissions, you could…")

    burger_eq = total / 4.6
    led_days_eq = (total / 0.256) / 24
    car_km_eq = total / 0.17
    netflix_hours_eq = total / 0.055

    st.markdown(f"""
        <style>
        .equiv-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }}
        .equiv-card {{
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #52b788;
            text-align: center;
            transition: transform 0.2s ease;
        }}
        .equiv-card:hover {{
            transform: scale(1.02);
        }}
        .equiv-emoji {{
            font-size: 3.5em;
            margin-bottom: 15px;
        }}
        .equiv-text {{
            font-size: 1.05em;
            line-height: 1.6;
            color: #333;
        }}
        .equiv-value {{
            font-weight: 600;
            font-size: 1.2em;
            color: #1b4332;
        }}
        </style>

        <div class="equiv-grid">
            <div class="equiv-card">
                <div class="equiv-emoji">🍔</div>
                <div class="equiv-text">
                    Produce <span class="equiv-value">~{burger_eq:.0f}</span> beef burgers
                </div>
            </div>
            <div class="equiv-card">
                <div class="equiv-emoji">💡</div>
                <div class="equiv-text">
                    Keep 100 LED bulbs (10W) on for <span class="equiv-value">~{led_days_eq:.0f}</span> days
                </div>
            </div>
            <div class="equiv-card">
                <div class="equiv-emoji">🚗</div>
                <div class="equiv-text">
                    Drive a gasoline car for <span class="equiv-value">~{car_km_eq:.0f}</span> km
                </div>
            </div>
            <div class="equiv-card">
                <div class="equiv-emoji">📺</div>
                <div class="equiv-text">
                    Watch Netflix for <span class="equiv-value">~{netflix_hours_eq:.0f}</span> hours
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- FINALE MOTIVAZIONALE ---

    st.markdown(f"""
    <div style="text-align: center; padding: 40px 10px;">
        <h2 style="color: #1d3557;"> Visit the next page to discover useful tips for reducing your footprint!💥</h2>
    </div>
""", unsafe_allow_html=True)

    st.markdown("### ")
    left, _, right = st.columns([1, 4, 1])
    with left:
        if st.button("⬅️ Back", key="res_back_btn", use_container_width=True):
            st.session_state.page = "guess"  # oppure "main" se preferisci
            st.rerun()
    with right:
        if st.button("➡️ Discover Tips",
                     key="res_continue_btn",
                     use_container_width=True):
            st.session_state.page = "virtues"
            st.rerun()


def show_virtues():
    name = (st.session_state.get("name") or "").strip()
    st.markdown(f"""
        <div style="background: linear-gradient(to right, #d8f3dc, #a8dadc);
                    padding: 28px 16px; border-radius: 12px; margin-bottom: 16px; text-align:center;">
            <h2 style="margin:0; color:#1d3557; font-size:2.2rem; line-height:1.2;">
                {name}, here are some practical tips to shrink your digital footprint!
            </h2>
            <p style="margin:8px 0 0; color:#1b4332; font-size:1.05rem;">
                We’ll start with actions tailored to your highest-impact area, followed by general tips you can apply every day.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # =======================
    # PERSONALIZED TIPS
    # =======================

    # Prendi i risultati
    res = st.session_state.get("results", {})
    if res:
        # Ricostruisci il ranking categorie
        df_plot = pd.DataFrame({
            "Category": ["Devices", "Digital Activities", "Artificial Intelligence", "E-Waste"],
            "CO₂e (kg)": [res.get("Devices", 0), res.get("Digital Activities", 0), res.get("AI Tools", 0), res.get("E-Waste", 0)]
        })

        most_impact_cat = df_plot.sort_values("CO₂e (kg)", ascending=False).iloc[0]["Category"]

        detailed_tips = {
            "Devices": [
                "<b>Turn off devices when not in use</b> – Even in standby mode, they consume energy. Powering them off saves electricity and extends their lifespan.",
                "<b>Update software regularly</b> – This enhances efficiency and performance, often reducing energy consumption.",
                "<b>Activate power-saving settings, reduce screen brightness and enable dark mode</b> – This lowers energy use.",
                "<b>Choose accessories made from recycled or sustainable materials</b> – This minimizes the environmental impact of your tech choices."
            ],
            "E-Waste": [
                "<b>Avoid upgrading devices every year</b> – Extending device lifespan significantly reduces environmental impact.",
                "<b>Repair instead of replacing</b> – Fix broken electronics whenever possible to avoid unnecessary waste.",
                "<b>Consider buying refurbished devices</b> – They’re often as good as new, but with a much lower environmental footprint.",
                "<b>Recycle unused electronics properly</b> – Don’t store old devices at home or dispose of them in the environment! E-waste contains polluting and valuable materials that need specialized treatment."
            ],
            "Digital Activities": [
                "<b>Use your internet mindfully</b> – Close unused apps, avoid sending large attachments, and turn off video during calls when not essential.",
                "<b>Declutter your digital space</b> – Regularly delete unnecessary files, empty trash and spam folders, and clean up cloud storage to reduce digital pollution.",
                "<b>Share links instead of attachments</b> – For example, link to a document on OneDrive or Google Drive instead of attaching it in an email.",
                "<b>Use instant messaging for short, urgent messages</b> – It's more efficient than email for quick communications."
            ],
            "Artificial Intelligence": [
                "<b>Use search engines for simple tasks</b> – They consume far less energy than AI tools.",
                "<b>Disable AI-generated results in search engines</b> – (e.g., on Bing: go to Settings > Search > Uncheck \"Include AI-powered answers\" or similar option)",
                "<b>Prefer smaller AI models when possible</b> – For basic tasks, use lighter versions like GPT-4o-mini instead of more energy-intensive models.",
                "<b>Be concise in AI prompts and require concise answers</b> – Short inputs and outputs require less processing."
            ]
        }

        with st.expander(f"📌 Tips to reduce your {most_impact_cat} footprint", expanded=True):
            for tip in detailed_tips.get(most_impact_cat, []):
                st.markdown(f"""
                    <div style="background-color: #e3fced; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        {tip}
                    </div>
                """, unsafe_allow_html=True)

        # Bonus tips da altre categorie
        other_categories = [cat for cat in detailed_tips if cat != most_impact_cat]
        # Se hai meno di 3 categorie alternative, limita la sample di conseguenza
        import random
        k = min(3, len(other_categories))
        extra_pool = random.sample(other_categories, k) if k > 0 else []

        with st.expander("📌 Some Extra Tips", expanded=False):
            for cat in extra_pool:
                tip = random.choice(detailed_tips[cat])
                st.markdown(f"""
                    <div style="background-color: #e3fced; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        {tip}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Complete the previous steps to unlock your personalized tips.")


    st.markdown("""
        <style>
        .virtue-card {
            background-color: #e7f5ff;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
            border-left: 6px solid #74C0FC;
        }
        </style>
    """, unsafe_allow_html=True)

    name = st.session_state.get("name", "").strip() or "there"

    # Raccogli virtù
    virtues = []

    # 1) Devices usati: elenca i device usati
    used_devices = []
    for dev_id, vals in st.session_state.get("device_inputs", {}).items():
        if vals.get("used") == "Used":
            base = dev_id.rsplit("_", 1)[0]
            used_devices.append(base)
    if used_devices:
        unique_used = ", ".join(sorted(set(used_devices)))
        virtues.append(f"You chose a used device for your {unique_used}! This typically reduces manufacturing emissions by 30–50% per device.")

    # 2) Device longevity: usati per più di 5 anni
    long_lived_devices = []
    for dev_id, vals in st.session_state.get("device_inputs", {}).items():
        try:
            if float(vals.get("years", 0)) > 5:
                base = dev_id.rsplit("_", 1)[0]
                long_lived_devices.append(base)
        except Exception:
            pass

    if long_lived_devices:
        names = ", ".join(sorted(set(long_lived_devices)))
        virtues.append(f"You use your {names} for more than 5 years! Extending device life reduces the need for new production and saves valuable resources.")

    
    # 3) End-of-life virtuoso (almeno uno dei device)
    good_eols = {
        "I bring it to a certified e-waste collection center",
        "I return it to manufacturer for recycling or reuse",
        "I sell or donate it to someone else",
    }
    has_good_eol = any(
        vals.get("eol") in good_eols
        for vals in st.session_state.get("device_inputs", {}).values()
    )
    if has_good_eol:
        virtues.append("You dispose of devices responsibly! EU aims to achieve a correct e-waste disposal rate of 65%, but many countries are still below this threshold.")

    # 4) Poche email con allegato (1–10)
    if st.session_state.get("email_attach") == "1–10":
        virtues.append("You keep the exchange of emails with attachments low. An email with an attachment typically weighs almost ten times more than one without.")

    # 5) Cloud storage basso (<5GB o 5–20GB)
    if st.session_state.get("cloud") in ("<5GB", "5–20GB"):
        virtues.append("You keep your cloud storage light by cleaning up files you no longer need! This reduces the energy required to store and maintain them.")

    # 6) Spegnere il computer quando non usato
    if st.session_state.get("idle") == "I turn it off":
        virtues.append("You turn off your computer when not in use. This single action can save over 150 kWh of energy per year for a single computer!")


    # 7) Zero stampe
    if int(st.session_state.get("pages", 0)) == 0:
        virtues.append("You never print. This saves paper, ink, and the energy needed for printing... the trees thank you!")

    # 8) Uso moderato dell’AI (< 20 query/giorno)
    ai_total_queries = int(st.session_state.get("ai_total_queries", 0))
    if ai_total_queries <= 20:
        virtues.append(
            "You use AI sparingly, staying under 20 queries a day. This reduces the energy consumed by high-compute AI models."
        )



    if virtues:
        st.markdown("#### You’re already making smart choices")
        st.markdown(
            "<p style='margin-top:-4px; font-size:0.95rem; color:#1b4332;'>Here are a few great habits we noticed from your answers.</p>",
            unsafe_allow_html=True
        )
        for v in virtues:
            st.markdown(f'<div class="virtue-card">{v}</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='margin-top:-4px; font-size:0.95rem; color:#1b4332;'>Moreover, just by completing this tool, you're already part of the solution.</p>",
            unsafe_allow_html=True
        )
    st.markdown(f"#### Great job, {name}! Keep going💪")

    # Pulsante per passare ai risultati
    st.markdown("### ")

    left, _, right = st.columns([1, 4, 1])
    with left:
        if st.button("⬅️ Back to Results", key="virt_back_btn", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()
    with right:
        if st.button("✏️ Edit your answers", key="virt_edit_btn", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()   
    
    _, _, right = st.columns([1, 4, 1])        
    with right:
        if st.button("🔄Restart", key="virt_restart_btn", use_container_width=True):
            st.session_state.clear() 
            st.session_state.page = "intro"
            st.rerun()

# === PAGE NAVIGATION ===
if st.session_state.page == "intro":
    show_intro()
elif st.session_state.page == "main":
    show_main()
elif st.session_state.page == "guess":
    show_guess()
elif st.session_state.page == "results":
    show_results()
elif st.session_state.page == "virtues":
    show_virtues()



















































