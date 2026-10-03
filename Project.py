"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     FLOOD DISASTER RELIEF DISTRIBUTION SYSTEM — Visual Dashboard           ║
║     B.Tech (AIDS) | Amrita Vishwa Vidyapeetham, Delhi NCR                  ║
║                                                                              ║
║  HOW TO RUN:                                                                ║
║      python flood_relief_dashboard.py                                       ║
║      (Tkinter comes pre-installed with Python — no pip needed)             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import heapq
from collections import deque
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  THEME — Dark professional color palette
# ══════════════════════════════════════════════════════════════════════════════
C = {
    "bg":        "#1B2631",   # main background
    "panel":     "#212F3D",   # side panels
    "canvas":    "#0D1B2A",   # graph canvas
    "card":      "#1A2535",   # card backgrounds
    "border":    "#2E4057",   # borders
    "text":      "#ECF0F1",   # primary text
    "dim":       "#7F8C8D",   # dimmed text
    "critical":  "#E74C3C",   # critical severity
    "high":      "#E67E22",   # high severity
    "medium":    "#27AE60",   # medium severity
    "ctr_g":     "#2471A3",   # ground center
    "ctr_a":     "#7D3C98",   # air center
    "ctr_w":     "#117A65",   # water center
    "edge_ok":   "#1E8449",   # clear road
    "edge_dmg":  "#9A7D0A",   # damaged road
    "edge_fld":  "#7B241C",   # flooded road
    "gold":      "#F4D03F",   # dijkstra path / selected
    "visited":   "#1F618D",   # dijkstra visited
    "btn_fifo":  "#1A5276",   # fifo button
    "btn_prio":  "#4A235A",   # priority button
    "btn_rst":   "#641E16",   # reset button
    "btn_algo":  "#0E6655",   # algo buttons
    "white":     "#FFFFFF",
    "served":    "#1E8449",   # served village overlay
}

# ══════════════════════════════════════════════════════════════════════════════
#  NODE POSITIONS  on the 760 × 625 canvas
#  Laid out geographically: Bihar(top-left) Assam(top-right) Kerala(bottom)
# ══════════════════════════════════════════════════════════════════════════════
POS = {
    # ── Bihar ────────────────────────────────────────────────────
    "V01":  (125, 72),    # Rampur
    "V02":  (55,  165),   # Sitapur
    "V03":  (248, 55),    # Gopalganj
    "V04":  (215, 165),   # Majhauli
    "V05":  (318, 130),   # Hajipur (village)
    "RC01": (165, 245),   # Patna Relief Hub
    "RC02": (65,  245),   # Muzaffarpur Camp
    "RC03": (285, 245),   # Hajipur Depot
    # ── Assam ────────────────────────────────────────────────────
    "V06":  (455, 72),    # Morigaon
    "V07":  (572, 52),    # Nagaon
    "V08":  (445, 162),   # Dhubri
    "V09":  (530, 178),   # Barpeta
    "V10":  (685, 92),    # Lakhimpur
    "RC04": (492, 248),   # Guwahati Hub
    "RC05": (590, 215),   # Nagaon Camp
    "RC06": (678, 205),   # Jorhat Depot
    # ── Kerala ───────────────────────────────────────────────────
    "V11":  (172, 510),   # Alappuzha
    "V12":  (262, 572),   # Pathanamthitta
    "V13":  (368, 552),   # Kottayam
    "V14":  (335, 468),   # Ernakulam
    "V15":  (465, 450),   # Thrissur (village)
    "RC07": (98,  582),   # Thiruvananthapuram Hub
    "RC08": (308, 422),   # Kochi Camp
    "RC09": (452, 518),   # Thrissur Depot
    # ── Odisha ───────────────────────────────────────────────────
    "RC10": (592, 355),   # Bhubaneswar Reserve
}

