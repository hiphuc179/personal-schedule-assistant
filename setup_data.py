import json
import os

# ==========================================
# 1. KHAI BÁO DỮ LIỆU AMBIGUITY (BIGRAM - TRỌNG TÂM)
# ==========================================
# Đây là "bộ não" giúp phân biệt từ không dấu dựa vào từ đi kèm
ambiguity_dict = {
    # -> MƯA (Rain)
    "mua to": "mưa to", "mua nho": "mưa nhỏ", "mua rao": "mưa rào",
    "mua phung": "mưa phùn", "mua gio": "mưa gió", "mua bao": "mưa bão",
    "dang mua": "đang mưa", "troi mua": "trời mưa", "con mua": "cơn mưa",
    "mua dam": "mưa dầm", "mua da": "mưa đá",
    # -> MUA (Buy)
    "muon mua": "muốn mua", "di mua": "đi mua", "can mua": "cần mua",
    "mua sam": "mua sắm", "mua ban": "mua bán", "mua xe": "mua xe",
    "mua nha": "mua nhà", "mua do": "mua đồ", "mua qua": "mua quà",
    "mua ve": "mua vé", "dat mua": "đặt mua", "nguoi mua": "người mua",
    # --- 1. TOI (Tối vs Tôi) ---
    # -> TỐI (Thời gian)
    "toi nay": "tối nay", "toi qua": "tối qua", "toi mai": "tối mai", "toi mot": "tối mốt",
    "toi kia": "tối kia", "toi hom": "tối hôm", "buoi toi": "buổi tối",
    "toi t2": "tối thứ 2", "toi t3": "tối thứ 3", "toi t4": "tối thứ 4",
    "toi t5": "tối thứ 5", "toi t6": "tối thứ 6", "toi t7": "tối thứ 7",
    "toi cn": "tối chủ nhật", "toi chu nhat": "tối chủ nhật", 
    "den toi": "đến tối", "tu toi": "từ tối", "vao toi": "vào tối",
    # -> TÔI (Xưng hô)
    "toi di": "tôi đi", "toi an": "tôi ăn", "toi lam": "tôi làm", "toi hoc": "tôi học",
    "toi muon": "tôi muốn", "toi can": "tôi cần", "toi thich": "tôi thích", 
    "toi la": "tôi là", "toi se": "tôi sẽ", "toi dang": "tôi đang", "toi da": "tôi đã",
    "toi cung": "tôi cũng", "toi biet": "tôi biết", "toi thay": "tôi thấy", 
    "toi nghi": "tôi nghĩ", "toi ko": "tôi không", "toi khong": "tôi không",
    "cua toi": "của tôi", "cho toi": "cho tôi", "voi toi": "với tôi",
    "toi ten": "tôi tên", "toi o": "tôi ở", "toi ve": "tôi về",

    # --- 2. SANG (Sáng vs Sang) ---
    # -> SÁNG (Thời gian)
    "sang mai": "sáng mai", "sang nay": "sáng nay", "sang qua": "sáng qua", 
    "sang som": "sáng sớm", "buoi sang": "buổi sáng", "sang ra": "sáng ra",
    "sang t2": "sáng thứ 2", "sang t3": "sáng thứ 3", "sang t4": "sáng thứ 4",
    "sang t5": "sáng thứ 5", "sang t6": "sáng thứ 6", "sang t7": "sáng thứ 7",
    "sang cn": "sáng chủ nhật", "sang chu nhat": "sáng chủ nhật",
    # -> SANG (Động từ)
    "di sang": "đi sang", "chay sang": "chạy sang", "sang duong": "sang đường",
    "sang song": "sang sông", "sang kien": "sáng kiến", "sang tao": "sáng tạo",
    "sang chanh": "sang chảnh", "sang ten": "sang tên",

    # --- 3. CHIEU (Chiều vs Chiếu) ---
    # -> CHIỀU (Thời gian)
    "chieu nay": "chiều nay", "chieu mai": "chiều mai", "chieu qua": "chiều qua",
    "buoi chieu": "buổi chiều", "xe chieu": "xế chiều", "chieu t2": "chiều thứ 2",
    "chieu t3": "chiều thứ 3", "chieu t4": "chiều thứ 4", "chieu t5": "chiều thứ 5",
    "chieu t6": "chiều thứ 6", "chieu t7": "chiều thứ 7", "chieu cn": "chiều chủ nhật",
    # -> CHIỀU (Khác)
    "chieu cao": "chiều cao", "chieu rong": "chiều rộng", "chieu dai": "chiều dài",
    "chieu y": "chiều ý", "chieu chuong": "chiều chuộng", "cai chieu": "cái chiếu",
    "chieu phim": "chiếu phim", "doi chieu": "đối chiếu",

    # --- 4. HN (Hà Nội vs Hôm Nay) ---
   # -> HÀ NỘI (Địa điểm)
    "ve hn": "về hà nội", "o hn": "ở hà nội", "tai hn": "tại hà nội", 
    "den hn": "đến hà nội", "ra hn": "ra hà nội", "trong hn": "trong hà nội",
    "di hn": "đi hà nội", "ghe hn": "ghé hà nội", "cong tac hn": "công tác hà nội",
    "hn la thu do": "hà nội là thủ đô", "tp hn": "thành phố hà nội",
    "khu vuc hn": "khu vực hà nội", "nguoi hn": "người hà nội","hn la": "hà nội là",
    
    # -> HÔM NAY (Thời gian)
    "hn tui": "hôm nay tui", "hn toi": "hôm nay tôi", "hn mk": "hôm nay mình",
    "hn b": "hôm nay bạn", "hn ban": "hôm nay bạn", 
    "hn mua": "hôm nay mưa", "hn ranh": "hôm nay rảnh", 
    "hn met": "hôm nay mệt", "hn lam": "hôm nay làm", "hn di": "hôm nay đi",
    "hn nghi": "hôm nay nghỉ", "hn vui": "hôm nay vui", "hn chan": "hôm nay chán",
    "hn co": "hôm nay có", "hn mưa": "hôm nay mưa",

    # --- 5. MUON (Muốn vs Muộn/Mượn) ---
    # -> MUỐN (Động từ)
    "muon an": "muốn ăn", "muon di": "muốn đi", "muon lam": "muốn làm", 
    "muon ngu": "muốn ngủ", "muon xem": "muốn xem", "muon mua": "muốn mua",
    "muon noi": "muốn nói", "muon gap": "muốn gặp", "muon ve": "muốn về",
    # -> MUỘN (Tính từ thời gian)
    "hoc muon": "học muộn", "ve muon": "về muộn", "ngu muon": "ngủ muộn", 
    "den muon": "đến muộn", "lam muon": "làm muộn", "tre muon": "trễ muộn", 
    "qua muon": "quá muộn", "hoi muon": "hơi muộn", "sang muon": "sáng muộn",
    # -> MƯỢN
    "muon tien": "mượn tiền", "muon sach": "mượn sách", "cho muon": "cho mượn",

    # --- 6. BAN (Bận vs Bạn vs Bàn) ---
    # -> BẬN (Trạng thái)
    "dang ban": "đang bận", "ban roi": "bận rồi", "ban viec": "bận việc",
    "ban lam": "bận làm", "ban hoc": "bận học", "ban biu": "bận bịu",
    "hoi ban": "hơi bận", "qua ban": "quá bận",
    # -> BẠN (Người)
    "ban be": "bạn bè", "ban than": "bạn thân", "ban gai": "bạn gái",
    "ban trai": "bạn trai", "nha ban": "nhà bạn", "cung ban": "cùng bạn",
    "voi ban": "với bạn", "gap ban": "gặp bạn", "ket ban": "kết bạn",
    # -> BÀN
    "cai ban": "cái bàn", "ban bac": "bàn bạc", "ban ghe": "bàn ghế",
    "ban cong": "bàn công", "ban phim": "bàn phím",
    
    # --- 7. NAM (Năm vs Nam vs Nằm) ---
    "nam nay": "năm nay", "nam sau": "năm sau", "nam ngoai": "năm ngoái",
    "cuoi nam": "cuối năm", "dau nam": "đầu năm", "1 nam": "1 năm",
    "nam ngu": "nằm ngủ", "nam xuong": "nằm xuống", "mien nam": "miền nam",
    
    # --- 8. NGAY (Ngày vs Ngay) ---
    "ngay mai": "ngày mai", "ngay kia": "ngày kia", "ngay mot": "ngày mốt",
    "ngay le": "ngày lễ", "ca ngay": "cả ngày", "moi ngay": "mỗi ngày",
    "ngay xua": "ngày xưa",
    "lam ngay": "làm ngay", "di ngay": "đi ngay", "an ngay": "ăn ngay",
    "ve ngay": "về ngay", "ngay lap tuc": "ngay lập tức", "ngay bay gio": "ngay bây giờ",
   
    # --- TEENCODE CỤM TỪ ---
    "b s": "bạn sao", "s r": "sao rồi", "s roi": "sao rồi",
    "da vai": "đã vài", "vai s": "vài giây", "vai giay": "vài giây",
    "troi qua": "trôi qua", "r do": "rồi đó", "r ne": "rồi nè",
    "chg xong": "chưa xong", "chua xong": "chưa xong",
    "an cuoi": "ăn cưới", "dam cuoi": "đám cưới",
    "doi tac": "đối tác", "thu do": "thủ đô","ke di": "kệ đi","chan qua": "chán quá","vch chan qua": "vãi chưởng chán quá","dang mla to": "đang mưa to",
    "bai tap": "bài tập","chuyen cong tac": "chuyến công tác","troi qua":"trôi qua","giao ban":"giao ban"
    ,"gap nhau": "gặp nhau","gap ban":"gặp bạn","nay chua":"này chưa","sao nay chua":"sao nay chưa","bao cao":"báo cáo","giao ban":"giao ban"
}

