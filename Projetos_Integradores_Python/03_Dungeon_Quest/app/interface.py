"""Interface gráfica medieval escura para o RPG Dungeon Quest."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from app.armazenamento import carregar_aventura, guardar_aventura
from app.dados import COLUNAS_MASMORRA, LINHAS_MASMORRA
from app.logica import (
    calcular_ataque_total,
    calcular_defesa_total,
    criar_nova_aventura,
    defender_em_combate,
    executar_ataque_combate,
    fugir_combate,
    mover_heroi,
    obter_sala,
    usar_ou_equipar_item,
)

COR_FUNDO = "#120D1A"
COR_PAINEL = "#1E162B"
COR_CARD = "#2B203E"
COR_ROXO = "#9B59B6"
COR_TOCHA = "#F39C12"
COR_TEXTO = "#F4ECF7"
COR_SEC = "#BFA9CC"


class AplicacaoDungeonQuest:
    """Controlador da janela principal do jogo Dungeon Quest."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Dungeon Quest — Profundezas Púrpuras")
        self.raiz.geometry("1150x740")
        self.raiz.minsize(1000, 660)
        self.raiz.configure(bg=COR_FUNDO)

        self.estado = criar_nova_aventura("Cavaleiro")

        self._configurar_estilos()
        self._construir_interface()
        self._configurar_teclas()
        self.atualizar_interface()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=COR_FUNDO)
        estilo.configure("Painel.TFrame", background=COR_PAINEL)
        estilo.configure("Card.TFrame", background=COR_CARD)
        estilo.configure(
            "Titulo.TLabel",
            background=COR_PAINEL,
            foreground=COR_TOCHA,
            font=("Georgia", 14, "bold"),
        )
        estilo.configure(
            "Sub.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
        )
        estilo.configure(
            "Txt.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Sec.TLabel",
            background=COR_PAINEL,
            foreground=COR_SEC,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Arcano.TButton",
            background=COR_ROXO,
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Arcano.TButton", background=[("active", "#B06AB3")])
        estilo.configure(
            "Tocha.TButton",
            background=COR_TOCHA,
            foreground="#1A1208",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Tocha.TButton", background=[("active", "#F5B041")])
        estilo.configure(
            "Nav.TButton",
            background="#3A2B54",
            foreground=COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
            padding=5,
        )
        estilo.map("Nav.TButton", background=[("active", "#4E3A70")])
        estilo.configure(
            "HP.Horizontal.TProgressbar",
            troughcolor="#0E0A14",
            background="#E74C3C",
            thickness=15,
        )
        estilo.configure(
            "XP.Horizontal.TProgressbar",
            troughcolor="#0E0A14",
            background=COR_ROXO,
            thickness=12,
        )

    def _construir_interface(self) -> None:
        topo = ttk.Frame(self.raiz, style="Painel.TFrame", padding=(14, 10))
        topo.pack(fill=tk.X, padx=10, pady=(10, 6))

        ttk.Label(topo, text="⚔ Dungeon Quest", style="Titulo.TLabel").pack(side=tk.LEFT)
        self.lbl_resumo_topo = ttk.Label(topo, text="", style="Txt.TLabel")
        self.lbl_resumo_topo.pack(side=tk.LEFT, padx=20)

        btns_topo = ttk.Frame(topo, style="Painel.TFrame")
        btns_topo.pack(side=tk.RIGHT)
        ttk.Button(btns_topo, text="Nova Aventura", style="Nav.TButton", command=self._acao_nova).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns_topo, text="Guardar", style="Nav.TButton", command=self._acao_guardar).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns_topo, text="Carregar", style="Nav.TButton", command=self._acao_carregar).pack(
            side=tk.LEFT, padx=4
        )

        corpo = ttk.Frame(self.raiz)
        corpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Coluna esquerda: Masmorra + Navegação + Registo
        col_esq = ttk.Frame(corpo, style="Painel.TFrame", padding=12)
        col_esq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ttk.Label(
            col_esq,
            text="Mapa da Masmorra (Setas do teclado ou botões para explorar)",
            style="Sub.TLabel",
        ).pack(anchor=tk.W, pady=(0, 6))

        self.canvas_masmorra = tk.Canvas(
            col_esq,
            height=380,
            bg="#0B0811",
            highlightthickness=1,
            highlightbackground=COR_ROXO,
        )
        self.canvas_masmorra.pack(fill=tk.BOTH, expand=True)
        self.canvas_masmorra.bind("<Configure>", lambda _e: self._desenhar_masmorra())

        # Controles de movimento e combate
        painel_acoes = ttk.Frame(col_esq, style="Card.TFrame", padding=10)
        painel_acoes.pack(fill=tk.X, pady=8)

        frame_nav = ttk.Frame(painel_acoes, style="Card.TFrame")
        frame_nav.pack(side=tk.LEFT, padx=(0, 20))
        self.btn_norte = ttk.Button(
            frame_nav, text="▲ Norte", style="Nav.TButton", command=lambda: self._acao_mover(-1, 0)
        )
        self.btn_norte.grid(row=0, column=1, padx=2, pady=2)
        self.btn_oeste = ttk.Button(
            frame_nav, text="◀ Oeste", style="Nav.TButton", command=lambda: self._acao_mover(0, -1)
        )
        self.btn_oeste.grid(row=1, column=0, padx=2, pady=2)
        self.btn_este = ttk.Button(
            frame_nav, text="Este ▶", style="Nav.TButton", command=lambda: self._acao_mover(0, 1)
        )
        self.btn_este.grid(row=1, column=2, padx=2, pady=2)
        self.btn_sul = ttk.Button(
            frame_nav, text="▼ Sul", style="Nav.TButton", command=lambda: self._acao_mover(1, 0)
        )
        self.btn_sul.grid(row=2, column=1, padx=2, pady=2)

        frame_combate = ttk.Frame(painel_acoes, style="Card.TFrame")
        frame_combate.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lbl_combate_info = ttk.Label(
            frame_combate,
            text="Sem inimigos ativos na sala.",
            background=COR_CARD,
            foreground=COR_TOCHA,
            font=("Segoe UI", 10, "bold"),
            wraplength=360,
        )
        self.lbl_combate_info.pack(anchor=tk.W, pady=(0, 8))

        linha_c = ttk.Frame(frame_combate, style="Card.TFrame")
        linha_c.pack(anchor=tk.W)
        self.btn_atacar = ttk.Button(
            linha_c, text="⚔ Atacar", style="Tocha.TButton", command=self._acao_atacar
        )
        self.btn_atacar.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_defender = ttk.Button(
            linha_c, text="🛡 Defender", style="Arcano.TButton", command=self._acao_defender
        )
        self.btn_defender.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_fugir = ttk.Button(
            linha_c, text="🏃 Fugir", style="Nav.TButton", command=self._acao_fugir
        )
        self.btn_fugir.pack(side=tk.LEFT)

        ttk.Label(col_esq, text="Crónicas da Masmorra", style="Sub.TLabel").pack(anchor=tk.W)
        self.txt_registo = tk.Text(
            col_esq,
            height=7,
            bg="#0B0811",
            fg=COR_TEXTO,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=8,
            pady=6,
        )
        self.txt_registo.pack(fill=tk.X, pady=(4, 0))

        # Coluna direita: Atributos do Herói + Inventário
        col_dir = ttk.Frame(corpo, style="Painel.TFrame", padding=12, width=410)
        col_dir.pack(side=tk.RIGHT, fill=tk.BOTH)
        col_dir.pack_propagate(False)

        self.lbl_heroi_nome = ttk.Label(col_dir, text="", style="Titulo.TLabel")
        self.lbl_heroi_nome.pack(anchor=tk.W)

        frame_hp = ttk.Frame(col_dir, style="Painel.TFrame")
        frame_hp.pack(fill=tk.X, pady=(8, 4))
        self.lbl_hp = ttk.Label(frame_hp, text="HP", style="Txt.TLabel")
        self.lbl_hp.pack(anchor=tk.W)
        self.barra_hp = ttk.Progressbar(frame_hp, style="HP.Horizontal.TProgressbar")
        self.barra_hp.pack(fill=tk.X, pady=2)

        self.lbl_xp = ttk.Label(frame_hp, text="XP", style="Sec.TLabel")
        self.lbl_xp.pack(anchor=tk.W, pady=(4, 0))
        self.barra_xp = ttk.Progressbar(frame_hp, style="XP.Horizontal.TProgressbar")
        self.barra_xp.pack(fill=tk.X, pady=2)

        self.lbl_atributos = ttk.Label(
            col_dir, text="", style="Txt.TLabel", justify=tk.LEFT
        )
        self.lbl_atributos.pack(anchor=tk.W, pady=8)

        ttk.Separator(col_dir).pack(fill=tk.X, pady=6)
        ttk.Label(col_dir, text="Inventário do Aventureiro", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(0, 6)
        )

        self.lista_inv = tk.Listbox(
            col_dir,
            bg="#120D1A",
            fg=COR_TEXTO,
            selectbackground=COR_ROXO,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#3A2B54",
        )
        self.lista_inv.pack(fill=tk.BOTH, expand=True)
        self.lista_inv.bind("<<ListboxSelect>>", self._ao_selecionar_item)

        self.lbl_item_desc = ttk.Label(
            col_dir, text="Seleciona um item para ver a descrição.", style="Sec.TLabel", wraplength=380
        )
        self.lbl_item_desc.pack(anchor=tk.W, pady=6)

        self.btn_usar_item = ttk.Button(
            col_dir,
            text="Usar / Equipar Item Selecionado",
            style="Arcano.TButton",
            command=self._acao_usar_item,
        )
        self.btn_usar_item.pack(fill=tk.X)

    def _configurar_teclas(self) -> None:
        self.raiz.bind("<Up>", lambda _e: self._acao_mover(-1, 0))
        self.raiz.bind("<Down>", lambda _e: self._acao_mover(1, 0))
        self.raiz.bind("<Left>", lambda _e: self._acao_mover(0, -1))
        self.raiz.bind("<Right>", lambda _e: self._acao_mover(0, 1))

    def _desenhar_masmorra(self) -> None:
        self.canvas_masmorra.delete("all")
        larg = max(320, self.canvas_masmorra.winfo_width())
        alt = max(280, self.canvas_masmorra.winfo_height())
        margem = 14
        espaco = 6
        lc = (larg - 2 * margem - (COLUNAS_MASMORRA - 1) * espaco) / COLUNAS_MASMORRA
        ac = (alt - 2 * margem - (LINHAS_MASMORRA - 1) * espaco) / LINHAS_MASMORRA

        pos_lin, pos_col = self.estado["posicao"]

        for sala in self.estado["salas"]:
            x0 = margem + sala["coluna"] * (lc + espaco)
            y0 = margem + sala["linha"] * (ac + espaco)
            x1 = x0 + lc
            y1 = y0 + ac
            eh_atual = sala["linha"] == pos_lin and sala["coluna"] == pos_col

            if not sala["visitada"]:
                cor = "#140F1D"
                borda = "#2C223D"
                texto = "?"
            else:
                if sala["tipo"] == "chefe":
                    cor = "#511834"
                    texto = "🐉 Chefe" if not sala["concluida"] else "✓ Chefe"
                elif sala["tipo"] == "monstro" and not sala["concluida"]:
                    cor = "#3D1D3B"
                    texto = f"{sala['monstro']['simbolo']} Monstro"
                elif sala["tipo"] == "tesouro" and not sala["concluida"]:
                    cor = "#3B2D17"
                    texto = "💎 Baú"
                elif sala["tipo"] == "fonte" and not sala["concluida"]:
                    cor = "#163345"
                    texto = "💧 Fonte"
                elif sala["tipo"] == "entrada":
                    cor = "#222E27"
                    texto = "🚪 Entrada"
                else:
                    cor = "#241B35"
                    texto = "· Limpa"
                borda = COR_TOCHA if eh_atual else "#5B4378"

            self.canvas_masmorra.create_rectangle(
                x0, y0, x1, y1, fill=cor, outline=borda, width=3 if eh_atual else 1
            )
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            if eh_atual:
                self.canvas_masmorra.create_text(
                    cx, cy - 8, text="🧙", fill="#FFFFFF", font=("Segoe UI", 14)
                )
                self.canvas_masmorra.create_text(
                    cx, cy + 16, text=texto, fill=COR_TOCHA, font=("Segoe UI", 8, "bold")
                )
            else:
                self.canvas_masmorra.create_text(
                    cx, cy, text=texto, fill="#E0D4EC", font=("Segoe UI", 9, "bold")
                )

    def atualizar_interface(self) -> None:
        """Atualiza mapa, atributos, combate, inventário e registo."""
        heroi = self.estado["heroi"]
        em_curso = self.estado["estado_jogo"] == "em_curso"
        em_combate = self.estado["em_combate"]

        self.lbl_resumo_topo.config(
            text=(
                f"Posição: ({self.estado['posicao'][0] + 1}, {self.estado['posicao'][1] + 1})  |  "
                f"Chefe em: (5, 5)"
            )
        )

        self.lbl_heroi_nome.config(text=f"{heroi['nome']} — Nível {heroi['nivel']}")
        self.barra_hp["maximum"] = heroi["hp_max"]
        self.barra_hp["value"] = heroi["hp"]
        self.lbl_hp.config(text=f"Vida (HP): {heroi['hp']} / {heroi['hp_max']}")

        self.barra_xp["maximum"] = heroi["xp_proximo"]
        self.barra_xp["value"] = heroi["xp"]
        self.lbl_xp.config(text=f"Experiência: {heroi['xp']} / {heroi['xp_proximo']}")

        atk = calcular_ataque_total(self.estado)
        defe = calcular_defesa_total(self.estado)
        arma_txt = heroi["arma"]["nome"] if heroi.get("arma") else "Nenhuma"
        arm_txt = heroi["armadura"]["nome"] if heroi.get("armadura") else "Nenhuma"
        self.lbl_atributos.config(
            text=(
                f"Ataque Total: {atk}  |  Defesa Total: {defe}  |  Ouro: {heroi['ouro']}\n"
                f"Arma: {arma_txt}\n"
                f"Armadura: {arm_txt}"
            )
        )

        # Estado dos botões de movimento e combate
        pode_mover = tk.NORMAL if (em_curso and not em_combate) else tk.DISABLED
        for btn in (self.btn_norte, self.btn_sul, self.btn_este, self.btn_oeste):
            btn.config(state=pode_mover)

        pode_combater = tk.NORMAL if (em_curso and em_combate) else tk.DISABLED
        self.btn_atacar.config(state=pode_combater)
        self.btn_defender.config(state=pode_combater)

        sala = obter_sala(self.estado, *self.estado["posicao"])
        if em_combate and sala and sala["monstro"]:
            m = sala["monstro"]
            self.lbl_combate_info.config(
                text=f"COMBATE: {m['simbolo']} {m['nome']} — HP: {m['hp']}/{m['hp_max']} | ATQ {m['ataque']} | DEF {m['defesa']}"
            )
            pode_fugir = tk.NORMAL if (em_curso and not m.get("chefe")) else tk.DISABLED
            self.btn_fugir.config(state=pode_fugir)
        else:
            self.lbl_combate_info.config(text="Exploração livre. Move-te para continuar.")
            self.btn_fugir.config(state=tk.DISABLED)

        # Atualiza inventário
        self.lista_inv.delete(0, tk.END)
        for item in heroi["inventario"]:
            self.lista_inv.insert(tk.END, f"[{item['tipo'].upper()}] {item['nome']}")
        self.btn_usar_item.config(state=tk.NORMAL if em_curso else tk.DISABLED)

        # Atualiza registo
        self.txt_registo.config(state=tk.NORMAL)
        self.txt_registo.delete("1.0", tk.END)
        for linha in reversed(self.estado["registo"][-25:]):
            self.txt_registo.insert(tk.END, f"• {linha}\n")
        self.txt_registo.config(state=tk.DISABLED)

        self._desenhar_masmorra()

    def _ao_selecionar_item(self, _evento: tk.Event) -> None:
        sel = self.lista_inv.curselection()
        if not sel:
            return
        item = self.estado["heroi"]["inventario"][sel[0]]
        self.lbl_item_desc.config(text=f"{item['nome']}: {item['descricao']}")

    def _acao_mover(self, dl: int, dc: int) -> None:
        ok, msg = mover_heroi(self.estado, dl, dc)
        if not ok:
            self.estado["registo"].append(msg)
        self.atualizar_interface()

    def _acao_atacar(self) -> None:
        executar_ataque_combate(self.estado)
        self.atualizar_interface()
        self._verificar_fim()

    def _acao_defender(self) -> None:
        defender_em_combate(self.estado)
        self.atualizar_interface()
        self._verificar_fim()

    def _acao_fugir(self) -> None:
        fugir_combate(self.estado)
        self.atualizar_interface()
        self._verificar_fim()

    def _acao_usar_item(self) -> None:
        sel = self.lista_inv.curselection()
        if not sel:
            messagebox.showinfo("Inventário", "Seleciona primeiro um item da lista.")
            return
        ok, msg = usar_ou_equipar_item(self.estado, sel[0])
        if not ok:
            messagebox.showwarning("Inventário", msg)
        self.atualizar_interface()

    def _verificar_fim(self) -> None:
        if self.estado["estado_jogo"] == "vitoria":
            messagebox.showinfo("Vitória!", self.estado["motivo_fim"])
        elif self.estado["estado_jogo"] == "derrota":
            messagebox.showerror("Derrota", self.estado["motivo_fim"])

    def _acao_nova(self) -> None:
        nome = simpledialog.askstring(
            "Nova Aventura", "Nome da tua personagem:", initialvalue="Cavaleiro", parent=self.raiz
        )
        if nome is not None:
            self.estado = criar_nova_aventura(nome)
            self.atualizar_interface()

    def _acao_guardar(self) -> None:
        ok, msg = guardar_aventura(self.estado)
        if ok:
            messagebox.showinfo("Guardar", msg)
        else:
            messagebox.showerror("Guardar", msg)

    def _acao_carregar(self) -> None:
        dados, msg = carregar_aventura()
        if dados is None:
            messagebox.showwarning("Carregar", msg)
            return
        self.estado = dados
        self.atualizar_interface()
        messagebox.showinfo("Carregar", msg)


def iniciar_interface() -> None:
    """Inicia a janela principal do RPG Dungeon Quest."""
    raiz = tk.Tk()
    AplicacaoDungeonQuest(raiz)
    raiz.mainloop()
