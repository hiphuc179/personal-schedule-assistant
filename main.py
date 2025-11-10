import streamlit as st
from streamlit_calendar import calendar


options = {
    "locale": "vi",
    "editable": True,
    "selectable": True,
    "initialView": "dayGridMonth",

    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "listDay,dayGridWeek,dayGridMonth"
    },
    "buttonText": {
        "today": "Hôm nay",
        "month": "Tháng",
        "week": "Tuần",
        "day": "Ngày",
        "list": "Danh sách",
    },
}

events = [
    {"title": "Conference", "start": "2025-11-10T10:40:00"},
    {"title": "Conference", "start": "2025-11-10T10:40:00"},
    {"title": "Conference", "start": "2025-11-10T10:40:00"},
    {"title": "Team Meeting", "start": "2025-11-11"}
]

custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 1.2rem;
    }

    --fc-button-active-bg-color: #007bff;
    --fc-button-text-color: black;

    .fc .fc-button {
            background-color: #007bff80;
            border-color: black;
            color: var(--fc-button-text-color);
    }
"""

calendar = calendar(
    events=events,
    options=options,
    custom_css=custom_css,
    key='calendar', # Assign a widget key to prevent state loss
    )
# st.write(calendar)