# AVDB18 Python蜘蛛
import base64
import hashlib
import json
import re
import time
import requests
from urllib.parse import quote, unquote

from base.spider import Spider as BaseSpider

SITE_HOST = "https://jdforrepam.com"
IMG_PROXY_BASE = "https://avdb.5569999.xyz"
JD_SIG_PREFIX = "lpw6vgqzsp"
JD_SIG_SECRET = "71cf27bb3c0bcdf207b64abecddc970098c7421ee7203b9cdae54478478a199e7d5a6e1a57691123c1a931c057842fb73ba3b3c83bcd69c17ccf174081e3d8aa"
JD_UA = "Dart/3.5 (dart:io)"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
PAGE_SIZE = 24
REQ_TIMEOUT = 8
BRAND = "🦋 蝴蝶影视"
BRAND_ACTOR = "🦋 TG群: @tvshare23"
TG_GROUP = "https://t.me/tvshare23"
JD_TYPE = {"all": "all", "censored": "0", "uncensored": "1", "western": "2", "fc2": "3"}
GETAV_HOSTS = ["https://getav.net", "https://getav.me", "https://getav.live", "https://getav.co", "https://getav.top"]
AV123_HOST = "https://123av.com"
U9A9_HOST = "https://u9a9.com"
MISSAV_SEARCH_HOST = "https://www.missav06.net"
MISSAV_PLAY_HOSTS = ["https://missav.ws", "https://www.missav06.net", "https://www.thisav.my"]
KANAV_HOSTS = ["https://kanav.ad", "https://kanav.info"]
P115_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 115Browser/36.0.0 Chromium/125.0"
P115_VIDEO_EXTS = ["mp4", "mkv", "avi", "mov", "ts", "m2ts", "webm", "wmv", "rmvb", "flv", "mpg", "mpeg"]
P115_CACHE_FOLDER = "AVDB-Streaming-Cache"
P115_G_KTS = bytes([
    0xf0, 0xe5, 0x69, 0xae, 0xbf, 0xdc, 0xbf, 0x8a,
    0x1a, 0x45, 0xe8, 0xbe, 0x7d, 0xa6, 0x73, 0xb8,
    0xde, 0x8f, 0xe7, 0xc4, 0x45, 0xda, 0x86, 0xc4,
    0x9b, 0x64, 0x8b, 0x14, 0x6a, 0xb4, 0xf1, 0xaa,
    0x38, 0x01, 0x35, 0x9e, 0x26, 0x69, 0x2c, 0x86,
    0x00, 0x6b, 0x4f, 0xa5, 0x36, 0x34, 0x62, 0xa6,
    0x2a, 0x96, 0x68, 0x18, 0xf2, 0x4a, 0xfd, 0xbd,
    0x6b, 0x97, 0x8f, 0x4d, 0x8f, 0x89, 0x13, 0xb7,
    0x6c, 0x8e, 0x93, 0xed, 0x0e, 0x0d, 0x48, 0x3e,
    0xd7, 0x2f, 0x88, 0xd8, 0xfe, 0xfe, 0x7e, 0x86,
    0x50, 0x95, 0x4f, 0xd1, 0xeb, 0x83, 0x26, 0x34,
    0xdb, 0x66, 0x7b, 0x9c, 0x7e, 0x9d, 0x7a, 0x81,
    0x32, 0xea, 0xb6, 0x33, 0xde, 0x3a, 0xa9, 0x59,
    0x34, 0x66, 0x3b, 0xaa, 0xba, 0x81, 0x60, 0x48,
    0xb9, 0xd5, 0x81, 0x9c, 0xf8, 0x6c, 0x84, 0x77,
    0xff, 0x54, 0x78, 0x26, 0x5f, 0xbe, 0xe8, 0x1e,
    0x36, 0x9f, 0x34, 0x80, 0x5c, 0x45, 0x2c, 0x9b,
    0x76, 0xd5, 0x1b, 0x8f, 0xcc, 0xc3, 0xb8, 0xf5,
])
P115_RSA_MOD = 0x8686980c0f5a24c4b9d43020cd2c22703ff3f450756529058b1cf88f09b8602136477198a6e2683149659bd122c33592fdb5ad47944ad1ea4d36c6b172aad6338c3bb6ac6227502d010993ac967d1aef00f0c8e038de2e4d3bc2ec368af2e9f10a6f1eda4f7262f136420c07c331b871bf139f74f3010e3c4fe57df3afb71683
P115_RSA_EXP = 0x10001

