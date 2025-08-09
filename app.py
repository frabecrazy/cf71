import streamlit as st
import pandas as pd
import random
import plotly.express as px
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Digital Carbon Footprint Calculator", layout="wide")

# Init session state
if "page" not in st.session_state or st.session_state.page not in ["intro", "main", "results"]:
    st.session_state.page = "intro"
if "role" not in st.session_state:
    st.session_state.role = ""
if "device_inputs" not in st.session_state:
    st.session_state.device_inputs = {}
if "results" not in st.session_state:
    st.session_state.results = {}
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

This calculator is tailored for **university students, professors, and staff members**, helping you estimate your CO₂e emissions from everyday digital activities — often overlooked, but increasingly relevant.

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
            st.warning("Please enter your name and select your role before continuing.")
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

    st.markdown(f"""<h1 style='font-size:2.2em; color:#1d3557;'>Hello <b>{st.session_state.name}</b>, it’s time to uncover the impact of your digital world! 🚀<br></h1>""", unsafe_allow_html=True)


    st.markdown(f"""
        <p style="font-size: 0.95em; color: #6c757d; margin-top: -8px;">
            First, we’ll ask you a few quick questions about your habits.<br>
            Din't worry, this won’t take more than <b>5 minutes</b>.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h3 style="margin-top: 25px; color:#1d3557;">💻 Devices</h3>
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

            col_confirm, _, col_remove = st.columns([1, 4, 1])

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

            with col_remove:
                if st.button(f"🗑 Remove {base_device}", key=f"remove_{device_id}"):
                    st.session_state.device_list.remove(device_id)
                    st.session_state.device_inputs.pop(device_id, None)
                    st.session_state.device_expanders.pop(device_id, None)
                    st.session_state.expander_tokens.pop(device_id, None)  # NEW
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

    wifi = st.slider("Estimated daily Wi-Fi connection time", 0.0, 8.0, 4.0, 0.5)
    pages = st.number_input("Printed pages per day", 0, 100, 0)

    idle = st.radio("When you're not using your computer...", ["I turn it off", "I leave it on (idle mode)", "I don’t have a computer"])


# --- CALCOLI 
    mail_total = (
        emails[email_plain] * 0.004 * DAYS
        + emails[email_attach] * 0.035 * DAYS
        + cloud_gb[cloud] * 0.01 * DAYS
    )

    wifi_total  = wifi  * 0.00584 * DAYS
    print_total = pages * 0.0045  * DAYS

    if idle == "I leave it on (idle mode)":
        idle_total = DAYS * 0.0104 * 16
    elif idle == "I turn it off":
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

            st.markdown("""
                    </div>
                </div>
            """, unsafe_allow_html=True)



    # === FINAL BUTTON (ALWAYS VISIBLE, VALIDATES ON CLICK) ===
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown("""
            <style>
                button[kind="primary"] {
                    background-color: #52b788 !important;
                    color: white !important;
                    padding: 1rem 1.5rem;
                    font-size: 1.2rem;
                    font-weight: 700;
                    border-radius: 10px;
                    border: none;
                }
                button[kind="primary"]:hover {
                    background-color: #40916c !important;
                }
            </style>
        """, unsafe_allow_html=True)

        button_clicked = st.button(f"🌍 {st.session_state.name}, discover Your Digital Carbon Footprint!", key="final", use_container_width=True)


        if button_clicked:
            unconfirmed_devices = [key for key in st.session_state.get("device_expanders", {}) if st.session_state.device_expanders[key]]

            missing_activities = False 


            if st.session_state.get("email_plain", "-- Select option --") == "-- Select option --":
                missing_activities = True
            if st.session_state.get("email_attach", "-- Select option --") == "-- Select option --":
                missing_activities = True
            if st.session_state.get("cloud", "-- Select option --") == "-- Select option --":
                missing_activities = True

            # Show warning(s) if something is missing
            if unconfirmed_devices:
                st.warning("⚠️ You have devices not yet confirmed. Please click 'Confirm' in each box to proceed.")
            if missing_activities:
                st.warning("⚠️ Please complete all digital activity fields before continuing.")

            # Proceed only if all is okay
            if not unconfirmed_devices and not missing_activities:
                st.session_state.results = {
                    "Devices": total_prod,
                    "E-Waste": total_eol,
                    "Digital Activities": digital_total,
                    "AI Tools": ai_total
                }
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
    st.markdown(f"""
        <div style="background-color:#d8f3dc; border-left: 6px solid #1b4332;
                    padding: 1em 1.5em; margin-top: 20px; border-radius: 10px;">
            <h3 style="margin: 0; font-size: 1.6em;">🌱 {st.session_state.name}, your total CO₂e is...</h3>
            <p style="font-size: 2.2em; font-weight: bold; color: #1b4332; margin: 0;">
                {total:.0f} kg/year
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- METRICHE IN GRIGLIA ---
    st.markdown("<br><h4>📦 Breakdown by source:</h4>", unsafe_allow_html=True)
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
    st.subheader("📊 Breakdown by Category")
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


    # --- TIPS PERSONALIZZATI ---
    detailed_tips = {
        "Devices": [
            "<b>Turn off devices when not in use</b> – Even in standby mode, they consume energy. Powering them off saves electricity and extends their lifespan.",
            "<b>Update software regularly</b> – This enhances efficiency and performance, often reducing energy consumption.",
            "<b>Activate power-saving settings, reduce screen brightness and enable dark mode</b> – This lower energy use.",
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

    # --- TITOLO + TIPS PER LA CATEGORIA PRINCIPALE ---
    most_impact_cat = df_plot.sort_values("CO₂e (kg)", ascending=False).iloc[0]["Category"]

    st.markdown(f"### 💡 Your biggest impact comes from: <b>{most_impact_cat}</b>", unsafe_allow_html=True)

    with st.expander("📌 Tips to reduce your footprint"):
        for tip in detailed_tips[most_impact_cat]:
            st.markdown(f"""
                <div style="background-color: #e3fced; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    {tip}
                </div>
            """, unsafe_allow_html=True)

    # --- EXTRA TIPS ---
    other_categories = [cat for cat in detailed_tips if cat != most_impact_cat]
    extra_tips = [random.choice(detailed_tips[cat]) for cat in random.sample(other_categories, 3)]

    st.markdown("### 💡 Some Extra Tips:")

    with st.expander("📌 Bonus advice from other categories"):
        for tip in extra_tips:
            st.markdown(f"""
                <div style="background-color: #e3fced; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    {tip}
                </div>
            """, unsafe_allow_html=True)



    st.divider()

    # --- EQUIVALENZE VISUALI ---
    st.markdown("### ♻️ With the same emissions, you could…")

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
        <h2 style="color: #1d3557;">💥 {st.session_state.get('name','')} , you are a Hero!</h2>
        <p style="font-size: 1.1em;">Just by completing this tool, you're already part of the solution.<br>
        Digital emissions are invisible, but not insignificant.</p>
    </div>
""", unsafe_allow_html=True)

    # --- PULSANTE RESTART ---
    st.markdown("### ")
    if st.button("🔁 Restart the Calculator"):
        st.session_state.clear()
        st.session_state.page = "intro"
        st.rerun()

def show_virtues():
    st.markdown("""
        <style>
        .virtue-card {
            background-color: #e3fced;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
            border-left: 6px solid #52b788;
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
        virtues.append(f"💻 **Used devices**: You chose refurbished/used for {unique_used} — this typically reduces manufacturing emissions by **30–50%**.")

    # 2) Meno di 3 devices
    device_count = len(st.session_state.get("device_list", []))
    if device_count and device_count < 3:
        virtues.append("📦 **Lean setup**: You own fewer than 3 devices, lowering embodied emissions.")

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
        virtues.append("♻️ **Responsible e-waste**: You choose certified collection, return-to-manufacturer, or donation.")

    # 4) Poche email con allegato (1–10)
    if st.session_state.get("email_attach") == "1–10":
        virtues.append("📎 **Light on attachments**: You keep attachment emails low and prefer link sharing (e.g., Drive/OneDrive).")

    # 5) Cloud storage basso (<5GB o 5–20GB)
    if st.session_state.get("cloud") in ("<5GB", "5–20GB"):
        virtues.append("☁️ **Minimal cloud footprint**: Your storage stays light — you clean up files you no longer need.")

    # 6) Spegnere il computer quando non usato
    idle_key = "When you're not using your computer..."
    if st.session_state.get(idle_key) == "I turn it off":
        virtues.append("🔌 **Power saver**: You turn off your computer when not in use, cutting idle energy waste.")

    # 7) Zero stampe
    pages = st.session_state.get("Printed pages per day", 0)
    try:
        if int(pages) == 0:
            virtues.append("🖨️ **Paperless**: You don’t print — nice save for trees and toner.")
    except Exception:
        pass

    # 8) Uso moderato dell’AI (< 20 query/giorno)
    try:
        ai_total_queries = 0
        for task in ai_factors.keys():
            ai_total_queries += int(st.session_state.get(task, 0) or 0)
        if ai_total_queries < 20:
            virtues.append("🤖 **Mindful AI**: You use AI sparingly (under ~20 queries/day).")
    except Exception:
        pass

    # Mostra massimo 3 virtù
    virtues_to_show = virtues[:3]

    st.markdown(f"""
        <div style="background: linear-gradient(to right, #d8f3dc, #a8dadc);
                    padding: 28px 16px; border-radius: 12px; margin-bottom: 16px; text-align:center;">
            <h2 style="margin:0; color:#1d3557;">🌟 {name}, your Digital Virtues</h2>
            <p style="margin:6px 0 0; color:#1b4332;">Here are a few great habits we noticed from your answers.</p>
        </div>
    """, unsafe_allow_html=True)

    if virtues_to_show:
        for v in virtues_to_show:
            st.markdown(f'<div class="virtue-card">{v}</div>', unsafe_allow_html=True)
    else:
        st.info("No standout virtues detected yet — try tweaking your inputs or complete all sections to see yours!")

    # (Opzionale) Piccolo riepilogo numerico
    total_found = len(virtues)
    st.caption(f"Showing up to 3 highlights • {total_found} virtue(s) detected in total.")

# === PAGE NAVIGATION ===
if st.session_state.page == "intro":
    show_intro()
elif st.session_state.page == "main":
    show_main()
elif st.session_state.page == "virtues":
    show_virtues()
elif st.session_state.page == "results":
    show_results()