# ==========================================
# 2. KHAI BÁO TEENCODE & TỪ ĐIỂN (BỔ SUNG)
# ==========================================
teencode_dict = {""
    # --- CƠ BẢN ---
    "ko": "không", "k": "không", "kh": "không", "hok": "không", "hong": "không","cai": "cái","bien": "biển",
     "đc": "được","hop": "họp",
    "dc": "được", "dk": "được", "ok": "được", "okie": "được","mla": "mưa",
    "nj": "nhé", "nhe": "nhé", "nhak": "nhé", "nhek": "nhé",
    "jui": "vui", "vuii": "vui", "vuiik": "vui","mõi":"mỗi",
    "thui": "thôi", "thuii": "thôi", "thoik": "thôi",
    "r": "rồi", "roi": "rồi", "rùi": "rồi", "ruoi": "rồi", "ròi": "rồi",
    "d": "đi", "di": "đi", "diu": "đi", "diuk": "đi",
    "ah": "à", "a": "à", "aiz": "à", "ak": "à",
    "eh": "ề", "êh": "ề", "ehh": "ề",
    "haizz": "hà", "hazz": "hà", "haiz": "hà",
    "ui": "ôi", "oai": "ôi", "oái": "ôi",
    "oy": "ơi", "oi": "ơi", "oiy": "ơi", "oí": "ơi",
    "uhm": "ừm","vch": "vãi chưởng", "vcl": "vãi chưởng",
    "vl": "vãi l*n","nay": "nay",
    "ahihi": "à hí hí", "hihi": "hí hí",
    "hehe": "hê hê", "jajaja": "jaja", "jaja": "jaja", "haha": "ha ha",
    "yolo": "you only live once","wa": "quá","tet": "tết","ne": "nè","dau":"đâu","do":"đó",
    # --- XƯNG HÔ ---
    "em": "em", "e": "em", "emk": "em", "emjk": "em",
    "anh": "anh", "a": "anh", "ak": "anh",
    "chi": "chị", "c": "chị", "ck": "chị",
    "ong": "ông",
    "ba": "bà", "bà": "bà","t": "tôi", "m": "mày", "mk": "mình", "mik": "mình", "mjk": "mình",
    "b": "bạn", "bn": "bạn", "cau": "cậu", 
    # --- XÁC NHẬN & PHỦ ĐỊNH ---
    "da": "đã", "r": "rồi", "roi": "rồi","mõi":"mỗi",
    "co": "có", "k co": "không có", "khong co": "không có",
    "chua": "chưa", "ch": "chưa",
    "phai": "phải", "đúng": "đúng", "dung": "đúng",
    "sai": "sai", "khong dung": "không đúng",
    "ok": "ok", "oke": "ok", "okie": "ok",
    "yes": "vâng", "yeah": "vâng", "yep": "vâng", "yup": "vâng",
    "uh": "ừ", "uhm": "ừm", "uk": "ừ", "ye": "vâng", "yep": "vâng",
    "nope": "không","nop":"nộp",
    "never": "không bao giờ",
    "khong": "không", "ko": "không", "k": "không",
    # --- CẢM XÚC ---
    "vui": "vui", "vui ve": "vui vẻ",
    "buon": "buồn", "met": "mệt", "mo": "mơ",
    "ghen": "ghen", "gato": "ghen tị",
    "tuc": "tức", 
    "sung": "sướng", "phuc": "phục",
    "that vong": "thất vọng", "that vọng": "thất vọng",
    "ngac nhien": "ngạc nhiên", "ngạc nhiên": "ngạc nhiên",
    "hoang mang": "hoang mang", "lo lang": "lo lắng",
    "ngan ngam": "ngần ngại",
    "tu tin": "tự tin", "tự tin": "tự tin",
    # --- TÍNH TỪ ---
    "de thuong": "dễ thương",
    "xinh": "xinh", "xinh xan": "xinh xan",
    "dep": "đẹp", "depp": "đẹp", "depp trai": "đẹp trai", "dep gai": "đẹp gái",
    "ngau": "ngầu", "ngau vo cung": "ngầu vô cùng", 
    "vs": "với", "z": "vậy", "j": "gì", "r": "rồi", "rui": "rồi",
    "thik": "thích", "thich": "thích", "thix": "thích",
    "iu": "yêu", "yeu": "yêu",
    "nhieu": "nhiều", "nhiu": "nhiều",
    "it": "ít",
    "nhat": "nhất", "nhat": "nhất",
    "tot": "tốt", "xau": "xấu",
    "kho": "khó", "de": "dễ",
    "nhanh": "nhanh", "cham": "chậm",
    "sang": "sáng", "toi": "tối",
    # --- DANH TỪ ---
     "nhao": "nhào", "nhao": "nhào",
    "truong": "trường", "cty": "công ty", "cong ty": "công ty",
    "lop": "lớp", "ban": "bạn", "ban be": "bạn bè",
    "nguoi yeu": "người yêu", "nguoi iu": "người yêu",
    "chuyen di": "chuyến đi", "cuoc di": "cuộc đi",
    "tien": "tiền", "tien bac": "tiền bạc",
    "xe may": "xe máy", "xe dap": "xe đạp", "xe hoi": "xe hơi",
    "dien thoai": "điện thoại", "dt": "điện thoại",
    "may tinh": "máy tính", "mt": "máy tính",
    "xm": "xe máy",
    "xh": "xe hơi",
    "xd": "xe đạp",
    "tivi": "tivi", "tv": "tivi",
    "xe": "xe",
    "com": "cơm", "bun": "bún", "pho": "phở","cuon": "cuốn",
    # --- ĐỘNG TỪ ---
    "di": "đi", "hoc": "học", "lam": "làm", "ngu": "ngủ", "an": "ăn", "choi": "chơi","voi": "với",
    "ve": "về", "den": "đến", "gap": "gấp", "nghe": "nghe", "xem": "xem",
    "mua": "mua", "doc": "đọc", "viet": "viết", "ngoi": "ngồi", "chay": "chạy", "tap": "tập", 
    "nghi": "nghỉ", "tam": "tắm","dang": "đang",
    "bit": "biết", "noi": "nói","gui": "gửi","hen": "hẹn",
    # --- TRẠNG TỪ ---
    "rat": "rất", "lam": "lắm",
    "kha": "khá", "hoi": "hơi", "tuong doi": "tương đối",
    # --- GIỚI TỪ ---
    "o": "ở", "tai": "tại", "tren": "trên", "duoi": "dưới", "trong": "trong", "ngoai": "ngoài",
    "den": "đến", "tu": "từ", "voi": "với",
    # --- LIÊN TỪ ---
    "va": "và", "cung": "cùng", "nhung": "nhưng", "hoac": "hoặc", "neu": "nếu", 
    "vi": "vì", "nen": "nên",
     # --- THỜI GIAN ---
    "hm nay": "hôm nay", "hnay": "hôm nay", "hqua": "hôm qua", "hm qua": "hôm qua",
    "tôi nay": "tối nay", "toi nay": "tối nay",
    "ngay mai": "ngày mai", "mai": "ngày mai", "mot": "ngày mốt",
    "h": "giờ", "g": "giờ", "p": "phút", "ph": "phút", "s": "giây",
    "sang": "sáng", "trua": "trưa", "chieu": "chiều", "toi": "tối", "khuya": "khuya","tuan":"tuần",
    "thang": "tháng", "nam": "năm",
    "thu": "thứ", "cn": "chủ nhật", "chu nhat": "chủ nhật",
    "h hom": "hôm hôm", "h hom nay": "hôm hôm nay",
    "vua moi": "vừa mới", "vua": "vừa",
    "gan day": "gần đây", "gan": "gần",
    # --- ĐỊA ĐIỂM ---
    "tp hcm": "thành phố hồ chí minh", "hcm": "hồ chí minh", "tphcm": "thành phố hồ chí minh","phong": "phòng",
    "hn": "hà nội", "sg": "sài gòn", "dn": "đà nẵng", "vt": "vũng tàu", "ct": "cần thơ", "dl": "đà lạt",
    "q1": "quận 1", "q2": "quận 2", "q3": "quận 3", "q4": "quận 4", "q5": "quận 5",
    "q6": "quận 6", "q7": "quận 7", "q8": "quận 8", "q9": "quận 9", "q10": "quận 10",
    "q11": "quận 11", "q12": "quận 12", "td": "thủ đức", "bt": "bình thạnh",
    "gv": "quận gò vấp", "tb": "quận tân bình", "pn": "phú nhuận",
    # --- HÀNH ĐỘNG ---
    "di": "đi", "hoc": "học", "lam": "làm", "ngu": "ngủ", "an": "ăn", "choi": "chơi","voi": "với",
    "ve": "về", "den": "đến", "nghe": "nghe", "xem": "xem", "mua": "mua", "ban": "bán",
    "doc": "đọc", "viet": "viết", "ngoi": "ngồi", "chay": "chạy", "tap": "tập", 
    "nghi": "nghỉ", "tam": "tắm", "ve": "về", "den": "đến",
    "bit": "biết", "noi": "nói", "thix": "thích", "iu": "yêu",
    "cam on": "cảm ơn", "tks": "cảm ơn", "thx": "cảm ơn",
    "sr": "xin lỗi", "sry": "xin lỗi",
    "muon": "muộn","luc":"lúc",
    "ranh": "rảnh", "kt":"kiểm tra","bt":"bài tập","tn":"tự nhiên","xh":"xã hội",
    # --- ĐỒ UỐNG & MÓN ĂN ---
    "cf": "cà phê", "ca phe": "cà phê", "trasua": "trà sữa", "tra sua": "trà sữa",
    "nuoc ep": "nước ép", "nuoc mia": "nước mía", "sinh to": "sinh tố",
    "com": "cơm", "pho": "phở", "bun": "bún", "banh mi": "bánh mì", "goi": "gỏi",
    "chao": "cháo", "mi quang": "mì quảng",
    # --- THỜI TIẾT ---
    "nang": "nắng", "gio": "gió", "lanh": "lạnh", "nong": "nóng",
    # --- THỨ CÁC NGÀY ---
    "t2": "thứ 2", "t3": "thứ 3", "t4": "thứ 4", "t5": "thứ 5",
    "t6": "thứ 6", "t7": "thứ 7", "cn": "chủ nhật", "chu nhat": "chủ nhật",

    #--- THỂ THAO ---
    "bong ro": "bóng rổ","cau long": "cầu lông","bong chuyen": "bóng chuyền","da bong": "đá bóng",
    "bong da": "bóng đá","da banh": "đá banh","bong ban": "bóng bàn","quan vot": "quần vợt","boi": "bơi","chay bo": "chạy bộ","dap xe": "đạp xe",""
    "the duc": "thể dục","the thao": "thể thao","tap the duc": "tập thể dục","tap the thao": "tập thể thao","san van dong": "sân vận động","nha thi dau": "nhà thi đấu","cong vien": "công viên","ho boi": "hồ bơi",
    "san bong": "sân bóng","rap phim": "rạp phim",
    

   
}

