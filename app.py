"""PawPal+ Pet Care Streamlit Application.

Integrates the core OOP backend models (Owner, Pet, Task, Scheduler)
with an interactive, modern dashboard UI.
"""

from datetime import date, datetime, time
import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PawPal+ Pet Care",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .badge-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .badge-item {
        display: flex;
        flex-direction: column;
    }
    .badge-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }
    .badge-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
    }
    
    .pet-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. Session State Management
# -----------------------------------------------------------------------------
if "owner" not in st.session_state:
    # Initialize default owner
    owner = Owner(
        name="Alex Carter",
        contact="alex@example.com",
        available_minutes=120,
        day_start=time(8, 0),
    )

    # Populate with 2 initial sample pets
    luna = Pet(name="Luna", species="Dog", breed="Golden Retriever", age_years=3.0, pet_id="pet_1")
    mochi = Pet(name="Mochi", species="Cat", breed="Siamese Cat", age_years=2.0, pet_id="pet_2")

    # Attach initial sample care tasks
    luna.add_task(
        Task(
            title="Morning Park Walk",
            description="Morning Park Walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            preferred_time=time(8, 30),
            scheduled_time=time(8, 30),
        )
    )
    luna.add_task(
        Task(
            title="Breakfast & Supplements",
            description="Breakfast & Supplements",
            duration_minutes=15,
            priority="high",
            category="feeding",
            preferred_time=time(8, 0),
            scheduled_time=time(8, 0),
        )
    )
    mochi.add_task(
        Task(
            title="Daily Insulin Dose",
            description="Daily Insulin Dose",
            duration_minutes=10,
            priority="critical",
            category="medication",
            preferred_time=time(8, 15),
            scheduled_time=time(8, 15),
        )
    )
    mochi.add_task(
        Task(
            title="Coat Brushing & Grooming",
            description="Coat Brushing & Grooming",
            duration_minutes=20,
            priority="medium",
            category="grooming",
            preferred_time=time(10, 0),
            scheduled_time=time(10, 0),
        )
    )

    owner.add_pet(luna)
    owner.add_pet(mochi)
    st.session_state.owner = owner

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

owner_obj: Owner = st.session_state.owner

# -----------------------------------------------------------------------------
# 3. Sidebar Controls: Owner Constraints
# -----------------------------------------------------------------------------
with st.sidebar:
    st.subheader("⚙️ Owner Settings")
    st.write(f"Logged in as **{owner_obj.name}**")

    new_budget = st.slider(
        "Daily Available Time Budget (minutes)",
        min_value=30,
        max_value=360,
        value=owner_obj.available_minutes,
        step=15,
    )
    if new_budget != owner_obj.available_minutes:
        owner_obj.available_minutes = new_budget
        st.toast(f"Updated time budget to {new_budget} min!")

    start_h = st.selectbox(
        "Day Start Hour",
        options=list(range(6, 12)),
        index=owner_obj.day_start.hour - 6 if 6 <= owner_obj.day_start.hour <= 11 else 2,
        format_func=lambda h: f"{h:02d}:00 AM",
    )
    if start_h != owner_obj.day_start.hour:
        owner_obj.day_start = time(start_h, 0)
        st.toast(f"Day start updated to {start_h:02d}:00 AM")

    strategy = st.selectbox(
        "Scheduling Algorithm",
        options=["priority_first", "duration_first"],
        index=0,
        help="priority_first ranks by importance; duration_first schedules shortest tasks first.",
    )
    st.session_state.scheduler.strategy = strategy

    st.divider()
    if st.button("🔄 Reset to Default Sample Data"):
        del st.session_state["owner"]
        del st.session_state["scheduler"]
        st.rerun()

# -----------------------------------------------------------------------------
# 4. App Shell: Header & Owner Summary Badge
# -----------------------------------------------------------------------------
all_tasks = owner_obj.get_all_tasks(pending_only=False)
pending_tasks = [t for t in all_tasks if not t.completed]
completed_tasks = [t for t in all_tasks if t.completed]
total_pets = len(owner_obj.pets)