# ══════════════════════════════════════════════════════════════════════════════
#  EDGES  (source, destination, distance_km, passability)
# ══════════════════════════════════════════════════════════════════════════════
EDGES = [
    ("RC01","V01",  45,"Yes"),    ("RC01","V02",  62,"Yes"),
    ("RC01","V04",  38,"Partial"),("RC02","V02",  18,"Yes"),
    ("RC02","V03",  55,"Yes"),    ("RC03","V05",  22,"Yes"),
    ("RC03","V04",  40,"Partial"),("V01", "V02",  30,"No"),
    ("V02", "V03",  48,"Yes"),    ("V03", "V04",  35,"Partial"),
    ("V04", "V05",  27,"No"),     ("RC04","V07",  50,"Yes"),
    ("RC04","V06",  75,"Yes"),    ("RC04","V08", 120,"Yes"),
    ("RC05","V07",  20,"Partial"),("RC05","V09",  45,"Yes"),
    ("RC06","V10",  90,"Yes"),    ("V06", "V07",  65,"No"),
    ("V07", "V09",  40,"Yes"),    ("V08", "V09",  80,"Yes"),
    ("V09", "V10", 110,"Partial"),("RC07","V11",  35,"Yes"),
    ("RC07","V12",  85,"Yes"),    ("RC08","V13",  40,"Yes"),
    ("RC08","V14",  15,"Yes"),    ("RC09","V15",  20,"Yes"),
    ("RC09","V13",  50,"Partial"),("V11", "V12",  60,"No"),
    ("V12", "V13",  55,"Yes"),    ("V13", "V14",  45,"Yes"),
    ("V14", "V15",  70,"Yes"),    ("RC01","RC02",  80,"Yes"),
    ("RC04","RC05", 100,"Yes"),   ("RC07","RC08",  60,"Yes"),
    ("RC08","RC09",  75,"Yes"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  STATIC DATA  — villages, centers, requests
# ══════════════════════════════════════════════════════════════════════════════
VILLAGE_DATA = {
    "V01":("Rampur",         "Bihar", 3200,"Critical",960,  6400, 320,True),
    "V02":("Sitapur",        "Bihar", 2800,"High",    840,  5600, 280,True),
    "V03":("Gopalganj",      "Bihar", 1500,"Medium",  450,  3000, 150,False),
    "V04":("Majhauli",       "Bihar", 2100,"High",    630,  4200, 210,True),
    "V05":("Hajipur",        "Bihar", 4000,"Critical",1200, 8000, 400,True),
    "V06":("Morigaon",       "Assam", 1800,"High",    540,  3600, 180,False),
    "V07":("Nagaon",         "Assam", 3500,"Critical",1050, 7000, 350,True),
    "V08":("Dhubri",         "Assam", 2200,"High",    660,  4400, 220,True),
    "V09":("Barpeta",        "Assam", 1600,"Medium",  480,  3200, 160,False),
    "V10":("Lakhimpur",      "Assam", 2900,"Critical",870,  5800, 290,True),
    "V11":("Alappuzha",      "Kerala",5000,"Critical",1500,10000, 500,True),
    "V12":("Pathanamthitta", "Kerala",3100,"High",    930,  6200, 310,True),
    "V13":("Kottayam",       "Kerala",2700,"High",    810,  5400, 270,False),
    "V14":("Ernakulam",      "Kerala",6000,"Critical",1800,12000, 600,True),
    "V15":("Thrissur",       "Kerala",2400,"Medium",  720,  4800, 240,False),
}

CENTER_DATA = {
    "RC01":("Patna Relief Hub",         "Bihar", "Ground",15000, 80000,5000,45,12,"Active"),
    "RC02":("Muzaffarpur Camp",          "Bihar", "Ground",8000,  40000,2500,28, 7,"Active"),
    "RC03":("Hajipur Depot",             "Bihar", "Ground",500,   25000,1500,20, 5,"Active"),
    "RC04":("Guwahati Hub",              "Assam", "Air",   18000, 90000,6000,55,15,"Active"),
    "RC05":("Nagaon Camp",               "Assam", "Water", 7000,  35000,2200,22, 6,"Active"),
    "RC06":("Jorhat Depot",              "Assam", "Ground",4000,  20000,1200,15, 4,"Active"),
    "RC07":("Thiruvananthapuram Hub",    "Kerala","Air",   20000,100000,7000,60,18,"Active"),
    "RC08":("Kochi Camp",                "Kerala","Ground",12000, 60000,4000,40,10,"Active"),
    "RC09":("Thrissur Depot",            "Kerala","Water", 6000,  30000,2000,18, 5,"Active"),
    "RC10":("Bhubaneswar Reserve",       "Odisha","Ground",10000, 50000,3500,35, 9,"Standby"),
}

MAX_RESOURCES = {cid: (d[3], d[4], d[5]) for cid, d in CENTER_DATA.items()}

REQUESTS = [
    ("V14","Food",   1800,"Critical"), ("V11","Water",  10000,"Critical"),
    ("V07","Medicine",350,"Critical"), ("V05","Food",    1200,"Critical"),
    ("V01","Water",  6400,"Critical"), ("V10","Food",     870,"Critical"),
    ("V14","Medicine",600,"Critical"), ("V02","Food",     840,"High"),
    ("V08","Water",  4400,"High"),     ("V12","Medicine", 310,"High"),
    ("V04","Water",  4200,"High"),     ("V13","Food",     810,"High"),
    ("V03","Medicine",150,"Medium"),   ("V06","Water",   3600,"High"),
    ("V09","Food",    480,"Medium"),   ("V15","Water",   4800,"Medium"),
    ("V05","Medicine",400,"Critical"), ("V11","Medicine", 500,"Critical"),
    ("V07","Food",   1050,"Critical"), ("V01","Food",     960,"Critical"),
]

SEV_RANK = {"Critical":1,"High":2,"Medium":3,"Low":4}

# ══════════════════════════════════════════════════════════════════════════════
#  DSA — GRAPH
# ══════════════════════════════════════════════════════════════════════════════
class Graph:
    def __init__(self):
        self._adj = {}

    def add_node(self, nid):
        if nid not in self._adj:
            self._adj[nid] = []

    def add_edge(self, u, v, w, passable):
        self.add_node(u); self.add_node(v)
        self._adj[u].append((v, w, passable))
        self._adj[v].append((u, w, passable))

    def neighbors(self, nid):
        return self._adj.get(nid, [])

    def all_nodes(self):
        return list(self._adj.keys())


# ══════════════════════════════════════════════════════════════════════════════
#  DSA — DIJKSTRA
# ══════════════════════════════════════════════════════════════════════════════
def dijkstra(graph, source, passable_only=True):
    INF    = float("inf")
    dist   = {n: INF  for n in graph.all_nodes()}
    parent = {n: None for n in graph.all_nodes()}
    dist[source] = 0
    heap   = [(0, source)]
    visited= set()
    while heap:
        cd, u = heapq.heappop(heap)
        if u in visited: continue
        visited.add(u)
        for v, w, p in graph.neighbors(u):
            if passable_only and p == "No": continue
            ew = w * 1.5 if p == "Partial" else w
            nd = cd + ew
            if nd < dist[v]:
                dist[v] = nd; parent[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, parent


def reconstruct(parent, target):
    path, n = [], target
    while n:
        path.append(n); n = parent[n]
    return list(reversed(path))


# ══════════════════════════════════════════════════════════════════════════════
#  DSA — BFS
# ══════════════════════════════════════════════════════════════════════════════
def bfs(graph, source, center_ids):
    visited = {source}
    q = deque([(source, [source])])
    while q:
        node, path = q.popleft()
        if node in center_ids and node != source:
            return node, len(path)-1, path
        for nb, _, p in graph.neighbors(node):
            if nb not in visited and p != "No":
                visited.add(nb); q.append((nb, path+[nb]))
    return None, 0, []


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD CLASS
# ══════════════════════════════════════════════════════════════════════════════
class FloodReliefDashboard:

    VR = 20    # village node radius
    CR = 24    # center node radius

    def __init__(self, root):
        self.root      = root
        self.graph     = Graph()
        self.resources = {}      # cid -> [food, water, medicine]
        self.served    = set()   # served village ids
        self.sim_on    = False
        self.mode      = tk.StringVar(value="FIFO")
        self.speed_ms  = 700
        self.pending_requests   = list(REQUESTS)
        self.delivery_log       = []
        self.selected_nid       = None
        self.waiting_for_click  = None   # "dijkstra" | "bfs"

        # Canvas item registries
        self.ovals  = {}   # nid -> oval id
        self.labels = {}   # nid -> text id
        self.e_lines= {}   # (u,v) sorted -> line id
        self.hi_items= []  # temporary highlight items

        self._init_data()
        self._setup_window()
        self._build_layout()
        self._draw_graph()
        self._refresh_queue()
        self._refresh_resources()
        self._status("Ready — Click a village node to inspect, or press a button to start.")

    # ── Data setup ────────────────────────────────────────────────────────────
    def _init_data(self):
        for u, v, w, p in EDGES:
            self.graph.add_edge(u, v, w, p)
        for cid, d in CENTER_DATA.items():
            self.resources[cid] = [d[3], d[4], d[5]]   # food, water, medicine

    def _reset_data(self):
        self.served.clear()
        self.delivery_log.clear()
        self.pending_requests = list(REQUESTS)
        for cid, d in CENTER_DATA.items():
            self.resources[cid] = [d[3], d[4], d[5]]
        self.sim_on = False
        self.selected_nid = None
        self.waiting_for_click = None

    # ── Window & layout ───────────────────────────────────────────────────────
    def _setup_window(self):
        self.root.title("Flood Disaster Relief Distribution System  |  Visual Dashboard")
        self.root.configure(bg=C["bg"])
        self.root.geometry("1390x860")
        self.root.resizable(False, False)

    def _build_layout(self):
        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = tk.Frame(self.root, bg=C["critical"], height=50)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="🌊  FLOOD DISASTER RELIEF DISTRIBUTION SYSTEM",
                 bg=C["critical"], fg=C["white"],
                 font=("Arial", 16, "bold")).pack(side="left", padx=15, pady=10)
        tk.Label(title_bar,
                 text="B.Tech AIDS | Amrita Vishwa Vidyapeetham | DSA + OOP Project",
                 bg=C["critical"], fg="#FADBD8",
                 font=("Arial", 9)).pack(side="right", padx=15, pady=10)

        # ── Main body ─────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left panel
        left = tk.Frame(body, bg=C["panel"], width=210)
        left.pack(side="left", fill="y", padx=(4,0), pady=4)
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Right panel
        right = tk.Frame(body, bg=C["panel"], width=408)
        right.pack(side="right", fill="y", padx=(0,4), pady=4)
        right.pack_propagate(False)
        self._build_right_panel(right)

        # Canvas frame (center)
        canv_frame = tk.Frame(body, bg=C["canvas"], bd=2, relief="flat")
        canv_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas = tk.Canvas(canv_frame, bg=C["canvas"],
                                highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # ── Status bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="")
        status_bar = tk.Frame(self.root, bg=C["border"], height=32)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self.status_var,
                 bg=C["border"], fg=C["gold"],
                 font=("Consolas", 9), anchor="w").pack(
                 side="left", padx=10, pady=6)

    def _build_left_panel(self, parent):
        def section(text):
            tk.Label(parent, text=text, bg=C["panel"], fg=C["dim"],
                     font=("Arial", 8, "bold")).pack(pady=(10,3), padx=8, anchor="w")

        def btn(parent, text, cmd, color):
            b = tk.Button(parent, text=text, command=cmd,
                          bg=color, fg=C["white"], relief="flat",
                          font=("Arial", 9, "bold"), cursor="hand2",
                          activebackground=C["gold"], activeforeground=C["bg"],
                          pady=5)
            b.pack(fill="x", padx=8, pady=2)
            return b

        section("── SIMULATION ──")
        btn(parent, "▶  Run FIFO Simulation",
            lambda: self._start_sim("FIFO"), C["btn_fifo"])
        btn(parent, "⭐  Run Priority Simulation",
            lambda: self._start_sim("Priority"), C["btn_prio"])
        btn(parent, "🔄  Reset Everything",
            self._reset, C["btn_rst"])

        section("── SPEED ──")
        spd_frame = tk.Frame(parent, bg=C["panel"])
        spd_frame.pack(fill="x", padx=8)
        self.speed_var = tk.IntVar(value=700)
        tk.Scale(spd_frame, from_=200, to=1500, orient="horizontal",
                 variable=self.speed_var,
                 command=lambda v: setattr(self, 'speed_ms', int(v)),
                 bg=C["panel"], fg=C["text"], troughcolor=C["border"],
                 highlightthickness=0, showvalue=False,
                 label="Fast ←──────→ Slow").pack(fill="x")

        section("── ALGORITHMS ──")
        btn(parent, "🔍 Dijkstra: Click Village",
            lambda: self._arm_click("dijkstra"), C["btn_algo"])
        btn(parent, "🔍 BFS: Click Village",
            lambda: self._arm_click("bfs"), C["btn_algo"])
        btn(parent, "⚖  Dijkstra vs BFS (All)",
            self._compare_all, C["btn_algo"])
        btn(parent, "📊 Show Sorting Demo",
            self._show_sorting, C["btn_algo"])

        section("── LEGEND ──")

        # Village severity legend with explanation
        sev_items = [
            ("●", C["critical"], "Critical", "Life risk, evacuate"),
            ("●", C["high"],     "High",     "Severe flooding"),
            ("●", C["medium"],   "Medium",   "Manageable flood"),
        ]
        for sym, col, sev, reason in sev_items:
            row = tk.Frame(parent, bg=C["panel"])
            row.pack(fill="x", padx=6, pady=1)
            tk.Label(row, text=sym, fg=col, bg=C["panel"],
                     font=("Arial", 13, "bold"), width=2).pack(side="left")
            col_text = tk.Frame(row, bg=C["panel"])
            col_text.pack(side="left")
            tk.Label(col_text, text=sev, fg=col, bg=C["panel"],
                     font=("Arial", 8, "bold")).pack(anchor="w")
            tk.Label(col_text, text=reason, fg=C["dim"], bg=C["panel"],
                     font=("Arial", 7)).pack(anchor="w")

        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", padx=8, pady=4)

        # Center types
        ctr_items = [
            ("■", C["ctr_g"], "Ground Center", "Truck 🚚 delivery"),
            ("■", C["ctr_a"], "Air Center",    "Helicopter 🚁"),
            ("■", C["ctr_w"], "Water Center",  "Boat 🚤 delivery"),
        ]
        for sym, col, cname, desc in ctr_items:
            row = tk.Frame(parent, bg=C["panel"])
            row.pack(fill="x", padx=6, pady=1)
            tk.Label(row, text=sym, fg=col, bg=C["panel"],
                     font=("Arial", 13, "bold"), width=2).pack(side="left")
            col_text = tk.Frame(row, bg=C["panel"])
            col_text.pack(side="left")
            tk.Label(col_text, text=cname, fg=C["text"], bg=C["panel"],
                     font=("Arial", 8, "bold")).pack(anchor="w")
            tk.Label(col_text, text=desc, fg=C["dim"], bg=C["panel"],
                     font=("Arial", 7)).pack(anchor="w")

        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", padx=8, pady=4)

        # Road types
        road_items = [
            ("━", C["edge_ok"],  "Clear Road",   "Vehicles pass freely"),
            ("╌", C["edge_dmg"], "Damaged Road", "1.5× slower (penalty)"),
            ("╌", C["edge_fld"], "Flooded Road", "Blocked, Dijkstra skips"),
            ("━", C["gold"],     "Dijkstra Path","Shortest route found"),
        ]
        for sym, col, rname, desc in road_items:
            row = tk.Frame(parent, bg=C["panel"])
            row.pack(fill="x", padx=6, pady=1)
            tk.Label(row, text=sym, fg=col, bg=C["panel"],
                     font=("Arial", 13, "bold"), width=2).pack(side="left")
            col_text = tk.Frame(row, bg=C["panel"])
            col_text.pack(side="left")
            tk.Label(col_text, text=rname, fg=C["text"], bg=C["panel"],
                     font=("Arial", 8, "bold")).pack(anchor="w")
            tk.Label(col_text, text=desc, fg=C["dim"], bg=C["panel"],
                     font=("Arial", 7)).pack(anchor="w")

    def _build_right_panel(self, parent):
        # ── Queue section ──────────────────────────────────────────────────
        tk.Label(parent, text="📋  REQUEST QUEUE",
                 bg=C["panel"], fg=C["gold"],
                 font=("Arial", 10, "bold")).pack(pady=(10,4), padx=10, anchor="w")

        q_frame = tk.Frame(parent, bg=C["card"], bd=1, relief="flat")
        q_frame.pack(fill="x", padx=8, pady=(0,6))

        self.queue_lb = tk.Listbox(q_frame, height=11,
                                   bg=C["card"], fg=C["text"],
                                   selectbackground=C["gold"],
                                   selectforeground=C["bg"],
                                   font=("Consolas", 8),
                                   bd=0, highlightthickness=0,
                                   activestyle="none")
        sb = tk.Scrollbar(q_frame, command=self.queue_lb.yview,
                          bg=C["border"])
        self.queue_lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.queue_lb.pack(fill="both", expand=True, padx=2, pady=2)

        # Queue stats row
        self.q_stats = tk.StringVar(value="")
        tk.Label(parent, textvariable=self.q_stats,
                 bg=C["panel"], fg=C["dim"],
                 font=("Arial", 8)).pack(padx=10, anchor="w")

        # ── Info section ───────────────────────────────────────────────────
        tk.Label(parent, text="ℹ️   NODE INFO",
                 bg=C["panel"], fg=C["gold"],
                 font=("Arial", 10, "bold")).pack(pady=(10,4), padx=10, anchor="w")

        info_frame = tk.Frame(parent, bg=C["card"], bd=1, relief="flat")
        info_frame.pack(fill="x", padx=8, pady=(0,6))

        self.info_text = tk.Text(info_frame, height=7, state="disabled",
                                 bg=C["card"], fg=C["text"],
                                 font=("Consolas", 8), bd=0,
                                 highlightthickness=0, wrap="word")
        self.info_text.pack(fill="both", padx=4, pady=4)

        # ── Resource bars ──────────────────────────────────────────────────
        tk.Label(parent, text="📦  RESOURCE LEVELS",
                 bg=C["panel"], fg=C["gold"],
                 font=("Arial", 10, "bold")).pack(pady=(6,4), padx=10, anchor="w")

        res_outer = tk.Frame(parent, bg=C["panel"])
        res_outer.pack(fill="both", expand=True, padx=6, pady=(0,6))

        self.res_canvas = tk.Canvas(res_outer, bg=C["card"],
                                    highlightthickness=0)
        res_sb = tk.Scrollbar(res_outer, orient="vertical",
                              command=self.res_canvas.yview)
        self.res_canvas.configure(yscrollcommand=res_sb.set)
        res_sb.pack(side="right", fill="y")
        self.res_canvas.pack(fill="both", expand=True)

        self.res_inner = tk.Frame(self.res_canvas, bg=C["card"])
        self.res_canvas.create_window((0,0), window=self.res_inner, anchor="nw")
        self.res_inner.bind("<Configure>",
            lambda e: self.res_canvas.configure(
                scrollregion=self.res_canvas.bbox("all")))

    # ── Graph drawing ──────────────────────────────────────────────────────────
    def _draw_graph(self):
        self.canvas.delete("all")
        self.ovals.clear(); self.labels.clear(); self.e_lines.clear()
        cw = self.canvas.winfo_width()  or 760
        ch = self.canvas.winfo_height() or 625

        self._draw_regions(cw, ch)
        self._draw_edges()
        self._draw_nodes()
        self._draw_graph_legend(cw, ch)

    def _draw_regions(self, cw, ch):
        """Draw state name labels only — no boxes."""
        labels = [
            ("BIHAR",   30,  30),
            ("ASSAM",   415, 30),
            ("KERALA",  30,  400),
            ("ODISHA",  535, 295),
        ]
        for name, x, y in labels:
            self.canvas.create_text(x, y, text=name,
                anchor="nw", fill="#3E5570",
                font=("Arial", 16, "bold"))

    def _draw_edges(self):
        import math
        for u, v, dist, passable in EDGES:
            if u not in POS or v not in POS: continue
            x1,y1 = POS[u]; x2,y2 = POS[v]
            col   = (C["edge_ok"]  if passable=="Yes"
                else C["edge_dmg"] if passable=="Partial"
                else C["edge_fld"])
            dash  = () if passable=="Yes" else (6,4) if passable=="Partial" else (3,5)
            width = 2 if passable=="Yes" else 2
            lid   = self.canvas.create_line(x1,y1,x2,y2,
                        fill=col, width=width, dash=dash)
            key   = tuple(sorted([u,v]))
            self.e_lines[key] = lid

            # Distance label: offset perpendicular to edge for readability
            mx, my = (x1+x2)/2, (y1+y2)/2
            dx, dy = x2-x1, y2-y1
            length = math.hypot(dx, dy) or 1
            # Perpendicular unit vector, offset 9px away from line
            ox = -dy / length * 9
            oy =  dx / length * 9
            self.canvas.create_text(mx+ox, my+oy, text=f"{dist}km",
                fill="#8899AA", font=("Arial", 6, "bold"))

    def _draw_nodes(self):
        for nid in POS:
            self._draw_single_node(nid)

    def _draw_single_node(self, nid):
        x, y  = POS[nid]
        is_v  = nid.startswith("V")
        r     = self.VR if is_v else self.CR
        sev   = VILLAGE_DATA[nid][3] if is_v else None
        ctype = CENTER_DATA[nid][2] if not is_v else None

        # Fill color
        if is_v:
            fill = (C["critical"] if sev=="Critical"
                else C["high"]    if sev=="High"
                else C["medium"])
        else:
            fill = (C["ctr_g"] if ctype=="Ground"
                else C["ctr_a"] if ctype=="Air"
                else C["ctr_w"])

        if is_v and nid in self.served:
            fill = C["served"]

        oval = self.canvas.create_oval(x-r,y-r,x+r,y+r,
                   fill=fill, outline=C["white"], width=1.5,
                   tags=(nid, "node"))
        self.ovals[nid] = oval

        # Icon inside circle
        icon = ("V" if is_v else
                "✈" if ctype=="Air" else
                "⚓" if ctype=="Water" else "G")
        self.canvas.create_text(x, y, text=icon,
            fill=C["white"], font=("Arial", 9, "bold"), tags=nid)

        # Label below — with dark background rectangle for readability
        if is_v:
            name = VILLAGE_DATA[nid][0]
        else:
            name = CENTER_DATA[nid][0].split()[0]

        # Draw background pill behind text so it's visible over edges/bg
        lbl_y = y + r + 13
        char_w = 4.8   # approx pixel width per char at font size 8
        half_w = len(name) * char_w + 4
        bg_rect = self.canvas.create_rectangle(
            x - half_w, lbl_y - 7,
            x + half_w, lbl_y + 7,
            fill="#0D1B2A", outline=C["border"], width=0.5, tags=nid)

        lbl = self.canvas.create_text(x, lbl_y, text=name,
                  fill=C["white"], font=("Arial", 8, "bold"), tags=nid)
        self.labels[nid] = lbl
        # Bind click
        self.canvas.tag_bind(nid, "<Button-1>",
            lambda e, n=nid: self._on_node_click(n))
        self.canvas.tag_bind(nid, "<Enter>",
            lambda e, n=nid: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(nid, "<Leave>",
            lambda e: self.canvas.config(cursor="crosshair"))

    def _draw_graph_legend(self, cw, ch):
        pass  # legend is in left panel

    # ── Queue and resource panels ──────────────────────────────────────────────
    def _refresh_queue(self, highlight_idx=None):
        self.queue_lb.delete(0, tk.END)
        sev_order = ["Critical","High","Medium","Low"]
        reqs = (sorted(self.pending_requests,
                        key=lambda r: SEV_RANK.get(r[3],99))
                if self.mode.get()=="Priority"
                else self.pending_requests)

        for i, (vid, rtype, qty, sev) in enumerate(reqs):
            name = VILLAGE_DATA[vid][0]
            tag  = "🔴" if sev=="Critical" else "🟠" if sev=="High" else "🟢"
            self.queue_lb.insert(tk.END,
                f"  {tag} {name:<18} {rtype:<10} ×{qty:.0f}")
            # Color code rows
            row_col = (C["critical"] if sev=="Critical"
                   else C["high"]    if sev=="High"
                   else C["medium"])
            self.queue_lb.itemconfig(i, fg=row_col)

        if highlight_idx is not None and highlight_idx < self.queue_lb.size():
            self.queue_lb.selection_set(highlight_idx)
            self.queue_lb.see(highlight_idx)

        done = len(REQUESTS) - len(self.pending_requests)
        tot  = len(REQUESTS)
        self.q_stats.set(f"  {done}/{tot} processed  |  "
                         f"{len(self.served)}/15 villages served")

    def _refresh_resources(self):
        for w in self.res_inner.winfo_children():
            w.destroy()

        active_ids = [c for c in CENTER_DATA if CENTER_DATA[c][8]=="Active"]
        BAR_W = 350

        for cid in active_ids:
            d    = CENTER_DATA[cid]
            name = d[0]; ctype = d[2]
            icon = "🚁" if ctype=="Air" else "🚤" if ctype=="Water" else "🚚"
            cur  = self.resources[cid]
            mx   = MAX_RESOURCES[cid]

            # Center header
            hdr = tk.Frame(self.res_inner, bg=C["card"])
            hdr.pack(fill="x", padx=6, pady=(6,1))
            col = (C["ctr_a"] if ctype=="Air" else
                   C["ctr_w"] if ctype=="Water" else C["ctr_g"])
            tk.Label(hdr, text=f"{icon} {cid}", fg=col, bg=C["card"],
                     font=("Arial", 8, "bold"), width=6).pack(side="left")
            tk.Label(hdr, text=name[:22], fg=C["text"], bg=C["card"],
                     font=("Arial", 8)).pack(side="left", padx=4)

            # Three resource bars
            res_names = ["Food", "Water", "Medicine"]
            res_cols  = ["#E67E22","#2E86C1","#1E8449"]
            for i, (rname, rcol) in enumerate(zip(res_names, res_cols)):
                row = tk.Frame(self.res_inner, bg=C["card"])
                row.pack(fill="x", padx=8, pady=1)
                tk.Label(row, text=f"{rname[:3]}", fg=C["dim"], bg=C["card"],
                         font=("Consolas", 7), width=4).pack(side="left")
                # Bar background
                bar_bg = tk.Frame(row, bg=C["border"], height=8, width=BAR_W)
                bar_bg.pack(side="left", padx=2)
                bar_bg.pack_propagate(False)
                pct = max(0, min(1, cur[i] / mx[i])) if mx[i] > 0 else 0
                bar_fill = tk.Frame(bar_bg, bg=rcol,
                                    height=8, width=int(BAR_W*pct))
                bar_fill.place(x=0, y=0)
                # Value label
                tk.Label(row, text=f"{cur[i]:,.0f}",
                         fg=rcol, bg=C["card"],
                         font=("Consolas", 7), width=8).pack(side="left")

            tk.Frame(self.res_inner, bg=C["border"], height=1).pack(
                fill="x", padx=6, pady=2)

    def _update_info(self, nid):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0","end")
        if nid is None:
            self.info_text.insert("end","  Click any node on the graph\n  to see its details here.")
        elif nid.startswith("V"):
            nm,st,pop,sev,fd,wt,med,evac = VILLAGE_DATA[nid]
            served = "✅ SERVED" if nid in self.served else "❌ Pending"
            evacs  = "⚠ YES" if evac else "No"
            self.info_text.insert("end",
                f"  VILLAGE: {nm}  [{nid}]\n"
                f"  State     : {st}\n"
                f"  Population: {pop:,}\n"
                f"  Severity  : {sev}\n"
                f"  Evacuation: {evacs}\n"
                f"  Status    : {served}\n"
                f"  ─────────────────────\n"
                f"  Demand → Food: {fd}kg\n"
                f"           Water: {wt}L\n"
                f"           Medicine: {med}u")
        else:
            nm,st,ct,mf,mw,mm,vol,veh,stat = CENTER_DATA[nid]
            cur = self.resources.get(nid,[mf,mw,mm])
            icon = "🚁" if ct=="Air" else "🚤" if ct=="Water" else "🚚"
            self.info_text.insert("end",
                f"  CENTER: {nm}\n"
                f"  ID: {nid}  |  {icon} {ct}\n"
                f"  State   : {st}\n"
                f"  Status  : {stat}\n"
                f"  Volunteers: {vol}  Vehicles: {veh}\n"
                f"  ─────────────────────\n"
                f"  Food    : {cur[0]:>8,.0f} / {mf:,} kg\n"
                f"  Water   : {cur[1]:>8,.0f} / {mw:,} L\n"
                f"  Medicine: {cur[2]:>8,.0f} / {mm:,} u")
        self.info_text.config(state="disabled")

    # ── Status ────────────────────────────────────────────────────────────────
    def _status(self, msg):
        self.status_var.set(f"  ▶  {msg}")

    # ── Click handling ────────────────────────────────────────────────────────
    def _on_canvas_click(self, event):
        """Handles click on empty canvas space."""
        if self.waiting_for_click:
            self._status("Please click directly on a village node (colored circle).")

    def _on_node_click(self, nid):
        """Handles click on a node."""
        # Clear previous selection
        self._clear_highlights()

        # Highlight selected node
        x, y = POS[nid]
        r = self.VR if nid.startswith("V") else self.CR
        glow = self.canvas.create_oval(x-r-5, y-r-5, x+r+5, y+r+5,
                   outline=C["gold"], width=3, fill="")
        self.hi_items.append(glow)

        self.selected_nid = nid
        self._update_info(nid)

        # If waiting for algorithm demo click
        if self.waiting_for_click == "dijkstra" and nid.startswith("V"):
            self.waiting_for_click = None
            self._run_dijkstra_demo(nid)
        elif self.waiting_for_click == "bfs" and nid.startswith("V"):
            self.waiting_for_click = None
            self._run_bfs_demo(nid)
        elif self.waiting_for_click:
            self._status("Please click a VILLAGE (red/orange/green circle), not a center.")

    def _arm_click(self, algo):
        self.waiting_for_click = algo
        name = "Dijkstra" if algo=="dijkstra" else "BFS"
        self._status(f"{name} armed — click any village node on the map...")

    # ── Algorithm demos ───────────────────────────────────────────────────────
    def _run_dijkstra_demo(self, source_vid):
        self._status(f"Dijkstra: Finding nearest center from {VILLAGE_DATA[source_vid][0]}...")
        active = [c for c in CENTER_DATA if CENTER_DATA[c][8]=="Active"]
        dist, parent = dijkstra(self.graph, source_vid, passable_only=True)

        best_cid = min(active, key=lambda c: dist.get(c, float("inf")))
        best_dist = dist.get(best_cid, float("inf"))

        if best_dist == float("inf"):
            self._status(f"No reachable center from {VILLAGE_DATA[source_vid][0]}!")
            return

        path = reconstruct(parent, best_cid)
        cname = CENTER_DATA[best_cid][0]

        self._animate_path(path, callback=lambda: (
            self._status(
                f"Dijkstra ✅  {VILLAGE_DATA[source_vid][0]} → {cname}  "
                f"| Distance: {best_dist:.1f} km  "
                f"| Route: {' → '.join(path)}"),
            self._update_info(source_vid)
        ))

    def _run_bfs_demo(self, source_vid):
        self._status(f"BFS: Finding nearest center from {VILLAGE_DATA[source_vid][0]}...")
        active = {c for c in CENTER_DATA if CENTER_DATA[c][8]=="Active"}
        cid, hops, path = bfs(self.graph, source_vid, active)

        if cid is None:
            self._status(f"No reachable center via BFS from {VILLAGE_DATA[source_vid][0]}!")
            return

        cname = CENTER_DATA[cid][0]
        self._animate_path(path, color=C["ctr_w"], callback=lambda: (
            self._status(
                f"BFS ✅  {VILLAGE_DATA[source_vid][0]} → {cname}  "
                f"| Hops: {hops}  | Route: {' → '.join(path)}")
        ))

    def _compare_all(self):
        self._clear_highlights()
        active = [c for c in CENTER_DATA if CENTER_DATA[c][8]=="Active"]
        cset   = set(active)
        lines  = [f"{'Village':<20} {'Dijkstra':<26} {'Dist':>7}  {'BFS':<26} {'Hops':>5}  {'Match'}"]
        lines  += ["─"*90]
        for vid, d in VILLAGE_DATA.items():
            name = d[0]
            dist_m, par = dijkstra(self.graph, vid)
            dc = min(active, key=lambda c: dist_m.get(c,float("inf")))
            dd = dist_m.get(dc,float("inf"))
            bc, bh, _  = bfs(self.graph, vid, cset)
            dn = CENTER_DATA[dc][0][:22] if dc else "None"
            bn = CENTER_DATA[bc][0][:22] if bc else "None"
            match = "✅" if dc==bc else "⚠️"
            lines.append(f"{name:<20} {dn:<26} {dd:>7.1f}  {bn:<26} {bh:>5}  {match}")

        self._show_popup("Dijkstra vs BFS — All Villages", "\n".join(lines))

    def _show_sorting(self):
        import time as _time
        RANK = {"Critical":1,"High":2,"Medium":3,"Low":4}
        villages = [(vid,d[0],d[3],d[1]) for vid,d in VILLAGE_DATA.items()]
        key = lambda v: RANK.get(v[2],99)

        results = []
        for name, fn in [("Bubble Sort",  self._bubble_sort),
                          ("Selection Sort",self._selection_sort),
                          ("Merge Sort",   self._merge_sort),
                          ("Heap Sort ✅", self._heap_sort)]:
            t0 = _time.perf_counter()
            sv, comps = fn(villages, key)
            ms = (_time.perf_counter()-t0)*1000
            top5 = ", ".join(v[1] for v in sv[:5])
            results.append(f"  {name:<18} {'O(N²)' if 'Bubble' in name or 'Select' in name else 'O(N logN)':<14}"
                          f" {comps:>8,}  {ms:>9.4f}ms   {top5}...")

        header = (f"  SORTING COMPARISON  |  N = {len(villages)} villages  "
                  f"|  Sorted by Flood Severity\n"
                  f"  {'─'*88}\n"
                  f"  {'Algorithm':<18} {'Complexity':<14} {'Comparisons':>10}  {'Time(ms)':>10}   First 5 Results\n"
                  f"  {'─'*88}")
        body   = "\n".join(results)
        footer = ("\n\n  💡  Heap Sort is what our Priority Queue uses internally.\n"
                  "      At N=10,000 villages: O(N²)≈100M comparisons vs O(NlogN)≈133K")
        self._show_popup("Sorting Algorithm Comparison", header+"\n"+body+footer)

    # ── Sorting implementations ───────────────────────────────────────────────
    def _bubble_sort(self, arr, key):
        a,n,c = arr[:],len(arr),0
        for i in range(n):
            for j in range(n-i-1):
                c+=1
                if key(a[j])>key(a[j+1]): a[j],a[j+1]=a[j+1],a[j]
        return a,c

    def _selection_sort(self, arr, key):
        a,n,c = arr[:],len(arr),0
        for i in range(n):
            m=i
            for j in range(i+1,n):
                c+=1
                if key(a[j])<key(a[m]): m=j
            a[i],a[m]=a[m],a[i]
        return a,c

    def _merge_sort(self, arr, key):
        c=[0]
        def merge(l,r):
            res,i,j=[],0,0
            while i<len(l) and j<len(r):
                c[0]+=1
                if key(l[i])<=key(r[j]): res.append(l[i]);i+=1
                else: res.append(r[j]);j+=1
            return res+l[i:]+r[j:]
        def sort(a):
            if len(a)<=1: return a
            m=len(a)//2
            return merge(sort(a[:m]),sort(a[m:]))
        return sort(arr[:]),c[0]

    def _heap_sort(self, arr, key):
        heap,c=[],[0]
        for idx,item in enumerate(arr):
            c[0]+=1; heapq.heappush(heap,(key(item),idx,item))
        return [heapq.heappop(heap)[2] for _ in range(len(heap))],c[0]

    # ── Animations ────────────────────────────────────────────────────────────
    def _clear_highlights(self):
        for item in self.hi_items:
            try: self.canvas.delete(item)
            except: pass
        self.hi_items.clear()
        # Restore all edge colors
        for (u,v), lid in self.e_lines.items():
            for eu,ev,ew,ep in EDGES:
                if tuple(sorted([eu,ev]))==(u,v):
                    col = (C["edge_ok"]  if ep=="Yes"
                      else C["edge_dmg"] if ep=="Partial"
                      else C["edge_fld"])
                    self.canvas.itemconfig(lid, fill=col, width=2)
                    break
        # Restore node colors
        for nid in POS:
            if nid in self.ovals:
                self._restore_node_color(nid)

    def _restore_node_color(self, nid):
        is_v  = nid.startswith("V")
        sev   = VILLAGE_DATA[nid][3] if is_v else None
        ctype = CENTER_DATA[nid][2]  if not is_v else None
        if is_v:
            fill = (C["served"]   if nid in self.served
               else C["critical"] if sev=="Critical"
               else C["high"]     if sev=="High"
               else C["medium"])
        else:
            fill = (C["ctr_g"] if ctype=="Ground"
               else C["ctr_a"] if ctype=="Air"
               else C["ctr_w"])
        self.canvas.itemconfig(self.ovals[nid], fill=fill, outline=C["white"], width=1.5)

    def _animate_path(self, path, step=0, color=None, callback=None):
        if color is None: color = C["gold"]
        if step >= len(path):
            if callback: callback()
            return

        nid = path[step]
        # Highlight node
        self.canvas.itemconfig(self.ovals[nid],
                               fill=color, outline=C["white"], width=3)
        # Highlight edge from prev node
        if step > 0:
            key = tuple(sorted([path[step-1], nid]))
            if key in self.e_lines:
                lid = self.e_lines[key]
                self.canvas.itemconfig(lid, fill=color, width=4)
                self.hi_items.append(lid)

        self.root.after(self.speed_ms,
            lambda: self._animate_path(path, step+1, color, callback))

    def _flash_node(self, nid, color=None, flashes=4, count=0, after_cb=None):
        if color is None: color=C["gold"]
        if count >= flashes*2:
            self._restore_node_color(nid)
            if after_cb: after_cb()
            return
        if count%2==0:
            self.canvas.itemconfig(self.ovals[nid], fill=color, width=3)
        else:
            self._restore_node_color(nid)
        self.root.after(150, lambda: self._flash_node(
            nid, color, flashes, count+1, after_cb))

    # ── Simulation ────────────────────────────────────────────────────────────
    def _start_sim(self, mode):
        if self.sim_on:
            self._status("Simulation already running — please Reset first."); return
        self.sim_on = True
        self.mode.set(mode)
        self._status(f"Starting {mode} simulation — {len(self.pending_requests)} requests...")
        self._refresh_queue()

        # Build ordered request list
        if mode == "Priority":
            reqs = sorted(self.pending_requests,
                          key=lambda r: SEV_RANK.get(r[3],99))
        else:
            reqs = list(self.pending_requests)

        self._sim_step(reqs, 0)

    def _sim_step(self, reqs, idx):
        if not self.sim_on or idx >= len(reqs):
            self._sim_done()
            return

        req = reqs[idx]
        vid, rtype, qty, sev = req

        # Highlight in queue
        self._refresh_queue(highlight_idx=idx)

        # Flash village
        vname = VILLAGE_DATA[vid][0]
        self._status(f"[{idx+1}/{len(reqs)}] Processing: {vname} → {rtype} ×{qty:.0f}")
        self._clear_highlights()

        active = [c for c in CENTER_DATA if CENTER_DATA[c][8]=="Active"]
        dist_m, parent = dijkstra(self.graph, vid, passable_only=True)

        # Find nearest center that can fulfill
        rmap = {"Food":0,"Water":1,"Medicine":2}
        ri   = rmap.get(rtype, 0)

        chosen = None
        for c in sorted(active, key=lambda c: dist_m.get(c,float("inf"))):
            if dist_m.get(c,float("inf")) < float("inf"):
                if self.resources[c][ri] >= qty:
                    chosen = c; break

        def do_dispatch():
            if chosen:
                path  = reconstruct(parent, chosen)
                cname = CENTER_DATA[chosen][0]
                ctype = CENTER_DATA[chosen][2]
                icon  = "🚁" if ctype=="Air" else "🚤" if ctype=="Water" else "🚚"
                d     = dist_m.get(chosen,0)

                def after_path():
                    # Deduct resource
                    self.resources[chosen][ri] -= qty
                    self.served.add(vid)
                    # Mark served on canvas
                    self._restore_node_color(vid)
                    # Log
                    self.delivery_log.append((vid,chosen,rtype,qty))
                    self._status(f"  {icon} ✅ Dispatched → {vname} from {cname}  "
                                 f"({d:.0f} km)  |  "
                                 f"Remaining {rtype}: {self.resources[chosen][ri]:,.0f}")
                    self._refresh_resources()
                    self._refresh_queue()
                    # Next request
                    self.root.after(self.speed_ms,
                        lambda: self._sim_step(reqs, idx+1))

                self._animate_path(path, callback=after_path)
            else:
                self._status(f"  ⚠️  No center could fulfill {rtype} ×{qty:.0f} for {vname}. Skipping.")
                self.root.after(self.speed_ms * 2,
                    lambda: self._sim_step(reqs, idx+1))

        self._flash_node(vid, C["gold"], flashes=3, after_cb=do_dispatch)

    def _sim_done(self):
        self.sim_on = False
        ok   = len(self.served)
        tot  = len(VILLAGE_DATA)
        self._status(
            f"✅ Simulation complete — {len(self.delivery_log)} dispatched  |  "
            f"{ok}/{tot} villages served  |  Press Reset to run again.")
        self._refresh_queue()
        self._refresh_resources()
        self._show_final_report()

    def _show_final_report(self):
        lines = ["  DELIVERY SUMMARY\n  " + "─"*68]
        for vid, cid, rtype, qty in self.delivery_log:
            vn = VILLAGE_DATA[vid][0]
            cn = CENTER_DATA[cid][0]
            lines.append(f"  ✅  {vn:<20} ← {cn:<26} | {rtype:<10} ×{qty:.0f}")
        lines += [f"\n  Villages served: {len(self.served)}/{len(VILLAGE_DATA)}",
                  f"  Deliveries made: {len(self.delivery_log)}"]
        self._show_popup("Simulation Report", "\n".join(lines))

    def _reset(self):
        self.sim_on = False
        self._reset_data()
        self._clear_highlights()
        self._draw_graph()
        self._refresh_queue()
        self._refresh_resources()
        self._update_info(None)
        self._status("Reset complete — ready for new simulation.")

    # ── Popup window ─────────────────────────────────────────────────────────
    def _show_popup(self, title, content):
        pop = tk.Toplevel(self.root)
        pop.title(title)
        pop.configure(bg=C["bg"])
        pop.geometry("900x520")
        pop.resizable(True, True)

        tk.Label(pop, text=title, bg=C["critical"], fg=C["white"],
                 font=("Arial", 12, "bold")).pack(fill="x", pady=0)

        frame = tk.Frame(pop, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=4, pady=4)

        txt = tk.Text(frame, bg=C["card"], fg=C["text"],
                      font=("Consolas", 9), bd=0,
                      highlightthickness=0, wrap="none")
        sb_y = tk.Scrollbar(frame, command=txt.yview)
        sb_x = tk.Scrollbar(frame, command=txt.xview, orient="horizontal")
        txt.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        txt.pack(fill="both", expand=True)
        txt.insert("end", content)
        txt.config(state="disabled")

        tk.Button(pop, text="Close", command=pop.destroy,
                  bg=C["btn_rst"], fg=C["white"], font=("Arial", 9, "bold"),
                  relief="flat", cursor="hand2", pady=5).pack(
                  fill="x", padx=8, pady=6)

    # ── Canvas resize handler ─────────────────────────────────────────────────
    def on_resize(self, event=None):
        self.root.after(50, self._draw_graph)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    app  = FloodReliefDashboard(root)
    root.after(100, app._draw_graph)   # redraw after window fully renders
    root.mainloop()

if __name__ == "__main__":
    main()