TAG_OPTIONS = [
    {"value": "", "name": "全部"},
    {"value": "23", "name": "淫亂真實"},
    {"value": "51", "name": "出軌"},
    {"value": "52", "name": "強姦"},
    {"value": "54", "name": "亂倫"},
    {"value": "56", "name": "溫泉"},
    {"value": "64", "name": "女同性戀"},
    {"value": "86", "name": "企畫"},
    {"value": "107", "name": "戀腿癖"},
    {"value": "112", "name": "獵豔"},
    {"value": "145", "name": "偷窺"},
    {"value": "165", "name": "洗澡"},
    {"value": "2", "name": "其他戀物癖"},
    {"value": "7", "name": "處女"},
    {"value": "13", "name": "性愛"},
    {"value": "33", "name": "學校作品"},
    {"value": "34", "name": "妄想"},
    {"value": "63", "name": "M男"},
    {"value": "75", "name": "跳舞"},
    {"value": "103", "name": "戀物癖"},
    {"value": "109", "name": "戀乳癖"},
    {"value": "111", "name": "惡作劇"},
    {"value": "128", "name": "運動"},
    {"value": "130", "name": "倒追"},
    {"value": "132", "name": "女同接吻"},
    {"value": "135", "name": "美容院"},
    {"value": "149", "name": "奴隸"},
    {"value": "157", "name": "白天出軌"},
    {"value": "160", "name": "流汗"},
    {"value": "162", "name": "性騷擾"},
    {"value": "173", "name": "情侶"},
    {"value": "184", "name": "爛醉如泥的"},
    {"value": "185", "name": "魔鬼系"},
    {"value": "187", "name": "處男"},
    {"value": "196", "name": "殘忍畫面"},
    {"value": "200", "name": "性感的"},
    {"value": "206", "name": "曬黑"},
    {"value": "211", "name": "雙性人"},
    {"value": "218", "name": "全裸"},
    {"value": "221", "name": "正太控"},
    {"value": "234", "name": "觸手"},
    {"value": "243", "name": "正常"},
    {"value": "244", "name": "奇異的"},
    {"value": "249", "name": "蠻橫嬌羞"},
    {"value": "258", "name": "性轉換·女體化"},
    {"value": "277", "name": "男同性戀"},
    {"value": "291", "name": "韓國"},
    {"value": "293", "name": "偷窺"},
    {"value": "300", "name": "形象俱樂部"},
    {"value": "305", "name": "友誼"},
    {"value": "316", "name": "亞洲"},
    {"value": "318", "name": "暗黑系"},
    {"value": "323", "name": "天賦"},
    {"value": "343", "name": "被外國人幹"},
    {"value": "344", "name": "刺青紋身"},
    {"value": "349", "name": "黑白配"},
    {"value": "360", "name": "絕頂高潮"},
    {"value": "361", "name": "運動"},
    {"value": "362", "name": "純欲"},
    {"value": "386", "name": "經歷告白"},
    {"value": "387", "name": "濕身"},
    {"value": "1", "name": "高中女生"},
    {"value": "5", "name": "美少女"},
    {"value": "20", "name": "已婚婦女"},
    {"value": "27", "name": "藝人"},
    {"value": "44", "name": "姐姐"},
    {"value": "47", "name": "各種職業"},
    {"value": "48", "name": "蕩婦"},
    {"value": "55", "name": "母親"},
    {"value": "67", "name": "辣妹"},
    {"value": "70", "name": "妓女"},
    {"value": "101", "name": "新娘，年輕妻子"},
    {"value": "158", "name": "女教師"},
    {"value": "6", "name": "白人"},
    {"value": "16", "name": "婆婆"},
    {"value": "30", "name": "女大學生"},
    {"value": "32", "name": "偶像"},
    {"value": "82", "name": "明星臉"},
    {"value": "105", "name": "大小姐"},
    {"value": "108", "name": "秘書"},
    {"value": "115", "name": "護士"},
    {"value": "118", "name": "角色扮演者"},
    {"value": "133", "name": "賽車女郎"},
    {"value": "136", "name": "家教"},
    {"value": "137", "name": "黑人演員"},
    {"value": "139", "name": "妹妹"},
    {"value": "140", "name": "寡婦"},
    {"value": "142", "name": "女醫生"},
    {"value": "144", "name": "老闆娘，女主人"},
    {"value": "153", "name": "女主播"},
    {"value": "163", "name": "其他學生"},
    {"value": "169", "name": "模特兒"},
    {"value": "172", "name": "格鬥家"},
    {"value": "188", "name": "展場女孩"},
    {"value": "190", "name": "禮儀小姐"},
    {"value": "201", "name": "女檢察官"},
    {"value": "204", "name": "講師"},
    {"value": "224", "name": "服務生"},
    {"value": "233", "name": "伴侶"},
    {"value": "237", "name": "車掌小姐"},
    {"value": "245", "name": "女兒"},
    {"value": "246", "name": "年輕女孩"},
    {"value": "264", "name": "公主"},
    {"value": "265", "name": "童年朋友"},
    {"value": "274", "name": "飛特族"},
    {"value": "282", "name": "亞洲女演員"},
    {"value": "341", "name": "痴漢"},
    {"value": "363", "name": "御宅族"},
    {"value": "365", "name": "老太婆"},
    {"value": "366", "name": "老年男性"},
    {"value": "371", "name": "拉拉隊"},
    {"value": "377", "name": "媽媽的朋友"},
    {"value": "383", "name": "養女"},
    {"value": "384", "name": "女王"},
    {"value": "3", "name": "眼鏡"},
    {"value": "43", "name": "角色扮演"},
    {"value": "49", "name": "內衣"},
    {"value": "58", "name": "制服"},
    {"value": "78", "name": "水手服"},
    {"value": "84", "name": "泳裝"},
    {"value": "95", "name": "和服，喪服"},
    {"value": "106", "name": "連褲襪"},
    {"value": "113", "name": "女傭"},
    {"value": "127", "name": "運動短褲"},
    {"value": "151", "name": "女戰士"},
    {"value": "154", "name": "校服"},
    {"value": "4", "name": "制服外套"},
    {"value": "89", "name": "裸體圍裙"},
    {"value": "96", "name": "女忍者"},
    {"value": "99", "name": "身體意識"},
    {"value": "114", "name": "OL"},
    {"value": "116", "name": "貓耳女"},
    {"value": "125", "name": "短裙"},
    {"value": "126", "name": "學校泳裝"},
    {"value": "129", "name": "迷你裙"},
    {"value": "143", "name": "浴衣"},
    {"value": "156", "name": "猥褻穿著"},
    {"value": "177", "name": "緊身衣"},
    {"value": "181", "name": "娃娃"},
    {"value": "182", "name": "蘿莉角色扮演"},
    {"value": "192", "name": "女裝人妖"},
    {"value": "198", "name": "絲襪、過膝襪"},
    {"value": "199", "name": "泡泡襪"},
    {"value": "203", "name": "空中小姐"},
    {"value": "207", "name": "旗袍"},
    {"value": "216", "name": "兔女郎"},
    {"value": "223", "name": "女祭司"},
    {"value": "230", "name": "動畫人物"},
    {"value": "248", "name": "迷你裙警察"},
    {"value": "270", "name": "修女"},
    {"value": "297", "name": "COSPLAY服飾"},
    {"value": "352", "name": "高跟鞋"},
    {"value": "358", "name": "靴子"},
    {"value": "15", "name": "熟女"},
    {"value": "17", "name": "巨乳"},
    {"value": "19", "name": "蘿莉塔"},
    {"value": "22", "name": "無毛"},
    {"value": "57", "name": "美臀"},
    {"value": "65", "name": "苗條"},
    {"value": "91", "name": "美乳"},
    {"value": "98", "name": "巨大陰莖"},
    {"value": "104", "name": "胖女人"},
    {"value": "146", "name": "平胸"},
    {"value": "338", "name": "素人"},
    {"value": "62", "name": "高挑"},
    {"value": "92", "name": "孕婦"},
    {"value": "131", "name": "大屁股"},
    {"value": "134", "name": "瘦小身型"},
    {"value": "147", "name": "變性者"},
    {"value": "166", "name": "肌肉"},
    {"value": "217", "name": "超乳"},
    {"value": "339", "name": "美腳"},
    {"value": "388", "name": "多毛"},
    {"value": "14", "name": "乳交"},
    {"value": "18", "name": "中出"},
    {"value": "24", "name": "多P"},
    {"value": "25", "name": "69"},
    {"value": "36", "name": "淫語"},
    {"value": "37", "name": "女上位"},
    {"value": "38", "name": "自慰"},
    {"value": "46", "name": "顏射"},
    {"value": "68", "name": "潮吹"},
    {"value": "72", "name": "口交"},
    {"value": "73", "name": "舔陰"},
    {"value": "74", "name": "肛門・肛交"},
    {"value": "77", "name": "手指插入"},
    {"value": "102", "name": "手淫"},
    {"value": "123", "name": "深喉"},
    {"value": "42", "name": "放尿"},
    {"value": "61", "name": "足交"},
    {"value": "69", "name": "按摩"},
    {"value": "81", "name": "吞精"},
    {"value": "100", "name": "母乳"},
    {"value": "110", "name": "濫交"},
    {"value": "124", "name": "接吻"},
    {"value": "141", "name": "拳交"},
    {"value": "195", "name": "飲尿"},
    {"value": "197", "name": "騎乗位"},
    {"value": "202", "name": "排便"},
    {"value": "209", "name": "食糞"},
    {"value": "340", "name": "剃毛"},
    {"value": "342", "name": "二穴同入"},
    {"value": "354", "name": "兩女一男"},
    {"value": "355", "name": "兩男兩女"},
    {"value": "356", "name": "兩男一女"},
    {"value": "368", "name": "打屁股"},
    {"value": "373", "name": "約會"},
    {"value": "374", "name": "不穿內褲"},
    {"value": "375", "name": "不穿胸罩"},
    {"value": "376", "name": "後入"},
    {"value": "378", "name": "瑜伽·健身"},
    {"value": "379", "name": "白眼失神"},
    {"value": "385", "name": "搔癢"},
    {"value": "21", "name": "凌辱"},
    {"value": "29", "name": "捆綁"},
    {"value": "31", "name": "緊縛"},
    {"value": "41", "name": "輪姦"},
    {"value": "50", "name": "玩具"},
    {"value": "60", "name": "SM"},
    {"value": "66", "name": "戶外"},
    {"value": "71", "name": "乳液"},
    {"value": "79", "name": "羞恥"},
    {"value": "90", "name": "女優按摩棒"},
    {"value": "93", "name": "拘束"},
    {"value": "94", "name": "調教"},
    {"value": "170", "name": "立即口交"},
    {"value": "39", "name": "跳蛋"},
    {"value": "53", "name": "監禁"},
    {"value": "76", "name": "按摩棒"},
    {"value": "120", "name": "插入異物"},
    {"value": "138", "name": "灌腸"},
    {"value": "155", "name": "藥物"},
    {"value": "159", "name": "露出"},
    {"value": "171", "name": "汽車性愛"},
    {"value": "176", "name": "催眠"},
    {"value": "179", "name": "鴨嘴"},
    {"value": "180", "name": "糞便"},
    {"value": "225", "name": "脫衣"},
    {"value": "232", "name": "子宮頸"},
    {"value": "315", "name": "導尿"},
    {"value": "346", "name": "蒙面・面罩"},
    {"value": "350", "name": "唾液敷面"},
    {"value": "353", "name": "乳釘、穿孔、乳環"},
    {"value": "357", "name": "口球"},
    {"value": "364", "name": "輔助自慰"},
    {"value": "369", "name": "夫妻交換"},
    {"value": "372", "name": "假陽具"},
    {"value": "380", "name": "鼻鉤"},
    {"value": "382", "name": "蠟燭"},
    {"value": "389", "name": "站立後入"},
    {"value": "28", "name": "單體作品"},
    {"value": "80", "name": "首次亮相"},
    {"value": "164", "name": "故事集"},
    {"value": "175", "name": "經典"},
    {"value": "178", "name": "戀愛"},
    {"value": "212", "name": "VR"},
    {"value": "213", "name": "感謝祭"},
    {"value": "236", "name": "給女性觀眾"},
    {"value": "345", "name": "無碼流出"},
    {"value": "347", "name": "4K"},
    {"value": "348", "name": "無碼破解"},
    {"value": "351", "name": "綜藝"},
    {"value": "390", "name": "LTX破解"},
    {"value": "8", "name": "精選綜合"},
    {"value": "9", "name": "國外進口"},
    {"value": "10", "name": "4小時以上作品"},
    {"value": "11", "name": "戲劇"},
    {"value": "12", "name": "成人電影"},
    {"value": "26", "name": "介紹影片"},
    {"value": "45", "name": "第一人稱攝影"},
    {"value": "83", "name": "薄馬賽克"},
    {"value": "85", "name": "數位馬賽克"},
    {"value": "87", "name": "投稿"},
    {"value": "88", "name": "業餘"},
    {"value": "97", "name": "紀錄片"},
    {"value": "117", "name": "去背影片"},
    {"value": "121", "name": "獨立製作"},
    {"value": "148", "name": "主觀視角"},
    {"value": "150", "name": "戰鬥行動"},
    {"value": "152", "name": "特效"},
    {"value": "161", "name": "16小時以上作品"},
    {"value": "168", "name": "局部特寫"},
    {"value": "189", "name": "重印版"},
    {"value": "191", "name": "歷史劇"},
    {"value": "194", "name": "寫真偶像"},
    {"value": "227", "name": "3D"},
    {"value": "238", "name": "原作改編"},
    {"value": "242", "name": "訪問"},
    {"value": "250", "name": "教學"},
    {"value": "253", "name": "恐怖"},
    {"value": "254", "name": "西洋片"},
    {"value": "266", "name": "科幻"},
    {"value": "267", "name": "行動"},
    {"value": "271", "name": "綜合短篇"},
    {"value": "273", "name": "滑稽模仿"},
    {"value": "280", "name": "男性"},
    {"value": "284", "name": "冒險"},
    {"value": "285", "name": "模擬"},
    {"value": "292", "name": "愛好，文化"},
    {"value": "296", "name": "懸疑"},
    {"value": "311", "name": "R-15"},
    {"value": "312", "name": "美少女電影"},
    {"value": "314", "name": "感官作品"},
    {"value": "325", "name": "觸摸打字"},
    {"value": "330", "name": "素人作品"},
    {"value": "335", "name": "HDTV"},
    {"value": "367", "name": "心理驚悚"},
    {"value": "370", "name": "養尊處優"},
    {"value": "381", "name": "共演"},
]
ACTOR_OPTIONS = [
    {"value": "", "name": "全部"},
    {"value": "kzx6", "name": "田中檸檬（220）"},
    {"value": "R2Vg", "name": "波多野結衣（4290）"},
    {"value": "RJM8", "name": "新有菜（324）"},
    {"value": "Av2e", "name": "三上悠亜（318）"},
    {"value": "wm9B", "name": "明日花綺羅（402）"},
    {"value": "KxPb", "name": "涼森玲夢（181）"},
    {"value": "Ewa2", "name": "七森莉莉（160）"},
    {"value": "QE4G", "name": "園田美櫻（155）"},
    {"value": "96AR", "name": "君島美緒（1109）"},
    {"value": "DXE5", "name": "安齋拉拉（230）"},
    {"value": "x4MV", "name": "高崎聖子（163）"},
    {"value": "1KBW", "name": "JULIA（1255）"},
    {"value": "RAnD", "name": "相澤南（218）"},
    {"value": "WE4e", "name": "篠田優（2310）"},
    {"value": "ZOM6", "name": "佐佐木明希（1163）"},
    {"value": "b7A0", "name": "鈴木心春（257）"},
    {"value": "5Dya", "name": "彩美旬果（240）"},
    {"value": "NO1N", "name": "椎名空（704）"},
    {"value": "A5yq", "name": "葵司（476）"},
    {"value": "J9dd", "name": "紗倉真菜（268）"},
    {"value": "33nb", "name": "柚木蒂娜（538）"},
    {"value": "0dKX", "name": "桃乃木香奈（307）"},
    {"value": "19yv", "name": "三浦歩美（178）"},
    {"value": "0yVv", "name": "吉沢明歩（1422）"},
    {"value": "QNen", "name": "岬奈奈美（147）"},
    {"value": "0Bw3", "name": "吉根柚莉愛（1011）"},
    {"value": "5Oyz", "name": "天使萌（325）"},
    {"value": "G9P5", "name": "麻里梨夏（1192）"},
    {"value": "GMN7", "name": "星奈愛（1004）"},
    {"value": "vd5z", "name": "坂道美琉（247）"},
    {"value": "gyRE", "name": "美谷朱里（1250）"},
    {"value": "0edE", "name": "水卜櫻（221）"},
    {"value": "dxne", "name": "希崎潔西卡（521）"},
    {"value": "B0nG", "name": "蓮實克蕾兒（1920）"},
    {"value": "8GYx", "name": "結城乃乃（380）"},
    {"value": "Xa1G", "name": "白桃花（365）"},
    {"value": "Ng03", "name": "愛音麻里亞（125）"},
    {"value": "6v9D", "name": "浜崎真緒（2703）"},
    {"value": "dxqQ", "name": "里美尤利婭（525）"},
    {"value": "bvWB", "name": "櫻空桃（311）"},
    {"value": "qOA9", "name": "本田岬（305）"},
    {"value": "gDWg", "name": "西條琉璃（473）"},
    {"value": "nRKm", "name": "鈴村愛裏（333）"},
    {"value": "WZGR", "name": "倉多真央（1369）"},
    {"value": "rD3r", "name": "新井愛麗（1216）"},
    {"value": "w49n", "name": "若菜奈央（309）"},
    {"value": "69A0", "name": "河合明日菜（205）"},
    {"value": "35re", "name": "水野朝陽（1511）"},
    {"value": "g40m", "name": "三原穗香（811）"},
    {"value": "gB4E", "name": "西野翔（587）"},
    {"value": "0317", "name": "神坂朋子（199）"},
    {"value": "0x0v", "name": "小野夕子（203）"},
    {"value": "p7Nw", "name": "波木遙（316）"},
    {"value": "nAnV", "name": "唯井真尋（163）"},
    {"value": "BKMM", "name": "大槻響（3029）"},
    {"value": "N4YG", "name": "天海翼（517）"},
    {"value": "gwE", "name": "桃谷繪裏香（40）"},
    {"value": "EKz4", "name": "九重環奈（23）"},
    {"value": "PO5v", "name": "佐山愛（833）"},
    {"value": "M15A", "name": "佐佐波綾（805）"},
    {"value": "9dQE", "name": "蒂亞（282）"},
    {"value": "3Jdb", "name": "跡美珠裏（949）"},
    {"value": "pRMq", "name": "深田詠美（847）"},
    {"value": "5R56", "name": "篠田步美（1438）"},
    {"value": "E4bx", "name": "本真友裡（1031）"},
    {"value": "ZzNm", "name": "神宮寺奈緒（724）"},
    {"value": "YZm6", "name": "香椎梨亞（252）"},
    {"value": "O1bD", "name": "佳苗琉華（955）"},
    {"value": "A2Q0", "name": "小島南（441）"},
    {"value": "8BDW", "name": "山岸逢花（305）"},
    {"value": "6qA7", "name": "松下紗栄子（151）"},
    {"value": "94m6", "name": "松本芽依（458）"},
    {"value": "GW77", "name": "長谷川るい（127）"},
    {"value": "R1GK", "name": "澀谷果步（813）"},
    {"value": "4rw3", "name": "日向真凜（111）"},
    {"value": "AbBK", "name": "夢乃愛華（392）"},
    {"value": "36Qa", "name": "戶田真琴（174）"},
    {"value": "1014", "name": "伊東千奈美（53）"},
    {"value": "wVVz", "name": "奧田咲（440）"},
    {"value": "2D6w", "name": "上原亜衣（1348）"},
    {"value": "dENv", "name": "友田彩也香（1094）"},
    {"value": "rPrR", "name": "吉高寧寧（204）"},
    {"value": "bdpe", "name": "林美玲（18）"},
    {"value": "kyGz", "name": "吉川蓮（53）"},
    {"value": "vNKW", "name": "稻場流花（1194）"},
    {"value": "wK0z", "name": "希島愛裏（468）"},
    {"value": "XxvJ", "name": "音梓（32）"},
    {"value": "5rkM", "name": "栄川乃亜（749）"},
    {"value": "BWy1", "name": "藤浦惠（520）"},
    {"value": "M6mA", "name": "蕾（2194）"},
    {"value": "wBND", "name": "夕美紫苑（318）"},
    {"value": "1B29", "name": "星野娜美（253）"},
    {"value": "ZqB6", "name": "推川悠裡（1140）"},
    {"value": "zkJ7", "name": "河南實裡（423）"},
    {"value": "5BeM", "name": "七瀬あいり（92）"},
    {"value": "ne2M", "name": "桐嶋莉乃（326）"},
    {"value": "N74b", "name": "神波多一花（780）"},
    {"value": "YJeb", "name": "渚光希（1559）"},
    {"value": "eKgR", "name": "宮崎彩（821）"},
    {"value": "7BQJ", "name": "柚月向日葵（90）"},
]
NEW_ACTOR_OPTIONS = [
    {"value": "", "name": "全部"},
    {"value": "0R0O7", "name": "桐谷エマ（4）"},
    {"value": "W1E2q", "name": "大原伶菜（2）"},
    {"value": "zKg76", "name": "夏目琴理（1）"},
    {"value": "MmNgR", "name": "橘春花（2）"},
    {"value": "p3RGw", "name": "辻更紗（2）"},
    {"value": "9DN0X", "name": "蒼井なぎさ（2）"},
    {"value": "YnbPp", "name": "尹秀雅（2）"},
    {"value": "RdgVD", "name": "剱聖蓮（2）"},
    {"value": "rm9Nr", "name": "雪野緋七（2）"},
]

