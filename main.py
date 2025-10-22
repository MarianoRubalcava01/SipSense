import json
import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

'''    pip install -r requirements.txt to install packages'''

'''

APP CONFIG

'''
ctk.set_appearance_mode("system")  
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SipSense — Discover Your Perfect Drink")
app.geometry("1000x750")
app.minsize(860, 620)

DATA_FILE = "drinks.json"

'''Data Layer with dummy data
# Drink schema: {name, desc, is_non_alcoholic, sugar, image_path}'''
drinks_store = []

def load_data():
    """Load drinks from JSON; seed with a few examples if missing."""
    global drinks_store
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                drinks_store = json.load(f)
        except Exception:
            drinks_store = []
    if not drinks_store:
        drinks_store = [
            {"name":"Strawberry Mojito","desc":"Fresh mint, lime, strawberry",
             "is_non_alcoholic":False,"sugar":35,"image_path":""},
            {"name":"Matcha Latte","desc":"Creamy matcha with milk",
             "is_non_alcoholic":True,"sugar":20,"image_path":""},
            {"name":"Cold Brew Tonic","desc":"Bold coffee with sparkling tonic water",
             "is_non_alcoholic":True,"sugar":5,"image_path":""},
        ]
    save_data()

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(drinks_store, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save data: {e}")

load_data()

'''

Helper Function

'''
def ctki_from_path(path, size=(100, 100)):
    """Create a CTkImage from a local path if it exists."""
    try:
        if path and os.path.exists(path):
            return ctk.CTkImage(light_image=Image.open(path), size=size)
    except Exception:
        pass
    return None

def matches_filters(d, active_filters):
    """Filter logic with only Non-Alcoholic + Low Sugar."""
    if "Non-Alcoholic" in active_filters and not d.get("is_non_alcoholic", False):
        return False
    if "Low Sugar" in active_filters and d.get("sugar", 0) > 10:
        return False
    return True

'''

Tab Section

'''
tabs = ctk.CTkTabview(app, corner_radius=12)
tabs.pack(fill="both", expand=True, padx=20, pady=20)
home_tab = tabs.add("Home")
admin_tab = tabs.add("Admin")

'''Home Tab Section'''
'''Header Section'''
header = ctk.CTkFrame(home_tab, corner_radius=12)
header.pack(fill="x", padx=10, pady=(0, 10))

title = ctk.CTkLabel(header, text="🍹 SipSense", font=ctk.CTkFont(size=28, weight="bold"))
title.pack(side="left", padx=(15, 8), pady=15)
tagline = ctk.CTkLabel(header, text="AI-powered drink discovery that gets your vibe", font=ctk.CTkFont(size=14))
tagline.pack(side="left", pady=15)

''' Prompt Section'''
prompt_section = ctk.CTkFrame(home_tab, corner_radius=12)
prompt_section.pack(fill="x", padx=10, pady=(0, 10))

ctk.CTkLabel(prompt_section, text="What are you in the mood for?", font=ctk.CTkFont(size=16)).pack(pady=(12, 4))
prompt_box = ctk.CTkTextbox(prompt_section, height=70)
prompt_box.pack(padx=16, pady=(0, 10), fill="x")

'''Filter Bar'''
filter_bar = ctk.CTkFrame(home_tab, corner_radius=12)
filter_bar.pack(fill="x", padx=10, pady=(0, 10))

filter_options = ["Non-Alcoholic", "Low Sugar"]
active_filters = []

def toggle_filter(option):
    if option in active_filters:
        active_filters.remove(option)
    else:
        active_filters.append(option)
    refresh_results()

for option in filter_options:
    chk = ctk.CTkCheckBox(filter_bar, text=option, command=lambda o=option: toggle_filter(o))
    chk.pack(side="left", padx=8, pady=10)

'''Results'''
results_frame = ctk.CTkScrollableFrame(home_tab, label_text="Recommended Drinks", corner_radius=12)
results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

def open_details(drink):
    top = ctk.CTkToplevel(app)
    top.title(drink["name"])
    top.geometry("460x420")
    ctk.CTkLabel(top, text=drink["name"], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(16, 8))

    img = ctki_from_path(drink.get("image_path",""), size=(180, 180))
    if img:
        ctk.CTkLabel(top, image=img, text="").pack(pady=(0, 8))
        top._img = img  

    info_lines = [
        drink.get("desc",""),
        "",
        f"Non-Alcoholic: {'Yes' if drink.get('is_non_alcoholic') else 'No'}",
        f"Sugar: {drink.get('sugar',0)}",
    ]
    ctk.CTkLabel(top, text="\n".join(info_lines), justify="left", wraplength=400).pack(padx=16, pady=8)
    ctk.CTkButton(top, text="Close", command=top.destroy).pack(pady=12)

def card(drink, parent):
    wrapper = ctk.CTkFrame(parent, corner_radius=12)
    wrapper.pack(fill="x", padx=10, pady=10)

    '''Image Section for drink card'''
    img = ctki_from_path(drink.get("image_path",""), size=(80, 80))
    if img:
        img_lbl = ctk.CTkLabel(wrapper, image=img, text="")
        img_lbl.image = img
        img_lbl.pack(side="left", padx=12, pady=12)

    '''Middle Section Text for drink card'''
    inner = ctk.CTkFrame(wrapper, fg_color="transparent")
    inner.pack(side="left", fill="both", expand=True, padx=4, pady=8)
    ctk.CTkLabel(inner, text=drink["name"], font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
    ctk.CTkLabel(inner, text=drink.get("desc",""), wraplength=560, anchor="w", justify="left").pack(anchor="w")

    '''Right Action Section '''
    ctk.CTkButton(wrapper, text="View Details", width=120, command=lambda d=drink: open_details(d)).pack(side="right", padx=12, pady=12)

def refresh_results():
    for w in results_frame.winfo_children():
        if isinstance(w, ctk.CTkFrame):
            w.destroy()

    query = prompt_box.get("1.0", "end").strip().lower()
    filtered = []
    for d in drinks_store:
        if not matches_filters(d, active_filters):
            continue
        if query:
            hay = f"{d.get('name','')} {d.get('desc','')}".lower()
            if query not in hay:
                continue
        filtered.append(d)

    if not filtered:
        ctk.CTkLabel(results_frame, text="No matching drinks yet. Try fewer filters or different text.", font=ctk.CTkFont(size=14)).pack(pady=20)
        return

    for d in filtered:
        card(d, results_frame)

def get_suggestions():
    '''# Currently uses local filtering API with chat or some other api would go here'''
    refresh_results()

get_btn = ctk.CTkButton(prompt_section, text="✨ Get Suggestions", height=40, corner_radius=8, command=get_suggestions)
get_btn.pack(pady=(0, 12))

'''First Time rendering results'''
refresh_results()

'''

Admin Section

'''
admin_wrap = ctk.CTkFrame(admin_tab, corner_radius=12)
admin_wrap.pack(fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(admin_wrap, text="Admin — Manage Your Drinks", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
ctk.CTkLabel(admin_wrap, text="Add drinks one-by-one or import from CSV. Changes are saved to drinks.json.", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(0, 12))

form = ctk.CTkFrame(admin_wrap, corner_radius=12)
form.pack(fill="x", padx=12, pady=6)

'''# Fields (NO temperature)'''
name_var = tk.StringVar()
desc_var = tk.StringVar()
na_var = tk.BooleanVar(value=False)
sugar_var = tk.IntVar(value=10)
img_path_var = tk.StringVar()

row1 = ctk.CTkFrame(form, fg_color="transparent")
row1.pack(fill="x", padx=10, pady=(10, 6))
ctk.CTkLabel(row1, text="Name").pack(side="left", padx=(0, 6))
name_ent = ctk.CTkEntry(row1, textvariable=name_var)
name_ent.pack(side="left", fill="x", expand=True)

row2 = ctk.CTkFrame(form, fg_color="transparent")
row2.pack(fill="x", padx=10, pady=6)
ctk.CTkLabel(row2, text="Description").pack(side="left", padx=(0, 6))
desc_ent = ctk.CTkEntry(row2, textvariable=desc_var)
desc_ent.pack(side="left", fill="x", expand=True)

row3 = ctk.CTkFrame(form, fg_color="transparent")
row3.pack(fill="x", padx=10, pady=6)
na_chk = ctk.CTkCheckBox(row3, text="Non-Alcoholic", variable=na_var)
na_chk.pack(side="left", padx=(0, 16))
ctk.CTkLabel(row3, text="Sugar").pack(side="left", padx=(0, 6))
sugar_slider = ctk.CTkSlider(row3, from_=0, to=100, number_of_steps=100)
sugar_slider.set(sugar_var.get())
sugar_slider.pack(side="left", fill="x", expand=True, padx=(0, 8))
sugar_badge = ctk.CTkLabel(row3, text=str(sugar_var.get()))
sugar_badge.pack(side="left")
def update_sugar_label(v):
    val = int(float(v))
    sugar_var.set(val)
    sugar_badge.configure(text=str(val))
sugar_slider.configure(command=update_sugar_label)

row4 = ctk.CTkFrame(form, fg_color="transparent")
row4.pack(fill="x", padx=10, pady=(6, 12))
ctk.CTkLabel(row4, text="Image Path").pack(side="left", padx=(0, 6))
img_ent = ctk.CTkEntry(row4, textvariable=img_path_var)
img_ent.pack(side="left", fill="x", expand=True, padx=(0, 6))
def browse_image():
    path = filedialog.askopenfilename(title="Select Drink Image",
                                      filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.gif"), ("All files", "*.*")])
    if path:
        img_path_var.set(path)
ctk.CTkButton(row4, text="Browse…", width=100, command=browse_image).pack(side="left")

'''Action Functions'''
act_row = ctk.CTkFrame(admin_wrap, fg_color="transparent")
act_row.pack(fill="x", padx=12, pady=6)

def clear_form():
    name_var.set("")
    desc_var.set("")
    na_var.set(False)
    sugar_var.set(10)
    sugar_slider.set(10)
    img_path_var.set("")

def add_drink():
    name = name_var.get().strip()
    if not name:
        messagebox.showwarning("Missing Name", "Please enter a drink name.")
        return
    drink = {
        "name": name,
        "desc": desc_var.get().strip(),
        "is_non_alcoholic": bool(na_var.get()),
        "sugar": int(sugar_var.get()),
        "image_path": img_path_var.get().strip(),
    }
    drinks_store.append(drink)
    save_data()
    clear_form()
    refresh_admin_list()
    refresh_results()
    messagebox.showinfo("Added", f"“{name}” added.")

def import_csv():
    """
    CSV columns (no temp): name,desc,is_non_alcoholic,sugar,image_path
    - is_non_alcoholic accepts: 1/0, true/false, yes/no, y/n
    - sugar: 0–100
    """
    path = filedialog.askopenfilename(title="Import CSV", filetypes=[("CSV files","*.csv"), ("All files","*.*")])
    if not path:
        return
    added = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                nm = (row.get("name") or "").strip()
                if not nm:
                    continue
                drink = {
                    "name": nm,
                    "desc": (row.get("desc") or "").strip(),
                    "is_non_alcoholic": str(row.get("is_non_alcoholic","false")).lower() in ("1","true","yes","y"),
                    "sugar": int(float(row.get("sugar","0") or 0)),
                    "image_path": (row.get("image_path") or "").strip(),
                }
                drinks_store.append(drink)
                added += 1
        save_data()
        refresh_admin_list()
        refresh_results()
        messagebox.showinfo("Import Complete", f"Imported {added} drinks.")
    except Exception as e:
        messagebox.showerror("Import Error", f"Could not import: {e}")

def export_csv():
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Export CSV")
    if not path:
        return
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name","desc","is_non_alcoholic","sugar","image_path"])
            writer.writeheader()
            for d in drinks_store:
                writer.writerow(d)
        messagebox.showinfo("Exported", f"Saved to {path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Could not export: {e}")

ctk.CTkButton(act_row, text="Add Drink", command=add_drink).pack(side="left", padx=(0,8))
ctk.CTkButton(act_row, text="Import CSV", command=import_csv).pack(side="left", padx=8)
ctk.CTkButton(act_row, text="Export CSV", command=export_csv).pack(side="left", padx=8)

'''Admin List'''
admin_list = ctk.CTkScrollableFrame(admin_tab, label_text="Your Drinks", corner_radius=12)
admin_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

def delete_drink(idx):
    try:
        name = drinks_store[idx]["name"]
        del drinks_store[idx]
        save_data()
        refresh_admin_list()
        refresh_results()
        messagebox.showinfo("Deleted", f"Removed “{name}”.")
    except Exception:
        pass

def refresh_admin_list():
    for w in admin_list.winfo_children():
        if isinstance(w, ctk.CTkFrame):
            w.destroy()
    if not drinks_store:
        ctk.CTkLabel(admin_list, text="No drinks yet. Add some from the form above.", font=ctk.CTkFont(size=14)).pack(pady=16)
        return
    for i, d in enumerate(drinks_store):
        row = ctk.CTkFrame(admin_list, corner_radius=10)
        row.pack(fill="x", padx=10, pady=6)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        name_line = f"{d.get('name','')} • {'NA' if d.get('is_non_alcoholic') else 'Alcoholic'} • Sugar {d.get('sugar',0)}"
        ctk.CTkLabel(left, text=name_line, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(left, text=d.get("desc",""), wraplength=650, justify="left").pack(anchor="w")

        ctk.CTkButton(row, text="Delete", width=80, command=lambda idx=i: delete_drink(idx)).pack(side="right", padx=8, pady=8)

refresh_admin_list()


app.mainloop()
