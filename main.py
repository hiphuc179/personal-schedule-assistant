import streamlit as st
from streamlit_calendar import calendar
from database.database_service import EventManager
from datetime import datetime, time, timedelta

event_service = EventManager()
st.set_page_config(
    layout="wide",
    page_title="App đặt lịch",
)

if "calendar_version" not in st.session_state:
    st.session_state["calendar_version"] = 0
if "suppress_event_click" not in st.session_state:
    st.session_state["suppress_event_click"] = False
if "pending_open_event_id" not in st.session_state:
    st.session_state["pending_open_event_id"] = None
if "pending_update_event_id" not in st.session_state:
    st.session_state["pending_update_event_id"] = None
@st.dialog("Thêm sự kiện",on_dismiss="ignore")
def dialog_add_event():
    form_add_event = st.form("Thêm sự kiện", enter_to_submit=False)
    with form_add_event:
        input_event_name = st.text_input("Tên sự kiện")
        input_address = st.text_input("Nơi diễn ra")
        input_start_date = st.date_input("Nhập ngày bắt đầu")
        input_start_time = st.time_input("Nhập thời gian bắt đầu",value="now")
        input_end_date = st.date_input("Nhập ngày kết thúc (nếu có)", value=None)
        input_end_time = st.time_input("Nhập thời gian kết thúc", value=None)
        input_reminder_time = st.number_input("Thời gian nhắc trước (phút)", value=10)

    submitted = form_add_event.form_submit_button("Tạo")
    if submitted:
        start_datetime_string = datetime.combine(input_start_date, input_start_time).isoformat()
        end_datetime_string = None
        if input_end_date is None and input_end_time is None:
            end_datetime_string = datetime.combine(input_end_date, input_end_time).isoformat() if input_end_date and input_end_time else None

        event_service.create_event(
            eventName=input_event_name,
            place=input_address,
            startTime=start_datetime_string,
            endTime=end_datetime_string,
            reminderTime=int(input_reminder_time)
        )
        st.success("Sự kiện đã được tạo")
        st.session_state["suppress_event_click"] = True
        st.rerun()

@st.dialog("Cập nhận sự kiện",on_dismiss="ignore")
def dialog_update_event(event_id):
    event = event_service.get_event_by_id(event_id)
    form_add_event = st.form("Cập nhật sự kiện", enter_to_submit=False)
    with form_add_event:
        input_event_name = st.text_input("Tên sự kiện", value=event.event_name)
        input_address = st.text_input("Nơi diễn ra", value=event.place)
        input_start_date = st.date_input("Nhập ngày bắt đầu", value=datetime.fromisoformat(event.start_time).date())
        input_start_time = st.time_input("Nhập thời gian bắt đầu", value=datetime.fromisoformat(event.start_time).time())
        input_end_date = st.date_input("Nhập ngày kết thúc (nếu có)", value=datetime.fromisoformat(event.end_time).date() if event.end_time else None)
        input_end_time = st.time_input("Nhập thời gian kết thúc", value=datetime.fromisoformat(event.end_time).time() if event.end_time else None)
        input_reminder_time = st.number_input("Thời gian nhắc trước (phút)", value=event.reminder_time or 10)

    submitted = form_add_event.form_submit_button("Lưu")

    if submitted:
        start_datetime_string = datetime.combine(input_start_date, input_start_time).isoformat()
        end_datetime_string = None
        if input_end_date is None and input_end_time is None:
            end_datetime_string = datetime.combine(input_end_date, input_end_time).isoformat() if input_end_date and input_end_time else None
        status = "active" if datetime.fromisoformat(start_datetime_string) > datetime.now() else "inactive"
        event_service.update_event(
            eventName=input_event_name,
            place=input_address,
            startTime=start_datetime_string,
            endTime=end_datetime_string,
            reminderTime=int(input_reminder_time),
            eventId=event.id,
            status=status
        )
        st.success("Sự kiện đã được cập nhật")
        st.session_state["suppress_event_click"] = True
        st.rerun()

