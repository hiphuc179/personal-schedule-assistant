import json
import os

# ==========================================
# 1. KHAI BÁO DỮ LIỆU (TOÀN CỤC)
# ==========================================

# 1.1 Teencode & Không dấu
teencode_dict = {
    "da banh": "đá banh", "da bong": "đá bóng", "choi bong": "chơi bóng",
    "mua to": "mưa to", "dang mua": "đang mưa",
    "troi qua": "trôi qua", "roi do": "rồi đó",
    "cong tac": "công tác", "chuyen": "chuyến",
    "ke di": "kệ đi", "ko dc": "không được",
    "o": "ở", 
    
    "di": "đi", "hoc": "học", "muon": "muộn", 
    "ranh": "rảnh", "dau": "đâu", "dc": "được", "ok": "được",
    "ko": "không", "k": "không", "kh": "không",
    "vs": "với", "wa": "quá", "qua": "quá",
    "co": "có", "toi": "tôi", "t": "tôi", "m": "mày",
    "b": "bạn", "mk": "mình", "uhm": "ừm", "uh": "ừ", 
    "luon": "luôn", "ln": "luôn", "thui": "thôi",
    "cuon": "cuốn", "nhom": "nhóm", "tr": "trời", "mla": "mưa", 
    "vch": "vãi chưởng", "chua": "chưa", "chg": "chưa", "doc": "đọc",
    
    "hm nay": "hôm nay", "hqua": "hôm qua", "hom qua": "hôm qua",
    "tôi nay": "tối nay", "toi nay": "tối nay", # Fix tối nay
    "ngay mai": "ngày mai", "h": "giờ", "g": "giờ", "p": "phút",
    
    "tp hcm": "thành phố hồ chí minh", "hcm": "hồ chí minh", "hn": "hà nội","ha noi":"hà nội",
    "sg": "sài gòn", "dn": "đà nẵng", "vt": "vũng tàu", "ct": "cần thơ",
    "q1": "quận 1", "q2": "quận 2", "q3": "quận 3", "q4": "quận 4", 
    "q5": "quận 5", "q6": "quận 6", "q7": "quận 7", "q8": "quận 8", 
    "q9": "quận 9", "q10": "quận 10", "q11": "quận 11", "q12": "quận 12",
    "gv": "quận gò vấp", "tb": "quận tân bình"
}

# 1.2 Anh - Việt
en_vi_dict = {
    "set": "thiết lập", "book": "sách", "meeting": "cuộc họp", 
    "read": "đọc", "call": "gọi", "mess": "nhắn tin", 
    "confirm": "xác nhận", "boss": "sếp", "manager": "quản lý"
}

# 1.3 Ignore Words (Dạng LIST [])
ignore_words = [
    "deadline", "gym", "code", "bug", "fix", "demo", "python", "java", 
    "file", "js", "mail", "zalo", "report"
]

# 1.4 Locations (Dạng DICT {})
locations_dict = {
        "cities": [
            "hà nội", "hồ chí minh", "hcm", "sài gòn", "đà nẵng", "hải phòng", "cần thơ",
            "nha trang", "đà lạt", "vũng tàu", "huế", "quy nhơn", "buôn ma thuột",
            "phú quốc", "long xuyên", "biên hòa", "thủ đức", "bến tre", "cà mau",
            "cao bằng", "bắc ninh", "quảng ninh", "hạ long", "sapa", "lào cai",
            "hà giang", "mộc châu", "tiền giang", "thái bình", "nam định"
        ],
        "districts": [
            "quận 1", "quận 2", "quận 3", "quận 4", "quận 5", "quận 6",
            "quận 7", "quận 8", "quận 9", "quận 10", "quận 11", "quận 12",
            "gò vấp", "tân bình", "tân phú", "bình thạnh", "phú nhuận", "bình tân",
            "thủ đức", "bình chánh", "hóc môn", "củ chi", "nhà bè"
        ],
       "places": [
            "vincom", "aeon mall", "lotte mart", "gigamall", "takashimaya",
            "landmark 81", "bitexco", "keangnam", "time city", "royal city",
            "bến xe miền đông", "bến xe miền tây", "bến xe mỹ đình", "bến xe giáp bát",
            "sân bay tân sơn nhất", "sân bay nội bài", "sân bay đà nẵng",
            "bệnh viện chợ rẫy", "bệnh viện đại học y dược", "bệnh viện bạch mai",
            "bệnh viện nhi đồng", "bệnh viện từ dũ",
            "trường đại học sài gòn", "đại học bách khoa", "đại học quốc gia",
            "hadilao", "haidilao", "manwah", "kichi kichi", "gogi house", 
            "starbucks", "highland coffee", "phúc long", "the coffee house"
        ]
        }

# ==========================================
# 2. HÀM SETUP (GHI FILE)
# ==========================================
def setup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Logic tìm thư mục data thông minh
    if os.path.basename(base_dir) == "nlp":
        data_dir = os.path.join(base_dir, "data")
    else:
        data_dir = os.path.join(base_dir, "nlp", "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    # Ghi từng file
    with open(os.path.join(data_dir, "replace_dict.json"), "w", encoding="utf-8") as f:
        json.dump(teencode_dict, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(data_dir, "en_vi.json"), "w", encoding="utf-8") as f:
        json.dump(en_vi_dict, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(data_dir, "ignore_words.json"), "w", encoding="utf-8") as f:
        json.dump(ignore_words, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(data_dir, "locations.json"), "w", encoding="utf-8") as f:
        json.dump(locations_dict, f, ensure_ascii=False, indent=2)

    print("✅ ĐÃ UPDATE DỮ LIỆU THÀNH CÔNG!")

if __name__ == "__main__":
    setup()