header_col1, header_col2 = st.columns([1.8, 2.2])

with header_col1:
    st.title("🐾 PawPal+ Pet Care")
    st.caption("Smart Pet Care Management & Algorithmic Schedule Engine")

with header_col2:
    badge_html = f"""
    <div class="badge-card">
        <div class="badge-item">
            <span class="badge-label">👤 Owner</span>
            <span class="badge-value">{owner_obj.name}</span>
        </div>
        <div class="badge-item">
            <span class="badge-label">📧 Contact</span>
            <span class="badge-value">{owner_obj.contact or owner_obj.email}</span>
        </div>
        <div class="badge-item">
            <span class="badge-label">🐶 Pets</span>
            <span class="badge-value">{total_pets} registered</span>
        </div>
        <div class="badge-item">
            <span class="badge-label">⏰ Budget</span>
            <span class="badge-value">{owner_obj.available_minutes} min/day</span>
        </div>
        <div class="badge-item">
            <span class="badge-label">📋 Pending</span>
            <span class="badge-value">{len(pending_tasks)} tasks</span>
        </div>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

st.divider()

# Requirement 3: Metrics Row (Total Pets, Total Tasks, Pending Tasks, Completed Tasks)
m1, m2, m3, m4 = st.columns(4)
m1.metric("🐾 Total Pets", f"{total_pets}")
m2.metric("📋 Total Tasks", f"{len(all_tasks)}")
m3.metric("⏳ Pending Tasks", f"{len(pending_tasks)}")
m4.metric("✅ Completed Tasks", f"{len(completed_tasks)}")

# -----------------------------------------------------------------------------
# 5. Main Application Tabs
# -----------------------------------------------------------------------------
tab_dashboard, tab_manage = st.tabs(
    ["📅 Daily Schedule & Dashboard", "➕ Add / Manage Pets & Tasks"]
)

# -----------------------------------------------------------------------------
# Tab 1: Daily Schedule & Dashboard (Requirement 1 & 2)
# -----------------------------------------------------------------------------
with tab_dashboard:
    # Requirement 1: Pet Overview Section
    st.subheader("🐾 Active Pets")
    if not owner_obj.pets:
        st.info("No pets registered yet. Go to the 'Add / Manage' tab to add your first pet.")
    else:
        pet_cols = st.columns(min(max(len(owner_obj.pets), 1), 4))
        for idx, pet in enumerate(owner_obj.pets):
            col = pet_cols[idx % len(pet_cols)]
            species_emoji = {"dog": "🐶", "cat": "🐱", "bird": "🦜"}.get(
                pet.species.lower(), "🐾"
            )
            p_pending = len(pet.get_pending_tasks())
            badge_color = "#065f46" if p_pending == 0 else "#854d0e"
            with col:
                st.markdown(
                    f"""
                    <div class="pet-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0;">{species_emoji} {pet.name}</h4>
                            <span style="background:{badge_color}; color:#fff; font-size:0.75rem; padding:2px 8px; border-radius:9999px; font-weight:600;">
                                {p_pending} pending
                            </span>
                        </div>
                        <p style="margin:0.25rem 0 0 0; color:#94a3b8; font-size:0.85rem;">
                            <strong>{pet.species}</strong> • {pet.breed or 'Mixed'} ({pet.age_years} yrs)
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # Requirement 2: Schedule Table & Interactive Completion
    st.subheader("🗓️ Today's Schedule")

    # Conflict Detection Alert
    detected_conflicts = st.session_state.scheduler.detect_conflicts()
    if detected_conflicts:
        with st.container():
            st.warning(f"⚠️ **{len(detected_conflicts)} Schedule Conflict(s) Detected:**")
            for conf in detected_conflicts:
                st.caption(f"• {conf['warning_message']}")

    daily_schedule = st.session_state.scheduler.get_daily_schedule(st.session_state.owner)

    if not daily_schedule:
        st.info("No tasks scheduled yet. Add tasks in the 'Add / Manage' tab.")
    else:
        st.caption(
            f"Showing {len(daily_schedule)} tasks strictly ordered chronologically by scheduled time across all pets."
        )

        # Header row
        t_header = st.columns([1.2, 1.2, 2.8, 1.2, 1.2, 1.2, 1.2])
        t_header[0].markdown("**Time**")
        t_header[1].markdown("**Pet**")
        t_header[2].markdown("**Description**")
        t_header[3].markdown("**Duration**")
        t_header[4].markdown("**Priority**")
        t_header[5].markdown("**Status**")
        t_header[6].markdown("**Action**")

        st.markdown("<hr style='margin:0.2rem 0 0.6rem 0;'/>", unsafe_allow_html=True)

        priority_labels = {
            "critical": "🔴 Critical",
            "high": "🟠 High",
            "medium": "🟡 Medium",
            "low": "🟢 Low",
        }

        for task in daily_schedule:
            t_row = st.columns([1.2, 1.2, 2.8, 1.2, 1.2, 1.2, 1.2])

            effective_time = task.scheduled_time or task.start_time or task.preferred_time
            time_display = effective_time.strftime("%H:%M") if effective_time else "TBD"
            prio_display = priority_labels.get(task.priority.lower(), task.priority.upper())
            status_display = "✅ Done" if task.completed else "⏳ Pending"
            task_desc = task.description or task.title

            t_row[0].write(f"🕒 **{time_display}**")
            t_row[1].write(task.pet_name or "All")

            if task.completed:
                t_row[2].markdown(f"~~{task_desc}~~")
            else:
                t_row[2].write(task_desc)

            t_row[3].write(f"{task.duration_minutes} min")
            t_row[4].write(prio_display)
            t_row[5].write(status_display)

            with t_row[6]:
                if task.completed:
                    if st.button("Undo", key=f"btn_undo_{task.task_id}", help="Revert to pending"):
                        task.mark_pending()
                        st.rerun()
                else:
                    if st.button(
                        "Done",
                        key=f"btn_done_{task.task_id}",
                        type="primary",
                        help="Mark task complete",
                    ):
                        st.session_state.scheduler.complete_task(task.task_id)
                        st.rerun()

    # Algorithmic Budget Breakdown Expander
    with st.expander("⚡ Algorithmic Day Optimization (Time Budget & Explanation)", expanded=False):
        plan = st.session_state.scheduler.build_plan(owner_obj)
        sched_count = len(plan["scheduled"])
        skip_count = len(plan["skipped"])
        used_min = plan["minutes_used"]

        st.write(
            f"**Budget Analysis**: Using strategy `{st.session_state.scheduler.strategy}`, "
            f"**{sched_count} tasks** fit within the {owner_obj.available_minutes}-minute limit "
            f"({used_min} min used, {skip_count} skipped)."
        )
        st.text(st.session_state.scheduler.explain(plan))