def fetch_events_array():
    events = event_service.get_all_events()
    events_array = []
    for event in events:
        event_dict = {
            "id": event.id,
            "title": event.event_name,
            "start": event.start_time,
        }
        if event.end_time:
            event_dict["end"] = event.end_time
        events_array.append(event_dict)
    return events_array


@st.dialog("Chi tiết sự kiện",on_dismiss="ignore")
def dialog_detail_event(id):
    if id is None:
        st.info("Không có dữ liệu sự kiện để hiển thị.")
        st.rerun()
    event_id = id
    try:
        event_id = int(id)
    except Exception:
        event_id = id

    event = event_service.get_event_by_id(event_id)
    if event is None:
        return

    def format_datetime(iso_string):
        if not iso_string:
            return ""
        dt_object = datetime.fromisoformat(iso_string)
        return dt_object.strftime("%H:%M %d/%m/%Y")

    st.write("**Tên sự kiện:**", event.event_name)
    st.write("**Địa điểm:**", event.place)
    st.write("**Bắt đầu:**", format_datetime(event.start_time))
    st.write("**Kết thúc:**", format_datetime(event.end_time) or "(Không có)")
    st.write("**Nhắc trước (phút):**", event.reminder_time or "(Không có)")

    col1, col2 = st.columns([1,1])
    with col1:
        btn_edit = st.button("Chỉnh sửa")
        if btn_edit:
            # Queue the update dialog to open at top-level on next run
            st.session_state["pending_update_event_id"] = event.id
            st.rerun()
    with col2:
        btn_delete = st.button("Xóa")
        if btn_delete:
            try:
                deleted = event_service.delete_event(event_id=event.id)
                if deleted:
                    st.session_state["calendar_version"] += 1
                    st.session_state["suppress_event_click"] = True
                    st.success("Sự kiện đã được xóa")
                    st.rerun()
                else:
                    st.error("Xóa thất bại: sự kiện không tồn tại hoặc đã được xóa")
            except Exception as e:
                st.error(f"Xóa thất bại: {e}")

def display_calendar(allow_dialog=True):
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

    events = fetch_events_array()

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
        key=f"calendar-{st.session_state['calendar_version']}",
        callbacks=["eventClick"]
        )
    
    if allow_dialog and calendar_event:
        if st.session_state.get("suppress_event_click"):
            st.session_state["suppress_event_click"] = False
        else:
            if "callback" in calendar_event and calendar_event["callback"] == "eventClick":
                clicked_event = calendar_event["eventClick"]["event"]
                st.session_state["pending_open_event_id"] = clicked_event.get('id')
                st.rerun()

def display_main():
    st.header("Đặt lịch")
    header_left, header_right = st.columns([5,1],vertical_alignment="bottom")
    
    is_add_opening = False
    is_update_opening = False
    
    with header_left:
        st.text_input(label="Mô tả sự kiện", placeholder="Tên sự kiện, thời gian, địa điểm,...")
    with header_right :
        
        btn_add_event_auto = st.button("Thêm sự kiện tự động")
      
    main_container = st.container()
    with main_container:
        
        left, right = st.columns([1,1])
        
        with right:
            right_left, right_right = st.columns([1,1],vertical_alignment="bottom")
            with right_left:
                input_search_event = st.text_input("Tìm kiếm sự kiện",placeholder=" Enter để tìm")
            with right_right:
                btn_add_event = st.button("Thêm sự kiện")
                if btn_add_event:

                    is_add_opening = True
                    dialog_add_event()
        
        with left:

            allow_calendar_dialog = not is_add_opening and not is_update_opening
            display_calendar(allow_dialog=allow_calendar_dialog)


if st.session_state.get("pending_update_event_id"):
    pending = st.session_state.pop("pending_update_event_id")
    st.session_state["suppress_event_click"] = True
    dialog_update_event(pending)
elif st.session_state.get("pending_open_event_id"):
    pending = st.session_state.pop("pending_open_event_id")
    st.session_state["suppress_event_click"] = True
    dialog_detail_event(pending)

display_main()