# 1.3 Anh - Việt (Giữ nguyên hoặc thêm từ chuyên ngành IT của đại ca)
en_vi_dict = {
    "set": "thiết lập", "book": "sách", "meeting": "cuộc họp", 
    "read": "đọc", "call": "gọi", "mess": "nhắn tin", "inbox": "nhắn tin",
    "confirm": "xác nhận", "boss": "sếp", "manager": "quản lý",
    "deadline": "hạn chót", "task": "nhiệm vụ", "project": "dự án",
    "team": "nhóm", "report": "báo cáo", "review": "đánh giá",
    "cancel": "hủy", "delay": "hoãn", "check": "kiểm tra",
    "party": "tiệc",  "coffee": "cà phê","shop": "quán","restaurant": "nhà hàng",
    "lunch": "bữa trưa", "dinner": "bữa tối", "breakfast": "bữa sáng",
    "appointment": "cuộc hẹn","schedule": "lịch trình",
    "online": "trực tuyến", "offline": "ngoại tuyến",
    "video call": "gọi video", "zoom": "gọi video",
    "meeting room": "phòng họp","conference room": "phòng họp","tablet": "máy tính bảng","smartphone": "điện thoại thông minh","notebook": "máy tính xách tay","desktop": "máy tính để bàn",
    "email": "thư điện tử","inbox": "hộp thư","phong tap": "phòng tập"
}