PERIOD_OPTIONS = [
    {"value": "daily", "name": "日榜"},
    {"value": "weekly", "name": "周榜"},
    {"value": "monthly", "name": "月榜"},
]
TYPE_OPTIONS = [
    {"value": "all", "name": "全部"},
    {"value": "censored", "name": "有码"},
    {"value": "uncensored", "name": "无码"},
    {"value": "western", "name": "欧美"},
    {"value": "fc2", "name": "FC2"},
]
CATS = [
    {"id": "playback", "name": "热播榜", "kind": "playback"},
    {"id": "rank0", "name": "有码榜", "kind": "rank", "rtype": "0"},
    {"id": "rank1", "name": "无码榜", "kind": "rank", "rtype": "1"},
    {"id": "ltx", "name": "LTX破解", "kind": "ltx"},
    {"id": "rank3", "name": "FC2榜", "kind": "rank", "rtype": "3"},
    {"id": "rank2", "name": "欧美榜", "kind": "rank", "rtype": "2"},
    {"id": "latest", "name": "最新发布", "kind": "latest"},
    {"id": "top250", "name": "Top250", "kind": "top"},
    {"id": "recommend", "name": "热门推荐", "kind": "recommend"},
    {"id": "filter@@newactor", "name": "热门新人", "kind": "newactor"},
    {"id": "filter@@tag", "name": "分类专区", "kind": "tag"},
    {"id": "filter@@actor", "name": "女优专区", "kind": "actor"},
]


class JdLoginRequiredError(Exception):
    pass


class JdAuthError(Exception):
    pass


class JdApiError(Exception):
    pass


def p115_to_bytes(value, length=None):
    if length is None:
        length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big")


def p115_from_bytes(data):
    return int.from_bytes(data, "big")


def p115_acc_step_list(start, stop, step):
    res = []
    i = start + step
    while i < stop:
        res.append((start, i, step))
        start = i
        i = start + step
    if start != stop:
        res.append((start, stop, stop - start))
    return res


def p115_bytes_xor(v1, v2):
    return bytes(a ^ b for a, b in zip(v1, v2))


def p115_gen_key(rand_key, sk_len):
    xor_key = bytearray(sk_len)
    length = sk_len * (sk_len - 1)
    index = 0
    for i in range(sk_len):
        x = (rand_key[i] + P115_G_KTS[index]) & 0xFF
        xor_key[i] = P115_G_KTS[length] ^ x
        length -= sk_len
        index += sk_len
    return bytes(xor_key)


def p115_pad_pkcs1_v1_5(message):
    msg_len = len(message)
    buf = bytearray(128)
    end = 127 - msg_len
    for i in range(1, end):
        buf[i] = 0x02
    buf[128 - msg_len:] = message
    return p115_from_bytes(bytes(buf))


def p115_xor(src, key):
    out = bytearray(len(src))
    i = len(src) & 0b11
    if i:
        out[0:i] = p115_bytes_xor(src[0:i], key[0:i])
    for (s0, s1, _st) in p115_acc_step_list(i, len(src), len(key)):
        out[s0:s1] = p115_bytes_xor(src[s0:s1], key)
    return bytes(out)


