import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random
import json
import datetime

# ==========================================
# CONFIGURACIÓN Y TEMA (Professional Dark Mode)
# ==========================================
THEME = {
    "bg_dark": "#1e272e",       # Sidebar (Gris oscuro elegante)
    "bg_light": "#f5f6fa",      # Área de trabajo (Blanco humo)
    "accent": "#575fcf",        # Color principal (Azul/Morado vibrante)
    "success": "#0be881",       # Verde éxito
    "warning": "#ffdd59",       # Amarillo alerta
    "danger": "#ff3f34",        # Rojo peligro
    "text_sidebar": "#d2dae2",  # Texto claro para sidebar
    "console_bg": "#000000"     # Fondo consola
}

# ==========================================
# MOTOR LÓGICO (BACKEND)
# ==========================================
class GraphEngine:
    def __init__(self):
        self.G = nx.Graph()

    def agregar_arista(self, u, v, peso):
        # Evitar duplicados visuales si es posible, o actualizar peso
        self.G.add_edge(u, v, weight=peso)
        return f"Conexión: [{u}] --({peso})--> [{v}]"

    def limpiar_todo(self):
        self.G.clear()

    # --- Algoritmos ---
    def dijkstra(self, inicio, fin):
        try:
            path = nx.dijkstra_path(self.G, source=inicio, target=fin, weight='weight')
            cost = nx.dijkstra_path_length(self.G, source=inicio, target=fin, weight='weight')
            return path, cost
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None, float('inf')

    def mst_prim(self):
        if not self.G.nodes: return []
        T = nx.minimum_spanning_tree(self.G, algorithm='prim')
        return list(T.edges(data=True))

    def recorrido_bfs(self, inicio):
        if inicio not in self.G: return []
        return list(nx.bfs_edges(self.G, source=inicio))

    def recorrido_dfs(self, inicio):
        if inicio not in self.G: return []
        return list(nx.dfs_edges(self.G, source=inicio))

    def coloreado_greedy(self):
        # Estrategia de coloración para asignación de recursos
        return nx.coloring.greedy_color(self.G, strategy='largest_first')

    # --- Métricas Avanzadas ---
    def metricas_generales(self):
        if not self.G.nodes: return "Grafo vacío."
        
        info = (
            f"• Total Nodos: {self.G.number_of_nodes()}\n"
            f"• Total Aristas: {self.G.number_of_edges()}\n"
            f"• Densidad: {nx.density(self.G):.4f}\n"
            f"• Conectividad: {'Conexo' if nx.is_connected(self.G) else 'Disconexo'}\n"
            f"• Componentes: {nx.number_connected_components(self.G)}\n"
        )
        # Intento de verificar Euleriano (solo funciona si es conexo)
        if nx.is_connected(self.G):
            euler = "Sí" if nx.is_eulerian(self.G) else "No"
            info += f"• Es Euleriano: {euler}"
        return info

    def obtener_matriz_texto(self):
        if not self.G.nodes: return ""
        # Ordenar nodos para que la matriz se vea ordenada (8, 9, 10...)
        nodes = sorted(list(self.G.nodes), key=lambda x: int(x) if x.isdigit() else x)
        mat = nx.adjacency_matrix(self.G, nodelist=nodes).todense()
        
        header = "      " + "  ".join([f"{str(n):>4}" for n in nodes])
        rows = []
        for i, r in enumerate(mat):
            val_str = "  ".join([f"{x:>4}" for x in r.tolist()[0]])
            rows.append(f"{str(nodes[i]):>4} | {val_str}")
        return header + "\n" + ("-" * len(header)) + "\n" + "\n".join(rows)

