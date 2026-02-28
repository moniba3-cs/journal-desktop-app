import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, date

DATA_FILE = "journal_entries.json"

BG          = "#fff0f5"
CARD        = "#ffffff"
SIDEBAR     = "#fce4ec"
ACCENT      = "#f48fb1"
ACCENT2     = "#ce93d8"
LAVENDER    = "#e1bee7"
SOFT_PINK   = "#fce4ec"
TEXT        = "#4a2040"
MUTED       = "#b07090"
GREEN       = "#a5d6a7"
BORDER      = "#f8bbd0"
YELLOW      = "#fff9c4"

MOODS = [
    ("😊", "Happy",    "#fde68a"),
    ("😢", "Sad",      "#bfdbfe"),
    ("😌", "Calm",     "#bbf7d0"),
    ("😤", "Angry",    "#fecaca"),
    ("😰", "Anxious",  "#e9d5ff"),
    ("🥰", "Loved",    "#fbcfe8"),
    ("😴", "Tired",    "#e0e7ff"),
    ("🤩", "Excited",  "#fef08a"),
]

def load_entries():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_entries(entries):
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2)
class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 My Little Journal")
        self.root.geometry("820x620")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.entries = load_entries()
        self.selected_mood = None
        self.current_view = "write"  # write | history | stats
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh_history())

        self._build_ui()
        self._show_view("write")

    def _build_ui(self):
        
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=180)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

    
        tk.Label(self.sidebar, text="🌸", font=("Helvetica", 28),
                 bg=SIDEBAR).pack(pady=(28, 2))
        tk.Label(self.sidebar, text="my journal", font=("Helvetica", 13, "bold"),
                 bg=SIDEBAR, fg=TEXT).pack()
        tk.Label(self.sidebar, text="a safe little space ♡",
                 font=("Helvetica", 8), bg=SIDEBAR, fg=MUTED).pack(pady=(2, 24))


        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)


        self.nav_btns = {}
        nav_items = [
            ("write", "✏️  Write", "new entry"),
            ("history", "📖  History", "past entries"),
            ("stats", "✨  Mood Stats", "your patterns"),
        ]
        for key, label, sub in nav_items:
            btn_frame = tk.Frame(self.sidebar, bg=SIDEBAR, cursor="hand2")
            btn_frame.pack(fill="x", padx=12, pady=3)
            btn_frame.bind("<Button-1>", lambda e, k=key: self._show_view(k))

            lbl = tk.Label(btn_frame, text=label, font=("Helvetica", 10, "bold"),
                           bg=SIDEBAR, fg=TEXT, anchor="w", padx=10, pady=8,
                           cursor="hand2")
            lbl.pack(fill="x")
            lbl.bind("<Button-1>", lambda e, k=key: self._show_view(k))

            sub_lbl = tk.Label(btn_frame, text=sub, font=("Helvetica", 7),
                               bg=SIDEBAR, fg=MUTED, anchor="w", padx=10)
            sub_lbl.pack(fill="x")
            sub_lbl.bind("<Button-1>", lambda e, k=key: self._show_view(k))

            self.nav_btns[key] = (btn_frame, lbl, sub_lbl)

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)

        self.entry_count_lbl = tk.Label(self.sidebar, text="",
                                         font=("Helvetica", 8), bg=SIDEBAR, fg=MUTED)
        self.entry_count_lbl.pack()
        self._update_count()

        tk.Label(self.sidebar, text='"write it out ♡"',
                 font=("Helvetica", 8, "italic"), bg=SIDEBAR,
                 fg=MUTED, wraplength=150).pack(side="bottom", pady=20)

    
        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.write_frame = tk.Frame(self.main, bg=BG)


        today = datetime.now().strftime("%A, %B %d %Y")
        tk.Label(self.write_frame, text=today,
                 font=("Helvetica", 10), bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(28, 2))
        tk.Label(self.write_frame, text="How are you feeling today?",
                 font=("Helvetica", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=30)

        
        mood_outer = tk.Frame(self.write_frame, bg=BG)
        mood_outer.pack(fill="x", padx=30, pady=(14, 0))

        self.mood_frames = {}
        mood_grid = tk.Frame(mood_outer, bg=BG)
        mood_grid.pack(anchor="w")

        for i, (emoji, name, color) in enumerate(MOODS):
            col = i % 4
            row = i // 4
            f = tk.Frame(mood_grid, bg=CARD, relief="flat",
                         highlightthickness=2, highlightbackground=BORDER,
                         cursor="hand2")
            f.grid(row=row, column=col, padx=5, pady=5, ipadx=8, ipady=6)

            tk.Label(f, text=emoji, font=("Helvetica", 18), bg=CARD,
                     cursor="hand2").pack()
            tk.Label(f, text=name, font=("Helvetica", 7, "bold"),
                     bg=CARD, fg=MUTED, cursor="hand2").pack()

            for w in [f] + list(f.winfo_children()):
                w.bind("<Button-1>", lambda e, m=(emoji, name, color), fr=f: self._select_mood(m, fr))

            self.mood_frames[(emoji, name, color)] = f

    
        tk.Label(self.write_frame, text="Entry title",
                 font=("Helvetica", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(16, 2))
        self.title_entry = tk.Entry(self.write_frame, font=("Helvetica", 11),
                                    bg=CARD, fg=TEXT, relief="flat",
                                    highlightthickness=1, highlightbackground=BORDER,
                                    insertbackground=ACCENT)
        self.title_entry.pack(fill="x", padx=30, ipady=7)

        
        tk.Label(self.write_frame, text="What's on your mind?",
                 font=("Helvetica", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(12, 2))

        text_frame = tk.Frame(self.write_frame, bg=CARD,
                               highlightthickness=1, highlightbackground=BORDER)
        text_frame.pack(fill="both", padx=30, pady=(0, 12))

        self.body_text = tk.Text(text_frame, font=("Helvetica", 10),
                                  bg=CARD, fg=TEXT, relief="flat",
                                  wrap="word", height=6,
                                  insertbackground=ACCENT,
                                  padx=10, pady=10)
        self.body_text.pack(fill="both", expand=True)

    
        save_btn = tk.Button(self.write_frame, text="Save Entry 🌸",
                              font=("Helvetica", 11, "bold"),
                              bg=ACCENT, fg="white", relief="flat",
                              activebackground=ACCENT2, activeforeground="white",
                              cursor="hand2", padx=20, pady=10,
                              command=self._save_entry)
        save_btn.pack(padx=30, anchor="w")

    
        self.history_frame = tk.Frame(self.main, bg=BG)

        tk.Label(self.history_frame, text="📖 Past Entries",
                 font=("Helvetica", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(28, 4))

        
        search_frame = tk.Frame(self.history_frame, bg=CARD,
                                 highlightthickness=1, highlightbackground=BORDER)
        search_frame.pack(fill="x", padx=30, pady=(0, 12))
        tk.Label(search_frame, text="🔍", bg=CARD, font=("Helvetica", 11)).pack(side="left", padx=8)
        tk.Entry(search_frame, textvariable=self.search_var,
                 font=("Helvetica", 10), bg=CARD, fg=TEXT,
                 relief="flat", insertbackground=ACCENT).pack(side="left", fill="x",
                                                               expand=True, ipady=8)

        
        list_outer = tk.Frame(self.history_frame, bg=BG)
        list_outer.pack(fill="both", expand=True, padx=30)

        self.history_canvas = tk.Canvas(list_outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer, orient="vertical",
                                   command=self.history_canvas.yview)
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.history_canvas.pack(side="left", fill="both", expand=True)

        self.history_inner = tk.Frame(self.history_canvas, bg=BG)
        self.history_canvas.create_window((0, 0), window=self.history_inner, anchor="nw")
        self.history_inner.bind("<Configure>", lambda e: self.history_canvas.configure(
            scrollregion=self.history_canvas.bbox("all")))

    
        self.stats_frame = tk.Frame(self.main, bg=BG)
        self._build_stats_view()

    def _select_mood(self, mood, frame):
        # Reset all
        for (e, n, c), f in self.mood_frames.items():
            f.configure(bg=CARD, highlightbackground=BORDER)
            for w in f.winfo_children():
                w.configure(bg=CARD)

    
        emoji, name, color = mood
        frame.configure(bg=color, highlightbackground=ACCENT)
        for w in frame.winfo_children():
            w.configure(bg=color)

        self.selected_mood = mood

    def _save_entry(self):
        title = self.title_entry.get().strip()
        body = self.body_text.get("1.0", tk.END).strip()

        if not body:
            messagebox.showwarning("oops!", "Please write something first 🌸")
            return
        if not self.selected_mood:
            messagebox.showwarning("oops!", "Please pick a mood first 💕")
            return

        entry = {
            "id": int(datetime.now().timestamp()),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": title or "Untitled Entry",
            "body": body,
            "mood_emoji": self.selected_mood[0],
            "mood_name": self.selected_mood[1],
            "mood_color": self.selected_mood[2],
        }

        self.entries.insert(0, entry)
        save_entries(self.entries)

        self.title_entry.delete(0, tk.END)
        self.body_text.delete("1.0", tk.END)
        for (e, n, c), f in self.mood_frames.items():
            f.configure(bg=CARD, highlightbackground=BORDER)
            for w in f.winfo_children():
                w.configure(bg=CARD)
        self.selected_mood = None

        self._update_count()
        self._build_stats_view()
        messagebox.showinfo("saved! 🌸", "Your entry has been saved ♡")


    def refresh_history(self):
        for w in self.history_inner.winfo_children():
            w.destroy()

        query = self.search_var.get().lower()
        filtered = [e for e in self.entries
                    if query in e["title"].lower() or query in e["body"].lower()
                    or query in e["mood_name"].lower()]

        if not filtered:
            tk.Label(self.history_inner, text="no entries found 🌸",
                     font=("Helvetica", 11), bg=BG, fg=MUTED).pack(pady=40)
            return

        for entry in filtered:
            self._draw_entry_card(entry)

    def _draw_entry_card(self, entry):
        color = entry.get("mood_color", SOFT_PINK)

        card = tk.Frame(self.history_inner, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER,
                        pady=0)
        card.pack(fill="x", pady=6)

        
        tk.Frame(card, bg=color, width=6).pack(side="left", fill="y")

        content = tk.Frame(card, bg=CARD, padx=12, pady=10)
        content.pack(side="left", fill="both", expand=True)


        top = tk.Frame(content, bg=CARD)
        top.pack(fill="x")
        tk.Label(top, text=f"{entry['mood_emoji']} {entry['title']}",
                 font=("Helvetica", 10, "bold"), bg=CARD, fg=TEXT).pack(side="left")
        tk.Label(top, text=entry["date"], font=("Helvetica", 8),
                 bg=CARD, fg=MUTED).pack(side="right")

    
        badge_frame = tk.Frame(content, bg=CARD)
        badge_frame.pack(anchor="w", pady=(2, 4))
        badge = tk.Label(badge_frame, text=f" {entry['mood_name']} ",
                         font=("Helvetica", 7, "bold"),
                         bg=color, fg=TEXT, padx=4, pady=2)
        badge.pack(side="left")

        
        preview = entry["body"][:120] + ("..." if len(entry["body"]) > 120 else "")
        tk.Label(content, text=preview, font=("Helvetica", 9),
                 bg=CARD, fg=MUTED, wraplength=480, justify="left").pack(anchor="w")

    
        del_btn = tk.Button(card, text="✕", font=("Helvetica", 8),
                            bg=CARD, fg=MUTED, relief="flat", cursor="hand2",
                            command=lambda eid=entry["id"]: self._delete_entry(eid))
        del_btn.pack(side="right", padx=8)

    def _delete_entry(self, entry_id):
        if messagebox.askyesno("delete?", "Delete this entry? This can't be undone 🌸"):
            self.entries = [e for e in self.entries if e["id"] != entry_id]
            save_entries(self.entries)
            self._update_count()
            self.refresh_history()
            self._build_stats_view()


    def _build_stats_view(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        tk.Label(self.stats_frame, text="✨ Mood Stats",
                 font=("Helvetica", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(28, 4))
        tk.Label(self.stats_frame, text="your emotional patterns ♡",
                 font=("Helvetica", 9), bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(0, 16))

        if not self.entries:
            tk.Label(self.stats_frame, text="no entries yet 🌸\nstart writing to see your stats!",
                     font=("Helvetica", 11), bg=BG, fg=MUTED, justify="center").pack(pady=60)
            return

        
        streak = self._calc_streak()
        streak_frame = tk.Frame(self.stats_frame, bg=YELLOW,
                                 highlightthickness=1, highlightbackground=BORDER)
        streak_frame.pack(fill="x", padx=30, pady=(0, 14))
        tk.Label(streak_frame, text=f"🔥 {streak} day streak!",
                 font=("Helvetica", 13, "bold"), bg=YELLOW, fg=TEXT, pady=12).pack()
        tk.Label(streak_frame, text="keep writing every day ♡",
                 font=("Helvetica", 8), bg=YELLOW, fg=MUTED, pady=(0)).pack(pady=(0, 10))

        summary_row = tk.Frame(self.stats_frame, bg=BG)
        summary_row.pack(fill="x", padx=30, pady=(0, 16))

        total = len(self.entries)
        this_month = sum(1 for e in self.entries
                         if e["date"].startswith(datetime.now().strftime("%Y-%m")))

        for label, val in [("total entries", total), ("this month", this_month)]:
            card = tk.Frame(summary_row, bg=CARD,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", padx=(0, 10), ipadx=16, ipady=10)
            tk.Label(card, text=str(val), font=("Helvetica", 22, "bold"),
                     bg=CARD, fg=ACCENT2).pack()
            tk.Label(card, text=label, font=("Helvetica", 8),
                     bg=CARD, fg=MUTED).pack()

    
        tk.Label(self.stats_frame, text="mood breakdown",
                 font=("Helvetica", 10, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(0, 8))

        mood_counts = {}
        for e in self.entries:
            key = (e["mood_emoji"], e["mood_name"], e["mood_color"])
            mood_counts[key] = mood_counts.get(key, 0) + 1

        bar_frame = tk.Frame(self.stats_frame, bg=BG)
        bar_frame.pack(fill="x", padx=30)

        sorted_moods = sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)
        max_count = max(mood_counts.values()) if mood_counts else 1

        for (emoji, name, color), count in sorted_moods:
            row = tk.Frame(bar_frame, bg=BG)
            row.pack(fill="x", pady=3)

            tk.Label(row, text=f"{emoji} {name}",
                     font=("Helvetica", 9), bg=BG, fg=TEXT, width=12,
                     anchor="w").pack(side="left")

            bar_bg = tk.Frame(row, bg="#f3e8ef", height=18)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(0, 8))
            bar_bg.pack_propagate(False)

            bar_width = max(int((count / max_count) * 100), 5)
            bar_fill = tk.Frame(bar_bg, bg=color, height=18)
            bar_fill.place(relwidth=count / max_count, relheight=1)

            tk.Label(row, text=str(count), font=("Helvetica", 9, "bold"),
                     bg=BG, fg=MUTED).pack(side="left")

    def _calc_streak(self):
        if not self.entries:
            return 0
        dates = sorted(set(e["date"][:10] for e in self.entries), reverse=True)
        streak = 0
        check = date.today()
        for d in dates:
            entry_date = date.fromisoformat(d)
            if entry_date == check:
                streak += 1
                check = date.fromordinal(check.toordinal() - 1)
            elif entry_date < check:
                break
        return streak

    def _show_view(self, view):
        self.current_view = view
        self.write_frame.pack_forget()
        self.history_frame.pack_forget()
        self.stats_frame.pack_forget()

    
        for key, (f, lbl, sub) in self.nav_btns.items():
            active = key == view
            bg = "#f8d7e3" if active else SIDEBAR
            f.configure(bg=bg)
            lbl.configure(bg=bg, fg=ACCENT if active else TEXT)
            sub.configure(bg=bg)

        if view == "write":
            self.write_frame.pack(fill="both", expand=True)
        elif view == "history":
            self.history_frame.pack(fill="both", expand=True)
            self.refresh_history()
        elif view == "stats":
            self.stats_frame.pack(fill="both", expand=True)
            self._build_stats_view()

    def _update_count(self):
        n = len(self.entries)
        self.entry_count_lbl.config(text=f"{n} entr{'y' if n==1 else 'ies'} written")


if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()