def p115_encrypt(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    inner = p115_xor(p115_xor(data, bytes([0x8d, 0xa5, 0xa5, 0x8d]))[::-1],
                     bytes([0x78, 0x06, 0xad, 0x4c, 0x33, 0x86, 0x5d, 0x18, 0x4c, 0x01, 0x3f, 0x46]))
    xor_text = bytes(16) + inner
    total = ((len(xor_text) + 116) // 117) * 128
    cipher = bytearray(total)
    start = 0
    for (s0, s1, _st) in p115_acc_step_list(0, len(xor_text), 117):
        chunk = xor_text[s0:s1]
        val = pow(p115_pad_pkcs1_v1_5(chunk), P115_RSA_EXP, P115_RSA_MOD)
        cipher[start:start + 128] = p115_to_bytes(val, 128)
        start += 128
    return base64.b64encode(bytes(cipher)).decode("ascii")


def p115_decrypt(cipher_data):
    clean = re.sub(r"\s", "", cipher_data)
    if not re.match(r"^[A-Za-z0-9+/]*={0,2}$", clean) or len(clean) % 4 != 0:
        raise ValueError("115加密响应Base64无效")
    raw = base64.b64decode(clean)
    data = bytearray()
    for (s0, s1, _st) in p115_acc_step_list(0, len(raw), 128):
        p = pow(p115_from_bytes(raw[s0:s1]), P115_RSA_EXP, P115_RSA_MOD)
        b = p115_to_bytes(p)
        zi = b.find(b"\x00")
        data.extend(b[zi + 1:])
    data = bytes(data)
    key_l = p115_gen_key(data[0:16], 12)
    tmp = p115_xor(data[16:], key_l)[::-1]
    return p115_xor(tmp, bytes([0x8d, 0xa5, 0xa5, 0x8d])).decode("utf-8")


def format_remarks(brand="蝴蝶影视", meta=""):
    clean_meta = str(meta or "").strip()
    clean_meta = re.sub(r"[\r\n\t]+", " ", clean_meta).strip()
    if clean_meta:
        return "%s | %s" % (brand, clean_meta)
    return brand


def trim_text(s, n):
    text = str("" if s is None else s)
    if len(text) > n:
        return text[:n]
    return text


def fmt_size(byte_count, mb=None):
    b = 0
    try:
        b = float(byte_count or 0)
    except (TypeError, ValueError):
        b = 0
    if not b and mb:
        try:
            b = float(mb) * 1048576
        except (TypeError, ValueError):
            b = 0
    if not b:
        return ""
    if b >= 1073741824:
        return "%.1fG" % (b / 1073741824)
    if b >= 1048576:
        return "%dM" % int(b / 1048576 + 0.5)
    return "%dK" % int(b / 1024 + 0.5)


def safe_label(value):
    return str(value or "").replace("$", "＄").replace("#", "＃").strip()


def norm_num(s):
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())

class Spider(BaseSpider):
    def __init__(self):
        super(Spider, self).__init__()
        self.siteUrl = SITE_HOST
        self.host = SITE_HOST
        self.options = {}
        self._jd_token = ""
        self._jd_user = ""
        self._jd_pass = ""
        self._pan115_cookie = ""
        self._offline_cid = ""
        self._cache_cid = ""
        year = time.localtime()[0]
        self._year_options = [{"value": "", "name": "全部"}]
        for i in range(12):
            y = str(year - i)
            self._year_options.append({"value": y, "name": y})

    def init(self, extend=""):
        if isinstance(extend, dict):
            options = extend
        elif isinstance(extend, str) and extend.strip():
            try:
                options = json.loads(extend)
            except Exception:
                options = {}
        else:
            options = {}
        if not isinstance(options, dict):
            options = {}
        self.options = options
        host = str(options.get("host") or "").strip()
        if host and host.startswith("http"):
            self.host = host.rstrip("/")
            self.siteUrl = self.host
        else:
            self.host = SITE_HOST
            self.siteUrl = SITE_HOST
        self._jd_user = str(options.get("javdb_user") or "").strip()
        self._jd_pass = str(options.get("javdb_pass") or "").strip()
        self._pan115_cookie = str(options.get("pan115_cookie") or "").strip()
        self._offline_cid = str(options.get("offline_cid") or "").strip()
        self._jd_token = ""
        self._cache_cid = ""
        return True

    def getName(self):
        return "AVDB"

    def _filter_row(self, key, name, init, options):
        return {
            "key": key,
            "name": name,
            "init": init,
            "value": [{"n": o["name"], "v": o["value"]} for o in options],
        }

    def homeContent(self, filter):
        result = {
            "class": [{"type_id": c["id"], "type_name": c["name"]} for c in CATS]
        }
        if filter:
            period = self._filter_row("period", "时段", "daily", PERIOD_OPTIONS)
            ftype = self._filter_row("type", "类型", "all", TYPE_OPTIONS)
            tag = self._filter_row("tag", "题材", "", TAG_OPTIONS)
            year = self._filter_row("year", "年份", "", self._year_options)
            actor = self._filter_row("actor", "选择女优", "", ACTOR_OPTIONS)
            new_actor = self._filter_row("actor", "选择新人", "", NEW_ACTOR_OPTIONS)
            result["filters"] = {
                "playback": [period],
                "rank0": [period],
                "rank1": [period],
                "rank3": [period],
                "rank2": [period],
                "latest": [ftype],
                "top250": [ftype],
                "filter@@newactor": [new_actor],
                "filter@@tag": [tag, year, ftype],
                "filter@@actor": [actor],
            }
        return result

    def homeVideoContent(self):
        return {"list": []}

    def _jd_signature(self):
        ts = int(time.time())
        digest = hashlib.md5((str(ts) + JD_SIG_SECRET).encode("utf-8")).hexdigest()
        return "%s.%s.%s" % (ts, JD_SIG_PREFIX, digest)

    def _jd_headers(self, token):
        headers = {
            "User-Agent": JD_UA,
            "Accept-Language": "zh-TW",
            "jdSignature": self._jd_signature(),
        }
        if token:
            headers["Authorization"] = "Bearer " + token
        return headers

    def _qs(self, params):
        parts = []
        for key in sorted(params.keys()):
            val = params[key]
            if val is None or val == "":
                continue
            parts.append("%s=%s" % (quote(str(key), safe=""), quote(str(val), safe="")))
        return "&".join(parts)

    def _jd_is_auth_err(self, status, body):
        if status in (401, 403):
            return True
        msg = ""
        if isinstance(body, dict):
            msg = str(body.get("message") or "")
        return bool(re.search(r"请登录|請登錄|请登入|請登入|login|log in|unauthorized|authentication", msg, re.I))

    def _jd_call(self, path, params, token):
        url = self.host + path
        query = self._qs(params or {})
        if query:
            url = url + "?" + query
        last_err = None
        for attempt in range(2):
            try:
                resp = requests.get(url, headers=self._jd_headers(token), timeout=REQ_TIMEOUT)
                try:
                    body = resp.json()
                except Exception:
                    body = None
                return {"status": int(resp.status_code), "body": body}
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(0.6)
        raise last_err

    def _jd_login(self):
        if not self._jd_user or not self._jd_pass:
            return ""
        params = {
            "username": self._jd_user,
            "password": self._jd_pass,
            "device_uuid": "04b9534d-5118-53de-9f87-2ddded77111e",
            "device_name": "Chrome",
            "device_model": "Browser",
            "platform": "web",
            "system_version": "1.0",
            "app_version": "official",
            "app_version_number": "1.9.29",
            "app_channel": "official",
        }
        url = self.host + "/api/v1/sessions?" + self._qs(params)
        last_err = None
        resp = None
        for attempt in range(2):
            try:
                resp = requests.post(url, data="", headers=self._jd_headers(""), timeout=REQ_TIMEOUT)
                break
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(0.6)
        if resp is None:
            raise last_err
        try:
            body = resp.json()
        except Exception:
            body = None
        token = ""
        if isinstance(body, dict) and isinstance(body.get("data"), dict):
            token = body["data"].get("token") or ""
        if not token:
            msg = "未知错误"
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    msg = body.get("message") or err.get("message") or msg
                else:
                    msg = body.get("message") or msg
            raise JdApiError("JavDB 登录失败：" + str(msg) + "（请检查源 ext 里的 JavDB 账号密码）")
        self._jd_token = token
        return token

    def _jd_get(self, path, params):
        token = self._jd_token
        result = self._jd_call(path, params, token)
        body = result["body"]
        if isinstance(body, dict) and body.get("success") in (1, True):
            data = body.get("data")
            return data if isinstance(data, dict) else {}
        if self._jd_is_auth_err(result["status"], body):
            if self._jd_user and self._jd_pass:
                self._jd_token = ""
                token = self._jd_login()
                result = self._jd_call(path, params, token)
                body = result["body"]
                if isinstance(body, dict) and body.get("success") in (1, True):
                    data = body.get("data")
                    return data if isinstance(data, dict) else {}
                if self._jd_is_auth_err(result["status"], body):
                    raise JdAuthError("JavDB 登录状态异常：请检查源 ext 里的 JavDB 账号密码后重试")
            else:
                raise JdLoginRequiredError("此内容需要 JavDB 登录：请在源 ext 里填写 javdb_user 与 javdb_pass")
        if not isinstance(body, dict):
            raise JdApiError("JavDB 回包非 JSON（HTTP %s）" % result["status"])
        raise JdApiError(str(body.get("message") or ("JavDB 接口异常（HTTP %s）" % result["status"])))

    def _soft(self, fn):
        try:
            return fn()
        except Exception:
            return None

    def _movies_of(self, data):
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if isinstance(data.get("movies"), list):
                return data["movies"]
            if isinstance(data.get("items"), list):
                return data["items"]
        return []

    def _poster_of(self, raw):
        if not raw or not isinstance(raw, str):
            return ""
        return IMG_PROXY_BASE + "/api/v1/img-proxy/?url=" + quote(raw, safe="")

    def _raw_poster_of(self, m, big):
        if big:
            u = m.get("cover_url") or m.get("thumb_url")
        else:
            u = m.get("thumb_url") or m.get("cover_url")
        return u if isinstance(u, str) else ""

    def _card(self, m):
        flags = []
        if m.get("has_cnsub"):
            flags.append("中字")
        if m.get("can_play"):
            flags.append("可播")
        if m.get("magnets_count"):
            flags.append("磁力%s" % m.get("magnets_count"))
        raw_parts = []
        if m.get("number"):
            raw_parts.append(str(m.get("number")))
        if m.get("release_date"):
            raw_parts.append(str(m.get("release_date")))
        if m.get("duration"):
            raw_parts.append("%s分钟" % m.get("duration"))
        raw_parts.extend(flags)
        status_text = " · ".join(raw_parts)
        remarks = format_remarks(BRAND, status_text)
        mid = str(m.get("id") or "")
        number = str(m.get("number") or "")
        vod_id = "vod/" + mid
        if number:
            vod_id = vod_id + "@@" + quote(number, safe="")
        title = m.get("title") or m.get("origin_title") or number or mid
        return {
            "vod_id": vod_id,
            "vod_name": title,
            "vod_pic": self._poster_of(self._raw_poster_of(m, False)),
            "vod_remarks": remarks,
            "style": {"type": "rect", "ratio": 0.75},
        }

    def _page(self, items, pg):
        try:
            page = max(1, int(pg))
        except (TypeError, ValueError):
            page = 1
        if not items:
            return {"list": [], "page": page, "pagecount": 1, "limit": PAGE_SIZE, "total": 0}
        if len(items) >= PAGE_SIZE:
            return {"list": items, "page": page, "pagecount": page + 1, "limit": PAGE_SIZE, "total": (page + 1) * PAGE_SIZE}
        return {"list": items, "page": page, "pagecount": page, "limit": PAGE_SIZE, "total": (page - 1) * PAGE_SIZE + len(items)}

    def _page_all(self, items, pg):
        try:
            page = max(1, int(pg))
        except (TypeError, ValueError):
            page = 1
        total = len(items)
        start = (page - 1) * PAGE_SIZE
        return {
            "list": items[start:start + PAGE_SIZE],
            "page": page,
            "pagecount": max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE),
            "limit": PAGE_SIZE,
            "total": total,
        }

    def _brand_lines(self):
        return [
            "🦋 蝴蝶影视官方交流群：@tvshare23",
            "当前主站域名：" + self.host,
            "━" * 28,
            "━" * 7,
        ]

    def _jd_latest(self, ftype, page, limit):
        data = self._jd_get("/api/v1/movies/latest", {
            "type": JD_TYPE.get(ftype) or "all",
            "filter_by": "all",
            "sort_by": "update",
            "order_by": "desc",
            "page": page,
            "limit": limit,
        })
        return self._movies_of(data)

    def _jd_tag_movies(self, tag_id, year, ftype, single_type, page, limit):
        def fb(t):
            return ":".join([t, "t", "", tag_id or "", year or "", "", ""])

        def one(t, pg, lim):
            res = self._jd_get("/api/v1/movies/tags", {
                "filter_by": fb(t),
                "sort_by": "release",
                "order_by": "desc",
                "page": pg,
                "limit": lim,
            })
            return self._movies_of(res)

        if single_type:
            return one(single_type, page, limit)
        t = JD_TYPE.get(ftype) or "all"
        if t != "all":
            return one(t, page, limit)
        up_pages = max(1, -(-page * limit // 50))
        all_items = []
        for tt in ["0", "1", "2", "3", "4"]:
            acc = []
            for p in range(1, up_pages + 1):
                ms = self._soft(lambda tt=tt, p=p: one(tt, p, 50))
                if ms:
                    acc.extend(ms)
            all_items.extend(acc)
        seen = set()
        deduped = []
        for m in all_items:
            mid = str(m.get("id") or "")
            if not mid or mid in seen:
                continue
            seen.add(mid)
            deduped.append(m)
        deduped.sort(key=lambda m: str(m.get("release_date") or m.get("updated_at") or ""), reverse=True)
        start = (page - 1) * limit
        return deduped[start:start + limit]

    def _jd_actor_movies(self, actor_id, page, limit):
        res = self._jd_get("/api/v1/movies/tags", {
            "filter_by": "0:a:" + actor_id,
            "sort_by": "release",
            "order_by": "desc",
            "page": page,
            "limit": limit,
        })
        return self._movies_of(res)

    def _list_by_cat(self, cat, extend, page):
        kind = cat.get("kind")
        if kind == "playback":
            data = self._jd_get("/api/v1/rankings/playback", {
                "filter_by": "all",
                "period": str(extend.get("period") or "daily"),
            })
            return self._movies_of(data)
        if kind == "rank":
            data = self._jd_get("/api/v1/rankings", {
                "type": str(cat.get("rtype") or "0"),
                "period": str(extend.get("period") or "daily"),
            })
            return self._movies_of(data)
        if kind == "ltx":
            return self._jd_tag_movies("390", "", "all", "0", page, PAGE_SIZE)
        if kind == "latest":
            return self._jd_latest(str(extend.get("type") or "all"), page, PAGE_SIZE)
        if kind == "top":
            t = JD_TYPE.get(str(extend.get("type") or "all")) or "all"
            params = {"start_rank": 1, "ignore_watched": "false", "page": page, "limit": PAGE_SIZE}
            if t == "all":
                params["type"] = "all"
                params["type_value"] = ""
            else:
                params["type"] = "video_type"
                params["type_value"] = t
            data = self._jd_get("/api/v1/movies/top", params)
            return self._movies_of(data)
        if kind == "recommend":
            data = self._jd_get("/api/v1/movies/recommend", {"type": "0"})
            return self._movies_of(data)
        if kind == "tag":
            tag = str(extend.get("tag") or "")
            year = str(extend.get("year") or "")
            ftype = str(extend.get("type") or "all")
            if not tag and not year:
                return self._jd_latest(ftype, page, PAGE_SIZE)
            return self._jd_tag_movies(tag, year, ftype, "", page, PAGE_SIZE)
        if kind == "actor":
            actor = str(extend.get("actor") or "")
            if not actor:
                return self._jd_latest("all", page, PAGE_SIZE)
            return self._jd_actor_movies(actor, page, PAGE_SIZE)
        if kind == "newactor":
            actor = str(extend.get("actor") or "")
            if actor:
                return self._jd_actor_movies(actor, page, PAGE_SIZE)
            if page > 1:
                return []
            ids = []
            for row in NEW_ACTOR_OPTIONS:
                if row.get("value"):
                    ids.append(row["value"])
                if len(ids) >= 9:
                    break
            if not ids:
                return []
            all_items = []
            for a in ids:
                ms = self._soft(lambda a=a: self._jd_actor_movies(a, 1, 6))
                if ms:
                    all_items.extend(ms)
            seen = set()
            deduped = []
            for m in all_items:
                mid = str(m.get("id") or "")
                if not mid or mid in seen:
                    continue
                seen.add(mid)
                deduped.append(m)
            deduped.sort(key=lambda m: str(m.get("release_date") or ""), reverse=True)
            return deduped[:PAGE_SIZE]
        return []

    def categoryContent(self, tid, pg, filter, extend):
        extend = extend if isinstance(extend, dict) else {}
        try:
            page = max(1, int(pg))
        except (TypeError, ValueError):
            page = 1
        cat = None
        for c in CATS:
            if c["id"] == tid:
                cat = c
                break
        if cat is None:
            cat = CATS[6]
        try:
            movies = self._list_by_cat(cat, extend, page)
        except (JdLoginRequiredError, JdAuthError, JdApiError, requests.RequestException, ValueError, KeyError):
            movies = []
        items = [self._card(m) for m in movies]
        if cat.get("kind") in ("playback", "rank", "recommend"):
            return self._page_all(items, page)
        return self._page(items, page)

    def _parse_vod_id(self, raw):
        text = str(raw or "")
        if text.startswith("vod/"):
            text = text[4:]
        parts = text.split("@@", 1)
        mid = parts[0]
        number = ""
        if len(parts) > 1:
            try:
                number = unquote(parts[1])
            except Exception:
                number = parts[1]
        return mid, number

    def _detail_summary(self, m, number, detail_down, p115_count, partner_names, reviews, related_numbers=None):
        lines = self._brand_lines()
        if detail_down:
            lines.append("（JavDB 详情暂不可用，已先列出匹配到的资源，稍后刷新可重试）")
        score = m.get("score") or "-"
        if m.get("reviews_count"):
            score = "%s（%s人评）" % (score, m.get("reviews_count"))
        meta1 = "｜".join([
            "番号：" + (number or "-"),
            "发行：" + str(m.get("release_date") or "-"),
            "时长：" + (str(m.get("duration")) + "分钟" if m.get("duration") else "-"),
            "评分：" + str(score),
        ])
        lines.append(meta1)
        meta2 = []
        if m.get("maker_name"):
            meta2.append("厂牌：" + str(m.get("maker_name")))
        if m.get("series_name"):
            meta2.append("系列：" + str(m.get("series_name")))
        if meta2:
            lines.append("｜".join(meta2))
        actor_names = []
        for a in m.get("actors") or []:
            if isinstance(a, dict) and a.get("name"):
                actor_names.append(str(a.get("name")))
        if actor_names:
            lines.append("演员：" + "、".join(actor_names))
        tag_names = []
        for t in m.get("tags") or []:
            if isinstance(t, dict) and t.get("name"):
                tag_names.append(str(t.get("name")))
        if tag_names:
            lines.append("分类：" + "、".join(tag_names))
        if m.get("summary"):
            lines.append("简介：" + str(m.get("summary")))
        preview_images = m.get("preview_images")
        if isinstance(preview_images, list) and preview_images:
            lines.append("预告图：%s张" % len(preview_images))
        lines.append("想看：%s｜看过：%s｜评论：%s｜磁力：%s" % (
            m.get("want_watch_count") or 0,
            m.get("watched_count") or 0,
            m.get("comments_count") or 0,
            m.get("magnets_count") or 0,
        ))
        if p115_count:
            lines.append("115：已匹配 %s 个文件，可直接播放" % p115_count)
        if partner_names:
            lines.append("站源：" + "、".join(partner_names) + " 有此片，可直接播放")
        if related_numbers:
            lines.append("相关推荐：" + "、".join(related_numbers[:6]))
        if reviews:
            lines.append("")
            lines.append("【精选影评】")
            for r in reviews[:5]:
                if not isinstance(r, dict):
                    continue
                content = re.sub(r"\s+", " ", str(r.get("content") or "")).strip()
                if not content:
                    continue
                lines.append("%s ★%s（赞%s）：%s" % (
                    r.get("username") or "匿名",
                    r.get("score") or "-",
                    r.get("likes_count") or 0,
                    trim_text(content, 120),
                ))
        return "\n".join(lines)

    def _magnet_name(self, prefix, size_str, cnsub, hd, date):
        parts = [prefix]
        if size_str:
            parts.append(size_str)
        if cnsub:
            parts.append("中字")
        if hd:
            parts.append("高清")
        if date:
            parts.append(date)
        return trim_text(" ".join(parts), 72)

    def detailContent(self, ids):
        raw_id = ids[0] if isinstance(ids, (list, tuple)) and ids else str(ids or "")
        mid, ref_number = self._parse_vod_id(raw_id)
        if not mid:
            return {"list": [], "msg": "条目 id 缺失"}
        try:
            data = self._jd_get("/api/v4/movies/" + quote(mid, safe=""), {})
        except JdLoginRequiredError:
            return {"list": [], "msg": "此内容需要 JavDB 登录：请在源 ext 里填写 javdb_user 与 javdb_pass"}
        except JdAuthError:
            return {"list": [], "msg": "JavDB 登录状态异常：请检查源 ext 里的 JavDB 账号密码后重试"}
        except (JdApiError, requests.RequestException, ValueError, KeyError):
            return {"list": [], "msg": "详情请求失败，请稍后重试"}
        m = {}
        if isinstance(data, dict) and isinstance(data.get("movie"), dict):
            m = data["movie"]
        detail_down = not m.get("id")
        if detail_down:
            m["id"] = mid
            if ref_number:
                m["number"] = ref_number
        number = str(m.get("number") or ref_number or "")
        pre_number = ref_number or number
        mag_data = self._soft(lambda: self._jd_get("/api/v1/movies/" + quote(mid, safe="") + "/magnets", {}))
        rev_data = self._soft(lambda: self._jd_get("/api/v1/movies/" + quote(mid, safe="") + "/reviews", {"page": 1, "limit": 5}))
        p115_files = []
        if pre_number:
            found = self._soft(lambda: self._match115(pre_number))
            if isinstance(found, list):
                p115_files = found
        getav_hit = self._soft(lambda: self._probe_getav(pre_number)) if pre_number else None
        av123_hit = self._soft(lambda: self._probe_123(pre_number)) if pre_number else None
        missav_hit = self._soft(lambda: self._probe_missav(pre_number)) if pre_number else None
        kanav_hit = self._soft(lambda: self._probe_kanav(pre_number)) if pre_number else None
        av123_measure = ""
        if av123_hit:
            av123_measure = self._soft(lambda: self._measure_123(av123_hit["slug"])) or ""
        av123_ep_name = ("正片 · " + av123_measure) if av123_measure else "正片"
        partner_names = []
        if getav_hit:
            partner_names.append("GetAV")
        if av123_hit:
            partner_names.append("123AV")
        if missav_hit:
            partner_names.append("MissAV")
        if kanav_hit:
            partner_names.append("KanAV")
        reviews = []
        if isinstance(rev_data, dict) and isinstance(rev_data.get("reviews"), list):
            reviews = rev_data["reviews"]
        rel_movies = m.get("relative_movies") or []
        rel_eps = []
        rel_numbers = []
        for rm in rel_movies:
            if not isinstance(rm, dict):
                continue
            rid = str(rm.get("id") or "")
            rnum = str(rm.get("number") or "")
            if not rid:
                continue
            value = json.dumps({"kind": "related", "id": rid, "number": rnum}, ensure_ascii=False, separators=(",", ":"))
            rel_eps.append("%s$%s" % (safe_label(rnum or rid), value))
            if rnum:
                rel_numbers.append(rnum)
        summary = self._detail_summary(m, number, detail_down, len(p115_files), partner_names, reviews, rel_numbers)
        sources = []
        if p115_files:
            eps = []
            for idx, f in enumerate(p115_files):
                name = trim_text(str(f.get("name") or ""), 44)
                if f.get("size"):
                    name = name + "｜" + fmt_size(f.get("size"))
                value = json.dumps({"kind": "p115", "id": mid, "pc": f.get("pc") or "", "fid": f.get("fid") or ""}, ensure_ascii=False, separators=(",", ":"))
                eps.append("%s$%s" % (safe_label(name), value))
            sources.append(("🦋 蝴蝶·115云播", eps))
        mag_eps = []
        direct_eps = []
        mag_seen = set()
        if isinstance(mag_data, dict) and isinstance(mag_data.get("magnets"), list):
            for idx, g in enumerate(mag_data["magnets"][:30]):
                if not isinstance(g, dict):
                    continue
                link = g.get("magnet_url") or g.get("magnet") or g.get("url") or ""
                if not link and g.get("hash"):
                    link = "magnet:?xt=urn:btih:" + str(g.get("hash"))
                if not link:
                    continue
                size_bytes = g.get("size_bytes") or 0
                if not size_bytes and g.get("size"):
                    try:
                        size_bytes = round(float(g.get("size")) * 1048576)
                    except (TypeError, ValueError):
                        size_bytes = 0
                key = str(g.get("hash") or "").lower()
                if not key:
                    found = re.search(r"btih:([a-z0-9]+)", str(link), re.I)
                    if found:
                        key = found.group(1).lower()
                if not key:
                    key = str(link)
                if key in mag_seen:
                    continue
                mag_seen.add(key)
                name = self._magnet_name("[线上]", fmt_size(size_bytes), bool(g.get("cnsub")), bool(g.get("hd")), str(g.get("created_at") or ""))
                size_mb = 0
                if size_bytes:
                    size_mb = int(size_bytes / 1048576 + 0.5)
                value = json.dumps({"kind": "magnet", "id": mid, "number": number, "magnet": link, "magName": str(g.get("name") or ""), "sizeMb": size_mb}, ensure_ascii=False, separators=(",", ":"))
                mag_eps.append("%s$%s" % (safe_label(name), value))
                direct_value = json.dumps({"kind": "magnet_direct", "id": mid, "number": number, "magnet": link}, ensure_ascii=False, separators=(",", ":"))
                direct_eps.append("%s$%s" % (safe_label(name), direct_value))
        if len(mag_eps) < 10 and pre_number:
            agg = self._soft(lambda: self._probe_u9a9(pre_number))
            if isinstance(agg, list):
                for g in agg[:10]:
                    link = g.get("magnet") or ""
                    if not link:
                        continue
                    key = str(g.get("hash") or "").lower()
                    if not key:
                        found = re.search(r"btih:([a-z0-9]+)", link, re.I)
                        if found:
                            key = found.group(1).lower()
                    if not key or key in mag_seen:
                        continue
                    mag_seen.add(key)
                    size_bytes = g.get("size_bytes") or 0
                    size_mb = 0
                    if size_bytes:
                        size_mb = int(size_bytes / 1048576 + 0.5)
                    name = self._magnet_name("[聚合]", fmt_size(size_bytes), False, False, str(g.get("date") or ""))
                    value = json.dumps({"kind": "magnet", "id": mid, "number": number, "magnet": link, "magName": str(g.get("name") or ""), "sizeMb": size_mb}, ensure_ascii=False, separators=(",", ":"))
                    mag_eps.append("%s$%s" % (safe_label(name), value))
                    direct_value = json.dumps({"kind": "magnet_direct", "id": mid, "number": number, "magnet": link}, ensure_ascii=False, separators=(",", ":"))
                    direct_eps.append("%s$%s" % (safe_label(name), direct_value))
        if mag_eps:
            sources.append(("🦋 蝴蝶·115离线", mag_eps))
            sources.append(("🦋 蝴蝶·磁力直连", direct_eps))
        if getav_hit:
            eps = []
            for gt in getav_hit.get("tiers", []):
                value = json.dumps({"kind": "getav", "id": mid, "number": number, "url": gt.get("url") or "", "host": getav_hit.get("host") or ""}, ensure_ascii=False, separators=(",", ":"))
                eps.append("%s$%s" % (safe_label(gt.get("label") or "正片"), value))
            sources.append(("🦋 蝴蝶·GetAV", eps))
        if av123_hit:
            value = json.dumps({"kind": "av123", "id": mid, "slug": av123_hit.get("slug") or ""}, ensure_ascii=False, separators=(",", ":"))
            sources.append(("🦋 蝴蝶·123AV", ["%s$%s" % (safe_label(av123_ep_name), value)]))
        if missav_hit:
            value = json.dumps({"kind": "missav", "id": mid, "slug": missav_hit.get("slug") or ""}, ensure_ascii=False, separators=(",", ":"))
            sources.append(("🦋 蝴蝶·MissAV", ["%s$%s" % (safe_label("正片"), value)]))
        if kanav_hit:
            badge = kanav_hit.get("badge") or ""
            name = ("正片 · " + badge) if badge else "正片"
            value = json.dumps({"kind": "kanav", "id": mid, "host": kanav_hit.get("host") or "", "playPath": kanav_hit.get("playPath") or ""}, ensure_ascii=False, separators=(",", ":"))
            sources.append(("🦋 蝴蝶·KanAV", ["%s$%s" % (safe_label(name), value)]))
        if m.get("has_preview_video"):
            value = json.dumps({"kind": "preview", "id": mid}, ensure_ascii=False, separators=(",", ":"))
            sources.append(("🦋 蝴蝶·预告片", ["%s$%s" % (safe_label("预告片"), value)]))
        if rel_eps:
            sources.append(("🦋 相关推荐", rel_eps))
        if not sources:
            value = json.dumps({"kind": "info", "id": mid, "msg": "这部片暂时没有可用资源"}, ensure_ascii=False, separators=(",", ":"))
            sources.append(("资源", ["%s$%s" % (safe_label("暂无资源"), value)]))
        play_from = "$$$".join([s[0] for s in sources])
        play_url = "$$$".join(["#".join(s[1]) for s in sources])
        raw_parts = []
        if number:
            raw_parts.append(number)
        if m.get("release_date"):
            raw_parts.append(str(m.get("release_date")))
        if m.get("duration"):
            raw_parts.append("%s分钟" % m.get("duration"))
        remarks = format_remarks(BRAND, " · ".join(raw_parts))
        actor_names = []
        for a in m.get("actors") or []:
            if isinstance(a, dict) and a.get("name"):
                actor_names.append(str(a.get("name")))
        poster = self._poster_of(self._raw_poster_of(m, True))
        title = m.get("title") or m.get("origin_title") or number or mid
        year = ""
        if m.get("release_date"):
            year = str(m.get("release_date"))[:4]
        vod = {
            "vod_id": raw_id,
            "vod_name": title,
            "vod_pic": poster,
            "vod_bg": poster,
            "vod_background": poster,
            "vod_banner": poster,
            "vod_year": year,
            "vod_remarks": remarks,
            "vod_actor": "、".join(actor_names) if actor_names else BRAND_ACTOR,
            "vod_director": BRAND,
            "vod_content": summary,
            "vod_play_from": play_from,
            "vod_play_url": play_url,
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        try:
            page = max(1, int(pg))
        except (TypeError, ValueError):
            page = 1
        keyword = str(key or "").strip()
        if not keyword:
            return {"list": [], "page": page, "pagecount": 1, "limit": PAGE_SIZE, "total": 0}
        try:
            data = self._jd_get("/api/v2/search", {
                "q": keyword,
                "type": "movie",
                "movie_type": "all",
                "movie_sort_by": "relevance",
                "page": page,
                "limit": PAGE_SIZE,
            })
        except JdLoginRequiredError:
            return {"list": [], "page": page, "pagecount": 1, "limit": PAGE_SIZE, "total": 0, "msg": "搜索需要 JavDB 登录：请在源 ext 里填写 javdb_user 与 javdb_pass"}
        except JdAuthError:
            return {"list": [], "page": page, "pagecount": 1, "limit": PAGE_SIZE, "total": 0, "msg": "JavDB 登录状态异常：请检查源 ext 里的 JavDB 账号密码后重试"}
        except (JdApiError, requests.RequestException, ValueError, KeyError):
            return {"list": [], "page": page, "pagecount": 1, "limit": PAGE_SIZE, "total": 0, "msg": "搜索请求失败，请稍后重试"}
        movies = self._movies_of(data)
        items = [self._card(m) for m in movies]
        result = self._page(items, page)
        return result

    def _play_related(self, ref):
        mid = str(ref.get("id") or "")
        number = str(ref.get("number") or "")
        if not mid:
            return {"parse": 0, "msg": "无效的播放 ID"}
        vod_id = "vod/" + mid + ("@@" + quote(number, safe="") if number else "")
        detail = self.detailContent([vod_id])
        items = detail.get("list", []) if isinstance(detail, dict) else []
        if not items:
            return {"parse": 0, "msg": str(detail.get("msg") or "未找到该影片") if isinstance(detail, dict) else "未找到该影片"}
        vod = items[0]
        play_url = str(vod.get("vod_play_url") or "")
        if not play_url:
            return {"parse": 0, "msg": "这部片暂时没有可用资源"}
        first_group = play_url.split("$$$")[0]
        first_ep = first_group.split("#")[0] if first_group else ""
        if "$" not in first_ep:
            return {"parse": 0, "msg": "这部片暂时没有可用资源"}
        value = first_ep.split("$", 1)[1]
        try:
            next_ref = json.loads(value)
        except Exception:
            return {"parse": 0, "msg": "这部片暂时没有可用资源"}
        if not isinstance(next_ref, dict) or next_ref.get("kind") == "related":
            return {"parse": 0, "msg": "这部片暂时没有可用资源"}
        return self.playerContent("", json.dumps(next_ref, ensure_ascii=False), "")

    def playerContent(self, flag, id, vipFlags):
        try:
            ref = json.loads(str(id or ""))
        except Exception:
            return {"parse": 0, "msg": "无效的播放 ID"}
        if not isinstance(ref, dict):
            return {"parse": 0, "msg": "无效的播放 ID"}
        kind = ref.get("kind") or ""
        mid = str(ref.get("id") or "")
        if kind == "related" and mid:
            return self._play_related(ref)
        if kind == "preview" and mid:
            data = self._soft(lambda: self._jd_get("/api/v4/movies/" + quote(mid, safe=""), {}))
            url = ""
            if isinstance(data, dict) and isinstance(data.get("movie"), dict):
                url = data["movie"].get("preview_video_url") or ""
            if url:
                return {"parse": 0, "jx": 0, "url": url, "header": {"User-Agent": UA}, "format": "hls"}
            return {"parse": 1, "url": "https://javdb.com/v/" + mid, "header": {"User-Agent": UA}}
        if kind == "p115" and ref.get("pc"):
            if not self._pan115_cookie:
                return {"parse": 0, "msg": "请先在源 ext 里填写 pan115_cookie"}
            try:
                play = self._play115(str(ref.get("pc")))
            except Exception:
                return {"parse": 0, "msg": "115 取链失败：直链与 HLS 均不可用，请检查 115 Cookie 是否有效"}
            return {"parse": 0, "jx": 0, "url": play["url"], "header": play["headers"], "format": play["format"]}
        if kind == "magnet_direct":
            if not ref.get("magnet"):
                return {"parse": 0, "msg": "这条候选没有可播放的链接，换一条试试"}
            return {"parse": 0, "jx": 0, "url": str(ref.get("magnet")), "header": {"User-Agent": UA}}
        if kind == "magnet":
            number = str(ref.get("number") or "")
            if number and self._pan115_cookie:
                files = self._soft(lambda: self._match115(number))
                if files:
                    try:
                        play = self._play115(str(files[0].get("pc") or ""))
                        return {"parse": 0, "jx": 0, "url": play["url"], "header": play["headers"], "format": play["format"]}
                    except Exception:
                        pass
            if not ref.get("magnet"):
                return {"parse": 0, "msg": "这条候选没有可提交的链接，换一条试试"}
            return self._submit_magnet_or_msg({
                "magnet": str(ref.get("magnet") or ""),
                "number": number,
                "movieId": mid,
                "name": str(ref.get("magName") or ""),
                "sizeMb": ref.get("sizeMb") or 0,
            })
        if kind == "getav":
            try:
                play = self._play_getav(ref)
            except Exception:
                return {"parse": 0, "msg": "GetAV 取链失败，请稍后重试"}
            return {"parse": 0, "jx": 0, "url": play["url"], "header": play["headers"], "format": "hls"}
        if kind == "av123" and ref.get("slug"):
            try:
                play = self._play_123(str(ref.get("slug")))
            except Exception:
                return {"parse": 0, "msg": "123AV 取链失败，请稍后重试"}
            return {"parse": 0, "jx": 0, "url": play["url"], "header": play["headers"], "format": play["format"]}
        if kind == "missav" and ref.get("slug"):
            try:
                play = self._play_missav(str(ref.get("slug")))
            except Exception:
                return {"parse": 0, "msg": "MissAV 取链失败，请稍后重试"}
            return {"parse": 0, "jx": 0, "url": play["url"], "header": play["headers"], "format": "hls"}
        if kind == "kanav" and ref.get("playPath"):
            try:
                play = self._play_kanav(ref)
            except Exception:
                return {"parse": 0, "msg": "KanAV 取链失败，请稍后重试"}
            return {"parse": 0, "jx": 0, "url": play["url"], "header": play["headers"], "format": play["format"]}
        if kind == "info":
            return {"parse": 0, "msg": str(ref.get("msg") or "说明条，无播放内容")}
        return {"parse": 0, "msg": "不支持的播放类型"}

    def _submit_magnet_or_msg(self, job):
        result = self._soft(lambda: self._submit_offline115(job))
        if isinstance(result, dict) and result.get("ok"):
            return {"parse": 0, "msg": "已提交 115 离线下载，完成后刷新详情即可播放"}
        if isinstance(result, dict) and result.get("why") == "nocookie":
            return {"parse": 0, "msg": "115 离线提交需要 115 Cookie：请先在源 ext 里填写 pan115_cookie"}
        if isinstance(result, dict) and result.get("why") == "nocache":
            return {"parse": 0, "msg": "未找到 AVDB-Streaming-Cache 目录：请在 115 里确认该目录存在，或在源 ext 填写离线目录 CID"}
        if isinstance(result, dict) and result.get("why") == "fail" and result.get("msg"):
            return {"parse": 0, "msg": "115 离线提交失败：" + str(result.get("msg"))}
        return {"parse": 0, "msg": "115 离线提交失败，请稍后重试"}

    def _p115_headers(self):
        headers = {"User-Agent": P115_UA, "Referer": "https://115.com/"}
        if self._pan115_cookie:
            headers["Cookie"] = self._pan115_cookie
        return headers

    def _p115_get(self, url):
        last_err = None
        for attempt in range(2):
            try:
                resp = requests.get(url, headers=self._p115_headers(), timeout=REQ_TIMEOUT)
                try:
                    body = resp.json()
                except Exception:
                    body = None
                if not isinstance(body, dict):
                    raise ValueError("115 回包非 JSON")
                return body
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(0.5)
        raise last_err

    def _list115(self, cid, limit):
        url = "https://webapi.115.com/files?aid=1&cid=" + quote(str(cid), safe="") + "&o=user_ptime&asc=0&offset=0&limit=" + str(limit or 60) + "&show_dir=1&format=json"
        body = self._p115_get(url)
        if not body.get("state") or not isinstance(body.get("data"), list):
            raise ValueError("115 目录读取失败")
        return body["data"]

    def _search115(self, kw, cid, limit):
        url = "https://webapi.115.com/files/search?search_value=" + quote(str(kw), safe="") + "&cid=" + quote(str(0 if cid is None else cid), safe="") + "&offset=0&limit=" + str(limit or 100) + "&format=json&aid=1&show_dir=1&o=file_name&asc=1"
        body = self._p115_get(url)
        if not body.get("state") or not isinstance(body.get("data"), list):
            raise ValueError("115 搜索失败")
        return body["data"]

    def _find_cache_cid(self):
        if self._offline_cid:
            return self._offline_cid
        if self._cache_cid:
            return self._cache_cid
        if not self._pan115_cookie:
            return ""
        items = self._soft(lambda: self._search115(P115_CACHE_FOLDER, 0, 20))
        cid = ""
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict) and it.get("cid") and not it.get("fid") and str(it.get("n") or "") == P115_CACHE_FOLDER:
                    cid = str(it.get("cid"))
                    break
        if cid:
            self._cache_cid = cid
        return cid

    def _is_video_file(self, it):
        if not isinstance(it, dict) or not it.get("fid"):
            return False
        name = str(it.get("n") or "")
        dot = name.rfind(".")
        if dot < 0:
            return False
        return name[dot + 1:].lower() in P115_VIDEO_EXTS

    def _file_of_115(self, it):
        size = 0
        try:
            size = int(it.get("s") or 0)
        except (TypeError, ValueError):
            size = 0
        return {"fid": str(it.get("fid")), "pc": str(it.get("pc") or ""), "name": str(it.get("n") or ""), "size": size}

    def _expand115_folder(self, cid):
        items = self._soft(lambda: self._list115(cid, 80))
        if not isinstance(items, list):
            return []
        files = []
        for it in items:
            if self._is_video_file(it):
                files.append(self._file_of_115(it))
        for it in items:
            if isinstance(it, dict) and it.get("cid") and not it.get("fid"):
                sub = self._soft(lambda cid=it.get("cid"): self._list115(str(cid), 80))
                if isinstance(sub, list):
                    for s in sub:
                        if self._is_video_file(s):
                            files.append(self._file_of_115(s))
        return files

    def _rank115_files(self, files, number):
        nn = norm_num(number)
        big = [f for f in files if f.get("size", 0) >= 30 * 1048576]
        pool = big if big else files
        seen = set()
        uniq = []
        for f in pool:
            if not f.get("pc") or f.get("fid") in seen:
                continue
            seen.add(f.get("fid"))
            uniq.append(f)
        uniq.sort(key=lambda f: (0 if nn in norm_num(f.get("name") or "") else 1, -(f.get("size") or 0)))
        return uniq[:6]

    def _match115(self, number):
        if not self._pan115_cookie or not number:
            return []
        nn = norm_num(number)
        if not nn:
            return []
        cid = self._soft(lambda: self._find_cache_cid())
        if cid:
            items = self._soft(lambda: self._list115(cid, 100))
            if isinstance(items, list):
                files = []
                for it in items:
                    if not isinstance(it, dict) or nn not in norm_num(it.get("n") or ""):
                        continue
                    if it.get("fid") and self._is_video_file(it):
                        files.append(self._file_of_115(it))
                    elif it.get("cid") and not it.get("fid"):
                        files.extend(self._expand115_folder(str(it.get("cid"))))
                ranked = self._rank115_files(files, number)
                if ranked:
                    return ranked
        search_items = self._soft(lambda: self._search115(number, 0, 100))
        if not isinstance(search_items, list):
            return []
        s_files = []
        folders = 0
        for it in search_items:
            if not isinstance(it, dict) or nn not in norm_num(it.get("n") or ""):
                continue
            if it.get("fid") and self._is_video_file(it):
                s_files.append(self._file_of_115(it))
            elif it.get("cid") and not it.get("fid") and folders < 3:
                folders += 1
                s_files.extend(self._expand115_folder(str(it.get("cid"))))
        return self._rank115_files(s_files, number)

    def _submit_offline115(self, job):
        if not self._pan115_cookie:
            return {"ok": False, "why": "nocookie"}
        cid = self._find_cache_cid()
        if not cid:
            return {"ok": False, "why": "nocache"}
        body = "url=" + quote(str(job.get("magnet") or ""), safe="") + "&wp_path_id=" + quote(cid, safe="") + "&cid=" + quote(cid, safe="")
        headers = dict(self._p115_headers())
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        last_err = None
        resp = None
        for attempt in range(2):
            try:
                resp = requests.post("https://115.com/web/lixian/?ct=lixian&ac=add_task_url", data=body, headers=headers, timeout=REQ_TIMEOUT)
                break
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(0.5)
        if resp is None:
            raise last_err
        try:
            data = resp.json()
        except Exception:
            data = None
        if isinstance(data, dict) and (data.get("state") is True or data.get("status") in (1, "1", True)):
            return {"ok": True, "why": ""}
        msg = ""
        if isinstance(data, dict):
            msg = data.get("error") or data.get("message") or data.get("msg") or data.get("err_msg") or data.get("error_msg") or data.get("errmsg") or ""
        if msg:
            return {"ok": False, "why": "fail", "msg": str(msg)}
        return {"ok": False, "why": "fail", "msg": "115 未返回确认结果，请稍后到 115 离线列表确认"}

    def _downurl115(self, pc):
        encoded = p115_encrypt(json.dumps({"pickcode": pc}, ensure_ascii=False, separators=(",", ":")))
        ts = int(time.time())
        headers = dict(self._p115_headers())
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        last_err = None
        resp = None
        for attempt in range(2):
            try:
                resp = requests.post("https://proapi.115.com/app/chrome/downurl?t=" + str(ts), data="data=" + quote(encoded, safe=""), headers=headers, timeout=REQ_TIMEOUT)
                break
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(0.5)
        if resp is None:
            raise last_err
        try:
            data = resp.json()
        except Exception:
            data = None
        if not isinstance(data, dict) or data.get("state") is not True or not isinstance(data.get("data"), str):
            return None
        dec = json.loads(p115_decrypt(data["data"]))
        keys = list(dec.keys()) if isinstance(dec, dict) else []
        inner = dec[keys[0]] if keys else None
        if not isinstance(inner, dict):
            return None
        url = ""
        if isinstance(inner.get("url"), str):
            url = inner.get("url")
        elif isinstance(inner.get("url"), dict):
            url = inner["url"].get("url") or ""
        if not url:
            return None
        auth = inner.get("auth_cookie")
        if not isinstance(auth, dict) and isinstance(inner.get("url"), dict):
            auth = inner["url"].get("auth_cookie")
        headers_out = {"User-Agent": P115_UA}
        if isinstance(auth, dict) and auth.get("name") and auth.get("value"):
            headers_out["Cookie"] = str(auth.get("name")) + "=" + str(auth.get("value"))
        return {"url": url, "headers": headers_out}

    def _video115(self, pc):
        body = self._p115_get("https://webapi.115.com/files/video?pickcode=" + quote(pc, safe=""))
        if not body.get("state") or not body.get("video_url"):
            return None
        return {"url": body["video_url"]}

    def _play115(self, pc):
        direct = self._soft(lambda: self._downurl115(pc))
        if direct:
            return {"url": direct["url"], "headers": direct["headers"], "format": "file"}
        video = self._soft(lambda: self._video115(pc))
        if video:
            return {"url": video["url"], "headers": self._p115_headers(), "format": "hls"}
        raise ValueError("115 取链失败")

    def _site_get(self, url, headers=None, timeout=REQ_TIMEOUT):
        hdrs = {
            "User-Agent": UA,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if headers:
            hdrs.update(headers)
        resp = requests.get(url, headers=hdrs, timeout=timeout)
        text = ""
        try:
            text = resp.text
        except Exception:
            text = ""
        return {"status": int(resp.status_code), "text": text, "finalUrl": resp.url or url}

    def _getav_tiers(self, data):
        all_items = []
        for vs in data.get("videoSources") or []:
            if not isinstance(vs, dict):
                continue
            u = self._getav_abs_stream(vs.get("url"))
            if not u:
                continue
            all_items.append({
                "rank": self._getav_q_rank(vs.get("type")),
                "ver": self._getav_ver(vs.get("type")),
                "pri": int(vs.get("priority") or 0),
                "url": u,
            })
        if data.get("localM3u8Path4k"):
            all_items.append({"rank": 2160, "ver": "", "pri": -1, "url": self._getav_abs_stream(data.get("localM3u8Path4k"))})
        if data.get("localM3u8Path"):
            all_items.append({"rank": 1080, "ver": "", "pri": -1, "url": self._getav_abs_stream(data.get("localM3u8Path"))})
        if data.get("localM3u8PathUc"):
            all_items.append({"rank": 720, "ver": "流出", "pri": -1, "url": self._getav_abs_stream(data.get("localM3u8PathUc"))})
        by_key = {}
        for c in all_items:
            if not c.get("url"):
                continue
            key = "%s|%s" % (c["rank"], c["ver"])
            if key not in by_key or by_key[key]["pri"] < c["pri"]:
                by_key[key] = c
        tiers = list(by_key.values())
        tiers.sort(key=lambda c: (-c["rank"], -c["pri"]))
        for t in tiers:
            t["label"] = self._getav_label(t["rank"], t["ver"])
        return tiers

    def _getav_abs_stream(self, u):
        u = str(u or "").strip()
        if not u:
            return ""
        if u.startswith("//"):
            return "https:" + u
        if u.startswith("/"):
            return "https://static.worldstatic.com" + u
        return u

    def _getav_q_rank(self, s):
        v = str(s or "").lower()
        if "4k" in v or "2160" in v:
            return 2160
        found = re.search(r"(\d{3,4})p", v)
        if found:
            return int(found.group(1))
        return 0

    def _getav_ver(self, s):
        v = str(s or "").lower()
        if re.search(r"(^|_)cn(_|$)", v) or "cnsub" in v:
            return "中字"
        if re.search(r"(^|_)uc(_|$)", v) or "uncensored" in v:
            return "流出"
        return ""

    def _getav_label(self, rank, ver):
        label = "正片"
        if rank:
            label = label + " · " + ("4K" if rank >= 2160 else "%dP" % rank)
        if ver:
            label = label + " · " + ver
        return label

    def _getav_api_on(self, host, lower):
        r = self._site_get(host + "/api/movies/" + quote(lower, safe=""), {
            "Accept": "application/json",
            "Referer": host + "/zh",
        })
        if r["status"] != 200:
            return None
        try:
            body = json.loads(r["text"])
        except Exception:
            return None
        data = body.get("data") if isinstance(body, dict) else None
        if not isinstance(data, dict):
            return None
        tiers = [t for t in self._getav_tiers(data) if t.get("rank") in (1080, 720)]
        if not tiers:
            return None
        return {"host": host, "tiers": tiers}

    def _probe_getav(self, number):
        lower = str(number or "").lower()
        if not lower:
            return None
        for host in GETAV_HOSTS:
            hit = self._soft(lambda host=host: self._getav_api_on(host, lower))
            if hit:
                return hit
        return None

    def _getav_m3u8_suffix(self, u):
        u = str(u or "")
        if re.search(r"\.m3u8(?:[?#]|$)", u, re.I):
            return u
        i = len(u)
        for ch in ("?", "#"):
            pos = u.find(ch)
            if pos != -1 and pos < i:
                i = pos
        path = u[:i]
        rest = u[i:]
        if re.search(r"\.txt$", path, re.I):
            path = re.sub(r"\.txt$", ".m3u8", path, flags=re.I)
        else:
            path = path + ".m3u8"
        return path + rest

    def _play_getav(self, ref):
        url = str(ref.get("url") or "")
        if not url and ref.get("number"):
            hit = self._soft(lambda: self._probe_getav(ref.get("number")))
            if hit and hit.get("tiers"):
                url = hit["tiers"][0].get("url") or ""
        if not url:
            raise ValueError("GetAV 取链失败")
        url = self._getav_m3u8_suffix(url)
        return {"url": url, "headers": {"User-Agent": UA}}

    def _probe_123(self, number):
        lower = str(number or "").lower()
        if not lower:
            return None
        r = self._site_get(AV123_HOST + "/cn/search?keyword=" + quote(number, safe=""), {
            "Referer": AV123_HOST + "/",
        })
        if r["status"] != 200 or not r["text"]:
            return None
        needle = "/cn/v/" + lower
        at = r["text"].find(needle)
        while at != -1:
            nxt = r["text"][at + len(needle):at + len(needle) + 1]
            if nxt in ('"', "'", "?", "#"):
                return {"slug": lower}
            at = r["text"].find(needle, at + 1)
        return None

    def _probe_u9a9(self, number):
        lower = str(number or "").lower()
        if not lower:
            return None
        r = self._site_get(U9A9_HOST + "/?type=2&search=" + quote(number, safe=""), {
            "Referer": U9A9_HOST + "/",
        })
        if r["status"] != 200 or not r["text"]:
            return None
        parts = [p for p in re.split(r"[^a-z0-9]+", lower) if p]
        if not parts:
            return None
        num_pat = re.compile(r"(?<![a-z0-9])" + r"[\s\-_.]*".join(re.escape(p) for p in parts) + r"(?![0-9])")
        out = []
        seen = set()
        for chunk in r["text"].split("<tr"):
            found = re.search(r"magnet:\?xt=urn:btih:([0-9a-fA-F]{40})", chunk, re.I)
            if not found:
                continue
            key = found.group(1).lower()
            if key in seen:
                continue
            title_m = re.search(r"title=\"([^\"]+)\"", chunk)
            if not title_m:
                continue
            title = title_m.group(1).strip()
            if not num_pat.search(title.lower()):
                continue
            link_m = re.search(r"href=\"(magnet:[^\"]+)\"", chunk)
            if not link_m:
                continue
            link = link_m.group(1).replace("&amp;", "&")
            size_bytes = 0
            size_m = re.search(r"<td class=\"text-center\">(\d+(?:\.\d+)?)\s*(GB|MB|KB)</td>", chunk)
            if size_m:
                try:
                    num = float(size_m.group(1))
                except (TypeError, ValueError):
                    num = 0
                unit = size_m.group(2)
                if unit == "GB":
                    size_bytes = int(num * 1073741824)
                elif unit == "MB":
                    size_bytes = int(num * 1048576)
                else:
                    size_bytes = int(num * 1024)
            date = ""
            date_m = re.search(r"<td class=\"text-center\">(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}</td>", chunk)
            if date_m:
                date = date_m.group(1)
            seen.add(key)
            out.append({"hash": key, "magnet": link, "name": title, "size_bytes": size_bytes, "date": date})
            if len(out) >= 10:
                break
        return out

    def _play_123(self, slug):
        page_url = AV123_HOST + "/cn/v/" + slug
        res = self._site_get(page_url, {"Referer": AV123_HOST + "/cn/"})
        html = res["text"] or ""
        if not html:
            raise ValueError("123AV 详情页拉取失败")
        play_url = ""
        pj = re.search(r"x-data=\"player\(JSON\.parse\('([\s\S]*?)'\)", html)
        if pj:
            try:
                clean = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), pj.group(1))
                clean = clean.replace("\\/", "/").replace("\\'", "'")
                eps = json.loads(clean)
                if isinstance(eps, list):
                    for ep in eps:
                        if not isinstance(ep, dict):
                            continue
                        u = str(ep.get("url") or "").strip().replace("\\/", "/").replace("\\", "")
                        if u:
                            play_url = u
                            break
            except Exception:
                pass
        if not play_url:
            found = re.findall(r"[\"'](https?:\\?/\\?/[^\"']*(?:javplayer|player|embed|\.m3u8)[^\"']*)[\"']", html) or []
            for raw in found:
                u = raw.replace("\\/", "/").replace("\\", "")
                if u:
                    play_url = u
                    break
        if not play_url:
            raise ValueError("123AV 未找到播放地址")
        if re.search(r"\.(m3u8|mp4|flv|mpd)(\?|$)", play_url, re.I) or "index.png" in play_url:
            return {
                "url": play_url,
                "headers": {"User-Agent": UA, "Referer": AV123_HOST + "/cn/"},
                "format": "hls" if ".m3u8" in play_url else "auto",
            }
        inner = self._soft(lambda: self._site_get(play_url, {"Referer": page_url}))
        if inner and inner.get("text"):
            m3 = re.search(r"[\"'](https?://[^\"']+\.m3u8[^\"']*)[\"']", inner["text"], re.I)
            if m3:
                return {
                    "url": m3.group(1).replace("\\/", "/"),
                    "headers": {"User-Agent": UA, "Referer": play_url},
                    "format": "hls",
                }
            mp4s = re.findall(r"[\"'](https?://[^\"']+\.mp4[^\"']*)[\"']", inner["text"], re.I) or []
            for raw in mp4s:
                u2 = raw.replace("\\/", "/")
                if not re.search(r"sample|preview|trailer", u2, re.I):
                    return {"url": u2, "headers": {"User-Agent": UA, "Referer": play_url}, "format": "auto"}
        em = re.match(r"^(https?://[^/]+)/e/([a-zA-Z0-9_]+)", play_url, re.I)
        if em:
            q = ""
            if "?" in play_url:
                q = play_url[play_url.index("?"):] + "&"
            else:
                q = "?"
            api_res = self._soft(lambda: self._site_get(em.group(1) + "/stream" + q + "id=" + em.group(2), {"Referer": play_url}))
            data = None
            if api_res and api_res.get("text"):
                try:
                    data = json.loads(api_res["text"])
                except Exception:
                    data = None
            stream = ""
            if isinstance(data, dict) and isinstance(data.get("media"), dict):
                stream = data["media"].get("stream") or ""
            if stream:
                return {
                    "url": str(stream).replace("\\/", "/"),
                    "headers": {"User-Agent": UA, "Referer": play_url},
                    "format": "hls",
                }
        raise ValueError("123AV 取链失败")

    def _measure_123(self, slug):
        try:
            r = self._play_123(slug)
        except Exception:
            return ""
        url = r.get("url") or ""
        if not url or ".m3u8" not in url:
            return ""
        try:
            pl = self._site_get(url, r.get("headers") or {"Referer": AV123_HOST + "/cn/"}, timeout=3)
            text = pl.get("text") or ""
        except Exception:
            return ""
        heights = [int(h) for h in re.findall(r"RESOLUTION=\d+x(\d+)", text)]
        if not heights:
            return ""
        top = max(heights)
        if top >= 2160:
            return "4K"
        return "%dP" % top

    def _probe_missav(self, number):
        lower = str(number or "").lower()
        if not lower:
            return None
        r = self._site_get(MISSAV_SEARCH_HOST + "/dm247/cn/search/" + quote(number, safe=""), {
            "Referer": MISSAV_SEARCH_HOST + "/",
        })
        if r["status"] != 200 or not r["text"] or "Just a moment" in r["text"]:
            return None
        pattern = r"/(?:dm\d+/)?cn/" + re.escape(lower) + r"[\"'?#]"
        if re.search(pattern, r["text"]):
            return {"slug": lower}
        return None

    def _extract_surrit_uuid(self, html):
        src = str(html or "")
        found = re.search(r"hls\.loadSource\([\"']https?://[^/]+/([a-f0-9-]{36})/playlist\.m3u8[\"']\)", src)
        if found:
            return found.group(1)
        ub = re.search(r"urls:\s*\[\s*[\"']([^\"']+)[\"']", src)
        if ub:
            link = ub.group(1)
            if "sample" not in link and "preview" not in link:
                u = re.search(r"([a-f0-9-]{36})", link)
                if u:
                    return u.group(1)
        scripts = re.findall(r"<script[^>]*>([\s\S]*?)</script>", src, re.I)
        for sc in scripts:
            if ("surrit.com" in sc or "sixyik.com" in sc) and "sample" not in sc:
                for val in re.findall(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", sc) or []:
                    pos = sc.find(val)
                    around = sc[max(0, pos - 40):pos + 60]
                    bad = False
                    for word in ("user_uuid", "sample", "preview", "thumbnail", "recombee"):
                        if word in around:
                            bad = True
                            break
                    if not bad:
                        return val
        for found in re.finditer(r"https?://(?:surrit\.com|sixyik\.com)/([a-f0-9-]{36})/(?:playlist\.m3u8)?", src):
            pos = found.start()
            if "sample" not in src[max(0, pos - 30):pos + 60]:
                return found.group(1)
        return ""

    def _play_missav(self, slug):
        uuid = ""
        for host in MISSAV_PLAY_HOSTS:
            r = self._soft(lambda host=host: self._site_get(host + "/dm247/cn/" + slug, {"Referer": host + "/"}))
            if r and r.get("status") == 200 and len(r.get("text") or "") > 3000:
                uuid = self._extract_surrit_uuid(r["text"])
                if uuid:
                    break
        if not uuid:
            raise ValueError("MissAV 取链失败")
        return {
            "url": "https://surrit.com/" + uuid + "/playlist.m3u8",
            "headers": {"User-Agent": UA, "Referer": "https://missav.ws/", "Origin": "https://missav.ws"},
        }

    def _kanav_find_hit(self, text, number):
        src = str(text or "")
        pattern = r"<a[^>]+href=[\"'](/index\.php/vod/play/[^\"']+)[\"'][^>]*>(?:\s*<[^>]+>)*\s*" + re.escape(number) + r"(?![A-Za-z0-9-])"
        found = re.search(pattern, src, re.I)
        if not found:
            return None
        item_start = src.rfind("video-item", 0, found.start())
        win = src[item_start if item_start >= 0 else max(0, found.start() - 1600):found.start() + 200]
        badge = re.search(r"<span class=\"model-view-left\">([^<]{1,12})</span>", win)
        return {"playPath": found.group(1), "badge": badge.group(1).strip() if badge else ""}

    def _kanav_search_on(self, host, number):
        r = self._site_get(host + "/index.php/vod/search.html?wd=" + quote(number, safe=""), {
            "Referer": host + "/",
        })
        if r["status"] != 200 or not r["text"] or "Just a moment" in r["text"]:
            return None
        hit = self._kanav_find_hit(r["text"], number)
        if not hit:
            return None
        return {"host": host, "playPath": hit["playPath"], "badge": hit["badge"]}

    def _probe_kanav(self, number):
        if not number:
            return None
        for host in KANAV_HOSTS:
            hit = self._soft(lambda host=host: self._kanav_search_on(host, number))
            if hit:
                return hit
        return None

    def _play_kanav(self, ref):
        pref = []
        base_list = [str(ref.get("host") or "")] + list(KANAV_HOSTS)
        for h in base_list:
            if h and h not in pref:
                pref.append(h)
        html = ""
        for cur in pref:
            rr = self._soft(lambda cur=cur: self._site_get(cur + str(ref.get("playPath") or ""), {"Referer": cur + "/"}))
            if rr and rr.get("status") == 200 and rr.get("text"):
                html = rr["text"]
                break
        found = re.search(r"player_aaaa=(\{[\s\S]*?\})\s*</script>", html) or re.search(r"player_aaaa=(\{[\s\S]*?\});", html)
        if not found:
            raise ValueError("KanAV 播放页解析失败")
        try:
            conf = json.loads(found.group(1))
        except Exception:
            conf = None
        if not isinstance(conf, dict):
            raise ValueError("KanAV 播放页解析失败")
        url = str(conf.get("url") or "")
        if not url:
            raise ValueError("KanAV 未找到播放地址")
        try:
            enc = int(conf.get("encrypt") or 0)
            if enc == 2:
                url = unquote(str(url))
                clean = str(url).replace("-", "+").replace("_", "/").replace(" ", "")
                while len(clean) % 4:
                    clean = clean + "="
                raw = base64.b64decode(clean)
                url = unquote(raw.decode("utf-8"))
            elif enc == 1:
                url = unquote(url)
        except Exception:
            raise ValueError("KanAV 播放地址解码失败")
        if not re.match(r"^https?://", url, re.I):
            raise ValueError("KanAV 播放地址异常")
        return {
            "url": url,
            "headers": {"User-Agent": UA, "Referer": "https://kanav.ad/"},
            "format": "hls" if ".m3u8" in url else "auto",
        }

    def manualVideoCheck(self):
        return False

    def isVideoFormat(self, url):
        path = str(url or "").lower()
        return path.endswith((".m3u8", ".mpd", ".mp4", ".mkv", ".flv", ".mp3", ".m4a", ".aac"))

    def destroy(self):
        self.options = {}
        self._jd_token = ""

    def liveContent(self):
        return ""

    def action(self, action):
        return {"msg": "不支持此操作"}

    def localProxy(self, params):
        return [404, "text/plain; charset=utf-8", "Proxy not configured"]
