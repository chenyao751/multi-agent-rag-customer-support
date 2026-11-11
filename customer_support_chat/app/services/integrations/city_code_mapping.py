"""Chinese City Name to IATA Code Mapping

Maps Chinese city names to their IATA three-letter codes.
Includes major cities in China and common international destinations.
"""

# 中国主要城市 IATA 代码映射
CITY_CODE_MAP = {
    # 直辖市
    "北京": "BJS",
    "上海": "SHA",
    "天津": "TSN",
    "重庆": "CKG",

    # 省会城市
    "广州": "CAN",
    "深圳": "SZX",
    "成都": "CTU",
    "杭州": "HGH",
    "西安": "SIA",
    "南京": "NKG",
    "武汉": "WUH",
    "沈阳": "SHE",
    "长春": "CGQ",
    "哈尔滨": "HRB",
    "济南": "TNA",
    "郑州": "CGO",
    "太原": "TYN",
    "石家庄": "SJW",
    "呼和浩特": "HET",
    "长沙": "CSX",
    "南昌": "KHN",
    "合肥": "HFE",
    "福州": "FOC",
    "南宁": "NNG",
    "昆明": "KMG",
    "贵阳": "KWE",
    "兰州": "LHW",
    "西宁": "XNN",
    "银川": "INC",
    "乌鲁木齐": "URC",
    "拉萨": "LXA",
    "海口": "HAK",

    # 其他主要城市
    "厦门": "XMN",
    "青岛": "TAO",
    "大连": "DLC",
    "宁波": "NGB",
    "苏州": "SZV",
    "无锡": "WUX",
    "温州": "WNZ",
    "珠海": "ZUH",
    "三亚": "SYX",
    "桂林": "KWL",
    "丽江": "LJG",
    "张家界": "DYG",

    # 常见国际目的地（用于中转查询）
    "东京": "TYO",
    "大阪": "OSA",
    "首尔": "SEL",
    "釜山": "PUS",
    "曼谷": "BKK",
    "新加坡": "SIN",
    "吉隆坡": "KUL",
    "雅加达": "JKT",
    "马尼拉": "MNL",
    "河内": "HAN",
    "胡志明": "SGN",
    "金边": "PNH",
    "仰光": "RGN",
    "加德满都": "KTM",
    "悉尼": "SYD",
    "墨尔本": "MEL",
    "奥克兰": "AKL",
    "伦敦": "LON",
    "巴黎": "PAR",
    "法兰克福": "FRA",
    "阿姆斯特丹": "AMS",
    "罗马": "ROM",
    "马德里": "MAD",
    "莫斯科": "MOW",
    "迪拜": "DXB",
    "多哈": "DOH",
    "伊斯坦布尔": "IST",
    "纽约": "NYC",
    "洛杉矶": "LAX",
    "旧金山": "SFO",
    "芝加哥": "CHI",
    "西雅图": "SEA",
    "温哥华": "YVR",
    "多伦多": "YTO",
}

# 机场代码映射（用于用户明确指定机场时）
AIRPORT_CODE_MAP = {
    # 北京
    "首都机场": "PEK",
    "大兴机场": "PKX",
    "北京首都": "PEK",
    "北京大兴": "PKX",

    # 上海
    "浦东机场": "PVG",
    "虹桥机场": "SHA",
    "上海浦东": "PVG",
    "上海虹桥": "SHA",

    # 成都
    "双流机场": "CTU",
    "天府机场": "TFU",
    "成都双流": "CTU",
    "成都天府": "TFU",

    # 深圳
    "宝安机场": "SZX",
    "深圳宝安": "SZX",

    # 广州
    "白云机场": "CAN",
    "广州白云": "CAN",
}


def get_city_code(city_name: str) -> str:
    """Get IATA code for a Chinese city name.

    Args:
        city_name: Chinese city name

    Returns:
        IATA three-letter code, or the original name if not found
    """
    # Try exact match first
    if city_name in CITY_CODE_MAP:
        return CITY_CODE_MAP[city_name]

    # Try airport code map
    if city_name in AIRPORT_CODE_MAP:
        return AIRPORT_CODE_MAP[city_name]

    # If not found, return original (might already be IATA code)
    return city_name


def get_city_name(iata_code: str) -> str:
    """Get Chinese city name for an IATA code.

    Args:
        iata_code: IATA three-letter code

    Returns:
        Chinese city name, or the original code if not found
    """
    # Reverse lookup
    for city, code in CITY_CODE_MAP.items():
        if code == iata_code.upper():
            return city

    for airport, code in AIRPORT_CODE_MAP.items():
        if code == iata_code.upper():
            return airport

    return iata_code
