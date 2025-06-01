import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Medical Project Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stAppHeader {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        color: black;
    }

    .task-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 0.5rem;
        color: black;
    }

    .status-todo { border-left: 4px solid #ffc107; }
    .status-progress { border-left: 4px solid #17a2b8; }
    .status-done { border-left: 4px solid #28a745; }

    .sidebar .stSelectbox label {
        font-weight: bold;
        color: white !important;
    }

    /* Sidebar navigation dropdown styling - selected value display */
    .sidebar .stSelectbox > div > div > div[data-baseweb="select"] > div {
        color: white !important;
        background-color: transparent;
    }

    .sidebar .stSelectbox div[data-testid="stSelectbox"] > div > div {
        color: white !important;
    }

    /* Force white text for the displayed selection */
    .sidebar [data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: white !important;
    }

    /* Ensure text is black on white/light backgrounds */
    .stMetric .metric-value {
        color: black !important;
    }

    .stMetric .metric-label {
        color: black !important;
    }

    .stDataFrame {
        color: black;
    }

    /* Form elements with white backgrounds */
    .stTextInput > div > div > input {
        color: black;
    }

    .stSelectbox > div > div > div {
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["Task", "Start", "End", "Status", "Assignee"])
else:
    # Migration: Add Assignee column if it doesn't exist
    if 'Assignee' not in st.session_state.tasks.columns:
        st.session_state.tasks['Assignee'] = 'Project Manager'  # Default assignee
        st.info(" Tasks updated with assignee information!")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Team roles
TEAM_ROLES = [
    "Business Analyst",
    "DevOps",
    "Project Manager",
    "BackEnd Developer",
    "FrontEnd Developer",
    "Platform Engineer",
    "QA Engineer",
    "Architect"
]


if st.session_state.tasks.empty:
    # Mockup Data
    mockupTasks = pd.DataFrame([
        ["Definire User Stories", date(2025, 5, 16), date(2025, 5, 18), "To do", TEAM_ROLES[0]],
        ["Github repo", date(2025, 5, 13), date(2025, 5, 14), "To do", TEAM_ROLES[5]],

    ],
        columns=st.session_state.tasks.columns)
    st.session_state.tasks = pd.concat([st.session_state.tasks, mockupTasks], ignore_index=True)

# Sidebar navigation
st.sidebar.markdown("###  Navigation")
page = st.sidebar.selectbox(
    "Choose Page",
    ["Dashboard", "Task Management", "Team View", "Analytics"]
)

# Main header
st.markdown("""
<div class="main-header">
    <h1> MVP Medical Project Manager</h1>
    <p>Manage your medical development projects efficiently</p>
</div>
""", unsafe_allow_html=True)

# DASHBOARD PAGE
if page == "Dashboard":
    st.markdown("##  Project Dashboard")

    df = st.session_state.tasks

    if not df.empty:
        # Metrics row
        col1, col2, col3, col4, col5 = st.columns(5)

        total_tasks = len(df)
        done_tasks = len(df[df['Status'] == 'Done'])
        in_progress_tasks = len(df[df['Status'] == 'In progres'])
        todo_tasks = len(df[df['Status'] == 'To do'])
        remaining_tasks=todo_tasks+in_progress_tasks

        progress_percentage = int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0

        with col1:
            st.metric(" Total Tasks", total_tasks)
        with col2:
            st.metric(" Completed", done_tasks)
        with col3:
            st.metric(" In Progress", in_progress_tasks)
        with col4:
            st.metric(" To Do", todo_tasks)
        with col5:
            st.metric(" Remaining tasks",remaining_tasks)

        # Progress bar
        st.markdown("### Project Progress")
        progress_bar = st.progress(progress_percentage / 100)
        st.markdown(f"**{progress_percentage}%** Complete")

        # Recent tasks
        st.markdown("###  Recent Tasks")
        recent_tasks = df.tail(5)
        for _, task in recent_tasks.iterrows():
            status_class = f"status-{task['Status'].lower().replace(' ', '')}"
            assignee_display = task.get('Assignee', 'Unassigned')
            st.markdown(f"""
            <div class="task-card {status_class}">
                <strong>{task['Task']}</strong><br>
                 {assignee_display} |  {task['Start']} - {task['End']} | 
                <span style="color: {'#28a745' if task['Status'] == 'Done' else '#17a2b8' if task['Status'] == 'In progres' else '#ffc107'}">
                    {task['Status']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(" No tasks yet. Go to Task Management to add your first task!")

# TASK MANAGEMENT PAGE
elif page == "Task Management":
    st.markdown("##  Task Management")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Add New Task")
        with st.form("add_task", clear_on_submit=True):
            task_name = st.text_input(" Task Name")
            assignee = st.selectbox(" Assign To", TEAM_ROLES)
            start_date = st.date_input(" Start Date", value=date.today())
            end_date = st.date_input(" End Date", value=date.today())
            status = st.selectbox(" Status", ["To do", "In progres", "Done"])

            submit = st.form_submit_button(" Add Task", use_container_width=True)

            if submit and task_name:
                new_row = pd.DataFrame([[task_name, start_date, end_date, status, assignee]],
                                       columns=st.session_state.tasks.columns)
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
                st.success(" Task added successfully!")
                st.rerun()

    with col2:
        st.markdown("###  Current Tasks")
        df = st.session_state.tasks

        if not df.empty:
            # Quick status update
            st.markdown("#### Quick Status Update")
            for idx, task in df.iterrows():
                col_task, col_status, col_update = st.columns([3, 1, 1])

                with col_task:
                    assignee_display = task.get('Assignee', 'Unassigned')
                    st.write(f"**{task['Task']}** ({assignee_display})")

                with col_status:
                    current_status = task['Status']
                    status_color = {'To do': '🔴', 'In progres': '🟡', 'Done': '🟢'}
                    st.write(f"{status_color.get(current_status, '⚪')} {current_status}")

                with col_update:
                    new_status = st.selectbox(
                        "Update",
                        ["To do", "In progres", "Done"],
                        index=["To do", "In progres", "Done"].index(current_status),
                        key=f"status_{idx}"
                    )
                    if new_status != current_status:
                        st.session_state.tasks.loc[idx, 'Status'] = new_status
                        st.rerun()

            # Task table
            st.markdown("#### All Tasks")
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Task": st.column_config.TextColumn("Task Name", width="medium"),
                    "Assignee": st.column_config.TextColumn("Assigned To", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Start": st.column_config.DateColumn("Start Date"),
                    "End": st.column_config.DateColumn("End Date")
                }
            )

            # Export and bulk actions - restructured to avoid nested columns
            st.markdown("####  Export & Bulk Actions")

            # Export section
            with st.expander(" Export Data"):
                csv_data = df.to_csv(index=False)
                st.download_button(
                    " Download Tasks CSV",
                    csv_data,
                    "medical_project_tasks.csv",
                    use_container_width=True
                )

            # Bulk actions section - no nested columns
            with st.expander(" Bulk Actions"):
                st.warning("Bulk delete actions cannot be undone!")

                if st.button(" Delete All Completed Tasks", use_container_width=True):
                    completed_count = len(df[df['Status'] == 'Done'])
                    if completed_count > 0:
                        st.session_state.tasks = st.session_state.tasks[
                            st.session_state.tasks['Status'] != 'Done'].reset_index(drop=True)
                        st.success(f" Deleted {completed_count} completed tasks!")
                        st.rerun()
                    else:
                        st.info("No completed tasks to delete.")

                if st.button("🗑 Delete All Tasks", use_container_width=True):
                    task_count = len(df)
                    st.session_state.tasks = pd.DataFrame(
                        columns=["Task", "Start", "End", "Status", "Assignee"])
                    st.success(f"Deleted all {task_count} tasks!")
                    st.rerun()
        else:
            st.info("No tasks available. Add some tasks to get started!")

# TEAM VIEW PAGE
elif page == "Team View":
    st.markdown("##  Team View")

    df = st.session_state.tasks

    if not df.empty and 'Assignee' in df.columns:
        # Team workload
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Team Workload")
            workload = df.groupby('Assignee').size().reset_index(name='Task Count')
            fig_workload = px.bar(
                workload,
                x='Assignee',
                y='Task Count',
                color='Task Count',
                range_color=[0,2],
                color_continuous_scale='Blues'
            )
            fig_workload.update_layout(showlegend=False)
            st.plotly_chart(fig_workload, use_container_width=True)

        with col2:
            st.markdown("### Status Distribution")
            status_dist = df['Status'].value_counts()
            fig_status = px.pie(
                values=status_dist.values,
                names=status_dist.index,
                color_discrete_map={
                    'To do': '#ffc107',
                    'In progres': '#17a2b8',
                    'Done': '#28a745'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)

        # Team member details
        st.markdown("###  Team Member Tasks")
        if len(df['Assignee'].unique()) > 0:
            selected_member = st.selectbox("Select Team Member", df['Assignee'].unique())

            member_tasks = df[df['Assignee'] == selected_member]

            for _, task in member_tasks.iterrows():
                status_color = {'To do': '#ffc107', 'In progres': '#17a2b8', 'Done': '#28a745'}
                st.markdown(f"""
                <div class="task-card" style="border-left: 4px solid {status_color.get(task['Status'], '#6c757d')}">
                    <h4>{task['Task']}</h4>
                    <p><strong>Status:</strong> {task['Status']}</p>
                    <p><strong>Duration:</strong> {task['Start']} → {task['End']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No assignees found. Please add tasks with assigned team members.")
    elif not df.empty:
        st.warning("⚠ Existing tasks need to be updated with assignee information. Please go to Dashboard to update.")

        # Show button to update all tasks
        if st.button(" Update All Tasks with Default Assignee"):
            st.session_state.tasks['Assignee'] = 'Project Manager'
            st.success(" All tasks updated with default assignee!")
            st.rerun()
    else:
        st.info("No tasks available for team analysis.")

# ANALYTICS PAGE
elif page == "Analytics":
    st.markdown("##  Project Analytics")

    df = st.session_state.tasks

    if not df.empty:
        # Gantt chart
        st.markdown("###  Project Timeline (Gantt Chart)")
        df_gantt = df.copy()
        df_gantt["Start"] = pd.to_datetime(df_gantt["Start"])
        df_gantt["End"] = pd.to_datetime(df_gantt["End"])

        # Color mapping for status
        color_map = {'To do': '#ffc107', 'In progres': '#17a2b8', 'Done': '#28a745'}

        fig = px.timeline(
            df_gantt,
            x_start="Start",
            x_end="End",
            y="Task",
            color="Status",
            color_discrete_map=color_map,
            hover_data=["Assignee"]
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="Tasks",
            height=max(400, len(df) * 50)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Timeline analysis
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("###  Task Duration Analysis")
            df_gantt['Duration'] = (df_gantt['End'] - df_gantt['Start']).dt.days
            avg_duration = df_gantt['Duration'].mean()
            st.metric("Average Task Duration", f"{avg_duration:.1f} days")

            fig_duration = px.histogram(
                df_gantt,
                x='Duration',
                nbins=10,
                title="Task Duration Distribution"
            )
            st.plotly_chart(fig_duration, use_container_width=True)

        with col2:
            st.markdown("###  Tasks by Assignee Timeline")
            fig_assignee = px.timeline(
                df_gantt,
                x_start="Start",
                x_end="End",
                y="Assignee",
                color="Status",
                color_discrete_map=color_map,
                hover_data=["Task"]
            )
            fig_assignee.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_assignee, use_container_width=True)
    else:
        st.info(" No data available for analytics. Add some tasks first!")

# Footer
st.markdown("---")
st.markdown("*MVP Medical Project Manager* ")