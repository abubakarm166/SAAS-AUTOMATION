'''Import packages'''
import os
import pandas as pd
from datetime import datetime
import re
import requests
import json
import numpy as np
import pytesseract
from PIL import Image, ImageOps
import cv2
import pyautogui
from pywinauto import Application, Desktop
import ast
import copy
import math
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import HorizontalBarChart
import tkinter as tk
from tkinter import ttk
from io import BytesIO
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Image as rImage
from email.message import EmailMessage
import ssl
import smtplib
            

'''Provide either 1 for yes, or 0 for no'''
test_mode=0

'''Specify text type elements for processing'''
text_types=['text/1d-interleaved-parityfec', 'text/cache-manifest', 'text/calendar', 
            'text/cql', 'text/cql-expression', 'text/cql-identifier', 'text/css', 
            'text/csv', 'text/csv-schema', 'text/directory', 'text/dns', 'text/ecmascript', 
            'text/encaprtp', 'text/enriched', 'text/example', 'text/fhirpath', 
            'text/flexfec', 'text/fwdred', 'text/gff3', 'text/grammar-ref-list', 
            'text/hl7v2', 'text/html', 'text/javascript', 'text/jcr-cnd', 'text/markdown', 
            'text/mizar', 'text/n3', 'text/org', 'text/parameters', 'text/parityfec', 
            'text/plain', 'text/provenance-notation', 'text/prs.fallenstein.rst', 
            'text/prs.lines.tag', 'text/prs.prop.logic', 'text/prs.texi', 'text/raptorfec', 
            'text/RED', 'text/rfc822-headers', 'text/richtext', 'text/rtf', 'text/rtp-enc-aescm128', 
            'text/rtploopback', 'text/rtx', 'text/SGML', 'text/shaclc', 'text/shex', 
            'text/spdx', 'text/strings', 'text/t140', 'text/tab-separated-values', 
            'text/troff', 'text/turtle', 'text/ulpfec', 'text/uri-list', 'text/vcard', 
            'text/vnd.a', 'text/vnd.abc', 'text/vnd.ascii-art', 'text/vnd.curl', 
            'text/vnd.debian.copyright', 'text/vnd.DMClientScript', 'text/vnd.dvb.subtitle', 
            'text/vnd.esmertec.theme-descriptor', 'text/vnd.exchangeable', 'text/vnd.familysearch.gedcom', 
            'text/vnd.ficlab.flt', 'text/vnd.fly', 'text/vnd.fmi.flexstor', 'text/vnd.gml', 
            'text/vnd.graphviz', 'text/vnd.hans', 'text/vnd.hgl', 'text/vnd.in3d.3dml', 
            'text/vnd.in3d.spot', 'text/vnd.IPTC.NewsML', 'text/vnd.IPTC.NITF', 
            'text/vnd.latex-z', 'text/vnd.motorola.reflex', 'text/vnd.ms-mediapackage', 
            'text/vnd.net2phone.commcenter.command', 'text/vnd.radisys.msml-basic-layout', 
            'text/vnd.senx.warpscript', 'text/vnd.si.uricatalogue', 'text/vnd.sun.j2me.app-descriptor', 
            'text/vnd.sosi', 'text/vnd.typst', 'text/vnd.trolltech.linguist', 'text/vnd.vcf', 
            'text/vnd.wap.si', 'text/vnd.wap.sl', 'text/vnd.wap.wml', 'text/vnd.wap.wmlscript', 
            'text/vnd.zoo.kcl', 'text/vtt', 'text/wgsl', 'text/xml', 'text/xml-external-parsed-entity']

text_content_types = [
    "text/html",
    "text/plain",
    "text/css",
    "text/javascript",
    "application/javascript",
    "text/markdown",
    "text/xml",
    "application/xml",
    "application/xhtml+xml",
    "application/json",
    "application/ld+json",
    "text/csv",
    "application/pdf",
    "text/calendar",
    "application/rss+xml",
    "application/atom+xml",
    "application/yaml"
]

'------------------------------------------------------------------------------'
'''Grab active url'''
#desktop = Desktop(backend="uia")
#chrome = desktop.window(title_re=".*Chrome.*", found_index=0)
#app = Application(backend="uia").connect(handle=chrome.handle)

desktop = Desktop(backend="uia")
wins = desktop.windows(title_re=".*Chrome.*", visible_only=True)
#for w in wins:
#    print(w.window_text(), w.handle)
chrome_win = wins[0]
app = Application(backend="uia").connect(handle=chrome_win.handle)

wins[0]


#app = Application(backend='uia')
#app.connect(title_re=".*Chrome.*")
'------------------------------------------------------------------------------'
#element_name="Address and search bar"

dlg = app.top_window()

#url = dlg.child_window(title=element_name, control_type="Edit").get_value()

url = dlg.child_window(control_type="Edit", found_index=0).get_value()

print(url)

if url[:3] != "http":
    url='https://' + url

print(url)

# Send a normal browser-like request
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; DataAccess/1.0)"
}
response = requests.get(url, headers=headers)

# Normalize header and detect content type
content_type = response.headers.get("Content-Type", "").lower()

# Check if the content type might contain visible text
if any(ct in content_type for ct in text_content_types):
    # Decode safely respecting charset
    encoding = response.encoding or "utf-8"
    text_content = response.content.decode(encoding, errors="ignore")

    # Optional: collapse excessive whitespace for visibility
    visible_text = " ".join(text_content.split())

else:
    print(f"Content type '{content_type}' is not text-based.")
    
#Efficiently replace substrings for testing str.replace() vs re.compile()
'''Initiate address filtering criteria and compile regex'''

streets=['avenue', 'boulevard', 'circle', 'court', 'drive', 'expressway', 'highway', 
         'junction', 'lane', 'parkway', 'place', 'plaza', 'road', 'route', 'street', 
         'terrace', 'trail', 'avenue,', 'boulevard,', 'circle,', 'court,', 'drive,', 'expressway,', 'highway,', 
         'junction,', 'lane,', 'parkway,', 'place,', 'plaza,', 'road,', 'route,', 'street,', 
         'terrace,', 'trail,', 'walk','way', 'ave', 'blvd', 'cir', 'ct', 'dr', 'expy', 
         'hwy', 'jct', 'ln', 'pkwy', 'pl', 'plz', 'rd', 'rte', 'st', 
         'ter', 'trl', 'wk', 'terr'] 

streets = ['Alley', 'Anex', 'Arcade', 'Avenue', 'Bayou', 'Beach', 'Bend', 'Bluff', 'Bluffs', 'Bottom', 'Boulevard', 'Branch', 'Bridge', 'Brook', 'Brooks', 'Burg', 'Burgs', 'Bypass', 'Camp', 'Canyon', 'Cape', 'Causeway', 'Center', 'Centers', 'Circle', 'Circles', 'Cliff', 'Cliffs', 'Club', 'Common', 'Commons', 'Corner', 'Corners', 'Course', 'Court', 'Courts', 'Cove', 'Coves', 'Creek', 'Crescent', 'Crest', 'Crossing', 'Crossroad', 'Crossroads', 'Curve', 'Dale', 'Dam', 'Divide', 'Drive', 'Drives', 'Estate', 'Estates', 'Expressway', 'Extension', 'Extensions', 'Fall', 'Falls', 'Ferry', 'Field', 'Fields', 'Flat', 'Flats', 'Ford', 'Fords', 'Forest', 'Forge', 'Forges', 'Fork', 'Forks', 'Fort', 'Freeway', 'Garden', 'Gardens', 'Gateway', 'Glen', 'Glens', 'Green', 'Greens', 'Grove', 'Groves', 'Harbor', 'Harbors', 'Haven', 'Heights', 'Highway', 'Hill', 'Hills', 'Hollow', 'Inlet', 'Island', 'Islands', 'Isle', 'Junction', 'Junctions', 'Key', 'Keys', 'Knoll', 'Knolls', 'Lake', 'Lakes', 'Land', 'Landing', 'Lane', 'Light', 'Lights', 'Loaf', 'Lock', 'Locks', 'Lodge', 'Loop', 'Mall', 'Manor', 'Manors', 'Meadow', 'Meadows', 'Mews', 'Mill', 'Mills', 'Mission', 'Motorway', 'Mount', 'Mountain', 'Mountains', 'Neck', 'Orchard', 'Oval', 'Overpass', 'Park', 'Parks', 'Parkway', 'Parkways', 'Pass', 'Passage', 'Path', 'Pike', 'Pine', 'Pines', 'Place', 'Plain', 'Plains', 'Plaza', 'Point', 'Points', 'Port', 'Ports', 'Prairie', 'Radial', 'Ramp', 'Ranch', 'Rapid', 'Rapids', 'Rest', 'Ridge', 'Ridges', 'River', 'Road', 'Roads', 'Route', 'Row', 'Rue', 'Run', 'Shoal', 'Shoals', 'Shore', 'Shores', 'Skyway', 'Spring', 'Springs', 'Spur', 'Spurs', 'Square', 'Squares', 'Station', 'Stravenue', 'Stream', 'Street', 'Streets', 'Summit', 'Terrace', 'Terrace', 'Throughway', 'Trace', 'Track', 'Trafficway', 'Trail', 'Trailer', 'Tunnel', 'Turnpike', 'Underpass', 'Union', 'Unions', 'Valley', 'Valleys', 'Viaduct', 'View', 'Views', 'Village', 'Villages', 'Ville', 'Vista', 'Walk', 'Walk', 'Walks', 'Wall', 'Way', 'Ways', 'Well', 'Wells', 'Aly', 'Anx', 'Arc', 'Ave', 'Byu', 'Bch', 'Bnd', 'Blf', 'Blfs', 'Btm', 'Blvd', 'Br', 'Brg', 'Brk', 'Brks', 'Bg', 'Bgs', 'Byp', 'Cp', 'Cyn', 'Cpe', 'Cswy', 'Ctr', 'Ctrs', 'Cir', 'Cirs', 'Clf', 'Clfs', 'Clb', 'Cmn', 'Cmns', 'Cor', 'Cors', 'Crse', 'Ct', 'Cts', 'Cv', 'Cvs', 'Crk', 'Cres', 'Crst', 'Xing', 'Xrd', 'Xrds', 'Curv', 'Dl', 'Dm', 'Dv', 'Dr', 'Drs', 'Est', 'Ests', 'Expy', 'Ext', 'Exts', 'Fall', 'Fls', 'Fry', 'Fld', 'Flds', 'Flt', 'Flts', 'Frd', 'Frds', 'Frst', 'Frg', 'Frgs', 'Frk', 'Frks', 'Ft', 'Fwy', 'Gdn', 'Gdns', 'Gtwy', 'Gln', 'Glns', 'Grn', 'Grns', 'Grv', 'Grvs', 'Hbr', 'Hbrs', 'Hvn', 'Hts', 'Hwy', 'Hl', 'Hls', 'Holw', 'Inlt', 'Is', 'Iss', 'Isle', 'Jct', 'Jcts', 'Ky', 'Kys', 'Knl', 'Knls', 'Lk', 'Lks', 'Land', 'Lndg', 'Ln', 'Lgt', 'Lgts', 'Lf', 'Lck', 'Lcks', 'Ldg', 'Loop', 'Mall', 'Mnr', 'Mnrs', 'Mdw', 'Mdws', 'Mews', 'Ml', 'Mls', 'Msn', 'Mtwy', 'Mt', 'Mtn', 'Mtns', 'Nck', 'Orch', 'Oval', 'Opas', 'Park', 'Park', 'Pkwy', 'Pkwy', 'Pass', 'Psge', 'Path', 'Pike', 'Pne', 'Pnes', 'Pl', 'Pln', 'Plns', 'Plz', 'Pt', 'Pts', 'Prt', 'Prts', 'Pr', 'Radl', 'Ramp', 'Rnch', 'Rpd', 'Rpds', 'Rst', 'Rdg', 'Rdgs', 'Riv', 'Rd', 'Rds', 'Rte', 'Row', 'Rue', 'Run', 'Shl', 'Shls', 'Shr', 'Shrs', 'Skwy', 'Spg', 'Spgs', 'Spur', 'Spur', 'Sq', 'Sqs', 'Sta', 'Stra', 'Strm', 'St', 'Sts', 'Smt', 'Terr', 'Ter', 'Trwy', 'Trce', 'Trak', 'Trfy', 'Trl', 'Trlr', 'Tunl', 'Tpke', 'Upas', 'Un', 'Uns', 'Vly', 'Vlys', 'Via', 'Vw', 'Vws', 'Vlg', 'Vlgs', 'Vl', 'Vis', 'Wlk', 'Walk', 'Walk', 'Wall', 'Way', 'Ways', 'Wl', 'Wls']


states=['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 
        'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 
        'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 
        'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 
        'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 
        'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 
        'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 
        'Washington', 'West Virginia', 'Wisconsin', 'Wyoming', 'AL', 'AK', 
        'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 
        'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 
        'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 
        'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 
        'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

streets_pattern = '|'.join(streets)
states_pattern = '|'.join(states)

# Word pattern allowing letters and optional trailing comma or period
#word_with_punct = r'[a-zA-Z]+(?:[.,])?'

# Allow alphanumeric plus optional punctuation
word_with_punct = r'[a-zA-Z0-9]+(?:[.,])?'


# Pattern for street and town names, allowing 1 to 4 words with optional punctuation
street_name_pattern = fr'(?:\s+{word_with_punct}){{1,4}}'

# Regex pattern encapsulating address format
pattern = re.compile(
    fr'\b\d+\b'                         # House number
    fr'{street_name_pattern}'           # Street name 1-4 words
    fr'\s+(?:{streets_pattern})[.,]?'   # Street type
    fr'{street_name_pattern}'           # Town name 1-4 words
    fr'\s+(?:{states_pattern})[.,]?'    # State abbreviation
    fr'\s*\d{{5}}(?:[.,]?)',             # ZIP code with optional punctuation
    flags=re.IGNORECASE
)


'''Apply regex to text'''
def find_matches(text):
    return [m.group(0).strip() for m in pattern.finditer(text)]

translation_table = str.maketrans({'"': " ", "/": " ", "<": " ", ">": " ", "=": " "})
vt_scrub = visible_text.translate(translation_table)
vt_scrub = re.sub(r'\s+', ' ', vt_scrub)

results1 = find_matches(visible_text)
results2 = find_matches(vt_scrub)



'''Take screenshot and scan for addresses'''
'''DIRECTORY ASSIGNMENT NEEDS TO BE MODIFIED FOR PROD'''
#folder_name = "address_capture_screenshots"

cwd=os.getcwd()

# Create the folder if it does not exist
#os.makedirs(folder_name, exist_ok=True)
os.path.abspath("full_screenshot_pyautogui.png")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#pyautogui.screenshot("full_screenshot_pyautogui_" + datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".png")
pyautogui.screenshot("full_screenshot_pyautogui_.png")
#ss_path=os.path.abspath("full_screenshot_pyautogui_" + datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".png")
ss_path=os.path.abspath("full_screenshot_pyautogui_.png")

#Load the .png image
image = Image.open(ss_path)

#Convert to grayscale
gray = ImageOps.grayscale(image)

#Convert to numpy array for OpenCV preprocessing
gray_np = np.array(gray)

#Apply Gaussian Blur (optional, reduces noise)
blurred = cv2.GaussianBlur(gray_np, (3, 3), 0)

#Apply Otsu's threshold for binarization
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 11, 2)

#Remove noise (morphological operations, optional)
kernel = np.ones((1, 1), np.uint8)
denoised = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

#Convert back to PIL Image for pytesseract
processed_img = Image.fromarray(denoised)

#Extract text
custom_config = r'--oem 3 --psm 6'
extracted_text = pytesseract.image_to_string(processed_img, config=custom_config)
extracted_text
#Combine all text lines into one output string
output_string = " ".join(extracted_text.splitlines())

town_name_pattern='(?:\\s+[a-zA-Z]+(?:[.,])?){1,4}'
print(output_string)

# Regex pattern encapsulating address format
pattern_no_zip = re.compile(
    fr'\b\d+\b'                           # house number
    fr'{street_name_pattern}'             # street name words
    fr'\s+(?:{streets_pattern})[.,]?'    # street type with optional punctuation
    fr'{town_name_pattern}'               # town name words
    fr'\s+(?:{states_pattern})[.,]?'     # state abbreviation with optional punctuation
    fr'(?:\s*\d{{5}})?'                   # optional ZIP code, without trailing punctuation
    fr'\b', 
    flags=re.IGNORECASE
)

def find_matches_no_zip(text):
    return [m.group(0).strip() for m in pattern_no_zip.finditer(text)]

if test_mode == 1:
    results3 = []