# ==========================================
# INTERFAZ GRÁFICA (FRONTEND)
# ==========================================
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GraphCore Studio - Entorno de Análisis de Algoritmos")
        self.geometry("1280x800")
        self.state('zoomed') # Pantalla completa en Windows
        
        self.engine = GraphEngine()
        self._setup_ui()
        self.show_splash() # Pantalla de carga inicial

    def _setup_ui(self):
        # Estilos visuales
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=THEME["bg_light"])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"))

        # --- Layout Principal ---
        self.sidebar = tk.Frame(self, bg=THEME["bg_dark"], width=300)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False) # Forzar ancho fijo

        self.main_area = tk.Frame(self, bg=THEME["bg_light"])
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Contenido Sidebar
        self._construir_sidebar()

        # Contenido Principal (Pestañas)
        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # TAB 1: Visualización
        self.tab_viz = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_viz, text=" 🕸️ Grafo Interactivo ")
        self._setup_canvas()

        # TAB 2: Datos y Matrices
        self.tab_data = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_data, text=" 📊 Métricas y Matriz ")
        self._setup_analisis_tab()

        # Consola Inferior
        self._setup_consola()

    def _construir_sidebar(self):
        # --- HEADER (TU NOMBRE AQUÍ) ---
        tk.Label(self.sidebar, text="GraphCore\nStudio", font=("Montserrat", 24, "bold"), bg=THEME["bg_dark"], fg=THEME["accent"]).pack(pady=(30, 5))
        
        # AQUÍ ESTÁ EL CAMBIO SOLICITADO:
        tk.Label(self.sidebar, text="Author: James Lucas Moreto", font=("Segoe UI", 11, "italic"), bg=THEME["bg_dark"], fg="#bdc3c7").pack(pady=(0, 20))

        # --- SECCIÓN 1: Construcción ---
        self._sep("CONSTRUCCIÓN")
        f_add = tk.Frame(self.sidebar, bg=THEME["bg_dark"])
        f_add.pack(fill=tk.X, padx=15)
        
        self.e_n1 = self._entry(f_add, "Nodo A:", 0)
        self.e_n2 = self._entry(f_add, "Nodo B:", 1)
        self.e_w = self._entry(f_add, "Peso:", 2)
        
        tk.Button(self.sidebar, text="➕ Agregar Arista", bg=THEME["accent"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=6, command=self.accion_agregar).pack(fill=tk.X, padx=20, pady=10)
        
        # Botones rápidos
        f_tools = tk.Frame(self.sidebar, bg=THEME["bg_dark"])
        f_tools.pack(fill=tk.X, padx=15)
        tk.Button(f_tools, text="🎲 Random", bg="#636e72", fg="white", bd=0, width=13, command=self.accion_random).pack(side=tk.LEFT, padx=2)
        tk.Button(f_tools, text="🗑 Limpiar", bg=THEME["danger"], fg="white", bd=0, width=13, command=self.accion_limpiar).pack(side=tk.RIGHT, padx=2)

        # --- SECCIÓN 2: Algoritmos ---
        self._sep("ANÁLISIS ALGORÍTMICO")
        f_algo = tk.Frame(self.sidebar, bg=THEME["bg_dark"])
        f_algo.pack(fill=tk.X, padx=15)
        self.e_start = self._entry(f_algo, "Inicio:", 0)
        self.e_end = self._entry(f_algo, "Fin:", 1)

        # Lista de algoritmos
        algos = [
            ("⚡ Ruta Corta (Dijkstra)", self.accion_dijkstra, THEME["success"]),
            ("🌲 Árbol Mínimo (Prim)", self.accion_prim, "#e67e22"),
            ("🔍 Recorrido BFS", self.accion_bfs, "#3498db"),
            ("🕵️ Recorrido DFS", self.accion_dfs, "#9b59b6"),
            ("🎨 Coloreado (Greedy)", self.accion_colorear, "#e84393")
        ]
        
        for txt, cmd, col in algos:
            tk.Button(self.sidebar, text=txt, bg=col, fg="white", bd=0, pady=5, anchor="w", padx=15, command=cmd).pack(fill=tk.X, padx=20, pady=2)

        # --- SECCIÓN 3: Archivos ---
        self._sep("PROYECTO")
        f_file = tk.Frame(self.sidebar, bg=THEME["bg_dark"])
        f_file.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(f_file, text="💾 Guardar", bg="#2f3542", fg="white", bd=0, width=12, command=self.accion_guardar).pack(side=tk.LEFT, padx=1)
        tk.Button(f_file, text="📂 Cargar", bg="#2f3542", fg="white", bd=0, width=12, command=self.accion_cargar).pack(side=tk.RIGHT, padx=1)

    def _sep(self, txt):
        tk.Label(self.sidebar, text=txt, bg=THEME["bg_dark"], fg="#7f8c8d", font=("Arial", 8, "bold")).pack(anchor="w", padx=20, pady=(20, 5))

    def _entry(self, parent, lbl, r):
        tk.Label(parent, text=lbl, bg=THEME["bg_dark"], fg="white").grid(row=r, column=0, sticky="w", pady=2)
        e = tk.Entry(parent, bg="#2d3436", fg="white", bd=0, insertbackground="white", width=16)
        e.grid(row=r, column=1, pady=2, padx=5)
        return e

    def _setup_canvas(self):
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_viz)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Toolbar flotante
        tbar = tk.Frame(self.tab_viz, bg="white")
        tbar.place(relx=0.98, rely=0.02, anchor="ne")
        tk.Button(tbar, text="📷 Exportar PNG", command=self.accion_foto, bg="#b2bec3", bd=0, padx=10).pack(side=tk.RIGHT)

    def _setup_analisis_tab(self):
        paned = tk.PanedWindow(self.tab_data, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel Izquierdo: Métricas
        fr_met = tk.LabelFrame(paned, text="Resumen Estadístico", bg="white", font=("Arial", 11, "bold"))
        paned.add(fr_met, width=350)
        self.lbl_stats = tk.Label(fr_met, text="...", justify=tk.LEFT, bg="white", font=("Consolas", 11), padx=10, pady=10)
        self.lbl_stats.pack(fill=tk.BOTH, expand=True)
        tk.Button(fr_met, text="🔄 Refrescar Datos", command=self.actualizar_datos, bg=THEME["accent"], fg="white").pack(fill=tk.X, padx=10, pady=10)
        
        # Panel Derecho: Matriz
        fr_mat = tk.LabelFrame(paned, text="Matriz de Adyacencia", bg="white", font=("Arial", 11, "bold"))
        paned.add(fr_mat)
        self.txt_mat = tk.Text(fr_mat, font=("Courier New", 10), padx=10, pady=10)
        self.txt_mat.pack(fill=tk.BOTH, expand=True)

    def _setup_consola(self):
        f_con = tk.Frame(self.main_area, bg="black", height=130)
        f_con.pack(side=tk.BOTTOM, fill=tk.X)
        f_con.pack_propagate(False)
        tk.Label(f_con, text=" SYSTEM TERMINAL >", bg="black", fg=THEME["success"], font=("Consolas", 10, "bold")).pack(anchor="w", padx=5)
        self.log_txt = tk.Text(f_con, bg="#0d0d0d", fg="#ecf0f1", font=("Consolas", 9), bd=0, state="disabled")
        self.log_txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

    def log(self, msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_txt.config(state="normal")
        self.log_txt.insert(tk.END, f"[{t}] {msg}\n")
        self.log_txt.see(tk.END)
        self.log_txt.config(state="disabled")

    # ==========================================
    # LÓGICA DE DIBUJO Y BOTONES
    # ==========================================
    def refresh_graph(self, path_edges=None, path_nodes=None, node_colors=None):
        self.ax.clear()
        
        if self.engine.G.number_of_nodes() == 0:
            self.ax.text(0.5, 0.5, "Grafo vacío. Añade nodos desde el panel izquierdo.", ha='center', color='gray')
            self.canvas.draw()
            return

        pos = nx.spring_layout(self.engine.G, seed=42)
        
        # Definir colores de nodos
        colors = [THEME["accent"]] * len(self.engine.G.nodes)
        if node_colors:
            palette = ['#e17055', '#00b894', '#0984e3', '#6c5ce7', '#fdcb6e', '#d63031']
            colors = []
            for n in self.engine.G.nodes:
                c_idx = node_colors.get(n, 0)
                colors.append(palette[c_idx % len(palette)])

        # Dibujar grafo base
        nx.draw_networkx_nodes(self.engine.G, pos, ax=self.ax, node_size=800, node_color=colors, edgecolors="white")
        nx.draw_networkx_edges(self.engine.G, pos, ax=self.ax, edge_color="#bdc3c7", width=2)
        nx.draw_networkx_labels(self.engine.G, pos, ax=self.ax, font_color="white", font_weight="bold")
        nx.draw_networkx_edge_labels(self.engine.G, pos, edge_labels=nx.get_edge_attributes(self.engine.G, "weight"), ax=self.ax)

        # Resaltar caminos
        if path_edges:
            nx.draw_networkx_edges(self.engine.G, pos, edgelist=path_edges, ax=self.ax, edge_color=THEME["warning"], width=4)
        if path_nodes and not node_colors:
            nx.draw_networkx_nodes(self.engine.G, pos, nodelist=path_nodes, ax=self.ax, node_color=THEME["warning"], node_size=850)

        self.ax.axis("off")
        self.canvas.draw()
        self.actualizar_datos()

    def actualizar_datos(self):
        self.lbl_stats.config(text=self.engine.metricas_generales())
        self.txt_mat.delete(1.0, tk.END)
        self.txt_mat.insert(tk.END, self.engine.obtener_matriz_texto())

    # --- Acciones ---
    def accion_agregar(self):
        try:
            u, v = self.e_n1.get(), self.e_n2.get()
            w = int(self.e_w.get())
            if u and v:
                msg = self.engine.agregar_arista(u, v, w)
                self.log(msg)
                self.refresh_graph()
                self.e_n1.delete(0, tk.END); self.e_n2.delete(0, tk.END); self.e_w.delete(0, tk.END)
                self.e_n1.focus()
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un número entero.")

    def accion_random(self):
        nodos = range(8, 17) # Personalizado según tu requerimiento
        u, v = str(random.choice(nodos)), str(random.choice(nodos))
        while u == v: v = str(random.choice(nodos))
        w = random.randint(1, 20)
        self.engine.agregar_arista(u, v, w)
        self.log(f"Aleatorio: {u}-{v} ({w})")
        self.refresh_graph()

    def accion_limpiar(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo?"):
            self.engine.limpiar_todo()
            self.refresh_graph()
            self.log("Sistema reiniciado.")

    def accion_dijkstra(self):
        s, e = self.e_start.get(), self.e_end.get()
        path, cost = self.engine.dijkstra(s, e)
        if path:
            self.log(f"Dijkstra: {path} | Costo: {cost}")
            edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            self.refresh_graph(path_edges=edges, path_nodes=path)
            messagebox.showinfo("Dijkstra", f"Camino: {' -> '.join(path)}\nCosto: {cost}")
        else:
            messagebox.showerror("Error", "No existe camino.")

    def accion_prim(self):
        edges = self.engine.mst_prim()
        if edges:
            simple = [(u, v) for u, v, d in edges]
            cost = sum(d['weight'] for u,v,d in edges)
            self.log(f"Prim MST Costo: {cost}")
            self.refresh_graph(path_edges=simple)
            messagebox.showinfo("Prim", f"Costo Total MST: {cost}")
        else:
            messagebox.showwarning("Aviso", "Grafo vacío.")

    def accion_bfs(self):
        s = self.e_start.get()
        edges = self.engine.recorrido_bfs(s)
        if edges:
            self.refresh_graph(path_edges=edges)
            self.log(f"BFS ejecutado desde {s}")
        else: messagebox.showerror("Error", "Nodo inicio inválido")

    def accion_dfs(self):
        s = self.e_start.get()
        edges = self.engine.recorrido_dfs(s)
        if edges:
            self.refresh_graph(path_edges=edges)
            self.log(f"DFS ejecutado desde {s}")
        else: messagebox.showerror("Error", "Nodo inicio inválido")

    def accion_colorear(self):
        if self.engine.G.number_of_nodes() > 0:
            cols = self.engine.coloreado_greedy()
            self.refresh_graph(node_colors=cols)
            self.log("Coloreado Greedy aplicado.")
        else: messagebox.showwarning("Aviso", "Sin nodos.")

    def accion_foto(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if f:
            self.fig.savefig(f)
            self.log(f"Imagen guardada: {f}")

    def accion_guardar(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            data = nx.node_link_data(self.engine.G)
            with open(f, 'w') as file: json.dump(data, file)
            self.log("Guardado exitoso.")

    def accion_cargar(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'r') as file: data = json.load(file)
            self.engine.G = nx.node_link_graph(data)
            self.refresh_graph()
            self.log("Carga exitosa.")

    def show_splash(self):
        splash = tk.Toplevel(self)
        splash.overrideredirect(True)
        splash.config(bg="#1e272e")
        
        w, h = 600, 350
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        splash.geometry(f"{w}x{h}+{x}+{y}")
        
        tk.Label(splash, text="GRAPHCORE STUDIO", font=("Montserrat", 30, "bold"), bg="#1e272e", fg="white").pack(pady=(70, 10))
        # NOMBRE EN PANTALLA DE CARGA
        tk.Label(splash, text="James Lucas Moreto", font=("Arial", 16), bg="#1e272e", fg=THEME["accent"]).pack()
        tk.Label(splash, text="Ingeniería de Sistemas de Información", font=("Arial", 10), bg="#1e272e", fg="gray").pack(pady=5)
        
        pb = ttk.Progressbar(splash, mode="determinate", length=400)
        pb.pack(pady=40)
        
        def step(v=0):
            if v <= 100:
                pb['value'] = v
                splash.after(25, step, v+2)
            else:
                splash.destroy()
                self.deiconify()
        
        self.withdraw()
        step()

if __name__ == "__main__":
    app = Application()
    app.mainloop()