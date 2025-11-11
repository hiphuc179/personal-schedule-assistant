import streamlit as st
from streamlit_calendar import calendar


st.set_page_config(
    layout="wide",
    page_title="App đặt lịch",
)

@st.dialog("Thêm sự kiện")
def modal_add_event():
    form_add_event = st.form("Thêm sự kiện")
    with form_add_event:
        input_event_title = st.text_input("Tên sự kiện")
        input_address = st.text_input("Nơi diễn ra")
        input_event_date = st.date_input("Nhập thời gian bắt đầu")
        input_start_time = st.time_input("Nhập thời gian bắt đầu",value="now")
        input_end_time = st.time_input("Nhập thời gian kết thúc", value=None)
        input_reminder_time = st.number_input("Thời gian nhắc trước (phút)", value=10)

    submitted = form_add_event.form_submit_button("Tạo")
    if submitted:

        st.rerun()


def display_calendar():
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
                border-color: white;
                color: var(--fc-button-text-color);
        }
    """

    calendar_event = calendar(
        events=events,
        options=options,
        custom_css=custom_css,
        key='calendar', # Assign a widget key to prevent state loss
        )

def display_main():
    st.header("Đặt lịch")
    header_left, header_right = st.columns([5,1],vertical_alignment="bottom")
   
    with header_left:
        st.text_input(label="Mô tả sự kiện", placeholder="Tên sự kiện, thời gian, địa điểm,...")
    with header_right :
        btn_add_event = st.button("Thêm sự kiện tự động")
      

    main_container = st.container()
    with main_container:
        
        left, right = st.columns([1,1])
        
        #right-side
        with right:
            right_left, right_right = st.columns([1,1],vertical_alignment="bottom")
            with right_left:
                input_search_event = st.text_input("Tìm kiếm sự kiện",placeholder=" Enter để tìm")
            with right_right:
                btn_add_event = st.button("Thêm sự kiện")
                if btn_add_event:
                    modal_add_event()
        
        #left-side
        with left:
            display_calendar()

    event_search_result_container = st.container


display_main()