# 1.4 Ignore Words (Các từ rác không cần quan tâm)
ignore_words = [
    "cái", "chiếc", "nha", "nhé", "nè", "ạ", "dạ", "vâng", 
    "thì", "mà", "là", "của", "cho", "với", "và","code","laptop","pc","mobile","gym","boss","manager"
]

# 1.5 Locations (Từ điển địa điểm để quét)
locations_dict = {
    "cities": [
        "hà nội", "hồ chí minh", "hcm", "sài gòn", "đà nẵng", "hải phòng", "cần thơ",
        "nha trang", "đà lạt", "vũng tàu", "huế", "quy nhơn", "buôn ma thuột",
        "phú quốc", "long xuyên", "biên hòa", "thủ đức", "bến tre", "cà mau",
        "cao bằng", "bắc ninh", "quảng ninh", "hạ long", "sapa", "lào cai",
        "hà giang", "mộc châu", "tiền giang", "thái bình", "nam định", "nghệ an", "thanh hóa"
    ],
    "districts": [
        "quận 1", "quận 2", "quận 3", "quận 4", "quận 5", "quận 6",
        "quận 7", "quận 8", "quận 9", "quận 10", "quận 11", "quận 12",
        "gò vấp", "tân bình", "tân phú", "bình thạnh", "phú nhuận", "bình tân",
        "thủ đức", "bình chánh", "hóc môn", "củ chi", "nhà bè",
        "hoàn kiếm", "đống đa", "ba đình", "hai bà trưng", "hoàng mai", "thanh xuân",
        "cầu giấy", "nam từ liêm", "bắc từ liêm", "tây hồ", "long biên"
    ],
    "places": [
        "vincom", "aeon mall", "lotte mart", "gigamall", "takashimaya",
        "landmark 81", "bitexco", "keangnam", "time city", "royal city",
        "bến xe miền đông", "bến xe miền tây", "bến xe mỹ đình", "bến xe giáp bát",
        "sân bay tân sơn nhất", "sân bay nội bài", "sân bay đà nẵng",
        "bệnh viện chợ rẫy", "bệnh viện đại học y dược", "bệnh viện bạch mai",
        "bệnh viện nhi đồng", "bệnh viện từ dũ", "bệnh viện 108",
        "trường đại học sài gòn", "đại học bách khoa", "đại học quốc gia", "đại học kinh tế",
        "hadilao", "haidilao", "manwah", "kichi kichi", "gogi house", 
        "starbucks", "highland coffee", "phúc long", "the coffee house",
        "sân vận động", "nhà thi đấu", "công viên", "hồ bơi", "sân bóng", "rạp phim","phòng tập", "phòng gym", "sân cầu lông", "sân tennis"
    ]
}

# ==========================================
# 2. HÀM SETUP (GHI FILE)
# ==========================================
def setup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Tìm đúng thư mục data
    if os.path.basename(base_dir) == "nlp":
        data_dir = os.path.join(base_dir, "data")
    else:
        data_dir = os.path.join(base_dir, "nlp", "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    # Ghi file Ambiguity
    with open(os.path.join(data_dir, "ambiguity.json"), "w", encoding="utf-8") as f:
        json.dump(ambiguity_dict, f, ensure_ascii=False, indent=2)
    
    # Ghi các file khác
    with open(os.path.join(data_dir, "replace_dict.json"), "w", encoding="utf-8") as f:
        json.dump(teencode_dict, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(data_dir, "en_vi.json"), "w", encoding="utf-8") as f:
        json.dump(en_vi_dict, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(data_dir, "ignore_words.json"), "w", encoding="utf-8") as f:
        json.dump(ignore_words, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(data_dir, "locations.json"), "w", encoding="utf-8") as f:
        json.dump(locations_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ ĐÃ UPDATE DỮ LIỆU THÀNH CÔNG! ({len(ambiguity_dict)} cặp ngữ cảnh, {len(teencode_dict)} từ teencode)")

if __name__ == "__main__":
    setup()