elif test_mode == 0:
    results3 = find_matches_no_zip(output_string)
else:
    results3 = []

results = results1 + results2 + results3
results=[i.lower().strip() for i in results]
results=list(set(results))
#results
count=[i for i in range(len(results))]
'''---------------Set up UI here for address confirmation/modification-----------------------------------'''

root = tk.Tk()
root.title("Confirm Addresses")
root.geometry("500x400")
root.minsize(500, 400)
rows = []

outer = ttk.Frame(root)
outer.pack(fill="both", expand=True)

canvas = tk.Canvas(outer, highlightthickness=0)
scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

container = ttk.Frame(canvas, padding=10)
window_id = canvas.create_window((0, 0), window=container, anchor="nw")

def on_frame_configure(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_canvas_configure(event):
    canvas.itemconfigure(window_id, width=event.width)

container.bind("<Configure>", on_frame_configure)
canvas.bind("<Configure>", on_canvas_configure)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

def add_row(text=""):
    row = ttk.Frame(container)
    row.pack(fill="x", pady=2)

    entry = ttk.Entry(row, width=60)
    entry.insert(0, text)
    entry.pack(side="left", padx=(0, 8), fill="x", expand=True)

    var = tk.BooleanVar(value=False)
    cb = ttk.Checkbutton(row, variable=var)
    cb.pack(side="left")

    rows.append((entry, cb, var))

def remove_selected():
    global results, rows
    selected_indices = [i for i, (_, _, var) in enumerate(rows) if var.get()]
    if not selected_indices:
        return

    for idx in reversed(selected_indices):
        entry, cb, var = rows[idx]
        entry.master.destroy()
        rows.pop(idx)

    root.update_idletasks()
    on_frame_configure()

def submit():
    global results
    results = [entry.get() for entry, _, _ in rows]
    selected_items = [entry.get() for entry, _, var in rows if var.get()]
    print("All rows:", results)
    print("Selected rows:", selected_items)
    root.destroy()

for s in results:
    add_row(s)

add_row("")

button_frame = ttk.Frame(root, padding=10)
button_frame.pack(fill="x", side="bottom")

ttk.Button(button_frame, text="Add Row", command=lambda: add_row("")).pack(side="left", padx=(0, 8))
ttk.Button(button_frame, text="Remove Selected", command=remove_selected).pack(side="left")
ttk.Button(button_frame, text="Submit", command=submit).pack(side="right")

root.protocol("WM_DELETE_WINDOW", root.destroy)
root.mainloop()
root.quit()

'----------------------Inputs pop-up-------------------------------------------'
user_em=''
interest_rate = 0.06
years = 30
discount_percentage = 0.25
closing_costs_input = 0.04
money_down_input = 0.2
operating_expenses_input = 0.02
additional_annual_income_input = 0
vacancy_allowance_percent_input = 0.05

'''Re-Tool rehab_costs_est_input and refi_loan_amount_input as % of value'''
lender_ltv_input = 0.75
rehab_costs_est_input = 0.25
refi_loan_amount_input = 0.5
refi_closing_costs_est_input = 0.04
num_months_holding=3

'------------------------'

root = tk.Tk()
root.title("Edit Inputs")

def parse_number(value):
    value = value.strip()
    if value == "":
        raise ValueError("Empty input")
    return int(value) if "." not in value else float(value)

fields = [
    ("Recipient Email", user_em, str),
    ("__label__", "Loan Inputs", None),
    ("Interest Rate", interest_rate, parse_number),
    ("Loan Length - Years", years, parse_number),
    ("Discount Percentage", discount_percentage, parse_number),
    ("__label__", "Financing Inputs", None),
    ("Closing Costs %", closing_costs_input, parse_number),
    ("Money Down %", money_down_input, parse_number),
    ("Operating Expenses %", operating_expenses_input, parse_number),
    ("Additional Income", additional_annual_income_input, parse_number),
    ("__label__", "Refi Inputs", None),
    ("Vacancy Allowance %", vacancy_allowance_percent_input, parse_number),
    ("Lender LTV Ratio", lender_ltv_input, parse_number),
    ("Rehab Costs %", rehab_costs_est_input, parse_number),
    ("Refi Loan Amount %", refi_loan_amount_input, parse_number),
    ("Refi Closing Costs %", refi_closing_costs_est_input, parse_number),
    ("Months Holding Property", num_months_holding, parse_number),
]

vars_map = {}

container = ttk.Frame(root, padding=10)
container.pack(fill="both", expand=True)

row = 0
for name, value, conv in fields:
    if name == "__label__":
        ttk.Label(
            container,
            text=value,
            font=("Arial", 11, "bold"),
            anchor="center"
        ).grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 3))
    else:
        ttk.Label(container, text=name).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value=str(value))
        vars_map[name] = var
        ttk.Entry(container, textvariable=var, width=20).grid(
            row=row, column=1, sticky="ew", padx=5, pady=3
        )
    row += 1

container.columnconfigure(1, weight=1)

def submit():
    global interest_rate, years, discount_percentage, closing_costs_input, user_em
    global money_down_input, operating_expenses_input, additional_annual_income_input
    global vacancy_allowance_percent_input, lender_ltv_input, rehab_costs_est_input
    global refi_loan_amount_input, refi_closing_costs_est_input

    converters = {name: conv for name, _, conv in fields if name != "__label__"}

    try:
        user_em = converters["Recipient Email"](vars_map["Recipient Email"].get())
        interest_rate = converters["Interest Rate"](vars_map["Interest Rate"].get())
        years = converters["Loan Length - Years"](vars_map["Loan Length - Years"].get())
        discount_percentage = converters["Discount Percentage"](vars_map["Discount Percentage"].get())
        closing_costs_input = converters["Closing Costs %"](vars_map["Closing Costs %"].get())
        money_down_input = converters["Money Down %"](vars_map["Money Down %"].get())
        operating_expenses_input = converters["Operating Expenses %"](vars_map["Operating Expenses %"].get())
        additional_annual_income_input = converters["Additional Income"](vars_map["Additional Income"].get())
        vacancy_allowance_percent_input = converters["Vacancy Allowance %"](vars_map["Vacancy Allowance %"].get())
        lender_ltv_input = converters["Lender LTV Ratio"](vars_map["Lender LTV Ratio"].get())
        rehab_costs_est_input = converters["Rehab Costs %"](vars_map["Rehab Costs %"].get())
        refi_loan_amount_input = converters["Refi Loan Amount %"](vars_map["Refi Loan Amount %"].get())
        refi_closing_costs_est_input = converters["Refi Closing Costs %"](vars_map["Refi Closing Costs %"].get())
    except ValueError as e:
        print(f"Invalid input: {e}")
        return

    print(interest_rate, years, discount_percentage)
    root.destroy()

ttk.Button(container, text="Submit", command=submit).grid(
    row=row, column=0, columnspan=2, pady=(10, 0)
)

root.protocol("WM_DELETE_WINDOW", root.destroy)
root.mainloop()
root.quit()

'''---------------SCRIPT SHOULD BE SPLIT HERE WITH THE ABOVE BEING INPUT TO THE BELOW--------------------'''

'''Create Listings Table'''
listings=pd.DataFrame()
#listings['Count']=count
try:
    results.remove("")
except:
    pass

listings['Address']=results

'''Parse ZIP Codes and assign to listings'''
zip_list=[]
for i in listings['Address']:
    k=i.split(" ")
    zip_list.append(k[-1:][0])

#Zip code ID
pattern = re.compile(r'\d{5}')

zip_results = []
for i in zip_list:
    match = pattern.search(i)
    if match:
        zip_results.append(match.group())
    else:
        zip_results.append(None)

listings['Zip']=zip_results
listings=listings[listings['Address'] != "N/A_Exception"]
listings.reset_index(drop=True, inplace=True)

'''Drop any addresses containing "#" which indicates land/condo'''
listings = listings[~listings['Address'].str.contains('#')].reset_index(drop=True)

'''Supplement with Rentcast API Info'''
'''---------------------Transform Addresses into API Strings-----------------'''

'''List of Addresses'''
adl=listings["Address"]

'''split addresses into single words - Listings NOT starting with # filtered here'''
adl_sp=[]
for i in adl:
    try:
        if int(i[0]):
            #adl_sp.append(i.split(" "))
            adl_sp.append([k.replace(",", "").replace(".", "") for k in i.split(" ")])
    except:
        print(i)
        pass

'''List state abbreviations for designating last part of address'''
states = ["AL", "AK", "AZ", "AR", "AS", "CA", "CO", "CT", "DE", "DC", "FL", 
          "GA", "GU", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", 
          "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "MP", "OH", "OK", "OR", "PA", "PR", "RI", 
          "SC", "SD", "TN", "TX", "TT", "UT", "VT", "VA", "VI", "WA", "WV", 
          "WI", "WY"]

'''Generate query URLs'''
url = "https://api.rentcast.io/v1/properties?address="

'''Generate API URL strings'''
for i in range(len(adl_sp)):
    for k in range(len(adl_sp[i])):
        if adl_sp[i][k] in states and adl_sp[i][k] != adl_sp[i][-1]:
            #adl_sp[i][k] = adl_sp[i][k].replace(adl_sp[i][k], (adl_sp[i][k] + "%2C%"))
            adl_sp[i][k] = adl_sp[i][k].replace(adl_sp[i][k], (adl_sp[i][k] + "%20"))
        elif adl_sp[i][k] not in states and adl_sp[i][k] != adl_sp[i][-1]:
            adl_sp[i][k] = adl_sp[i][k].replace(adl_sp[i][k], (adl_sp[i][k] + "%20"))
        else:
            pass

urls=[]
for i in range(len(adl_sp)):
    p = ''
    for k in range(len(adl_sp[i])):
        p += adl_sp[i][k]
    urls.append(p)

full_urls=[]
for i in urls:
    full_urls.append(url + i)

#Example URL
#url = "https://api.rentcast.io/v1/properties?address=" 2507 + "%20" + Island + "%20" + View + "%20" + Rd + "%2C" + "%20" + Essex + "%20" + MD + "%2C%" + 21221

'''---------------------Request URL Strings Finished-------------------------'''



'''-------Assign URL Strings to Corresponding listings['Address'] item-------'''

'''Run and record API query results'''
#Anonymize API key later
headers = {"accept": "application/json", "X-Api-Key": os.getenv("RENTCAST_API_KEY", "3f9f929546ec49a1a0492c3e60b21c42")}

res_list=[]
err_list=[]

for i in full_urls:
    response = requests.get(i, headers=headers)
    if isinstance(json.loads(response.text), list):
        res_list.append(json.loads(response.text)[0])
    elif isinstance(json.loads(response.text), dict): #bad-request responses caught here 
        res_list.append(json.loads(response.text))
    elif isinstance(response, dict):
        res_list.append(response)
    else:
        print(i)
        res_list.append(None)
        err_list.append(i)

'''Assign list of API responses to the listings df'''
listings['API_Responses']=res_list        

'''Relevant API Fields'''
key_list= ['addressLine1', 'addressLine2', 'assessorID', 'bathrooms', 'bedrooms', 
            'city', 'county', 'features', 'features_architectureType', 'features_cooling', 
            'features_coolingType', 'features_exteriorType', 'features_fireplace', 
            'features_fireplaceType', 'features_floorCount', 'features_foundationType', 
            'features_garage', 'features_garageSpaces', 'features_garageType', 
            'features_heating', 'features_heatingType', 'features_pool', 
            'features_poolType', 'features_roofType', 'features_roomCount', 
            'features_unitCount', 'features_viewType', 'formattedAddress', 
            'history', 'history_date', 'history_event', 'history_price', 'hoa', 
            'hoa_fee', 'id', 'lastSaleDate', 'lastSalePrice', 'latitude', 'legalDescription', 
            'longitude', 'lotSize', 'owner', 'owner_mailingAddress', 
            'owner_mailingAddress_addressLine1', 'owner_mailingAddress_addressLine2', 
            'owner_mailingAddress_city', 'owner_mailingAddress_formattedAddress', 
            'owner_mailingAddress_id', 'owner_mailingAddress_state', 'owner_mailingAddress_zipCode', 
            'owner_names', 'owner_type', 'ownerOccupied', 'propertyTaxes', 'propertyTaxes_total', 
            'propertyTaxes_year', 'propertyType', 'squareFootage', 'state', 'subdivision', 
            'taxAssessments', 'taxAssessments_improvements', 'taxAssessments_land', 
            'taxAssessments_value', 'taxAssessments_year', 'yearBuilt', 'zipCode', 'zoning']



'''Create columns for calculation values'''
l_empty=[-999999 for _ in range(len(listings))]
l_empty_none=[None for _ in range(len(listings))]

'''Initialize response value columns from key_list'''
for col in key_list:
    listings[col] = l_empty_none

#Create copy to avoid defragmentation
listings=listings.copy()
    