# -----------------------------------------------------------------------------
# Tab 2: Add / Manage Pets & Tasks
# -----------------------------------------------------------------------------
with tab_manage:
    col_pet_form, col_task_form = st.columns(2)

    # Form 1: Add New Pet
    with col_pet_form:
        st.subheader("🐾 Add New Pet")
        with st.form("add_pet_form"):
            pet_name = st.text_input("Name", placeholder="e.g. Charlie")
            species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
            breed = st.text_input("Breed", placeholder="e.g. Golden Retriever")
            age = st.number_input(
                "Age (Years)", min_value=0.0, max_value=35.0, value=1.0, step=0.5
            )

            submit_pet = st.form_submit_button("➕ Register Pet", use_container_width=True)
            if submit_pet:
                if not pet_name.strip():
                    st.error("Please provide a name for the pet.")
                else:
                    pet_id = f"pet_{len(owner_obj.pets) + 1}"
                    new_pet = Pet(
                        name=pet_name.strip(),
                        species=species,
                        breed=breed.strip(),
                        age_years=float(age),
                        pet_id=pet_id,
                    )
                    st.session_state.owner.add_pet(new_pet)
                    st.success(f"Added {new_pet.name} ({new_pet.species}) successfully!")
                    st.rerun()

    # Form 2: Schedule Task
    with col_task_form:
        st.subheader("🗓️ Schedule Task")
        if not owner_obj.pets:
            st.warning("No pets registered yet. Please add a pet before scheduling tasks.")
        else:
            with st.form("add_task_form"):
                pet_names = [p.name for p in owner_obj.pets]
                pet_map = {p.name: p for p in owner_obj.pets}
                selected_pet_name = st.selectbox("Select Pet", pet_names)
                selected_pet = pet_map[selected_pet_name]

                description = st.text_input("Description", placeholder="e.g. Afternoon Walk")
                task_date = st.date_input("Date", value=date.today())
                task_time = st.time_input("Time", value=time(9, 0))
                duration = st.number_input(
                    "Duration in minutes", min_value=1, max_value=240, value=30, step=5
                )
                priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=1)
                recurrence = st.selectbox("Recurrence", ["NONE", "DAILY", "WEEKLY"], index=0)

                submit_task = st.form_submit_button("➕ Add Task", use_container_width=True)
                if submit_task:
                    if not description.strip():
                        st.error("Please enter a task description.")
                    else:
                        task_dt = datetime.combine(task_date, task_time)
                        task_id = f"task_{datetime.now().timestamp()}"

                        desc_lower = description.lower()
                        cat = "general"
                        if "walk" in desc_lower:
                            cat = "walk"
                        elif any(
                            k in desc_lower
                            for k in ["feed", "food", "breakfast", "dinner", "lunch"]
                        ):
                            cat = "feeding"
                        elif any(
                            k in desc_lower
                            for k in ["med", "pill", "insulin", "dose", "vaccine"]
                        ):
                            cat = "medication"
                        elif any(
                            k in desc_lower
                            for k in ["vet", "doctor", "appointment", "checkup"]
                        ):
                            cat = "appointment"
                        elif any(
                            k in desc_lower for k in ["brush", "groom", "bath", "wash"]
                        ):
                            cat = "grooming"

                        new_task = Task(
                            title=description.strip(),
                            description=description.strip(),
                            duration_minutes=int(duration),
                            priority=priority.lower(),
                            category=cat,
                            preferred_time=task_time,
                            scheduled_time=task_time,
                            scheduled_datetime=task_dt,
                            pet_name=selected_pet.name,
                            recurrence=recurrence,
                            task_id=task_id,
                        )
                        selected_pet.add_task(new_task)
                        st.success(
                            f"Task '{new_task.title}' added for {selected_pet.name}!"
                        )
                        st.rerun()

    st.divider()

    # Current Pets & Tasks Management
    st.subheader("🐾 Registered Pets & Their Care Tasks")
    for pet in owner_obj.pets:
        with st.expander(
            f"{pet.name} ({pet.species} - {pet.breed or 'Mixed'}, {pet.age_years} yrs)",
            expanded=True,
        ):
            p_tasks = pet.tasks
            if not p_tasks:
                st.info(f"No tasks registered for {pet.name}.")
            else:
                for t in p_tasks:
                    c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1])
                    c1.write(f"**{t.title}** ({t.category.title()})")
                    c2.write(f"⏱️ {t.duration_minutes} min | [{t.priority.upper()}]")
                    c3.write(
                        f"🕒 {t.scheduled_time.strftime('%H:%M') if t.scheduled_time else 'Anytime'}"
                    )
                    if c4.button("🗑️", key=f"del_{t.task_id}", help="Delete task"):
                        pet.remove_task(t.task_id)
                        st.rerun()
