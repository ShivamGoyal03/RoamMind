"""
Utility module for mapping location aliases to their standard names.
This helps in normalizing location inputs for travel services.
"""

LOCATION_ALIASES = {
    # Indian Airports and Cities (with IATA codes)
    "aga": "agartala",
    "ixa": "agartala",
    "agartala": "agartala",
    
    "agx": "agatti",
    "agatti": "agatti",
    
    "agr": "agra",
    "taj": "agra",
    "agra": "agra",
    
    "amd": "ahmedabad",
    "ahd": "ahmedabad",
    "ahmedabad": "ahmedabad",
    
    "ajl": "aizawl",
    "aizawl": "aizawl",
    
    "atq": "amritsar",
    "golden temple": "amritsar",
    "amritsar": "amritsar",
    
    "ixu": "aurangabad",
    "aurangabad": "aurangabad",
    
    "ayj": "ayodhya",
    "ayodhya": "ayodhya",
    
    "ixb": "bagdogra",
    "bagdogra": "bagdogra",
    
    "bek": "bareilly",
    "bareilly": "bareilly",
    
    "ixg": "belagavi",
    "belgaum": "belagavi",
    "belagavi": "belagavi",
    
    "blr": "bengaluru",
    "bangalore": "bengaluru",
    "bengaluru": "bengaluru",
    "kia": "bengaluru",
    
    "bho": "bhopal",
    "bhopal": "bhopal",
    
    "bbi": "bhubaneswar",
    "bhubaneswar": "bhubaneswar",
    
    "ixc": "chandigarh",
    "chandigarh": "chandigarh",
    
    "maa": "chennai",
    "madras": "chennai",
    "chennai": "chennai",
    
    "cjb": "coimbatore",
    "coimbatore": "coimbatore",
    
    "dbr": "darbhanga",
    "darbhanga": "darbhanga",
    
    "ded": "dehradun",
    "dehradun": "dehradun",
    
    "del": "delhi",
    "new delhi": "delhi",
    "igi": "delhi",
    "delhi": "delhi",
    
    "dgh": "deoghar",
    "deoghar": "deoghar",
    
    "dhm": "dharamshala",
    "dharamshala": "dharamshala",
    
    "dib": "dibrugarh",
    "dibrugarh": "dibrugarh",
    
    "dmu": "dimapur",
    "dimapur": "dimapur",
    
    "diu": "diu",
    
    "rdp": "durgapur",
    "durgapur": "durgapur",
    
    "gay": "gaya",
    "gaya": "gaya",
    
    "goi": "goa",
    "dabolim": "goa",
    "mopa": "goa",
    "gox": "goa",
    "north goa": "goa",
    
    "gdb": "gondia",
    "gondia": "gondia",
    
    "gop": "gorakhpur",
    "gorakhpur": "gorakhpur",
    
    "gau": "guwahati",
    "guwahati": "guwahati",
    
    "gwl": "gwalior",
    "gwalior": "gwalior",
    
    "hsr": "hirasar",
    "hirasar": "hirasar",
    
    "hbx": "hubli",
    "hubli": "hubli",
    
    "hyd": "hyderabad",
    "rgi": "hyderabad",
    "rajiv gandhi": "hyderabad",
    "hyderabad": "hyderabad",
    
    "imf": "imphal",
    "imphal": "imphal",
    
    "idr": "indore",
    "indore": "indore",
    
    "hgi": "itanagar",
    "itanagar": "itanagar",
    
    "jlr": "jabalpur",
    "jabalpur": "jabalpur",
    
    "jgb": "jagdalpur",
    "jagdalpur": "jagdalpur",
    
    "jai": "jaipur",
    "jaipur": "jaipur",
    "pink city": "jaipur",
    
    "jsa": "jaisalmer",
    "jaisalmer": "jaisalmer",
    
    "ixj": "jammu",
    "jammu": "jammu",
    
    "jrg": "jharsuguda",
    "jharsuguda": "jharsuguda",
    
    "jdh": "jodhpur",
    "jodhpur": "jodhpur",
    
    "jrh": "jorhat",
    "jorhat": "jorhat",
    
    "cdp": "kadapa",
    "kadapa": "kadapa",
    
    "cnn": "kannur",
    "kannur": "kannur",
    
    "knu": "kanpur",
    "kanpur": "kanpur",
    
    "hjr": "khajuraho",
    "khajuraho": "khajuraho",
    
    "cok": "kochi",
    "cochin": "kochi",
    "kochi": "kochi",
    
    "klh": "kolhapur",
    "kolhapur": "kolhapur",
    
    "ccu": "kolkata",
    "calcutta": "kolkata",
    "kolkata": "kolkata",
    
    "ccj": "kozhikode",
    "calicut": "kozhikode",
    "kozhikode": "kozhikode",
    
    "kjb": "kurnool",
    "kurnool": "kurnool",
    
    "ixl": "leh",
    "leh": "leh",
    
    "lko": "lucknow",
    "lkw": "lucknow",
    "lucknow": "lucknow",
    
    "ixm": "madurai",
    "madurai": "madurai",
    
    "ixe": "mangaluru",
    "mangalore": "mangaluru",
    "mangaluru": "mangaluru",
    
    "bom": "mumbai",
    "bombay": "mumbai",
    "mumbai": "mumbai",
    
    "myq": "mysuru",
    "mysore": "mysuru",
    "mysuru": "mysuru",
    
    "nag": "nagpur",
    "nagpur": "nagpur",
    
    "isk": "nashik",
    "nashik": "nashik",
    
    "pgh": "pantnagar",
    "pantnagar": "pantnagar",
    
    "pat": "patna",
    "patna": "patna",
    
    "ixz": "port blair",
    "port blair": "port blair",
    
    "ixd": "prayagraj",
    "allahabad": "prayagraj",
    "prayagraj": "prayagraj",
    
    "pnq": "pune",
    "pune": "pune",
    
    "rpr": "raipur",
    "raipur": "raipur",
    
    "rja": "rajahmundry",
    "rajahmundry": "rajahmundry",
    
    "raj": "rajkot",
    "rajkot": "rajkot",
    
    "ixr": "ranchi",
    "ranchi": "ranchi",
    
    "sxv": "salem",
    "salem": "salem",
    
    "shl": "shillong",
    "shillong": "shillong",
    
    "sag": "shirdi",
    "shirdi": "shirdi",
    
    "rqy": "shivamogga",
    "shimoga": "shivamogga",
    "shivamogga": "shivamogga",
    
    "ixs": "silchar",
    "silchar": "silchar",
    
    "sxr": "srinagar",
    "srinagar": "srinagar",
    
    "stv": "surat",
    "surat": "surat",
    
    "trv": "thiruvananthapuram",
    "trivandrum": "thiruvananthapuram",
    "thiruvananthapuram": "thiruvananthapuram",
    
    "trz": "tiruchirappalli",
    "trichy": "tiruchirappalli",
    "tiruchirappalli": "tiruchirappalli",
    
    "tir": "tirupati",
    "tirupati": "tirupati",
    
    "tcr": "tuticorin",
    "tuticorin": "tuticorin",
    
    "udr": "udaipur",
    "udaipur": "udaipur",
    
    "bdq": "vadodara",
    "baroda": "vadodara",
    "vadodara": "vadodara",
    
    "vns": "varanasi",
    "benaras": "varanasi",
    "kashi": "varanasi",
    "varanasi": "varanasi",
    
    "vga": "vijayawada",
    "vijayawada": "vijayawada",
    
    "vtz": "visakhapatnam",
    "vizag": "visakhapatnam",
    "visakhapatnam": "visakhapatnam",
    
    # International Cities and Airport codes (keeping existing ones)
    "nyc": "new york",
    "new york city": "new york",
    "jfk": "new york",
    "lga": "new york",
    "ewr": "new york",
    
    "lax": "los angeles",
    "la": "los angeles",
    
    "sin": "singapore",
    "changi": "singapore",
    
    "dxb": "dubai",
    "dubai international": "dubai",
    "dwc": "dubai",
    
    "lhr": "london",
    "lon": "london",
    "gatwick": "london",
    "heathrow": "london",
    "stansted": "london",
    
    "hkg": "hong kong",
    "chek lap kok": "hong kong",
    
    "sfo": "san francisco",
    "frisco": "san francisco",
    
    # Popular Landmarks/Areas (keeping existing ones)
    "times square": "new york",
    "statue of liberty": "new york",
    "central park": "new york",
    
    "gateway of india": "mumbai",
    "marine drive": "mumbai",
    
    "india gate": "delhi",
    "red fort": "delhi",
    "qutub minar": "delhi",
    
    "victoria memorial": "kolkata",
    "howrah bridge": "kolkata",
    
    "taj mahal": "agra",
    "agra fort": "agra",
    
    "amber fort": "jaipur",
    "hawa mahal": "jaipur",
    
    "eiffel tower": "paris",
    "louvre": "paris",
    "notre dame": "paris",
    
    "burj khalifa": "dubai",
    "palm jumeirah": "dubai",
    "dubai mall": "dubai",
    
    "big ben": "london",
    "london eye": "london",
    "tower bridge": "london",
    
    "marina bay": "singapore",
    "gardens by the bay": "singapore",
    "sentosa": "singapore"
}

def get_standard_location_name(location: str) -> str:
    """
    Convert a location alias to its standard name.
    
    Args:
        location (str): The location alias or name to standardize
        
    Returns:
        str: The standardized location name, or the original if no mapping exists
    """
    if not location:
        return location
        
    # Convert to lowercase for case-insensitive matching
    normalized = location.lower().strip()
    
    # Return the mapped standard name if it exists, otherwise return the original
    return LOCATION_ALIASES.get(normalized, location)