listings['addressLine1'] = [resp.get('addressLine1', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['addressLine2'] = [resp.get('addressLine2', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['assessorID'] = [resp.get('assessorID', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['bathrooms'] = [resp.get('bathrooms', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['bedrooms'] = [resp.get('bedrooms',np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['city'] = [resp.get('city', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['county'] = [resp.get('county', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features'] = [resp.get('features', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_architectureType'] = [resp.get('features', {}).get('architectureType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_cooling'] = [resp.get('features', {}).get('cooling', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_coolingType'] = [resp.get('features', {}).get('coolingType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_exteriorType'] = [resp.get('features', {}).get('exteriorType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_fireplace'] = [resp.get('features', {}).get('fireplace', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_fireplaceType'] = [resp.get('features', {}).get('fireplaceType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_floorCount'] = [resp.get('features', {}).get('floorCount', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['features_foundationType'] = [resp.get('features', {}).get('foundationType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_garage'] = [resp.get('features', {}).get('garage', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_garageSpaces'] = [resp.get('features', {}).get('garageSpaces', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['features_garageType'] = [resp.get('features', {}).get('garageType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_heating'] = [resp.get('features', {}).get('heating', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_heatingType'] = [resp.get('features', {}).get('heatingType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_pool'] = [resp.get('features', {}).get('pool', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_poolType'] = [resp.get('features', {}).get('poolType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_roofType'] = [resp.get('features', {}).get('roofType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_roomCount'] = [resp.get('features', {}).get('roomCount', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['features_unitCount'] = [resp.get('features', {}).get('unitCount', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['features_architectureType'] = [resp.get('features', {}).get('architectureType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['features_viewType'] = [resp.get('features', {}).get('viewType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['formattedAddress'] = [resp.get('formattedAddress', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]

history=[]
history_date=[]
history_event=[]
history_price=[]

for i in range(len(listings)):
    try:
        history.append(listings['API_Responses'][i]['history'][next(reversed(listings['API_Responses'][i]['history']))]) #most recent event
    except:
        history.append(None)
    
    try:
        history_date.append(listings['API_Responses'][i]['history'][next(reversed(listings['API_Responses'][i]['history']))]['date']) #most recent event
    except:
        history_date.append(None)
    
    try:
        history_event.append(listings['API_Responses'][i]['history'][next(reversed(listings['API_Responses'][i]['history']))]['event']) #most recent event
    except:
        history_event.append(None)
    
    try:
        history_price.append(listings['API_Responses'][i]['history'][next(reversed(listings['API_Responses'][i]['history']))]['price']) #most recent event
    except:
        history_price.append(np.nan)

listings['history'] = history
listings['history_date'] = history_date
listings['history_event'] = history_event
listings['history_price'] = history_price

listings['hoa'] = [resp.get('hoa', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['hoa_fee'] = [resp.get('hoa', {}).get('fee', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['id'] = [resp.get('id', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['lastSaleDate'] = [resp.get('lastSaleDate', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['lastSalePrice'] = [resp.get('lastSalePrice', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['latitude'] = [resp.get('latitude', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['legalDescription'] = [resp.get('legalDescription', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['longitude'] = [resp.get('longitude', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['lotSize'] = [resp.get('lotSize', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['owner'] = [resp.get('owner', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress'] = [resp.get('owner', {}).get('mailingAddress', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_addressLine1'] = [resp.get('owner', {}).get('mailingAddress', {}).get('addressLine1', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_addressLine2'] = [resp.get('owner', {}).get('mailingAddress', {}).get('addressLine2', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_city'] = [resp.get('owner', {}).get('mailingAddress', {}).get('city', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_formattedAddress'] = [resp.get('owner', {}).get('mailingAddress', {}).get('formattedAddress', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_id'] = [resp.get('owner', {}).get('mailingAddress', {}).get('id', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_state'] = [resp.get('owner', {}).get('mailingAddress', {}).get('state', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['owner_mailingAddress_zipCode'] = [resp.get('owner', {}).get('mailingAddress', {}).get('zipCode', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]


owner_names=[]
for i in range(len(listings)):
    try:
        owner_names.append(", ".join(map(str, listings['API_Responses'][i]['owner']['names'])))
    except:
        owner_names.append(None)

listings['owner_names'] = owner_names

listings['owner_type'] = [resp.get('owner', {}).get('type', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['ownerOccupied'] = [resp.get('ownerOccupied', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]

propertyTaxes=[]
propertyTaxes_total=[]
propertyTaxes_year=[]

for i in range(len(listings)):
    try:
        propertyTaxes.append(listings['API_Responses'][i]['propertyTaxes'][next(reversed(listings['API_Responses'][i]['propertyTaxes']))]) #most recent event
    except:
        propertyTaxes.append(None)
    
    try:
        propertyTaxes_total.append(listings['API_Responses'][i]['propertyTaxes'][next(reversed(listings['API_Responses'][i]['propertyTaxes']))]['total']) #most recent event
    except:
        propertyTaxes_total.append(np.nan)
    
    try:
        propertyTaxes_year.append(listings['API_Responses'][i]['propertyTaxes'][next(reversed(listings['API_Responses'][i]['propertyTaxes']))]['year']) #most recent event
    except:
        propertyTaxes_year.append(None)

listings['propertyTaxes'] = propertyTaxes
listings['propertyTaxes_total'] = propertyTaxes_total
listings['propertyTaxes_year'] = propertyTaxes_year

listings['propertyType'] = [resp.get('propertyType', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['squareFootage'] = [resp.get('squareFootage', np.nan) if isinstance(resp, dict) else np.nan for resp in listings['API_Responses']]
listings['state'] = [resp.get('state', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['subdivision'] = [resp.get('subdivision', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['taxAssessments'] = [resp.get('taxAssessments', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]

taxAssessments_improvements=[]
taxAssessments_land=[]
taxAssessments_value=[]
taxAssessments_year=[]

for i in range(len(listings)):
    try:
        taxAssessments_improvements.append(listings['API_Responses'][i]['taxAssessments'][next(reversed(listings['API_Responses'][i]['taxAssessments']))]['improvements']) #most recent event
    except:
        taxAssessments_improvements.append(np.nan)
    
    try:
        taxAssessments_land.append(listings['API_Responses'][i]['taxAssessments'][next(reversed(listings['API_Responses'][i]['taxAssessments']))]['land']) #most recent event
    except:
        taxAssessments_land.append(np.nan)
    
    try:
        taxAssessments_value.append(listings['API_Responses'][i]['taxAssessments'][next(reversed(listings['API_Responses'][i]['taxAssessments']))]['value']) #most recent event
    except:
        taxAssessments_value.append(np.nan)

    try:
        taxAssessments_year.append(listings['API_Responses'][i]['taxAssessments'][next(reversed(listings['API_Responses'][i]['taxAssessments']))]['year']) #most recent event
    except:
        taxAssessments_year.append(None)

listings['taxAssessments_improvements'] = taxAssessments_improvements
listings['taxAssessments_land'] = taxAssessments_land
listings['taxAssessments_value'] = taxAssessments_value
listings['taxAssessments_year'] = taxAssessments_year


listings['yearBuilt'] = [resp.get('yearBuilt', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['zipCode'] = [resp.get('zipCode', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]
listings['zoning'] = [resp.get('zoning', None) if isinstance(resp, dict) else None for resp in listings['API_Responses']]

#Create copy to avoid defragmentation
listings=listings.copy()

'''------------listings['Address'] API responses mapped to listings----------'''
'''Generate primary and alternate API URLs for Rent and Value Comp tables'''
val_url = "https://api.rentcast.io/v1/avm/value?address="
rent_url = "https://api.rentcast.io/v1/avm/rent/long-term?address="

search_radius = 5
days_old = 90
comp_count = 5

pt_input=[]
for i in range(len(listings)):
    try:
        pt_input.append(str(listings['propertyType'][i].replace(" ", "%20")))
    except:
        pt_input.append('nan')
        
val_alt_url=[]
rent_alt_url=[]

for i in range(len(listings)):
    g=listings['Address'][i].replace(" ", "%20").replace(",", "")
    p= g + '&propertyType=' + pt_input[i] + '&bedrooms=' + str(listings['bedrooms'][i]) + '&bathrooms=' + str(listings['bathrooms'][i]) + '&squareFootage=' + str(listings['squareFootage'][i]) + '&maxRadius=' + str(search_radius) + '&daysOld=' + str(days_old) + '&compCount=' + str(comp_count)
    val_alt_url.append(val_url + p)
    rent_alt_url.append(rent_url + p)

val_url_full=[]
rent_url_full=[]
for i in range(len(listings)):
    g = listings['Address'][i].replace(" ", "%20").replace(",", "")
    p = g + '&propertyType=' + pt_input[i] + '&bedrooms=' + str(listings['bedrooms'][i]) + '&bathrooms=' + str(listings['bathrooms'][i]) + '&squareFootage=' + str(listings['squareFootage'][i]) + '&maxRadius=' + str(search_radius) + '&daysOld=' + str(days_old) + '&compCount=' + str(comp_count) 
    val_url_full.append(val_url + p)
    rent_url_full.append(rent_url + p)


'''Run Value and Rent Comp API calls and record to list'''
val_res_list=[]
val_err_list=[]
for i in range(len(val_url_full)):
    response = requests.get(val_url_full[i], headers=headers)
    if isinstance(json.loads(response.text), list) and response.status_code == 200:
        #response = requests.get(val_url_full[i], headers=headers)
        val_res_list.append(json.loads(response.text)[0])
    elif isinstance(json.loads(response.text), dict) and response.status_code == 200:
        #response = requests.get(val_url_full[i], headers=headers)
        val_res_list.append(json.loads(response.text))
    elif isinstance(json.loads(response.text), list) and response.status_code != 200:
        response_alt = requests.get(val_alt_url[i], headers=headers)
        val_res_list.append(json.loads(response_alt.text)[0])
    elif isinstance(json.loads(response.text), dict) and response.status_code != 200:
        response_alt = requests.get(val_alt_url[i], headers=headers)
        val_res_list.append(json.loads(response_alt.text))
    else:
        print(i)
        val_res_list.append(None)
        val_err_list.append(i)

rent_res_list=[]
rent_err_list=[]

for i in range(len(rent_url_full)):
    response = requests.get(rent_url_full[i], headers=headers)
    if isinstance(json.loads(response.text), list):
        #response = requests.get(rent_url_full[i], headers=headers)
        rent_res_list.append(json.loads(response.text)[0])
    elif isinstance(json.loads(response.text), dict):
        #response = requests.get(rent_url_full[i], headers=headers)
        rent_res_list.append(json.loads(response.text))
    elif isinstance(json.loads(response.text), list) and response.status_code != 200:
        response_alt = requests.get(rent_alt_url[i], headers=headers)
        rent_res_list.append(json.loads(response_alt.text)[0])
    elif isinstance(json.loads(response.text), dict) and response.status_code != 200:
        response_alt = requests.get(rent_alt_url[i], headers=headers)
        rent_res_list.append(json.loads(response_alt.text))
    else:
        print(i)
        rent_res_list.append(None)
        rent_err_list.append(i)

listings['Value_API_Responses'] = val_res_list
listings['Rent_API_Responses'] = rent_res_list

'''Get list of all keys from listings API responses'''
def get_nested_keys(d, parent_key=''):
    keys = []
    for k, v in d.items():
        full_key = f"{parent_key}_{k}" if parent_key else k
        if isinstance(v, dict):
            keys.extend(get_nested_keys(v, full_key))
        else:
            keys.append(full_key)
    return keys

val_keys=[]
rent_keys=[]
for i in range(len(listings)):
    val_keys.append(get_nested_keys(listings['Value_API_Responses'][i]))
    rent_keys.append(get_nested_keys(listings['Rent_API_Responses'][i]))


#'''Get Reference list of all unique keys in listings API responses'''
#v_aku=[]
#r_aku=[]

#for i in val_keys:
#    for p in range(len(list(set(i)))):
#        v_aku.append(list(set(i))[p])

#for i in rent_keys:
#    for p in range(len(list(set(i)))):
#        r_aku.append(list(set(i))[p])
        
#v_aku=list(set(v_aku))    
#r_aku=list(set(r_aku))   

val_rent_key_list=['price', 'priceRangeLow','priceRangeHigh', 'rent', 'rentRangeLow', 'rentRangeHigh']

'''Initialize response value columns from key_list'''
for col in val_rent_key_list:
    listings[col] = l_empty

'''Assign Value and Rent API Response Values'''
listings['price'] = [resp.get('price', None) if isinstance(resp, dict) else np.nan for resp in listings['Value_API_Responses']]
listings['priceRangeLow'] = [resp.get('priceRangeLow', None) if isinstance(resp, dict) else np.nan for resp in listings['Value_API_Responses']]
listings['priceRangeHigh'] = [resp.get('priceRangeHigh', None) if isinstance(resp, dict) else np.nan for resp in listings['Value_API_Responses']]
    
listings['rent'] = [resp.get('rent', None) if isinstance(resp, dict) else np.nan for resp in listings['Rent_API_Responses']]
listings['rentRangeLow'] = [resp.get('rentRangeLow', None) if isinstance(resp, dict) else np.nan for resp in listings['Rent_API_Responses']]
listings['rentRangeHigh'] = [resp.get('rentRangeHigh', None) if isinstance(resp, dict) else np.nan for resp in listings['Rent_API_Responses']]
    
#Create copy to avoid defragmentation
listings=listings.copy()

'''Get Current Mortgage Rates'''
mort_url = 'https://api.api-ninjas.com/v1/mortgagerate'
mort_resp = requests.get(mort_url, headers={"X-Api-Key": os.getenv("API_NINJAS_API_KEY", "TSAvRrTlv64VZgLilis3mw==ABBtOu8cv86Qfszh")})

if mort_resp.status_code == requests.codes.ok:
    print(mort_resp.text)
    mort_dict=json.loads(mort_resp.text)[0]
    yr_30=float(json.loads(mort_resp.text)[0]['data']['frm_30']) *.01
    yr_15=float(json.loads(mort_resp.text)[0]['data']['frm_15']) *.01
    week=datetime.strptime(json.loads(mort_resp.text)[0]['data']['week'], "%Y-%m-%d")
else:
    print("Error:", response.status_code, response.text)

'''-----------------------User Inputs Begin Here----------------------------'''

'''User inputs known before purchase'''
num_periods_months = years * 12
original_loan_length_months = num_periods_months
periodic_interest_rate=interest_rate/12
dp_table=str(int(discount_percentage * 100)) + "%"

'''Create formulas'''
def all_in_costs(purchase_price, rehab_costs_est, closing_costs, num_months_holding, outstanding_principal_balance, original_loan_length_months):
#def all_in_costs(after_repair_value, lender_ltv):
    #purchase_price + rehab costs + holding costs + financing costs
    #k=after_repair_value*lender_ltv
    k=round(purchase_price + rehab_costs_est + closing_costs + (num_months_holding * (outstanding_principal_balance / original_loan_length_months)), 0)
    return k

def cap_rate(net_operating_income_, property_value):
    k=net_operating_income(gross_operating_income, operating_expenses)/property_value
    return round(k, 4)

def total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate):
    #k=monthly_loan_payment(outstanding_principal_balance, interest_rate)*original_loan_length_months
    if periodic_interest_rate == 0:
        k= (outstanding_principal_balance / original_loan_length_months) * original_loan_length_months
    else:
        k=(outstanding_principal_balance*periodic_interest_rate) / (1 - (1 + periodic_interest_rate) ** -original_loan_length_months) * original_loan_length_months
    return round(k, 2)

'''Debt service includes principal and interest'''
def debt_service_annual(total_loan_payment_, num_periods_months):
    k=(total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate)/num_periods_months) * 12
    return round(k, 2)

def debt_coverage_ratio(net_operating_income_, debt_service_annual_):
    k=net_operating_income(gross_operating_income, operating_expenses)/debt_service_annual(total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate), num_periods_months)
    return round(k, 3)

def debt_service_monthly(total_loan_payment_, num_periods_months):
    k=(total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate)/num_periods_months)
    return round(k, 2)

def equity_cap_rate(net_operating_income_, money_down):
    k=net_operating_income(gross_operating_income, operating_expenses)/money_down
    return round(k, 4)

def gross_rent_multiplier(property_value, gross_scheduled_income_):
    k=property_value/(gross_scheduled_income(potential_rent_generated, additional_annual_income) * 12)
    return round(k, 3)

#def gross_rent_multiplier(property_value, gross_scheduled_income_):
#    k=property_value/gross_scheduled_income(potential_rent_generated, additional_annual_income)
#    return round(k, 3)

def gross_scheduled_income(potential_rent_generated, additional_annual_income):
    #k=gross_operating_income+(potential_rent_generated-gross_operating_income)+additional_annual_income
    k=potential_rent_generated + additional_annual_income
    return round(k, 2)

def income_per_sq_ft(net_operating_income_, square_footage):
    k=net_operating_income(gross_operating_income, operating_expenses)/square_footage
    return round(k, 2)

def income_per_unit(net_operating_income_, unit_count):
    k=net_operating_income(gross_operating_income, operating_expenses)/unit_count
    return round(k, 2)


#BRRRR
def max_purchase_price(all_in_costs_, refi_closing_costs_est, closing_costs, rehab_costs_est):
    #k=all_in_costs(after_repair_value, lender_ltv)-refi_closing_costs_est-rehab_costs_est-closing_costs
    k=all_in_costs(purchase_price, rehab_costs_est, closing_costs, num_months_holding, outstanding_principal_balance, original_loan_length_months) - refi_closing_costs_est - rehab_costs_est-closing_costs
    return round(k, 2)

def net_income_multiplier(cap_rate_):
    k=1/cap_rate(net_operating_income(gross_operating_income, operating_expenses), property_value)
    return round(k, 4)

def net_operating_income(gross_operating_income, operating_expenses):
    k=gross_operating_income-operating_expenses
    return round(k, 2)

def operating_expense_ratio(operating_expenses, gross_operating_income):
    k=operating_expenses/gross_operating_income
    return round(k, 4)

def price_per_sq_ft(purchase_price, square_footage):
    k=purchase_price/square_footage
    return round(k, 2)

def price_per_unit(purchase_price, unit_count):
    k=purchase_price/unit_count
    return round(k, 2)

def vacancy_allowance(gross_scheduled_income_, vacancy_allowance_percent):
    k=gross_scheduled_income(potential_rent_generated, additional_annual_income) * vacancy_allowance_percent
    return round(k, 2)

def value(net_operating_income_, cap_rate_):
    k=net_operating_income(gross_operating_income, operating_expenses)/cap_rate(net_operating_income(gross_operating_income, operating_expenses), property_value)
    return round(k, 2)

'''Create calculation columns'''
col_list=['all_in_costs', 'cap_rate', 'total_loan_payment', 
            'debt_service_annual', 'debt_coverage_ratio', 
            'debt_service_monthly', 'equity_cap_rate', 
           'gross_rent_multiplier', 'gross_scheduled_income', 
           'income_per_sq_ft', 'income_per_unit', 'max_purchase_price', 
           'net_income_multiplier', 'net_operating_income', 
           'operating_expense_ratio', 'price_per_sq_ft', 
           'price_per_unit', 'vacancy_allowance', 'value', 
           'purchase_price']

for i in col_list:
    listings[i] = l_empty

#Create copy to avoid defragmentation
listings=listings.copy()

'''Ensure proper null value assignment'''
for i in range(len(listings)):    
    if pd.isna(listings['squareFootage'][i]) == True:
        listings.loc[i, 'squareFootage'] = np.nan
    elif np.isnan(listings['squareFootage'][i]) == True:
        listings.loc[i, 'squareFootage'] = np.nan

for i in range(len(listings)):    
    if pd.isna(listings['features_unitCount'][i]) == True:
        listings.loc[i, 'features_unitCount'] = 1
    elif np.isnan(listings['features_unitCount'][i]) == True:
        listings.loc[i, 'features_unitCount'] = 1

for i in range(len(listings)):    
    if pd.isna(listings['price'][i]) == True:
        listings['price'][i] = np.nan
    elif np.isnan(listings['price'][i]) == True:
        listings['price'][i] = np.nan
    else:
        pass

for i in range(len(listings)):    
    if pd.isna(listings['rent'][i]) == True:
        listings['rent'][i] = np.nan
    elif np.isnan(listings['rent'][i]) == True:
        listings['rent'][i] = np.nan
    else:
        pass

'''Perform calculations and append to listings'''
square_footage = listings['squareFootage']
unit_count = listings['features_unitCount']
property_value = listings['price']
potential_rent_generated = listings['rent']

'-----------------------------------------------------------------'

purchase_price = listings['price'] - (listings['price'] * discount_percentage)
closing_costs = closing_costs_input * purchase_price #user input, default should be 4% of purchase_price
money_down = money_down_input * purchase_price #user input 
cash_invested = closing_costs + money_down
operating_expenses = operating_expenses_input * purchase_price #user input, use 2% as default
additional_annual_income = additional_annual_income_input #user input for things like parking, laundry, storage, interest, etc.
vacancy_allowance_percent = vacancy_allowance_percent_input #user input
gross_operating_income = ((listings['rent'] - (listings['rent'] * vacancy_allowance_percent)) * 12) + additional_annual_income
after_repair_value = listings['price']

lender_ltv = lender_ltv_input #user input, 0.75 default value
rehab_costs_est = rehab_costs_est_input * listings['price'] #user input
outstanding_principal_balance=purchase_price - money_down
'''periodic_interest_rate=interest_rate/12'''
refi_loan_amount = refi_loan_amount_input * listings['price']#user input
refi_closing_costs_est = refi_loan_amount * refi_closing_costs_est_input #user input, use 4% as default


listings['refi_loan_amount'] = refi_loan_amount
listings['refi_closing_costs'] = refi_closing_costs_est


#listings['all_in_costs'] = all_in_costs(after_repair_value, lender_ltv)
listings['all_in_costs'] = all_in_costs(purchase_price, rehab_costs_est, closing_costs, num_months_holding, outstanding_principal_balance, original_loan_length_months)
listings['cap_rate'] = cap_rate(net_operating_income(gross_operating_income, operating_expenses), property_value)
listings['total_loan_payment'] = total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate)
listings['debt_service_annual'] = debt_service_annual(total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate), num_periods_months)
listings['debt_coverage_ratio'] = debt_coverage_ratio(net_operating_income(gross_operating_income, operating_expenses), debt_service_annual(total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate), num_periods_months))
listings['debt_service_monthly'] = debt_service_monthly(total_loan_payment(outstanding_principal_balance, original_loan_length_months, periodic_interest_rate), num_periods_months)
listings['equity_cap_rate'] = equity_cap_rate(net_operating_income(gross_operating_income, operating_expenses), money_down)
listings['gross_rent_multiplier'] = gross_rent_multiplier(property_value, gross_scheduled_income(potential_rent_generated, additional_annual_income))
listings['gross_scheduled_income'] = gross_scheduled_income(potential_rent_generated, additional_annual_income)
listings['income_per_sq_ft'] = income_per_sq_ft(net_operating_income(gross_operating_income, operating_expenses), square_footage)
listings['income_per_unit'] = income_per_unit(net_operating_income(gross_operating_income, operating_expenses), unit_count)

try:
    if refi_loan_amount:
        #listings['max_purchase_price'] = max_purchase_price(all_in_costs(after_repair_value, lender_ltv), refi_closing_costs_est, closing_costs, rehab_costs_est)
        listings['max_purchase_price'] = max_purchase_price(all_in_costs(purchase_price, rehab_costs_est, closing_costs, num_months_holding, outstanding_principal_balance, original_loan_length_months), refi_closing_costs_est, closing_costs, rehab_costs_est)
except:
    pass

listings['net_income_multiplier'] = net_income_multiplier(cap_rate(net_operating_income(gross_operating_income, operating_expenses), property_value))
listings['net_operating_income'] = net_operating_income(gross_operating_income, operating_expenses)
listings['operating_expense_ratio'] = operating_expense_ratio(operating_expenses, gross_operating_income)
listings['price_per_sq_ft'] = price_per_sq_ft(purchase_price, square_footage)
listings['price_per_unit'] = price_per_unit(purchase_price, unit_count)
listings['vacancy_allowance'] = vacancy_allowance(gross_scheduled_income(potential_rent_generated, additional_annual_income), vacancy_allowance_percent)
listings['value'] = value(net_operating_income(gross_operating_income, operating_expenses), cap_rate(net_operating_income(gross_operating_income, operating_expenses), property_value))
listings['purchase_price'] = purchase_price
listings['money_down'] = money_down

'''Initiate modified datetime columns'''
listings['lastSaleDate_mod'] = l_empty_none
listings['lastSaleDate_Month'] = l_empty
listings['lastSaleDate_Year'] = l_empty
listings['lastSaleDate_Qtr_Yr'] = l_empty_none
listings['lastSaleDate_Qtr'] = l_empty_none


'''Calculate modified datetime column vallues and assign'''
lsd=[]
for i in range(len(listings)):
    try:
        lsd.append(datetime.strptime(str(listings['lastSaleDate'][i]), "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=0, minute=0, second=0, microsecond=0))
    except:
        lsd.append(None)

listings['lastSaleDate_mod']=lsd

lsdm=[]
lsdy=[]

for i in range(len(listings)):
    try:
        lsdm.append(listings['lastSaleDate_mod'][i].month)
    except:
        lsdm.append(np.nan)
    try:
        lsdy.append(listings['lastSaleDate_mod'][i].year)
    except:
        lsdy.append(np.nan)

listings['lastSaleDate_Month']=lsdm
listings['lastSaleDate_Year']=lsdy

lsdq=[]

for i in range(len(listings)):
    if listings['lastSaleDate_Month'][i] < 4:
        try:
            lsdq.append(str(1))
        except:
            pass
    elif listings['lastSaleDate_Month'][i] >= 4 and listings['lastSaleDate_Month'][i] < 7:
        try:
            lsdq.append(str(2))
        except:
            pass
    elif listings['lastSaleDate_Month'][i] >= 7 and listings['lastSaleDate_Month'][i] < 10:
        try:
            lsdq.append(str(3))
        except:
            pass
    elif listings['lastSaleDate_Month'][i] >= 10:
        try:
            lsdq.append(str(4))
        except:
            pass
    else:
        lsdq.append(None)
        pass            

listings['lastSaleDate_Qtr']=lsdq

lsdqr=[]

for i in range(len(listings)):
    try:
        lsdqr.append(str(listings['lastSaleDate_Qtr'][i]) + " " + str(listings['lastSaleDate_Year'][i]))
    except:
        lsdqr.append(None)
        pass

listings['lastSaleDate_Qtr_Yr']=lsdqr

#Create copy to avoid defragmentation
listings=listings.copy()

'''Bring in ZIP code level data'''

zip_url = "https://api.rentcast.io/v1/markets?zipCode=29611&dataType=All&historyRange=6"
lookback_range = 6
zip_uni=list(filter(None, list(set(listings['Zip'].tolist() + listings['zipCode'].tolist()))))
zip_urls=[]
for i in zip_uni:
    zip_urls.append("https://api.rentcast.io/v1/markets?zipCode=" + str(i) + "&dataType=All&historyRange=" + str(lookback_range))

'---------------------------------------------------------'

'''Run Zip Code API calls and record to list'''
zip_res_list=[]
zip_err_list=[]
zip_resp=[]
for i in range(len(zip_urls)):
    response = requests.get(zip_urls[i], headers=headers)
    if isinstance(json.loads(response.text), list) and response.status_code == 200:
        #response = requests.get(val_url_full[i], headers=headers)
        zip_res_list.append(json.loads(response.text)[0])
        zip_resp.append(zip_uni[i])
    elif isinstance(json.loads(response.text), dict) and response.status_code == 200:
        #response = requests.get(val_url_full[i], headers=headers)
        zip_res_list.append(json.loads(response.text))
        zip_resp.append(zip_uni[i])
    else:
        zip_res_list.append(None)
        zip_resp.append(zip_uni[i])
        print(i)
        #zip_err_list.append(i)


for i in zip_res_list:
    try:
        del i['saleData']['history']
    except:
        print('No History')
        pass
        
    try:
        del i['rentalData']['history']
    except:
        print('No History')
        pass

def replace_values(obj):
    # If it's a dict, recurse on each value
    if isinstance(obj, dict):
        return {k: replace_values(v) for k, v in obj.items()}
    # If it's a list (or other iterable you care about), recurse on each element
    elif isinstance(obj, list):
        return [replace_values(v) for v in obj]
    else:
        # Replace ints/floats (but not bools) with np.nan
        if isinstance(obj, (int, float)) and not isinstance(obj, bool):
            return np.nan
        # Replace strings with "None"
        if isinstance(obj, str):
            return "None"
        # Leave everything else as-is
        return obj


max_len=[]
for i in zip_res_list:
    max_len.append(len(str(i)))

ml = max_len.index(max(max_len))
bdict=replace_values(zip_res_list[ml])

'''Drop history from saleData and rentalData.
   This will allow for a null dict template for use with zip codes lacking data.'''


'---------------------------------------------------------'

listings['Zip_Response'] = l_empty_none

sales_zip_col=['lastUpdatedDate_sales',
 'averagePrice',
 'medianPrice',
 'minPrice',
 'maxPrice',
 'averagePricePerSquareFoot',
 'medianPricePerSquareFoot',
 'minPricePerSquareFoot',
 'maxPricePerSquareFoot',
 'averageSquareFootage_sales',
 'medianSquareFootage_sales',
 'minSquareFootage_sales',
 'maxSquareFootage_sales',
 'averageDaysOnMarket_sales',
 'medianDaysOnMarket_sales',
 'minDaysOnMarket_sales',
 'maxDaysOnMarket_sales',
 'newListings_sales',
 'totalListings_sales']

rent_zip_col=['lastUpdatedDate_rent',
 'averageRent',
 'medianRent',
 'minRent',
 'maxRent',
 'averageRentPerSquareFoot',
 'medianRentPerSquareFoot',
 'minRentPerSquareFoot',
 'maxRentPerSquareFoot',
 'averageSquareFootage_rent',
 'medianSquareFootage_rent',
 'minSquareFootage_rent',
 'maxSquareFootage_rent',
 'averageDaysOnMarket_rent',
 'medianDaysOnMarket_rent',
 'minDaysOnMarket_rent',
 'maxDaysOnMarket_rent',
 'newListings_rent',
 'totalListings_rent']

for i in rent_zip_col:
    listings[i] = l_empty

for i in sales_zip_col:
    listings[i] = l_empty

#Create copy to avoid defragmentation
listings=listings.copy()

for i in range(len(listings)):
    zip_code = listings['Zip'][i]
    matched = False
    for j in range(len(zip_resp)):
        if zip_code == zip_resp[j]:
            resp = zip_res_list[j]
            if isinstance(resp, dict):
                listings.at[i, 'Zip_Response'] = resp
            else:
                listings.at[i, 'Zip_Response'] = copy.deepcopy(bdict)
            matched = True
            break
    if not matched or listings.at[i, 'Zip_Response'] is None:
        listings.at[i, 'Zip_Response'] = copy.deepcopy(bdict)

for i in range(len(listings)):
    zr = listings.at[i, 'Zip_Response']
    if zr is None or not isinstance(zr, dict):
        zr = copy.deepcopy(bdict)
    if "saleData" not in zr:
        zr['saleData'] = bdict["saleData"]
    if "rentalData" not in zr:
        zr['rentalData'] = bdict["rentalData"]
    if "id" not in zr:
        zr['id'] = bdict["id"]
    if "zipCode" not in zr:
        zr['zipCode'] = bdict["zipCode"]
    listings.at[i, 'Zip_Response'] = zr


'''Generate Key Lists for Sales and Rental Dicts'''
# Zip_Response keys: ['id', 'zipCode', 'saleData', 'rentalData']
sales_keys=[i for i in listings['Zip_Response'][0]['saleData'].keys()]
#rent_keys=[i for i in listings['Zip_Response'][0]['rentalData'].keys()]

'''Assign Zip Code Level API Response Values to listings'''
#Rent
listings['Zip_Response']
listings['lastUpdatedDate_rent'] = [z.get('rentalData', {}).get('lastUpdatedDate', np.nan) for z in listings['Zip_Response']]
listings['averageRent'] = [z.get('rentalData', {}).get('averageRent', np.nan) for z in listings['Zip_Response']]
listings['medianRent'] = [z.get('rentalData', {}).get('medianRent', np.nan) for z in listings['Zip_Response']]
listings['minRent'] = [z.get('rentalData', {}).get('minRent', np.nan) for z in listings['Zip_Response']]
listings['maxRent'] = [z.get('rentalData', {}).get('maxRent', np.nan) for z in listings['Zip_Response']]
listings['averageRentPerSquareFoot'] = [z.get('rentalData', {}).get('averageRentPerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['medianRentPerSquareFoot'] = [z.get('rentalData', {}).get('medianRentPerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['minRentPerSquareFoot'] = [z.get('rentalData', {}).get('minRentPerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['maxRentPerSquareFoot'] = [z.get('rentalData', {}).get('maxRentPerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['averageSquareFootage_rent'] = [z.get('rentalData', {}).get('averageSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['medianSquareFootage_rent'] = [z.get('rentalData', {}).get('medianSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['minSquareFootage_rent'] = [z.get('rentalData', {}).get('minSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['maxSquareFootage_rent'] = [z.get('rentalData', {}).get('maxSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['averageDaysOnMarket_rent'] = [z.get('rentalData', {}).get('averageDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['medianDaysOnMarket_rent'] = [z.get('rentalData', {}).get('medianDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['minDaysOnMarket_rent'] = [z.get('rentalData', {}).get('minDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['maxDaysOnMarket_rent'] = [z.get('rentalData', {}).get('maxDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['newListings_rent'] = [z.get('rentalData', {}).get('newListings', np.nan) for z in listings['Zip_Response']]
listings['totalListings_rent'] = [z.get('rentalData', {}).get('totalListings', np.nan) for z in listings['Zip_Response']]

#Sales
listings['lastUpdatedDate_sales'] = [z.get('saleData', {}).get('lastUpdatedDate', np.nan) for z in listings['Zip_Response']]
listings['averagePrice'] = [z.get('saleData', {}).get('averagePrice', np.nan) for z in listings['Zip_Response']]
listings['medianPrice'] = [z.get('saleData', {}).get('medianPrice', np.nan) for z in listings['Zip_Response']]
listings['minPrice'] = [z.get('saleData', {}).get('minPrice', np.nan) for z in listings['Zip_Response']]
listings['maxPrice'] = [z.get('saleData', {}).get('maxPrice', np.nan) for z in listings['Zip_Response']]
listings['averagePricePerSquareFoot'] = [z.get('saleData', {}).get('averagePricePerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['medianPricePerSquareFoot'] = [z.get('saleData', {}).get('medianPricePerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['minPricePerSquareFoot'] = [z.get('saleData', {}).get('minPricePerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['maxPricePerSquareFoot'] = [z.get('saleData', {}).get('maxPricePerSquareFoot', np.nan) for z in listings['Zip_Response']]
listings['averageSquareFootage_sales'] = [z.get('saleData', {}).get('averageSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['medianSquareFootage_sales'] = [z.get('saleData', {}).get('medianSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['minSquareFootage_sales'] = [z.get('saleData', {}).get('minSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['maxSquareFootage_sales'] = [z.get('saleData', {}).get('maxSquareFootage', np.nan) for z in listings['Zip_Response']]
listings['averageDaysOnMarket_sales'] = [z.get('saleData', {}).get('averageDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['medianDaysOnMarket_sales'] = [z.get('saleData', {}).get('medianDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['minDaysOnMarket_sales'] = [z.get('saleData', {}).get('minDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['maxDaysOnMarket_sales'] = [z.get('saleData', {}).get('maxDaysOnMarket', np.nan) for z in listings['Zip_Response']]
listings['newListings_sales'] = [z.get('saleData', {}).get('newListings', np.nan) for z in listings['Zip_Response']]
listings['totalListings_sales'] = [z.get('saleData', {}).get('totalListings', np.nan) for z in listings['Zip_Response']]

'''Get all compiled keys'''
zip_keys=[]
for i in range(len(listings)):
    zip_keys.append(get_nested_keys(listings['Zip_Response'][i]))

#'''Get Reference list of all unique keys in listings API responses'''
#z_aku=[]
#for i in zip_keys:
#    for p in range(len(list(set(i)))):
#        z_aku.append(list(set(i))[p])

#z_aku=list(set(z_aku))    
#z_aku

rd='[{"propertyType": None, "averageRent": None, "medianRent": None, "minRent": None, "maxRent": None, "averageRentPerSquareFoot": None, "medianRentPerSquareFoot": None, "minRentPerSquareFoot": None, "maxRentPerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averageRent": None, "medianRent": None, "minRent": None, "maxRent": None, "averageRentPerSquareFoot": None, "medianRentPerSquareFoot": None, "minRentPerSquareFoot": None, "maxRentPerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averageRent": None, "medianRent": None, "minRent": None, "maxRent": None, "averageRentPerSquareFoot": None, "medianRentPerSquareFoot": None, "minRentPerSquareFoot": None, "maxRentPerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averageRent": None, "medianRent": None, "minRent": None, "maxRent": None, "averageRentPerSquareFoot": None, "medianRentPerSquareFoot": None, "minRentPerSquareFoot": None, "maxRentPerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}]'
sd='[{"propertyType": None, "averagePrice": None, "medianPrice": None, "minPrice": None, "maxPrice": None, "averagePricePerSquareFoot": None, "medianPricePerSquareFoot": None, "minPricePerSquareFoot": None, "maxPricePerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averagePrice": None, "medianPrice": None, "minPrice": None, "maxPrice": None, "averagePricePerSquareFoot": None, "medianPricePerSquareFoot": None, "minPricePerSquareFoot": None, "maxPricePerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averagePrice": None, "medianPrice": None, "minPrice": None, "maxPrice": None, "averagePricePerSquareFoot": None, "medianPricePerSquareFoot": None, "minPricePerSquareFoot": None, "maxPricePerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averagePrice": None, "medianPrice": None, "minPrice": None, "maxPrice": None, "averagePricePerSquareFoot": None, "medianPricePerSquareFoot": None, "minPricePerSquareFoot": None, "maxPricePerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}, {"propertyType": None, "averagePrice": None, "medianPrice": None, "minPrice": None, "maxPrice": None, "averagePricePerSquareFoot": None, "medianPricePerSquareFoot": None, "minPricePerSquareFoot": None, "maxPricePerSquareFoot": None, "averageSquareFootage": None, "medianSquareFootage": None, "minSquareFootage": None, "maxSquareFootage": None, "averageDaysOnMarket": None, "medianDaysOnMarket": None, "minDaysOnMarket": None, "maxDaysOnMarket": None, "newListings": None, "totalListings": None}]'

rd_r = ast.literal_eval(rd)
sd_r = ast.literal_eval(sd)


'''Zip_Response'''
'''Get the condensed dicts for propertyType/bedrooms/rent/sales splits'''
rent_bedroom_dict=[]
for j in range(len(listings)):
    combined = {}
    try:
        dict_list=listings['Zip_Response'][j]['rentalData']['dataByBedrooms']
    except:
        dict_list=rd_r
        
    for i, d in enumerate(dict_list, start=1):  # n = 1..4
        for k, v in d.items():
            new_key = f"{k}_{i}"   # append "_n" where n is position in list
            combined[new_key] = v
    rent_bedroom_dict.append(combined)
listings['Zip_Response_Rental_Bedroom'] = rent_bedroom_dict


rent_property_dict=[]
for j in range(len(listings)):
    combined = {}
    try:
        dict_list=listings['Zip_Response'][j]['rentalData']['dataByPropertyType']
    except:
        dict_list=rd_r
    for i, d in enumerate(dict_list, start=1):  # n = 1..4
        for k, v in d.items():
            new_key = f"{k}_{i}"   # append "_n" where n is position in list
            combined[new_key] = v
    rent_property_dict.append(combined)
listings['Zip_Response_Rental_Property'] = rent_property_dict

sale_bedroom_dict=[]
for j in range(len(listings)):
    combined = {}
    try:
        dict_list=listings['Zip_Response'][j]['saleData']['dataByBedrooms']
    except:
        dict_list=sd_r
    for i, d in enumerate(dict_list, start=1):  # n = 1..4
        for k, v in d.items():
            new_key = f"{k}_{i}"   # append "_n" where n is position in list
            combined[new_key] = v
    sale_bedroom_dict.append(combined)
listings['Zip_Response_Sale_Bedroom'] = sale_bedroom_dict

sale_property_dict=[]
for j in range(len(listings)):
    combined = {}
    try:
        dict_list=listings['Zip_Response'][j]['saleData']['dataByPropertyType']
    except:
        dict_list=sd_r
    for i, d in enumerate(dict_list, start=1):  # n = 1..4
        for k, v in d.items():
            new_key = f"{k}_{i}"   # append "_n" where n is position in list
            combined[new_key] = v
    sale_property_dict.append(combined)
listings['Zip_Response_Sale_Property'] = sale_property_dict

'''Get correct dictionary by bedrooms and propertyType for rent and sales branches'''
#Zip_Response_Sale_Property
matched_id_keys_p_s = []
for _, row in listings.iterrows():
    d = row['Zip_Response_Sale_Property']
    target = row['propertyType']

    suffix = None
    for k, v in d.items():
        if k.startswith('propertyType_') and v == target:
            suffix = k.split('_', 1)[1]
            break

    matched_id_keys_p_s.append(f'_{suffix}' if suffix else None)

#Zip_Response_Sale_Bedroom
matched_id_keys_b_s = []
for _, row in listings.iterrows():
    d = row['Zip_Response_Sale_Bedroom']
    target = row['bedrooms']

    suffix = None
    for k, v in d.items():
        if k.startswith('bedrooms_') and v == target:
            suffix = k.split('_', 1)[1]
            break

    matched_id_keys_b_s.append(f'_{suffix}' if suffix else None)

#Zip_Response_Rental_Property
matched_id_keys_p_r = []
for _, row in listings.iterrows():
    d = row['Zip_Response_Rental_Property']
    target = row['propertyType']

    suffix = None
    for k, v in d.items():
        if k.startswith('propertyType_') and v == target:
            suffix = k.split('_', 1)[1]
            break

    matched_id_keys_p_r.append(f'_{suffix}' if suffix else None)

#Zip_Response_Rental_Bedroom
matched_id_keys_b_r = []
for _, row in listings.iterrows():
    d = row['Zip_Response_Rental_Bedroom']
    target = row['bedrooms']

    suffix = None
    for k, v in d.items():
        if k.startswith('bedrooms_') and v == target:
            suffix = k.split('_', 1)[1]
            break

    matched_id_keys_b_r.append(f'_{suffix}' if suffix else None)

'''Generate value lists'''
_1 = []
_2 = []
_3 = []
_4 = []
_5 = []
_6 = []
_7 = []
_8 = []
_9 = []
_10 = []
_11 = []
_12 = []
_13 = []
_14 = []
_15 = []
_16 = []
_17 = []
_18 = []

_19 = []
_20 = []
_21 = []
_22 = []
_23 = []
_24 = []
_25 = []
_26 = []
_27 = []
_28 = []
_29 = []
_30 = []
_31 = []
_32 = []
_33 = []
_34 = []
_35 = []
_36 = []

_37 = []
_38 = []
_39 = []
_40 = []
_41 = []
_42 = []
_43 = []
_44 = []
_45 = []
_46 = []
_47 = []
_48 = []
_49 = []
_50 = []
_51 = []
_52 = []
_53 = []
_54 = []

_55 = []
_56 = []
_57 = []
_58 = []
_59 = []
_60 = []
_61 = []
_62 = []
_63 = []
_64 = []
_65 = []
_66 = []
_67 = []
_68 = []
_69 = []
_70 = []
_71 = []
_72 = []

'''Compile all value lists'''
all_list=[_1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11, _12, _13, _14, _15, _16, 
      _17, _18, _19, _20, _21, _22, _23, _24, _25, _26, _27, _28, _29, _30, 
      _31, _32, _33, _34, _35, _36, _37, _38, _39, _40, _41, _42, _43, _44, 
      _45, _46, _47, _48, _49, _50, _51, _52, _53, _54, _55, _56, _57, _58, 
      _59, _60, _61, _62, _63, _64, _65, _66, _67, _68, _69, _70, _71, _72]

'''Create lists for iterative formula inputs'''
zip_rspb = ['Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Rental_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Sale_Property', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Rental_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom', 'Zip_Response_Sale_Bedroom']
zip_rspb_var = ['averageRent', 'medianRent', 'minRent', 'maxRent', 'averageRentPerSquareFoot', 'medianRentPerSquareFoot', 'minRentPerSquareFoot', 'maxRentPerSquareFoot', 'averageSquareFootage', 'medianSquareFootage', 'minSquareFootage', 'maxSquareFootage', 'averageDaysOnMarket', 'medianDaysOnMarket', 'minDaysOnMarket', 'maxDaysOnMarket', 'newListings', 'totalListings', 'averagePrice', 'medianPrice', 'minPrice', 'maxPrice', 'averagePricePerSquareFoot', 'medianPricePerSquareFoot', 'minPricePerSquareFoot', 'maxPricePerSquareFoot', 'averageSquareFootage', 'medianSquareFootage', 'minSquareFootage', 'maxSquareFootage', 'averageDaysOnMarket', 'medianDaysOnMarket', 'minDaysOnMarket', 'maxDaysOnMarket', 'newListings', 'totalListings', 'averageRent', 'medianRent', 'minRent', 'maxRent', 'averageRentPerSquareFoot', 'medianRentPerSquareFoot', 'minRentPerSquareFoot', 'maxRentPerSquareFoot', 'averageSquareFootage', 'medianSquareFootage', 'minSquareFootage', 'maxSquareFootage', 'averageDaysOnMarket', 'medianDaysOnMarket', 'minDaysOnMarket', 'maxDaysOnMarket', 'newListings', 'totalListings', 'averagePrice', 'medianPrice', 'minPrice', 'maxPrice', 'averagePricePerSquareFoot', 'medianPricePerSquareFoot', 'minPricePerSquareFoot', 'maxPricePerSquareFoot', 'averageSquareFootage', 'medianSquareFootage', 'minSquareFootage', 'maxSquareFootage', 'averageDaysOnMarket', 'medianDaysOnMarket', 'minDaysOnMarket', 'maxDaysOnMarket', 'newListings', 'totalListings']
zip_rspb_suf_l = [matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_r, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_p_s, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_r, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s, matched_id_keys_b_s]

'''Assign matched dict values to lists in all_lists'''
for i in range(len(all_list)):
    for j in range(len(listings)):
        try:
            all_list[i].append(listings[zip_rspb[i]][j][str(zip_rspb_var[i] + zip_rspb_suf_l[i][j])]) 
        except:
            all_list[i].append(np.nan)
            #pass


'''Assign values to listings, note that the assignments are ordered'''
#Property_Rental    
listings['averageRent_PropType'] = _1
listings['medianRent_PropType'] = _2
listings['minRent_PropType'] = _3
listings['maxRent_PropType'] = _4
listings['averageRentPerSquareFoot_PropType'] = _5
listings['medianRentPerSquareFoot_PropType'] = _6
listings['minRentPerSquareFoot_PropType'] = _7
listings['maxRentPerSquareFoot_PropType'] = _8
listings['averageSquareFootage_rent_PropType'] = _9
listings['medianSquareFootage_rent_PropType'] = _10
listings['minSquareFootage_rent_PropType'] = _11
listings['maxSquareFootage_rent_PropType'] = _12
listings['averageDaysOnMarket_rent_PropType'] = _13
listings['medianDaysOnMarket_rent_PropType'] = _14
listings['minDaysOnMarket_rent_PropType'] = _15
listings['maxDaysOnMarket_rent_PropType'] = _16
listings['newListings_rent_PropType'] = _17
listings['totalListings_rent_PropType'] = _18

#Property_Sale
listings['averagePrice_PropType'] = _19
listings['medianPrice_PropType'] = _20
listings['minPrice_PropType'] = _21
listings['maxPrice_PropType'] = _22
listings['averagePricePerSquareFoot_PropType'] = _23
listings['medianPricePerSquareFoot_PropType'] = _24
listings['minPricePerSquareFoot_PropType'] = _25
listings['maxPricePerSquareFoot_PropType'] = _26
listings['averageSquareFootage_sales_PropType'] = _27
listings['medianSquareFootage_sales_PropType'] = _28
listings['minSquareFootage_sales_PropType'] = _29
listings['maxSquareFootage_sales_PropType'] = _30
listings['averageDaysOnMarket_sales_PropType'] = _31
listings['medianDaysOnMarket_sales_PropType'] = _32
listings['minDaysOnMarket_sales_PropType'] = _33
listings['maxDaysOnMarket_sales_PropType'] = _34
listings['newListings_sales_PropType'] = _35
listings['totalListings_sales_PropType'] = _36

#Bedrooms_Rental
listings['averageRent_BedCount'] = _37
listings['medianRent_BedCount'] = _38
listings['minRent_BedCount'] = _39
listings['maxRent_BedCount'] = _40
listings['averageRentPerSquareFoot_BedCount'] = _41
listings['medianRentPerSquareFoot_BedCount'] = _42
listings['minRentPerSquareFoot_BedCount'] = _43
listings['maxRentPerSquareFoot_BedCount'] = _44
listings['averageSquareFootage_rent_BedCount'] = _45
listings['medianSquareFootage_rent_BedCount'] = _46
listings['minSquareFootage_rent_BedCount'] = _47
listings['maxSquareFootage_rent_BedCount'] = _48
listings['averageDaysOnMarket_rent_BedCount'] = _49
listings['medianDaysOnMarket_rent_BedCount'] = _50
listings['minDaysOnMarket_rent_BedCount'] = _51
listings['maxDaysOnMarket_rent_BedCount'] = _52
listings['newListings_rent_BedCount'] = _53
listings['totalListings_rent_BedCount'] = _54

#Bedrooms_Sale
listings['averagePrice_BedCount'] = _55
listings['medianPrice_BedCount'] = _56
listings['minPrice_BedCount'] = _57
listings['maxPrice_BedCount'] = _58
listings['averagePricePerSquareFoot_BedCount'] = _59
listings['medianPricePerSquareFoot_BedCount'] = _60
listings['minPricePerSquareFoot_BedCount'] = _61
listings['maxPricePerSquareFoot_BedCount'] = _62
listings['averageSquareFootage_sales_BedCount'] = _63
listings['medianSquareFootage_sales_BedCount'] = _64
listings['minSquareFootage_sales_BedCount'] = _65
listings['maxSquareFootage_sales_BedCount'] = _66
listings['averageDaysOnMarket_sales_BedCount'] = _67
listings['medianDaysOnMarket_sales_BedCount'] = _68
listings['minDaysOnMarket_sales_BedCount'] = _69
listings['maxDaysOnMarket_sales_BedCount'] = _70
listings['newListings_sales_BedCount'] = _71
listings['totalListings_sales_BedCount'] = _72

#Create copy to avoid defragmentation
listings=listings.copy()

'''Create Buy and Hold and Fix and Flip Scores'''

#Convert to baseline
purchase_price_b = listings['averagePrice'] - (listings['averagePrice'] * discount_percentage)
money_down_b = money_down_input * purchase_price_b
gross_operating_income_b = ((listings['averageRent'] - (listings['averageRent'] * vacancy_allowance_percent)) * 12) + additional_annual_income
operating_expenses_b = operating_expenses_input * purchase_price_b
equity_cap_rate_b = net_operating_income(gross_operating_income_b, operating_expenses_b)/money_down_b
net_operating_income(gross_operating_income_b, operating_expenses_b)
cap_rate_b=net_operating_income(gross_operating_income_b, operating_expenses_b)/listings['averagePrice']

potential_rent_generated_b = listings['averageRent']
property_value_b = listings['averagePrice']
gross_scheduled_income_b=listings['averageRent'] + additional_annual_income
gross_rent_multiplier_b= property_value_b/(gross_scheduled_income_b * 12)
#gross_rent_multiplier_b= property_value_b/gross_scheduled_income_b


money_down_b = money_down_input * listings['averagePrice'] #user input
outstanding_principal_balance_b=listings['averagePrice'] - money_down_b
net_operating_income_b=net_operating_income(gross_operating_income_b, operating_expenses_b)
debt_service_annual_b=(total_loan_payment(outstanding_principal_balance_b, original_loan_length_months, periodic_interest_rate)/num_periods_months) * 12
operating_expense_ratio_b=operating_expenses_b/gross_operating_income_b
debt_coverage_ratio_b=net_operating_income_b / debt_service_annual_b
vacancy_allowance_b=gross_scheduled_income_b * vacancy_allowance_percent
value_b = net_operating_income_b/cap_rate_b


listings['rentPerSquareFoot'] = [i for i in listings['rent']/listings['squareFootage']]
listings['marketCapRate'] = [i for i in (listings['averageRent'] * 12)/listings['averagePrice']]
listings['ARV_Recovery'] = [i for i in listings['averagePrice'] / listings['all_in_costs']]
listings['rentToPriceRatio'] = [ i for i in (listings['rent'] * 12)/ listings['price']]
#listings['IncomePerSquareFoot'] = [ i for i in listings['rentPerSquareFoot']/listings['medianRentPerSquareFoot_BedCount']]

listings['all_in_costs_baseline'] = listings['averagePrice'] * lender_ltv
listings['rentPerSquareFoot_baseline'] = [i for i in listings['averageRentPerSquareFoot']]
listings['ARV_Recovery_baseline'] = [i for i in listings['averagePrice'] / listings['all_in_costs_baseline']]
listings['value_baseline'] = value_b                                          
listings['rentToPriceRatio_baseline'] = [ i for i in (listings['averageRent'] * 12)/ listings['value_baseline']]
listings['income_per_sq_ft_baseline'] = [ i for i in listings['rentPerSquareFoot_baseline']/listings['averageRentPerSquareFoot']]

#listings['averagePrice']asas

listings['equity_cap_rate_baseline'] = net_operating_income(gross_operating_income_b, operating_expenses_b)/money_down_b
listings['net_operating_income_baseline'] = net_operating_income_b
listings['debt_service_annual_baseline']=debt_service_annual_b
listings['gross_rent_multiplier_baseline'] = gross_rent_multiplier_b
listings['debt_coverage_ratio_baseline'] = debt_coverage_ratio_b
listings['operating_expense_ratio_baseline'] = operating_expense_ratio_b
listings['debt_service_annual_baseline'] = debt_service_annual_b
listings['vacancy_allowance_baseline'] = vacancy_allowance_b

#BH
#Completed: cap_rate: listings['marketCapRate'], vacancy_allowance, operating_expense_ratio, 
brrr_met = ['cap_rate', 'debt_coverage_ratio', 'net_operating_income', 'operating_expense_ratio', 'vacancy_allowance']

brrr_met_norm = ['cap_rate_norm', 'debt_coverage_ratio_norm', 
                 'net_operating_income_norm', 'operating_expense_ratio_norm', 
                 'vacancy_allowance_norm']

for i in brrr_met_norm:
    listings[i] = l_empty


#Columns for Individ. Properties
listings['cap_rate_norm'] = (listings['cap_rate'] - listings['cap_rate'].min()) / (listings['cap_rate'].max() - listings['cap_rate'].min())
listings['debt_coverage_ratio_norm'] = (listings['debt_coverage_ratio'] - listings['debt_coverage_ratio'].min()) / (listings['debt_coverage_ratio'].max() - listings['debt_coverage_ratio'].min())
listings['operating_expense_ratio_norm'] = (listings['operating_expense_ratio'] - listings['operating_expense_ratio'].min()) / (listings['operating_expense_ratio'].max() - listings['operating_expense_ratio'].min())
listings['net_operating_income_norm'] = (listings['net_operating_income'] - listings['net_operating_income'].min()) / (listings['net_operating_income'].max() - listings['net_operating_income'].min())
listings['vacancy_allowance_norm'] = (listings['vacancy_allowance'] - listings['vacancy_allowance'].min()) / (listings['vacancy_allowance'].max() - listings['vacancy_allowance'].min())        
#listings[i] = (listings[i] - listings[i].min()) / (listings[i].max() - listings[i].min())

#Columns for Baseline Properties
listings['marketCapRate_norm'] = (listings['marketCapRate'] - listings['marketCapRate'].min()) / (listings['marketCapRate'].max() - listings['marketCapRate'].min())
listings['debt_coverage_ratio_baseline_norm'] = (listings['debt_coverage_ratio_baseline'] - listings['debt_coverage_ratio_baseline'].min()) / (listings['debt_coverage_ratio_baseline'].max() - listings['debt_coverage_ratio_baseline'].min())
listings['operating_expense_ratio_baseline_norm'] = (listings['operating_expense_ratio_baseline'] - listings['operating_expense_ratio_baseline'].min()) / (listings['operating_expense_ratio_baseline'].max() - listings['operating_expense_ratio_baseline'].min())
listings['net_operating_income_baseline_norm'] = (listings['net_operating_income_baseline'] - listings['net_operating_income_baseline'].min()) / (listings['net_operating_income_baseline'].max() - listings['net_operating_income_baseline'].min())
listings['vacancy_allowance_baseline_norm'] = (listings['vacancy_allowance_baseline'] - listings['vacancy_allowance_baseline'].min()) / (listings['vacancy_allowance_baseline'].max() - listings['vacancy_allowance_baseline'].min())        


# Example weights - adjust to reflect your investing preferences
w1, w2, w3, w4, w5 = 0.2, 0.2, 0.2, 0.2, 0.2

# Assume df contains normalized columns (values between 0 and 1) for the relevant metrics
bhs=[]
bhs_b=[]

for i in range(len(listings)):
    bhs.append(
    w1 * listings['cap_rate_norm'][i] +
    w2 * listings['debt_coverage_ratio_norm'][i] +
    w3 * listings['net_operating_income_norm'][i] +
    w4 * (1 - listings['operating_expense_ratio_norm'][i]) +
    w5 * (1 - listings['vacancy_allowance_norm'][i])
)
    bhs_b.append(
    w1 * listings['marketCapRate_norm'][i] +
    w2 * listings['debt_coverage_ratio_baseline_norm'][i] +
    w3 * listings['net_operating_income_baseline_norm'][i] +
    w4 * (1 - listings['operating_expense_ratio_baseline_norm'][i]) +
    w5 * (1 - listings['vacancy_allowance_baseline_norm'][i])
)

listings['buy_hold_score'] = bhs
listings['buy_hold_score_baseline'] = bhs_b
listings['BHS'] = listings['buy_hold_score'] / listings['buy_hold_score_baseline']

#FF
ff_met = ['profit_margin', 'all_in_cost_pct']
for i in ff_met:
    listings[i] = l_empty

listings['profit_margin'] = (listings['value'] - listings['all_in_costs']) / listings['value']
listings['all_in_cost_pct'] = listings['all_in_costs'] / listings['value']

listings['profit_margin_baseline']=(listings['value_baseline'] - listings['all_in_costs_baseline']) / listings['value_baseline']
listings['all_in_cost_pct_baseline'] = listings['all_in_costs_baseline'] / listings['value_baseline']
#listings['value_baseline'] = listings['medianPrice_BedCount']
listings['price_per_sq_ft_baseline'] = listings['averagePricePerSquareFoot']

listings['profit_margin_norm'] = (listings['profit_margin'] - listings['profit_margin'].min()) / (listings['profit_margin'].max() - listings['profit_margin'].min())
listings['all_in_cost_pct_norm'] = (listings['all_in_cost_pct'] - listings['all_in_cost_pct'].min()) / (listings['all_in_cost_pct'].max() - listings['all_in_cost_pct'].min())
listings['value_norm'] = (listings['value'] - listings['value'].min()) / (listings['value'].max() - listings['value'].min())
listings['price_per_sq_ft_norm'] = (listings['price_per_sq_ft'] - listings['price_per_sq_ft'].min()) / (listings['price_per_sq_ft'].max() - listings['price_per_sq_ft'].min())

listings['price_norm'] = (listings['price'] - listings['price'].min()) / (listings['price'].max() - listings['price'].min())
listings['averagePrice_norm'] = (listings['averagePrice'] - listings['averagePrice'].min()) / (listings['averagePrice'].max() - listings['averagePrice'].min())

listings['profit_margin_baseline_norm'] = (listings['profit_margin_baseline'] - listings['profit_margin_baseline'].min()) / (listings['profit_margin_baseline'].max() - listings['profit_margin'].min())
listings['all_in_cost_pct_baseline_norm'] = (listings['all_in_cost_pct_baseline'] - listings['all_in_cost_pct_baseline'].min()) / (listings['all_in_cost_pct_baseline'].max() - listings['all_in_cost_pct_baseline'].min())
listings['value_baseline_norm'] = (listings['value_baseline'] - listings['value_baseline'].min()) / (listings['value_baseline'].max() - listings['value_baseline'].min())
listings['price_per_sq_ft_baseline_norm'] = (listings['price_per_sq_ft_baseline'] - listings['price_per_sq_ft_baseline'].min()) / (listings['price_per_sq_ft_baseline'].max() - listings['price_per_sq_ft_baseline'].min())

# Example weights (total should sum to 1)
wa, wb, wc, wd = 0.44, 0.29, 0.24, 0.03

ffs=[]
ffs_b=[]
for i in range(len(listings)):
    ffs.append(
        #wa * listings['profit_margin_norm'][i] +
        wa * listings['profit_margin'][i] +
        wb * (1 - listings['all_in_cost_pct'][i]) +
        wc * listings['value_norm'][i] +
        #wd * (1 - listings['price_per_sq_ft_norm'][i])
        wd * (1 - listings['price_norm'][i])
)
    ffs_b.append(
        #wa * listings['profit_margin_baseline_norm'][i] +
        wa * listings['profit_margin_baseline'][i] +
        wb * (1 - listings['all_in_cost_pct_baseline'][i]) +
        wc * listings['value_baseline_norm'][i] +
        #wd * (1 - listings['price_per_sq_ft_baseline_norm'][i])
        wd * (1 - listings['averagePrice_norm'][i])
)

listings['fix_flip_score'] = ffs
listings['fix_flip_score_baseline'] = ffs_b
listings['FFS'] = listings['fix_flip_score'] / listings['fix_flip_score_baseline']

listings['Total_Score'] = (listings['fix_flip_score'] + listings['buy_hold_score']) / (listings['fix_flip_score_baseline'] + listings['buy_hold_score_baseline'])

'''Drop redundant columns'''
drop_cols=['features', 'owner', 'owner_mailingAddress', 'Value_API_Responses', 
           'Rent_API_Responses', 'Zip_Response', 'Zip_Response_Rental_Bedroom', 
           'Zip_Response_Rental_Property', 'Zip_Response_Sale_Bedroom', 
           'Zip_Response_Sale_Property', 'API_Responses']

try:
    listings.drop(columns=drop_cols, inplace=True) 
except:
    pass

#Create copy to avoid defragmentation
listings=listings.copy()

listings['all_in_cost_pct_diff'] = (listings['all_in_cost_pct'] / listings['all_in_cost_pct_baseline']) - 1
listings['all_in_costs_diff'] = listings['all_in_costs'] / listings['all_in_costs_baseline']
listings['cap_rate_diff'] = listings['cap_rate']/ listings['marketCapRate']
listings['debt_coverage_ratio_diff'] = listings['debt_coverage_ratio'] / listings['debt_coverage_ratio_baseline']
listings['debt_service_annual_diff'] = listings['debt_service_annual'] / listings['debt_service_annual_baseline']
listings['equity_cap_rate_diff'] = listings['equity_cap_rate'] / listings['equity_cap_rate_baseline']
listings['gross_rent_multiplier_diff'] = listings['gross_rent_multiplier'] / listings['gross_rent_multiplier_baseline'] 
listings['IncomePerSquareFoot_diff'] = listings['income_per_sq_ft'] / listings['income_per_sq_ft_baseline'] 
listings['net_operating_income_diff'] = listings['net_operating_income'] / listings['net_operating_income_baseline']
listings['operating_expense_ratio_diff'] = listings['operating_expense_ratio'] / listings['operating_expense_ratio_baseline'] 
listings['price_per_sq_ft_diff'] = listings['price_per_sq_ft'] / listings['price_per_sq_ft_baseline'] 
listings['profit_margin_diff'] = listings['profit_margin'] / listings['profit_margin_baseline'] 
listings['rentPerSquareFoot_diff'] = listings['rentPerSquareFoot'] / listings['rentPerSquareFoot_baseline'] 
listings['rentToPriceRatio_diff'] = listings['rentToPriceRatio'] / listings['rentToPriceRatio_baseline'] 
listings['vacancy_allowance_diff'] = listings['vacancy_allowance'] / listings['vacancy_allowance_baseline'] 
listings['value_diff'] = listings['value'] / listings['value_baseline']


'''Assign Initial Pool of Attributes'''
#i=0
bar_cols = [listings['value_diff'], listings['vacancy_allowance_diff'], 
            listings['rentToPriceRatio_diff'], listings['rentPerSquareFoot_diff'], 
            listings['profit_margin_diff'], listings['price_per_sq_ft_diff'], 
            listings['operating_expense_ratio_diff'], listings['net_operating_income_diff'], 
            listings['IncomePerSquareFoot_diff'], listings['gross_rent_multiplier_diff'], 
            listings['equity_cap_rate_diff'], listings['debt_service_annual_diff'], 
            listings['debt_coverage_ratio_diff'], listings['cap_rate_diff'], 
            listings['all_in_costs_diff'], listings['all_in_cost_pct_diff']]

bar_labels = ["Value Diff.", "Vacancy Allowance Diff.", "Rent/Price Ratio Diff.", 
              "Rent per Sq. Ft. Diff.", "Profit Margin Diff.", "Price per Sq. Ft.", 
              "Operating Expense Ratio Diff.", "Net Operating Income Diff.", 
              "Income per Sq. Ft. Diff.", "Gross Rent Multiplier Diff.", 
              "Equity Cap Rate Diff.", "Annual Debt Service Diff.", 
              "Debt Coverage Ratio Diff.", "Cap Rate Diff.", "All in Costs Diff.", 
              "All in Costs % Diff."]

bar_names = ["value_diff", "vacancy_allowance_diff", "rentToPriceRatio_diff", 
                  "rentPerSquareFoot_diff", "profit_margin_diff", "price_per_sq_ft_diff", 
                  "operating_expense_ratio_diff", "net_operating_income_diff", 
                  "IncomePerSquareFoot_diff", "gross_rent_multiplier_diff", 
                  "equity_cap_rate_diff", "debt_service_annual_diff", "debt_coverage_ratio_diff", 
                  "cap_rate_diff", "all_in_costs_diff", "all_in_cost_pct_diff"]

tab_cols = [listings['purchase_price'], listings['cap_rate'], listings['debt_coverage_ratio'], 
            listings['equity_cap_rate'], listings['gross_rent_multiplier'],
            listings['gross_scheduled_income'], listings['income_per_unit'], 
            listings['income_per_sq_ft'], listings['net_income_multiplier'], 
            listings['net_operating_income'], listings['operating_expense_ratio'], 
            listings['value'], listings['rentToPriceRatio'], listings['all_in_costs'], 
            listings['total_loan_payment'], listings['debt_service_annual'], 
            listings['debt_service_monthly'], listings['max_purchase_price'], 
            listings['propertyTaxes_total'], listings['propertyTaxes_year'], 
            listings['propertyType'], listings['bedrooms'], listings['bathrooms'], 
            listings['squareFootage'], listings['features_unitCount'], listings['lotSize'], 
            listings['yearBuilt'], listings['zoning'], listings['features_architectureType'], 
            listings['features_fireplace'], listings['features_garage'], listings['features_garageType'], 
            listings['features_cooling'], listings['features_coolingType'], listings['features_heating'], 
            listings['medianDaysOnMarket_rent'], listings['totalListings_rent'], listings['medianPricePerSquareFoot'], 
            listings['medianDaysOnMarket_sales'], listings['totalListings_sales'], listings['marketCapRate'], 
            listings['all_in_costs_baseline'], listings['rentPerSquareFoot_baseline'], 
            listings['rentToPriceRatio_baseline'], listings['income_per_sq_ft_baseline'], 
            listings['equity_cap_rate_baseline'], listings['gross_rent_multiplier_baseline'], 
            listings['net_operating_income_baseline'], listings['debt_service_annual_baseline'], 
            listings['debt_coverage_ratio_baseline'], listings['operating_expense_ratio_baseline'], 
            listings['vacancy_allowance_baseline'], listings['buy_hold_score_baseline'], 
            listings['profit_margin_baseline'], listings['all_in_cost_pct_baseline'], 
            listings['value_baseline'], listings['price_per_sq_ft_baseline']]

tab_labels = [f"Purchase Price at {dp_table} discount", "Cap Rate", "Debt Coverage Ratio", 
              "Equity Cap Rate", "Gross Rent Multiplier", "Gross Scheduled Income", 
              "Income Per Unit", "Income Per Sq Ft", "Net Income Multiplier", 
              "Net Operating Income", "Operating Expense Ratio", "Value", 
              "Rent to Price Ratio", "All in Costs", "Total Loan Payment", 
              "Debt Service - Annual", "Debt Service - Monthly", "Maximum Purchase Price", 
              "Property Taxes", "Property Tax Year", "Property Type", "Bedrooms", 
              "Bathrooms", "Square Footage", "Unit Count", "Lot Size", "Year Built", 
              "Zoning", "Architecture Type", "Has Fireplace", "Has Garage", "Garage Type", 
              "Has A/C", "A/C Type", "Has Heating", "Median Rental Days on Market", 
              "Total Rental Listings", "Median Price per Sq.Ft", "Median Days On Market", 
              "Total Sale Listings", "Market Cap Rate", "All in Costs", "Rent per Sq.Ft", 
              "Rent to Price Ratio", "Income per Sq.Ft", "Equity Cap Rate", "Gross Rent Multiplier", 
              "Net Operating Income", "Annual Debt Service", "Debt Coverage Ratio", 
              "Operating Expense Ratio", "Vacancy Allowance", "Buy and Hold Score", 
              "Profit Margin", "All in Costs %", "Value", "Price per Sq.Ft"]

tab_names = ["purchase_price","cap_rate","debt_coverage_ratio","equity_cap_rate", 
            "gross_rent_multiplier","gross_scheduled_income","income_per_unit", 
            "income_per_sq_ft","net_income_multiplier","net_operating_income", 
            "operating_expense_ratio","value","rentToPriceRatio","all_in_costs", 
            "total_loan_payment","debt_service_annual","debt_service_monthly", 
            "max_purchase_price","propertyTaxes_total","propertyTaxes_year", 
            "propertyType","bedrooms","bathrooms","squareFootage","features_unitCount", 
            "lotSize","yearBuilt","zoning","features_architectureType","features_fireplace", 
            "features_garage","features_garageType","features_cooling","features_coolingType", 
            "features_heating","medianDaysOnMarket_rent","totalListings_rent", 
            "medianPricePerSquareFoot","medianDaysOnMarket_sales","totalListings_sales",
            "marketCapRate","all_in_costs_baseline","rentPerSquareFoot_baseline", 
            "rentToPriceRatio_baseline","income_per_sq_ft_baseline","equity_cap_rate_baseline", 
            "gross_rent_multiplier_baseline","net_operating_income_baseline", 
            "debt_service_annual_baseline","debt_coverage_ratio_baseline", 
            "operating_expense_ratio_baseline","vacancy_allowance_baseline", 
            "buy_hold_score_baseline","profit_margin_baseline","all_in_cost_pct_baseline", 
            "value_baseline","price_per_sq_ft_baseline"]


'''-------------Above stays out of loop---------------'''

'-----------------------------------------------------------------------------'
'''Create pdf report - table'''
#convert_cols=['all_in_cost_pct_baseline', 'all_in_costs', 'bathrooms', 'bedrooms', 'debt_service_annual', 'debt_service_annual_baseline', 'debt_service_monthly', 'features_unitCount', 'gross_scheduled_income', 'income_per_sq_ft', 'income_per_unit', 'income_per_sq_ft_baseline', 'lotSize', 'max_purchase_price', 'medianDaysOnMarket_rent', 'medianPricePerSquareFoot', 'net_operating_income', 'net_operating_income_baseline', 'price_per_sq_ft_baseline', 'propertyTaxes_total', 'propertyTaxes_year', 'purchase_price', 'rentPerSquareFoot_baseline', 'squareFootage', 'total_loan_payment', 'totalListings_rent', 'vacancy_allowance_baseline', 'value', 'value_baseline', 'yearBuilt']
convert_cols=['all_in_cost_pct_baseline', 'all_in_costs', 'bathrooms', 'bedrooms', 
              'debt_service_annual', 'debt_service_annual_baseline', 'debt_service_monthly', 
              'features_unitCount', 'gross_scheduled_income', 'income_per_sq_ft', 
              'income_per_unit', 'income_per_sq_ft_baseline', 'lotSize', 'max_purchase_price', 
              'medianDaysOnMarket_rent', 'medianPricePerSquareFoot', 'net_operating_income', 
              'net_operating_income_baseline', 'price_per_sq_ft_baseline', 'propertyTaxes_total', 
              'propertyTaxes_year', 'purchase_price', 'rentPerSquareFoot_baseline', 'squareFootage', 
              'total_loan_payment', 'totalListings_rent', 'vacancy_allowance_baseline', 'value', 
              'value_baseline', 'yearBuilt']


NULL_INT = -999999  # or any other sentinel integer you want

def safe_int(x):
    # Treat NaN / None / '' as NULL_INT
    if x is None or x == "" or (isinstance(x, float) and np.isnan(x)):
        return NULL_INT
    # If it's already a digit string, convert to int
    if isinstance(x, str) and x.isdigit():
        return int(x)
    # Otherwise, assume numeric and cast to int
    return int(x)

for col in convert_cols:
    listings[col] = listings[col].apply(safe_int)

'''-------------------REPORT CREATION LOOP BEGINS HERE----------------------'''
for i in range(len(listings)):
    '------------------------------------------------'
    '''Initiate master doc'''
    if listings["formattedAddress"][i] is not None:
        doc = SimpleDocTemplate(f'{listings["formattedAddress"][i]} Property Report.pdf', pagesize=letter)
    else:
        doc = SimpleDocTemplate(f'{listings["Address"][i]} Property Report.pdf', pagesize=letter)
    
    '------------------------------------------------'
    '''Create Street View Cover Sheet'''    
    lat_long = str(listings['latitude'][i]) + "," + str(listings['longitude'][i])
    svpic=requests.get("https://maps.googleapis.com/maps/api/streetview?size=600x300&location=" + lat_long + "&heading=151.78&pitch=-0.76&key=" + os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyA_5BoEzUmYM9NjthkUJx3u5ds7L1YA18M"))
    img = Image.open(BytesIO(svpic.content))
    '----------------------'
    pdf_path = "title_and_image.pdf"

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
    )
    
    story_cover = []
    try:
        story_cover.append(Paragraph(f'{listings["formattedAddress"][i]} Property Report', title_style))
    except:
        story_cover.append(Paragraph(f'{listings["Address"][i]} Property Report', title_style))
        
    story_cover.append(Spacer(1, 24))
    
    img_buffer = BytesIO(svpic.content)
    img_buffer.seek(0)
    
    img = rImage(img_buffer)
    img.hAlign = "CENTER"
    story_cover.append(img)    
    '------------------------------------------------'
    '''Filter null values out of bar chart'''    
    bar_cols_valid=[]
    bar_labels_valid=[]
    bar_names_valid=[]
    
    for p in range(len(bar_cols)):
        bar_cols[p] = bar_cols[p].replace(-999999, "N/A")
    
    for p in range(len(bar_cols)):
        if str([bar_cols[p][i] if isinstance(bar_cols[p][i], (int, float)) else np.nan][0]) == 'nan':
            pass
        else:
            bar_cols_valid.append(bar_cols[p])
            bar_labels_valid.append(bar_labels[p])
            bar_names_valid.append(bar_names[p])


#    for col in bar_cols_valid:
#        listings[col] = listings[col].apply(safe_int)

    '------------------------------------------------'
    '''Bar Chart Axis Setting'''
    mm_cols = [listings[b][i] for b in bar_names_valid]

    story_bar = []

    if not mm_cols:
        story_bar.append(Paragraph(
            "Zip Code Benchmark Comparison: No valid benchmark data available for chart.",
            styles["BodyText"]
        ))
    else:
        min_val = round(math.floor((min(mm_cols) - (0.25 *min(mm_cols))))) 
        max_val = round(math.ceil((max(mm_cols) + (0.25 *max(mm_cols)))))

        vals = np.linspace(min_val, max_val, num=10)[1:-1]  # drop endpoints [web:213][web:221]
        ticks = tuple(int(round(v)) for v in vals) 
        ticks_l = [int(round(v)) for v in vals]     

        filename="hbar_custom2.pdf"
        cats=bar_labels_valid
        values=[round(listings[col][i], 2) for col in bar_names_valid]
        values=[0.001 if x == 0.00 else x for x in values]
        title="Zip Code Benchmark Comparison (% Above or Below Baseline)"
        title_font="Helvetica-Bold"
        body_font="Helvetica"
        title_font_size=12
        axis_font_size=8
        tick_values=ticks_l        # list of tick positions, or None for auto
        value_range=(min_val, max_val)        # (min, max) or None
        pos_bar_color=colors.green
        neg_bar_color=colors.red
    #):
        if cats is None:
            cats = ["No Valid Attributes", "No Valid Attributes", "No Valid Attributes"]
        if values is None:
            values = [-1, 0, 1]

        #doc = SimpleDocTemplate(filename, pagesize=letter)

        dw_width, dw_height = 400, 200
        dw = Drawing(dw_width, dw_height)

        chart_x = 50
        chart_y = 0
        chart_width = 375
        chart_height = 14 * len(mm_cols)

        # Centered title over chart
        title_x = chart_x + chart_width / 2.0
        title_y = chart_y + chart_height + 25
        dw.add(String(
            title_x,
            title_y,
            title,
            textAnchor="middle",
            fontName=title_font,
            fontSize=title_font_size,
        ))

        bc = HorizontalBarChart()
        bc.x = chart_x
        bc.y = chart_y
        bc.width = chart_width
        bc.height = chart_height
        bc.data = [values]

        # Categories on left
        bc.categoryAxis.categoryNames = cats
        bc.categoryAxis.labelAxisMode = "low"
        bc.categoryAxis.labels.boxAnchor = "e"
        bc.categoryAxis.labels.fontName = body_font
        bc.categoryAxis.labels.fontSize = axis_font_size

        bc.barLabels.fontName = "Helvetica"
        bc.barLabels.fontSize = 8
        
        bc.barLabelFormat = '%0.2f'
        bc.barLabels.nudge = 20

        # Value axis styling
        bc.valueAxis.visibleTicks = 0          # remove small tick marks
        bc.valueAxis.labels.fontName = body_font
        bc.valueAxis.labels.fontSize = axis_font_size

        if tick_values is not None:
            bc.valueAxis.valueSteps = list(tick_values)

        if value_range is not None:
            vmin, vmax = value_range
            bc.valueAxis.valueMin = vmin
            bc.valueAxis.valueMax = vmax

        # Border around chart area
        bc.strokeColor = colors.black

        # Bar colors parameterized
        for p, v in enumerate(values):
            bc.bars[(0, p)].fillColor = pos_bar_color if v >= 0 else neg_bar_color

        dw.add(bc)
        story_bar.append(dw)
    '------------------------------------------------'
    '''Story Generation - Financials/Characteristics/Zip'''
    
    if listings["formattedAddress"][i] is not None:
        pdf_file = f'{listings["formattedAddress"][i]} Property Report.pdf'
    else:
        pdf_file = f'{listings["Address"][i]} Property Report.pdf'
    
    story1 = []
    story1.append(Paragraph(f"{listings['formattedAddress'][i]}",
                       styles["Title"]))   # from your own data [file:67]
    story1.append(Spacer(1, 18))
    '------------------------------------------------'
    '''FINANCIAL TABLE'''
    data_fin = [
        ["Financials", ""],
        #[Paragraph(f"Purchase Price at {dp_table} discount", styles['BodyText']),        f"${str(int(listings['purchase_price'][i]))}"],
        [f"Purchase Price at {dp_table} discount",   f"{'N/A' if listings['purchase_price'][i] == -999999 else '$' + str(int(listings['purchase_price'][i]))}"],
        ["Cap Rate",              f"{str(round(listings['cap_rate'][i] * 100, 2)) + '%'}"],
        ["Debt Coverage Ratio",   f"{str(round(listings['debt_coverage_ratio'][i], 2))}"],
        ["Equity Cap Rate",       f"{str(round(listings['equity_cap_rate'][i] * 100, 2)) + '%'}"],
        ["Gross Rent Multiplier", f"{str(round(listings['gross_rent_multiplier'][i], 2))}"],
        ["Gross Scheduled Income",   f"{'N/A' if listings['gross_scheduled_income'][i] == -999999 else '$' + str(int(listings['gross_scheduled_income'][i]))}"],
        ["Income Per Unit",   f"{'N/A' if listings['income_per_unit'][i] == -999999 else '$' + str(int(listings['income_per_unit'][i]))}"],
        ["Income Per Sq Ft",   f"{'N/A' if listings['income_per_sq_ft'][i] == -999999 else '$' + str(int(listings['income_per_sq_ft'][i]))}"],
        ["Net Income Multiplier", f"{str(round(listings['net_income_multiplier'][i], 2))}"],
        ["Net Operating Income",   f"{'N/A' if listings['net_operating_income'][i] == -999999 else '$' + str(int(listings['net_operating_income'][i]))}"],
        ["Operating Expense Ratio",f"{str(round(listings['operating_expense_ratio'][i], 2))}"],
        ["Value",   f"{'N/A' if listings['value'][i] == -999999 else '$' + str(int(listings['value'][i]))}"],
        ["Rent to Price Ratio",      f"{str(round(listings['rentToPriceRatio'][i], 2))}"],
        ["All in Costs",   f"{'N/A' if listings['all_in_costs'][i] == -999999 else '$' + str(int(listings['all_in_costs'][i]))}"],
        ["Total Loan Payment",   f"{'N/A' if listings['total_loan_payment'][i] == -999999 else '$' + str(int(listings['total_loan_payment'][i]))}"],
        ["Debt Service - Annual",   f"{'N/A' if listings['debt_service_annual'][i] == -999999 else '$' + str(int(listings['debt_service_annual'][i]))}"],
        ["Debt Service - Monthly",   f"{'N/A' if listings['debt_service_monthly'][i] == -999999 else '$' + str(int(listings['debt_service_monthly'][i]))}"],
        ["Maximum Purchase Price",   f"{'N/A' if listings['max_purchase_price'][i] == -999999 else '$' + str(int(listings['max_purchase_price'][i]))}"],
        ["Property Taxes",   f"{'N/A' if listings['propertyTaxes_total'][i] == -999999 else '$' + str(int(listings['propertyTaxes_total'][i]))}"],
        ["Property Tax Year",   f"{'N/A' if listings['propertyTaxes_year'][i] == -999999 else str(int(listings['propertyTaxes_year'][i]))}"],
    ]
        
    data_fin[0][0] = Paragraph("<b>Financials</b>", styles["BodyText"])
    table_style = TableStyle([
        # span header across both columns (row 0, col 0..1)
        ("SPAN", (0, 0), (1, 0)),           # merge first row
        ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (1, 0), "MIDDLE"),

        # green first column (rows 1..end)
        ("BACKGROUND", (0, 1), (0, -1), colors.darkseagreen),

        # text alignment
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),

        # borders and grid
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),

        # padding
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])

    fin_table = Table(data_fin, colWidths=[160, 80], hAlign="LEFT")
    fin_table.setStyle(table_style)
    
    '------------------------------------------------'
    '''PROPERTY TABLE'''
    
    data_prop = [
        ["Property Characteristics", ""],
        ["Property Type",f"{'N/A' if listings['propertyType'][i] == None else str(listings['propertyType'][i])}"],
        ["Bedrooms",f"{'N/A' if listings['bedrooms'][i] == -999999 else str(int(listings['bedrooms'][i]))}"],
        ["Bathrooms",f"{'N/A' if listings['bathrooms'][i] == -999999 else str(int(listings['bathrooms'][i]))}"    ],
        ["Square Footage",    f"{'N/A' if listings['squareFootage'][i] == -999999 else str(int(listings['squareFootage'][i]))}"],
        ["Unit Count",          f"{'N/A' if listings['features_unitCount'][i] == -999999 else str(int(listings['features_unitCount'][i]))}"],
        ["Lot Size",      f"{'N/A' if listings['lotSize'][i] == -999999 else str(int(listings['lotSize'][i]))}"],
        ["Year Built",                 f"{'N/A' if listings['yearBuilt'][i] == -999999 else str(int(listings['yearBuilt'][i]))}"],
        ["Zoning",f"{'N/A' if listings['zoning'][i] == None else str(listings['zoning'][i])}"],
        ["Architecture Type",f"{'N/A' if listings['features_architectureType'][i] == None else str(listings['features_architectureType'][i])}"],
        ["Has Fireplace",f"{'N/A' if listings['features_fireplace'][i] == None else str(listings['features_fireplace'][i])}"],
        ["Has Garage",f"{'N/A' if listings['features_garage'][i] == None else str(listings['features_garage'][i])}"],
        ["Garage Type",f"{'N/A' if listings['features_garageType'][i] == None else str(listings['features_garageType'][i])}"],
        ["Has A/C",f"{'N/A' if listings['features_cooling'][i] == None else str(listings['features_cooling'][i])}"],
        ["A/C Type",f"{'N/A' if listings['features_coolingType'][i] == None else str(listings['features_coolingType'][i])}"],
        ["Has Heating",f"{'N/A' if listings['features_heating'][i] == None else str(listings['features_heating'][i])}"],
    ]

    data_prop[0][0] = Paragraph("<b>Property Characteristics</b>", styles["BodyText"])
    table_style = TableStyle([
        # span header across both columns (row 0, col 0..1)
        ("SPAN", (0, 0), (1, 0)),           # merge first row
        ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (1, 0), "MIDDLE"),

        # green first column (rows 1..end)
        ("BACKGROUND", (0, 1), (0, -1), colors.powderblue),

        # text alignment
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),

        # borders and grid
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),

        # padding
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])

    prop_table = Table(data_prop, colWidths=[160, 80], hAlign="RIGHT")
    prop_table.setStyle(table_style)

    # outer table with one row and two columns
    outer = Table([[prop_table, fin_table]],
                  colWidths=[300, 300])   # control left/right widths here

    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),   # align both inner tables to the same top
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    story1.append(outer)
    '------------------------------------------------'
    '''ZIP CODE STATISTICS'''
    title = "Zip Code Statistics"
   
    #Adapt below patterns to zip blocks, applied to nan values.
    #f"{'N/A' if listings['features_unitCount'][i] == -999999 else str(int(listings['features_unitCount'][i]))}"
    #f"{'N/A' if listings['features_heating'][i] == None else str(listings['features_heating'][i])}"
    
    #left_block = [
    #    ['ZIP Code Level Benchmarks', ""],
    #    ["Median Days on Rental Market", f"{'N/A' if str(listings['medianDaysOnMarket_rent'][i]) == 'nan' else str(listings['medianDaysOnMarket_rent'][i])}"],
    #    ["Total Rental Listings", f"{'N/A' if str(listings['totalListings_rent'][i]) == 'nan' else str(listings['totalListings_rent'][i])}"],
    #    ["Median Price per Sq.Ft", f"{'N/A' if str(int(round(listings['medianPricePerSquareFoot'][i]))) == 'nan' else str(int(round(listings['medianPricePerSquareFoot'][i])))}"], #round to 0, str w '$'
    #    ["Median Days On Market", f"{'N/A' if str(listings['medianDaysOnMarket_sales'][i]) == 'nan' else str(listings['medianDaysOnMarket_sales'][i])}"],
    #    ["Total Sale Listings", f"{'N/A' if str(listings['totalListings_sales'][i]) == 'nan' else str(listings['totalListings_sales'][i])}"],
    #    ["Market Cap Rate",  f"{'N/A' if str(round(listings['marketCapRate'][i] * 100, 2)) == 'nan' else str(round(listings['marketCapRate'][i] * 100, 2)) + '%'}"], #round to 2 then * 100, str with %
    #    ["All in Costs", f"{'N/A' if str(int(round(listings['all_in_costs_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['all_in_costs_baseline'][i], 0)))}"], #round to 0, str with $
    #    ["Rent per Sq.Ft", f"{'N/A' if str(int(round(listings['rentPerSquareFoot_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['rentPerSquareFoot_baseline'][i], 0)))}"], #round to 0, str with $
    #    ["Rent to Price Ratio", f"{'N/A' if str(round(listings['rentToPriceRatio_baseline'][i], 2)) == 'nan' else str(round(listings['rentToPriceRatio_baseline'][i], 2))}"], #round to 2
    #    ["Income per Sq.Ft", f"{'N/A' if str(int(round(listings['income_per_sq_ft_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['rentPerSquareFoot_baseline'][i], 0)))}"], #round to 0, str with $
    #    ["Equity Cap Rate", f"{'N/A' if str(round(listings['equity_cap_rate_baseline'][i] * 100, 2)) == 'nan' else str(round(listings['equity_cap_rate_baseline'][i] * 100, 2)) + '%'}"], #round to 2 then * 100, str with %
    #]

    #left_block[0][0] = Paragraph("<b>ZIP Level Statistics Cont.</b>", styles["BodyText"])
    
    #right_block = [
    #    ["", ""],
    #    ["Gross Rent Multiplier", f"{'N/A' if str(round(listings['gross_rent_multiplier_baseline'][i], 2)) == 'nan' else str(round(listings['gross_rent_multiplier_baseline'][i], 2))}"], #round to 2
    #    ["Net Operating Income", f"{'N/A' if str(int(round(listings['net_operating_income_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['net_operating_income_baseline'][i], 0)))}"], #round to 0, str with $ 
    #    ["Annual Debt Service", f"{'N/A' if str(int(round(listings['debt_service_annual_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['debt_service_annual_baseline'][i], 0)))}"], #round to 0, str with $
    #    ["Debt Coverage Ratio", f"{'N/A' if str(round(listings['debt_coverage_ratio_baseline'][i], 2)) == 'nan' else str(round(listings['debt_coverage_ratio_baseline'][i], 2))}"], #round to 2
    #    ["Operating Expense Ratio", f"{'N/A' if str(round(listings['operating_expense_ratio_baseline'][i], 2)) == 'nan' else str(round(listings['operating_expense_ratio_baseline'][i], 2))}"], #round to 2
    #    ["Vacancy Allowance", f"{'N/A' if str(int(round(listings['vacancy_allowance_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['vacancy_allowance_baseline'][i], 0)))}"], #round to 0, str with $
    #    ["Buy and Hold Score", f"{'N/A' if str(round(listings['buy_hold_score_baseline'][i], 2)) == 'nan' else str(round(listings['buy_hold_score_baseline'][i], 2))}"], #round to 2
    #    ["Profit Margin", f"{'N/A' if str(round(listings['profit_margin_baseline'][i], 2)) == 'nan' else str(round(listings['profit_margin_baseline'][i], 2))}"], #round to 2
    #    ["All in Costs %", f"{'N/A' if str(round(listings['all_in_cost_pct_baseline'][i], 2)) == 'nan' else str(round(listings['all_in_cost_pct_baseline'][i], 2))}"], #round to 2
    #    ["Value", f"{'N/A' if str(int(round(listings['value_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['value_baseline'][i], 0)))}"], #round to 0, str with $
    #    ["Price per Sq.Ft", f"{'N/A' if str(int(round(listings['price_per_sq_ft_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['price_per_sq_ft_baseline'][i], 0)))}"], #round to 0, str with $
    #]
    
    #right_block[0][0] = Paragraph("<b>ZIP Level Statistics</b>", styles["BodyText"])

    com_block = [
        ['ZIP Code Level Benchmarks', ""],
        ["Median Days on Rental Market", f"{'N/A' if str(listings['medianDaysOnMarket_rent'][i]) == 'nan' else str(listings['medianDaysOnMarket_rent'][i])}"],
        ["Total Rental Listings", f"{'N/A' if str(listings['totalListings_rent'][i]) == 'nan' else str(listings['totalListings_rent'][i])}"],
        ["Median Price per Sq.Ft", f"{'N/A' if str(int(round(listings['medianPricePerSquareFoot'][i]))) == 'nan' else str(int(round(listings['medianPricePerSquareFoot'][i])))}"], #round to 0, str w '$'
        ["Median Days On Market", f"{'N/A' if str(listings['medianDaysOnMarket_sales'][i]) == 'nan' else str(listings['medianDaysOnMarket_sales'][i])}"],
        ["Total Sale Listings", f"{'N/A' if str(listings['totalListings_sales'][i]) == 'nan' else str(listings['totalListings_sales'][i])}"],
        ["Market Cap Rate",  f"{'N/A' if str(round(listings['marketCapRate'][i] * 100, 2)) == 'nan' else str(round(listings['marketCapRate'][i] * 100, 2)) + '%'}"], #round to 2 then * 100, str with %
        ["All in Costs", f"{'N/A' if str(int(round(listings['all_in_costs_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['all_in_costs_baseline'][i], 0)))}"], #round to 0, str with $
        ["Rent per Sq.Ft", f"{'N/A' if str(int(round(listings['rentPerSquareFoot_baseline'][i], 2))) == 'nan' else '$' + str(int(round(listings['rentPerSquareFoot_baseline'][i], 2)))}"], #round to 0, str with $
        ["Rent to Price Ratio", f"{'N/A' if str(round(listings['rentToPriceRatio_baseline'][i], 2)) == 'nan' else str(round(listings['rentToPriceRatio_baseline'][i], 2))}"], #round to 2
        ["Income per Sq.Ft", f"{'N/A' if str(int(round(listings['income_per_sq_ft_baseline'][i], 2))) == 'nan' else '$' + str(int(round(listings['rentPerSquareFoot_baseline'][i], 2)))}"], #round to 0, str with $
        ["Equity Cap Rate", f"{'N/A' if str(round(listings['equity_cap_rate_baseline'][i] * 100, 2)) == 'nan' else str(round(listings['equity_cap_rate_baseline'][i] * 100, 2)) + '%'}"], #round to 2 then * 100, str with %
        ["Gross Rent Multiplier", f"{'N/A' if str(round(listings['gross_rent_multiplier_baseline'][i], 2)) == 'nan' else str(round(listings['gross_rent_multiplier_baseline'][i], 2))}"], #round to 2
        ["Net Operating Income", f"{'N/A' if str(int(round(listings['net_operating_income_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['net_operating_income_baseline'][i], 0)))}"], #round to 0, str with $ 
        ["Annual Debt Service", f"{'N/A' if str(int(round(listings['debt_service_annual_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['debt_service_annual_baseline'][i], 0)))}"], #round to 0, str with $
        ["Debt Coverage Ratio", f"{'N/A' if str(round(listings['debt_coverage_ratio_baseline'][i], 2)) == 'nan' else str(round(listings['debt_coverage_ratio_baseline'][i], 2))}"], #round to 2
        ["Operating Expense Ratio", f"{'N/A' if str(round(listings['operating_expense_ratio_baseline'][i], 2)) == 'nan' else str(round(listings['operating_expense_ratio_baseline'][i], 2))}"], #round to 2
        ["Vacancy Allowance", f"{'N/A' if str(int(round(listings['vacancy_allowance_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['vacancy_allowance_baseline'][i], 0)))}"], #round to 0, str with $
        ["Buy and Hold Score", f"{'N/A' if str(round(listings['buy_hold_score_baseline'][i], 2)) == 'nan' else str(round(listings['buy_hold_score_baseline'][i], 2))}"], #round to 2
        ["Profit Margin", f"{'N/A' if str(round(listings['profit_margin_baseline'][i], 2)) == 'nan' else str(round(listings['profit_margin_baseline'][i], 2))}"], #round to 2
        #["All in Costs %", f"{'N/A' if str(round(listings['all_in_cost_pct_baseline'][i], 2)) == 'nan' else str(round(listings['all_in_cost_pct_baseline'][i], 2) * 100) + '%'}"], #round to 2
        ["Value", f"{'N/A' if str(int(round(listings['value_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['value_baseline'][i], 0)))}"], #round to 0, str with $
        ["Price per Sq.Ft", f"{'N/A' if str(int(round(listings['price_per_sq_ft_baseline'][i], 0))) == 'nan' else '$' + str(int(round(listings['price_per_sq_ft_baseline'][i], 0)))}"], #round to 0, str with $

    ]

    com_block[0][0] = Paragraph("<b>ZIP Level Statistics</b>", styles["BodyText"])

    '------------------------------------------------'
    table_style = TableStyle([
        # span header across both columns (row 0, col 0..1)
        ("SPAN", (0, 0), (1, 0)),           # merge first row
        ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (1, 0), "MIDDLE"),
    
        # green first column (rows 1..end)
        ("BACKGROUND", (0, 1), (0, -1), colors.lightcoral),
    
        # text alignment
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
    
        # borders and grid
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
    
        # padding
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
    
    
    #z1_table = Table(right_block, colWidths=[160, 80], hAlign="RIGHT") #assign to left and right
    #z1_table.setStyle(table_style) #assign to left and right
    
    #z2_table = Table(left_block, colWidths=[160, 80], hAlign="LEFT") #assign to left and right
    #z2_table.setStyle(table_style) #assign to left and right
    
    z3_table = Table(com_block, colWidths=[160, 80], hAlign="CENTER") #assign to left and right
    z3_table.setStyle(table_style) #assign to left and right

    
    # outer table with one row and two columns
    #outer_zip = Table([[z1_table, z2_table]],
    #              colWidths=[300, 300])   # control left/right widths here
    
    #outer_zip.setStyle(TableStyle([
    #    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),   # align both inner tables to the same top
    #    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    #]))
    
    #story1.append(outer_zip)
    story1.append(Spacer(1, 200))
    story1.append(z3_table)
    '------------------------------------------------'
    '''OWNER STATISTICS'''
        
    if listings["formattedAddress"][i] is not None:
        pdf_file = f'{listings["formattedAddress"][i]} Property Report.pdf'
    else:
        pdf_file = f'{listings["Address"][i]} Property Report.pdf'
    
    styles = getSampleStyleSheet()
    
    story_owner = []
    story_owner.append(Paragraph(f"{listings['formattedAddress'][i]}",
                       styles["Title"]))   # from your own data [file:67]

    title = "Owner Statistics"
   
    owner_block = [
        ['Owner Info', ""],
        ["Owner Type", str(listings['owner_type'][i])],
        ["Owner Address", str(listings['owner_mailingAddress_formattedAddress'][i])],
        ["Owner Name(s)", str(listings['owner_names'][i])], #round to 0, str w '$'
        ["Owner Occupied", str(listings['ownerOccupied'][i])],
    ]
    
    owner_block[0][0] = Paragraph("<b>Owner Info</b>", styles["BodyText"])

    table_style = TableStyle([
        # span header across both columns (row 0, col 0..1)
        ("SPAN", (0, 0), (1, 0)),           # merge first row
        ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (1, 0), "MIDDLE"),
    
        # green first column (rows 1..end)
        ("BACKGROUND", (0, 1), (0, -1), colors.silver),
    
        # text alignment
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
    
        # borders and grid
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
    
        # padding
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
    
    owner_table = Table(owner_block, colWidths=[120, 160]) #assign to left and right

    story_owner.append(owner_table)
    
    
    story_combo=[]
    story_combo.extend(story_cover)
    story_combo.append(PageBreak())   
    story_combo.extend(story1)
    story_combo.append(PageBreak())
    story_combo.extend(story_bar)
    story_combo.append(PageBreak())
    story_combo.extend(story_owner)
    doc.build(story_combo)
'--------------------------------'

'''Send pdf reports to email'''
listings_em=listings.copy()
listings_em=listings_em[["formattedAddress", "medianDaysOnMarket_rent", "totalListings_rent", 
                         "medianPricePerSquareFoot", "medianDaysOnMarket_sales", 
                         "totalListings_sales", "marketCapRate", "all_in_costs_baseline", 
                         "rentPerSquareFoot_baseline", "rentToPriceRatio_baseline", 
                         "income_per_sq_ft_baseline", "equity_cap_rate_baseline", 
                         "gross_rent_multiplier_baseline", "net_operating_income_baseline", 
                         "debt_service_annual_baseline", "debt_coverage_ratio_baseline", 
                         "operating_expense_ratio_baseline", "vacancy_allowance_baseline", 
                         "buy_hold_score_baseline", "profit_margin_baseline", 
                         "all_in_cost_pct_baseline", "value_baseline", 
                         "price_per_sq_ft_baseline", "propertyType", "bedrooms", 
                         "bathrooms", "squareFootage", "features_unitCount", 
                         "lotSize", "yearBuilt", "zoning", "features_architectureType", 
                         "features_fireplace", "features_garage", "features_garageType", 
                         "features_cooling", "features_coolingType", "features_heating", 
                         "purchase_price", "cap_rate", "debt_coverage_ratio", "equity_cap_rate", 
                         "gross_rent_multiplier", "gross_scheduled_income", "income_per_unit", 
                         "income_per_sq_ft", "net_income_multiplier", "net_operating_income", 
                         "operating_expense_ratio", "value", "rentToPriceRatio", "all_in_costs", 
                         "total_loan_payment", "debt_service_annual", "debt_service_monthly", 
                         "max_purchase_price", "propertyTaxes_total", "propertyTaxes_year"]]

listings_em.to_excel('Listings Report Data.xlsx')

if user_em and os.getenv("SNAPSHOT_SKIP_EMAIL", "false").lower() != "true":
    email_sender = os.getenv("SMTP_USERNAME", "hatemdj09@gmail.com")
    password = os.getenv("SMTP_PASSWORD", "qkxc rptb wfrm tjdu")
    email_receiver = user_em
    subject = 'SnapShot Property Report'
    body = 'See the attached reports for your recently analyzed properties.'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = user_em
    em['Subject'] = subject
    em.set_content(body)

    #Add pdfs
    for i in range(len(listings)):

        if listings["formattedAddress"][i] is not None:
            pdf_path = f'{listings["formattedAddress"][i]} Property Report.pdf'
        else:
            pdf_path = f'{listings["Address"][i]} Property Report.pdf'
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        em.add_attachment(
            pdf_bytes,
            maintype='application',
            subtype='pdf',
            filename=pdf_path
        )

    pdf_path = 'Listings Report Data.xlsx'

    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
        
    em.add_attachment(
        pdf_bytes,
        maintype='application',
        subtype='pdf',
        filename='Listings Report Data.xlsx'
    )

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.send_message(em)

