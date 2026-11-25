"""Interface gráfica Tkinter para o Simulador de Porto Marítimo."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.armazenamento import carregar_porto, guardar_porto
from app.dados import ORDEM_DIMENSOES, ORDEM_PRIORIDADES, TIPOS_CONTENTOR
from app.logica import (
    adicionar_contentor_patio,
    atracar_navio,
    atribuir_cais_otimizado,
    criar_novo_porto,
    executar_ciclo_portuario,
    expedir_contentor,
    gerar_navio_aleatorio,
    obter_fila_espera_ordenada,
    obter_indicadores,
    obter_navio,
    registar_navio,
)

COR_FUNDO = "#0D1E2E"
COR_PAINEL = "#152C42"
COR_CARD = "#1D3C58"
COR_LARANJA = "#F39C12"
COR_CIANO = "#4FC3F7"
COR_TEXTO = "#ECF5FC"
COR_SEC = "#A6C2D9"


class AplicacaoPortoMaritimo:
    """Controlador da interface do Port Manager."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Port Manager — Simulador de Porto Marítimo")
        self.raiz.geometry("1200x770")
        self.raiz.minsize(1060, 680)
        self.raiz.configure(bg=COR_FUNDO)

        self.estado = criar_novo_porto()

        self._configurar_estilos()
        self._construir_interface()
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
            foreground=COR_LARANJA,
            font=("Segoe UI", 14, "bold"),
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
            "Porto.TButton",
            background=COR_LARANJA,
            foreground="#1A1A1A",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Porto.TButton", background=[("active", "#F5B041")])
        estilo.configure(
            "Acao.TButton",
            background="#265073",
            foreground=COR_TEXTO,
            font=("Segoe UI", 9, "bold"),
            padding=5,
        )
        estilo.map("Acao.TButton", background=[("active", "#326896")])
        estilo.configure("TNotebook", background=COR_PAINEL, borderwidth=0)
        estilo.configure(
            "TNotebook.Tab",
            background=COR_CARD,
            foreground=COR_TEXTO,
            padding=(10, 5),
            font=("Segoe UI", 9, "bold"),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", COR_LARANJA)],
            foreground=[("selected", "#1A1A1A")],
        )
        estilo.configure(
            "Treeview",
            background="#102334",
            foreground=COR_TEXTO,
            fieldbackground="#102334",
            rowheight=24,
        )
        estilo.configure(
            "Treeview.Heading",
            background=COR_CARD,
            foreground=COR_LARANJA,
            font=("Segoe UI", 9, "bold"),
        )

    def _construir_interface(self) -> None:
        topo = ttk.Frame(self.raiz, style="Painel.TFrame", padding=(14, 10))
        topo.pack(fill=tk.X, padx=10, pady=(10, 6))

        self.lbl_ciclo = ttk.Label(topo, text="Ciclo 1", style="Titulo.TLabel")
        self.lbl_ciclo.pack(side=tk.LEFT)

        self.lbl_financas_topo = ttk.Label(topo, text="", style="Txt.TLabel")
        self.lbl_financas_topo.pack(side=tk.LEFT, padx=18)

        btns_topo = ttk.Frame(topo, style="Painel.TFrame")
        btns_topo.pack(side=tk.RIGHT)
        ttk.Button(btns_topo, text="Novo Porto", style="Acao.TButton", command=self._acao_novo).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(btns_topo, text="Guardar", style="Acao.TButton", command=self._acao_guardar).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(btns_topo, text="Carregar", style="Acao.TButton", command=self._acao_carregar).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(
            btns_topo,
            text="Otimizar Cais ⚡",
            style="Acao.TButton",
            command=self._acao_otimizar,
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            btns_topo,
            text="Executar Ciclo ▶",
            style="Porto.TButton",
            command=self._acao_executar_ciclo,
        ).pack(side=tk.LEFT, padx=(4, 0))

        corpo = ttk.Frame(self.raiz)
        corpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Coluna esquerda: Vista do Porto + Indicadores + Histórico
        col_esq = ttk.Frame(corpo, style="Painel.TFrame", padding=12)
        col_esq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ttk.Label(
            col_esq,
            text="Terminal Portuário (Cais, Gruas, Navios e Parque de Contentores)",
            style="Sub.TLabel",
        ).pack(anchor=tk.W, pady=(0, 6))

        self.canvas_porto = tk.Canvas(
            col_esq,
            height=390,
            bg="#0B2D48",
            highlightthickness=1,
            highlightbackground=COR_CIANO,
        )
        self.canvas_porto.pack(fill=tk.BOTH, expand=True)
        self.canvas_porto.bind("<Configure>", lambda _e: self._desenhar_porto())

        frame_ind = ttk.Frame(col_esq, style="Card.TFrame", padding=10)
        frame_ind.pack(fill=tk.X, pady=8)
        self.lbl_indicadores = ttk.Label(
            frame_ind,
            text="",
            background=COR_CARD,
            foreground=COR_TEXTO,
            font=("Segoe UI", 9, "bold"),
            justify=tk.LEFT,
        )
        self.lbl_indicadores.pack(anchor=tk.W)

        ttk.Label(col_esq, text="Registo de Operações Portuárias", style="Sub.TLabel").pack(
            anchor=tk.W
        )
        self.txt_historico = tk.Text(
            col_esq,
            height=7,
            bg="#0A1824",
            fg=COR_TEXTO,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=8,
            pady=6,
        )
        self.txt_historico.pack(fill=tk.X, pady=(4, 0))

        # Coluna direita: Abas operacionais
        col_dir = ttk.Frame(corpo, style="Painel.TFrame", padding=12, width=510)
        col_dir.pack(side=tk.RIGHT, fill=tk.BOTH)
        col_dir.pack_propagate(False)

        self.abas = ttk.Notebook(col_dir)
        self.abas.pack(fill=tk.BOTH, expand=True)

        self.tab_navios = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)
        self.tab_cais = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)
        self.tab_contentores = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)
        self.tab_financeiro = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)

        self.abas.add(self.tab_navios, text="Navios & Fila")
        self.abas.add(self.tab_cais, text="Cais")
        self.abas.add(self.tab_contentores, text="Contentores")
        self.abas.add(self.tab_financeiro, text="Financeiro")

        self._construir_aba_navios()
        self._construir_aba_cais()
        self._construir_aba_contentores()
        self._construir_aba_financeiro()

    def _construir_aba_navios(self) -> None:
        card_reg = ttk.Frame(self.tab_navios, style="Card.TFrame", padding=10)
        card_reg.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(
            card_reg, text="Registar Novo Navio", background=COR_CARD, foreground=COR_LARANJA,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 6))

        ttk.Label(card_reg, text="Nome:", background=COR_CARD, foreground=COR_TEXTO).grid(
            row=1, column=0, sticky=tk.W, pady=3
        )
        self.var_navio_nome = tk.StringVar(value="N/M Lusitânia")
        ttk.Entry(card_reg, textvariable=self.var_navio_nome, width=18).grid(
            row=1, column=1, padx=4, pady=3, sticky=tk.W
        )

        ttk.Label(card_reg, text="Dimensão:", background=COR_CARD, foreground=COR_TEXTO).grid(
            row=1, column=2, sticky=tk.W, pady=3
        )
        self.var_navio_dim = tk.StringVar(value="Médio")
        ttk.Combobox(
            card_reg,
            textvariable=self.var_navio_dim,
            values=list(ORDEM_DIMENSOES.keys()),
            state="readonly",
            width=10,
        ).grid(row=1, column=3, padx=4, pady=3)

        ttk.Label(card_reg, text="Contentores:", background=COR_CARD, foreground=COR_TEXTO).grid(
            row=2, column=0, sticky=tk.W, pady=3
        )
        self.var_navio_qtd = tk.IntVar(value=8)
        ttk.Spinbox(card_reg, from_=1, to=40, textvariable=self.var_navio_qtd, width=8).grid(
            row=2, column=1, padx=4, pady=3, sticky=tk.W
        )

        ttk.Label(card_reg, text="Tipo Carga:", background=COR_CARD, foreground=COR_TEXTO).grid(
            row=2, column=2, sticky=tk.W, pady=3
        )
        self.var_navio_carga = tk.StringVar(value="Normal")
        ttk.Combobox(
            card_reg,
            textvariable=self.var_navio_carga,
            values=list(TIPOS_CONTENTOR.keys()),
            state="readonly",
            width=10,
        ).grid(row=2, column=3, padx=4, pady=3)

        ttk.Label(card_reg, text="Operação:", background=COR_CARD, foreground=COR_TEXTO).grid(
            row=3, column=0, sticky=tk.W, pady=3
        )
        self.var_navio_op = tk.StringVar(value="Descarga")
        ttk.Combobox(
            card_reg,
            textvariable=self.var_navio_op,
            values=["Descarga", "Carga"],
            state="readonly",
            width=12,
        ).grid(row=3, column=1, padx=4, pady=3, sticky=tk.W)

        ttk.Label(card_reg, text="Prioridade:", background=COR_CARD, foreground=COR_TEXTO).grid(
            row=3, column=2, sticky=tk.W, pady=3
        )
        self.var_navio_prio = tk.StringVar(value="Normal")
        ttk.Combobox(
            card_reg,
            textvariable=self.var_navio_prio,
            values=list(ORDEM_PRIORIDADES.keys()),
            state="readonly",
            width=10,
        ).grid(row=3, column=3, padx=4, pady=3)

        frame_btns = ttk.Frame(card_reg, style="Card.TFrame")
        frame_btns.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=(8, 0))
        ttk.Button(
            frame_btns, text="Registar na Fila", style="Porto.TButton", command=self._acao_registar_navio
        ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            frame_btns, text="+ Navio Aleatório", style="Acao.TButton", command=self._acao_navio_aleatorio
        ).pack(side=tk.LEFT)

        ttk.Label(self.tab_navios, text="Fila de Espera (Ordenada por Prioridade)", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(4, 4)
        )
        cols = ("id", "nome", "dim", "op", "cnt", "prio", "espera")
        self.tabela_fila = ttk.Treeview(self.tab_navios, columns=cols, show="headings", height=9)
        for c, tit, larg in [
            ("id", "ID", 65),
            ("nome", "Navio", 120),
            ("dim", "Dim.", 60),
            ("op", "Op.", 68),
            ("cnt", "Rest.", 48),
            ("prio", "Prioridade", 70),
            ("espera", "Espera", 55),
        ]:
            self.tabela_fila.heading(c, text=tit)
            self.tabela_fila.column(c, width=larg, anchor=tk.CENTER)
        self.tabela_fila.pack(fill=tk.BOTH, expand=True)

    def _construir_aba_cais(self) -> None:
        ttk.Label(self.tab_cais, text="Estado dos Cais do Terminal", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(0, 6)
        )
        cols = ("id", "nome", "cap", "gruas", "estado", "navio")
        self.tabela_cais = ttk.Treeview(self.tab_cais, columns=cols, show="headings", height=6)
        for c, tit, larg in [
            ("id", "ID", 62),
            ("nome", "Cais", 140),
            ("cap", "Cap. Máx", 72),
            ("gruas", "Gruas", 50),
            ("estado", "Estado", 75),
            ("navio", "Navio", 85),
        ]:
            self.tabela_cais.heading(c, text=tit)
            self.tabela_cais.column(c, width=larg, anchor=tk.CENTER)
        self.tabela_cais.pack(fill=tk.X, pady=(0, 10))

        card_atr = ttk.Frame(self.tab_cais, style="Card.TFrame", padding=10)
        card_atr.pack(fill=tk.X)
        ttk.Label(
            card_atr, text="Atracação Manual", background=COR_CARD, foreground=COR_LARANJA,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 6))

        linha1 = ttk.Frame(card_atr, style="Card.TFrame")
        linha1.pack(fill=tk.X, pady=3)
        ttk.Label(linha1, text="Navio em fila:", background=COR_CARD, foreground=COR_TEXTO, width=13).pack(
            side=tk.LEFT
        )
        self.var_atracar_navio = tk.StringVar()
        self.combo_atracar_navio = ttk.Combobox(
            linha1, textvariable=self.var_atracar_navio, state="readonly", width=28
        )
        self.combo_atracar_navio.pack(side=tk.LEFT, padx=4)

        linha2 = ttk.Frame(card_atr, style="Card.TFrame")
        linha2.pack(fill=tk.X, pady=3)
        ttk.Label(linha2, text="Cais destino:", background=COR_CARD, foreground=COR_TEXTO, width=13).pack(
            side=tk.LEFT
        )
        self.var_atracar_cais = tk.StringVar()
        self.combo_atracar_cais = ttk.Combobox(
            linha2, textvariable=self.var_atracar_cais, state="readonly", width=28
        )
        self.combo_atracar_cais.pack(side=tk.LEFT, padx=4)

        ttk.Button(
            card_atr, text="Atracar Navio no Cais", style="Porto.TButton", command=self._acao_atracar_manual
        ).pack(anchor=tk.W, pady=(8, 0))

    def _construir_aba_contentores(self) -> None:
        card_cnt = ttk.Frame(self.tab_contentores, style="Card.TFrame", padding=10)
        card_cnt.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            card_cnt, text="Entrada Direta / Expedição do Pátio", background=COR_CARD,
            foreground=COR_LARANJA, font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 6))

        linha = ttk.Frame(card_cnt, style="Card.TFrame")
        linha.pack(fill=tk.X)
        self.var_cnt_tipo = tk.StringVar(value="Normal")
        ttk.Combobox(
            linha, textvariable=self.var_cnt_tipo, values=list(TIPOS_CONTENTOR.keys()),
            state="readonly", width=13
        ).pack(side=tk.LEFT)
        ttk.Button(
            linha, text="+ Entrada Pátio", style="Acao.TButton", command=self._acao_add_contentor
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            linha, text="Expedir Selecionado (€)", style="Porto.TButton", command=self._acao_expedir_contentor
        ).pack(side=tk.LEFT)

        cols = ("id", "tipo", "local", "origem")
        self.tabela_contentores = ttk.Treeview(
            self.tab_contentores, columns=cols, show="headings", height=12
        )
        for c, tit, larg in [
            ("id", "ID", 90),
            ("tipo", "Tipo", 100),
            ("local", "Localização", 95),
            ("origem", "Origem", 160),
        ]:
            self.tabela_contentores.heading(c, text=tit)
            self.tabela_contentores.column(c, width=larg, anchor=tk.CENTER)
        self.tabela_contentores.pack(fill=tk.BOTH, expand=True)

    def _construir_aba_financeiro(self) -> None:
        card_fin = ttk.Frame(self.tab_financeiro, style="Card.TFrame", padding=14)
        card_fin.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(
            card_fin, text="Relatório Financeiro e Eficiência", background=COR_CARD,
            foreground=COR_LARANJA, font=("Segoe UI", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))

        self.lbl_relatorio_fin = ttk.Label(
            card_fin, text="", background=COR_CARD, foreground=COR_TEXTO,
            font=("Segoe UI", 10), justify=tk.LEFT
        )
        self.lbl_relatorio_fin.pack(anchor=tk.W)

    def _desenhar_porto(self) -> None:
        self.canvas_porto.delete("all")
        larg = max(420, self.canvas_porto.winfo_width())
        alt = max(280, self.canvas_porto.winfo_height())

        # Zona marítima (topo) e zona terrestre/pátio (base)
        y_cais = alt * 0.56
        self.canvas_porto.create_rectangle(0, 0, larg, y_cais, fill="#0D3B66", outline="")
        self.canvas_porto.create_rectangle(0, y_cais, larg, alt, fill="#34495E", outline="")
        self.canvas_porto.create_line(0, y_cais, larg, y_cais, fill="#BDC3C7", width=4)

        # Desenhar os 4 cais
        num_cais = len(self.estado["cais"])
        larg_cais = (larg - 40) / num_cais
        for idx, cais in enumerate(self.estado["cais"]):
            x0 = 20 + idx * larg_cais + 6
            x1 = 20 + (idx + 1) * larg_cais - 6
            cx = (x0 + x1) / 2

            # Estrutura do cais e grua simplificada
            cor_cais = "#C0392B" if cais["ocupado"] else "#27AE60"
            self.canvas_porto.create_rectangle(
                x0, y_cais - 12, x1, y_cais + 16, fill=cor_cais, outline="#FFFFFF", width=1
            )
            self.canvas_porto.create_text(
                cx, y_cais + 2, text=f"{cais['id']} ({cais['capacidade_dimensao']})",
                fill="#FFFFFF", font=("Segoe UI", 8, "bold")
            )
            # Grua
            self.canvas_porto.create_line(cx, y_cais - 12, cx, y_cais - 48, fill=COR_LARANJA, width=3)
            self.canvas_porto.create_line(cx - 18, y_cais - 48, cx + 22, y_cais - 48, fill=COR_LARANJA, width=3)

            # Navio atracado
            if cais["ocupado"] and cais["navio_id"]:
                navio = obter_navio(self.estado, cais["navio_id"])
                if navio:
                    self.canvas_porto.create_polygon(
                        x0 + 8, y_cais - 24,
                        x1 - 8, y_cais - 24,
                        x1 - 18, y_cais - 12,
                        x0 + 18, y_cais - 12,
                        fill="#E67E22", outline="#FFFFFF", width=2
                    )
                    self.canvas_porto.create_text(
                        cx, y_cais - 66,
                        text=f"🚢 {navio['id']} ({navio['contentores_restantes']} rest.)",
                        fill="#FFFFFF", font=("Segoe UI", 8, "bold")
                    )

        # Desenhar contentores no pátio (até 36 representados visualmente)
        self.canvas_porto.create_text(
            18, y_cais + 28, anchor=tk.W,
            text=f"Pátio de Contentores ({len(self.estado['contentores'])} em armazém):",
            fill="#ECF0F1", font=("Segoe UI", 9, "bold")
        )
        max_vis = min(36, len(self.estado["contentores"]))
        cols_cnt = 12
        cw = max(24, (larg - 48) / cols_cnt - 4)
        ch = 16
        for i in range(max_vis):
            cnt = self.estado["contentores"][i]
            col = i % cols_cnt
            lin = i // cols_cnt
            bx0 = 20 + col * (cw + 4)
            by0 = y_cais + 44 + lin * (ch + 5)
            cor = TIPOS_CONTENTOR[cnt["tipo"]]["cor"]
            self.canvas_porto.create_rectangle(
                bx0, by0, bx0 + cw, by0 + ch, fill=cor, outline="#111111"
            )

    def atualizar_interface(self) -> None:
        """Atualiza todos os painéis, tabelas e desenho do porto."""
        ind = obter_indicadores(self.estado)
        self.lbl_ciclo.config(text=f"Ciclo {ind['ciclo']}")
        self.lbl_financas_topo.config(
            text=(
                f"Receitas: {ind['receitas']:.2f} €  |  Custos: {ind['custos']:.2f} €  |  "
                f"Lucro: {ind['lucro']:.2f} €"
            )
        )
        self.lbl_indicadores.config(
            text=(
                f"Cais ocupados: {ind['cais_ocupados']}/{ind['total_cais']} ({ind['ocupacao_atual']}%)  |  "
                f"Utilização média: {ind['utilizacao_media']}%  |  "
                f"Navios em fila: {ind['navios_em_fila']}  |  "
                f"Espera média: {ind['tempo_medio_espera']} ciclos"
            )
        )

        # Tabela fila
        self.tabela_fila.delete(*self.tabela_fila.get_children())
        fila = obter_fila_espera_ordenada(self.estado)
        for n in fila:
            self.tabela_fila.insert(
                "", tk.END,
                values=(
                    n["id"], n["nome"], n["dimensao"], n["operacao"],
                    n["contentores_restantes"], n["prioridade"], f"{n['ciclos_espera']}c"
                ),
            )

        # Combos atracação manual
        opcoes_navios = [f"{n['id']} - {n['nome']} ({n['dimensao']})" for n in fila]
        self.combo_atracar_navio["values"] = opcoes_navios
        self.var_atracar_navio.set(opcoes_navios[0] if opcoes_navios else "")

        cais_livres = [
            f"{c['id']} - {c['capacidade_dimensao']}" for c in self.estado["cais"] if not c["ocupado"]
        ]
        self.combo_atracar_cais["values"] = cais_livres
        self.var_atracar_cais.set(cais_livres[0] if cais_livres else "")

        # Tabela cais
        self.tabela_cais.delete(*self.tabela_cais.get_children())
        for c in self.estado["cais"]:
            self.tabela_cais.insert(
                "", tk.END,
                values=(
                    c["id"], c["nome"], c["capacidade_dimensao"], c["gruas"],
                    "Ocupado" if c["ocupado"] else "Livre", c["navio_id"] or "-"
                ),
            )

        # Tabela contentores
        self.tabela_contentores.delete(*self.tabela_contentores.get_children())
        for cnt in self.estado["contentores"]:
            self.tabela_contentores.insert(
                "", tk.END,
                values=(cnt["id"], cnt["tipo"], cnt["localizacao"], cnt["origem"]),
            )

        # Relatório financeiro
        self.lbl_relatorio_fin.config(
            text=(
                f"Receitas Totais: {ind['receitas']:.2f} €\n"
                f"Custos Operacionais Totais: {ind['custos']:.2f} €\n"
                f"Lucro Líquido: {ind['lucro']:.2f} €\n\n"
                f"Navios Concluídos: {ind['navios_concluidos']}\n"
                f"Contentores Movimentados: {ind['contentores_movimentados']}\n"
                f"Contentores em Armazém: {ind['contentores_armazem']}\n"
                f"Taxa Média de Utilização dos Cais: {ind['utilizacao_media']}%\n"
                f"Tempo Médio de Espera na Fila: {ind['tempo_medio_espera']} ciclos"
            )
        )

        # Histórico
        self.txt_historico.config(state=tk.NORMAL)
        self.txt_historico.delete("1.0", tk.END)
        for linha in reversed(self.estado["historico"][-35:]):
            self.txt_historico.insert(tk.END, f"• {linha}\n")
        self.txt_historico.config(state=tk.DISABLED)

        self._desenhar_porto()

    def _acao_registar_navio(self) -> None:
        try:
            qtd = int(self.var_navio_qtd.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Erro", "Quantidade de contentores inválida.")
            return
        ok, msg, _ = registar_navio(
            self.estado,
            self.var_navio_nome.get(),
            self.var_navio_dim.get(),
            qtd,
            self.var_navio_op.get(),
            self.var_navio_prio.get(),
            self.var_navio_carga.get(),
        )
        if not ok:
            messagebox.showwarning("Registo de Navio", msg)
        self.atualizar_interface()

    def _acao_navio_aleatorio(self) -> None:
        gerar_navio_aleatorio(self.estado)
        self.atualizar_interface()

    def _acao_atracar_manual(self) -> None:
        nav_txt = self.var_atracar_navio.get()
        cais_txt = self.var_atracar_cais.get()
        if not nav_txt or not cais_txt:
            messagebox.showwarning("Atracação", "Seleciona um navio em fila e um cais livre.")
            return
        nav_id = nav_txt.split(" - ", 1)[0]
        cais_id = cais_txt.split(" - ", 1)[0]
        ok, msg = atracar_navio(self.estado, nav_id, cais_id)
        if not ok:
            messagebox.showwarning("Atracação", msg)
        self.atualizar_interface()

    def _acao_otimizar(self) -> None:
        msgs = atribuir_cais_otimizado(self.estado)
        if not msgs:
            messagebox.showinfo("Otimização", "Não há navios em fila compatíveis com cais livres neste momento.")
        self.atualizar_interface()

    def _acao_add_contentor(self) -> None:
        ok, msg, _ = adicionar_contentor_patio(self.estado, self.var_cnt_tipo.get())
        if ok:
            self.estado["historico"].append(f"Ciclo {self.estado['ciclo']}: {msg}")
        self.atualizar_interface()

    def _acao_expedir_contentor(self) -> None:
        sel = self.tabela_contentores.selection()
        if not sel:
            messagebox.showinfo("Expedição", "Seleciona primeiro um contentor na tabela.")
            return
        cid = self.tabela_contentores.item(sel[0], "values")[0]
        ok, msg = expedir_contentor(self.estado, cid)
        if not ok:
            messagebox.showwarning("Expedição", msg)
        self.atualizar_interface()

    def _acao_executar_ciclo(self) -> None:
        executar_ciclo_portuario(self.estado)
        self.atualizar_interface()

    def _acao_novo(self) -> None:
        if messagebox.askyesno("Novo Porto", "Desejas reiniciar o simulador portuário?"):
            self.estado = criar_novo_porto()
            self.atualizar_interface()

    def _acao_guardar(self) -> None:
        ok, msg = guardar_porto(self.estado)
        if ok:
            messagebox.showinfo("Guardar", msg)
        else:
            messagebox.showerror("Guardar", msg)

    def _acao_carregar(self) -> None:
        dados, msg = carregar_porto()
        if dados is None:
            messagebox.showwarning("Carregar", msg)
            return
        self.estado = dados
        self.atualizar_interface()
        messagebox.showinfo("Carregar", msg)


def iniciar_interface() -> None:
    """Inicia a janela principal do Port Manager."""
    raiz = tk.Tk()
    AplicacaoPortoMaritimo(raiz)
    raiz.mainloop()
