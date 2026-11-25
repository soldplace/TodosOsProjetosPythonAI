"""Interface gráfica Tkinter para o jogo Empire."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.armazenamento import carregar_partida, guardar_partida
from app.dados import (
    COLUNAS_MAPA,
    CUSTO_RECRUTAR_SOLDAO,
    FACCOES,
    LINHAS_MAPA,
    MELHORIAS_DISPONIVEIS,
    OBJETIVO_TERRITORIOS_VITORIA,
    TECNOLOGIAS_DISPONIVEIS,
    TIPOS_TERRITORIO,
    TOTAL_TERRITORIOS,
)
from app.logica import (
    atacar_territorio,
    calcular_manutencao_turno,
    calcular_producao_turno,
    calcular_total_tropas,
    construir_melhoria,
    contar_territorios_por_dono,
    criar_novo_jogo,
    investigar_tecnologia,
    mover_tropas,
    obter_territorio,
    obter_vizinhos_aliados,
    recrutar_soldados,
    terminar_turno,
)

COR_FUNDO = "#1B2028"
COR_PAINEL = "#252C37"
COR_CARD = "#2E3744"
COR_DOURADO = "#D4AF37"
COR_TEXTO = "#EAE6DF"
COR_TEXTO_SEC = "#A9B2C0"


class AplicacaoEmpire:
    """Controlador da janela principal do jogo Empire."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Empire — Conquista Territorial")
        self.raiz.geometry("1160x740")
        self.raiz.minsize(1020, 660)
        self.raiz.configure(bg=COR_FUNDO)

        self.estado = criar_novo_jogo()
        self.territorio_selecionado_id: int | None = 20  # Fortaleza inicial do jogador (4, 0)
        self.celulas_canvas: dict[int, int] = {}

        self._configurar_estilos()
        self._construir_interface()
        self.atualizar_tudo()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=COR_FUNDO)
        estilo.configure("Painel.TFrame", background=COR_PAINEL)
        estilo.configure("Card.TFrame", background=COR_CARD)
        estilo.configure(
            "Titulo.TLabel",
            background=COR_PAINEL,
            foreground=COR_DOURADO,
            font=("Segoe UI", 14, "bold"),
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
        )
        estilo.configure(
            "Info.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Sec.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO_SEC,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Gold.TButton",
            background=COR_DOURADO,
            foreground="#1A1A1A",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Gold.TButton", background=[("active", "#E5C158")])
        estilo.configure(
            "Acao.TButton",
            background="#3A4759",
            foreground=COR_TEXTO,
            font=("Segoe UI", 10),
            padding=5,
        )
        estilo.map("Acao.TButton", background=[("active", "#4B5B72")])
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
            background=[("selected", COR_DOURADO)],
            foreground=[("selected", "#1A1A1A")],
        )
        estilo.configure(
            "Dominio.Horizontal.TProgressbar",
            troughcolor="#161A20",
            background=COR_DOURADO,
            thickness=14,
        )

    def _construir_interface(self) -> None:
        # Barra superior (Recursos, turno e controlos)
        barra_top = ttk.Frame(self.raiz, style="Painel.TFrame", padding=(12, 8))
        barra_top.pack(fill=tk.X, padx=10, pady=(10, 6))

        self.lbl_turno = ttk.Label(barra_top, text="Turno 1", style="Titulo.TLabel")
        self.lbl_turno.pack(side=tk.LEFT, padx=(0, 18))

        self.lbl_recursos = ttk.Label(barra_top, text="", style="Info.TLabel")
        self.lbl_recursos.pack(side=tk.LEFT, padx=8)

        frame_botoes_top = ttk.Frame(barra_top, style="Painel.TFrame")
        frame_botoes_top.pack(side=tk.RIGHT)

        ttk.Button(
            frame_botoes_top, text="Novo Jogo", style="Acao.TButton", command=self._acao_novo_jogo
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            frame_botoes_top, text="Guardar", style="Acao.TButton", command=self._acao_guardar
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            frame_botoes_top, text="Carregar", style="Acao.TButton", command=self._acao_carregar
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            frame_botoes_top,
            text="Terminar Turno ▶",
            style="Gold.TButton",
            command=self._acao_terminar_turno,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Área principal dividida em Mapa (esquerda) e Gestão (direita)
        corpo = ttk.Frame(self.raiz)
        corpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Coluna esquerda: Mapa + Legenda + Barra de domínio
        col_esq = ttk.Frame(corpo, style="Painel.TFrame", padding=12)
        col_esq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ttk.Label(
            col_esq,
            text="Mapa Estratégico do Continente (Clica num território)",
            style="Subtitulo.TLabel",
        ).pack(anchor=tk.W, pady=(0, 8))

        self.canvas_mapa = tk.Canvas(
            col_esq, width=520, height=500, bg="#14181F", highlightthickness=1, highlightbackground=COR_DOURADO
        )
        self.canvas_mapa.pack(fill=tk.BOTH, expand=True)
        self.canvas_mapa.bind("<Configure>", lambda _e: self._desenhar_mapa())
        self.canvas_mapa.bind("<Button-1>", self._ao_clicar_mapa)

        # Legenda e progresso de vitória
        rodape_mapa = ttk.Frame(col_esq, style="Painel.TFrame", padding=(0, 8, 0, 0))
        rodape_mapa.pack(fill=tk.X)

        self.lbl_legenda = ttk.Label(rodape_mapa, text="", style="Sec.TLabel")
        self.lbl_legenda.pack(anchor=tk.W)

        frame_prog = ttk.Frame(rodape_mapa, style="Painel.TFrame")
        frame_prog.pack(fill=tk.X, pady=(6, 0))
        self.lbl_objetivo = ttk.Label(frame_prog, text="", style="Info.TLabel")
        self.lbl_objetivo.pack(side=tk.LEFT)
        self.barra_dominio = ttk.Progressbar(
            frame_prog,
            style="Dominio.Horizontal.TProgressbar",
            maximum=TOTAL_TERRITORIOS,
            value=3,
        )
        self.barra_dominio.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(12, 0))

        # Coluna direita: Resumo militar + Abas de comando
        col_dir = ttk.Frame(corpo, style="Painel.TFrame", padding=12, width=470)
        col_dir.pack(side=tk.RIGHT, fill=tk.BOTH)
        col_dir.pack_propagate(False)

        self.lbl_exercito = ttk.Label(col_dir, text="", style="Info.TLabel")
        self.lbl_exercito.pack(anchor=tk.W, pady=(0, 8))

        self.abas = ttk.Notebook(col_dir)
        self.abas.pack(fill=tk.BOTH, expand=True)

        self.tab_territorio = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)
        self.tab_melhorias = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)
        self.tab_tech = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)
        self.tab_registo = ttk.Frame(self.abas, style="Painel.TFrame", padding=10)

        self.abas.add(self.tab_territorio, text="Território")
        self.abas.add(self.tab_melhorias, text="Melhorias")
        self.abas.add(self.tab_tech, text="Tecnologias")
        self.abas.add(self.tab_registo, text="Registo")

        self._construir_aba_territorio()
        self._construir_aba_melhorias()
        self._construir_aba_tecnologias()
        self._construir_aba_registo()

    def _construir_aba_territorio(self) -> None:
        self.lbl_ter_nome = ttk.Label(self.tab_territorio, text="", style="Titulo.TLabel")
        self.lbl_ter_nome.pack(anchor=tk.W)

        self.lbl_ter_detalhes = ttk.Label(
            self.tab_territorio, text="", style="Info.TLabel", justify=tk.LEFT
        )
        self.lbl_ter_detalhes.pack(anchor=tk.W, pady=(6, 12))

        ttk.Separator(self.tab_territorio).pack(fill=tk.X, pady=6)

        # Secção Recrutar
        frame_rec = ttk.Frame(self.tab_territorio, style="Painel.TFrame")
        frame_rec.pack(fill=tk.X, pady=6)
        custo_txt = (
            f"Recrutar Soldados ({CUSTO_RECRUTAR_SOLDAO['ouro']} ouro, "
            f"{CUSTO_RECRUTAR_SOLDAO['alimentos']} alim., {CUSTO_RECRUTAR_SOLDAO['ferro']} ferro/unid.):"
        )
        ttk.Label(frame_rec, text=custo_txt, style="Sec.TLabel", wraplength=410).pack(anchor=tk.W)

        linha_rec = ttk.Frame(frame_rec, style="Painel.TFrame")
        linha_rec.pack(fill=tk.X, pady=4)
        self.var_qtd_recrutar = tk.IntVar(value=5)
        ttk.Spinbox(linha_rec, from_=1, to=50, textvariable=self.var_qtd_recrutar, width=8).pack(
            side=tk.LEFT
        )
        self.btn_recrutar = ttk.Button(
            linha_rec, text="Recrutar Aqui", style="Acao.TButton", command=self._acao_recrutar
        )
        self.btn_recrutar.pack(side=tk.LEFT, padx=8)

        ttk.Separator(self.tab_territorio).pack(fill=tk.X, pady=8)

        # Secção Atacar / Reforçar a partir de vizinho aliado
        ttk.Label(
            self.tab_territorio,
            text="Operações Militares (a partir de território aliado adjacente):",
            style="Subtitulo.TLabel",
        ).pack(anchor=tk.W)

        frame_op = ttk.Frame(self.tab_territorio, style="Painel.TFrame")
        frame_op.pack(fill=tk.X, pady=6)

        ttk.Label(frame_op, text="Origem aliada:", style="Info.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=3
        )
        self.var_origem = tk.StringVar()
        self.combo_origem = ttk.Combobox(
            frame_op, textvariable=self.var_origem, state="readonly", width=26
        )
        self.combo_origem.grid(row=0, column=1, padx=6, pady=3, sticky=tk.W)

        ttk.Label(frame_op, text="Tropas a enviar:", style="Info.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=3
        )
        self.var_tropas_op = tk.IntVar(value=5)
        ttk.Spinbox(frame_op, from_=1, to=200, textvariable=self.var_tropas_op, width=10).grid(
            row=1, column=1, padx=6, pady=3, sticky=tk.W
        )

        frame_btns_op = ttk.Frame(self.tab_territorio, style="Painel.TFrame")
        frame_btns_op.pack(fill=tk.X, pady=6)
        self.btn_atacar = ttk.Button(
            frame_btns_op, text="⚔ Atacar Território", style="Gold.TButton", command=self._acao_atacar
        )
        self.btn_atacar.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_mover = ttk.Button(
            frame_btns_op, text="🛡 Mover Tropas", style="Acao.TButton", command=self._acao_mover
        )
        self.btn_mover.pack(side=tk.LEFT)

    def _construir_aba_melhorias(self) -> None:
        self.widgets_melhorias: dict[str, tuple[ttk.Label, ttk.Button]] = {}
        for chave, info in MELHORIAS_DISPONIVEIS.items():
            card = ttk.Frame(self.tab_melhorias, style="Card.TFrame", padding=8)
            card.pack(fill=tk.X, pady=5)

            topo = ttk.Frame(card, style="Card.TFrame")
            topo.pack(fill=tk.X)
            lbl_titulo = ttk.Label(
                topo,
                text=f"{info['nome']} [{info['categoria']}]",
                background=COR_CARD,
                foreground=COR_DOURADO,
                font=("Segoe UI", 10, "bold"),
            )
            lbl_titulo.pack(side=tk.LEFT)

            btn = ttk.Button(
                topo,
                text="Melhorar",
                style="Acao.TButton",
                command=lambda c=chave: self._acao_melhorar(c),
            )
            btn.pack(side=tk.RIGHT)

            lbl_desc = ttk.Label(
                card,
                text="",
                background=COR_CARD,
                foreground=COR_TEXTO,
                font=("Segoe UI", 9),
                wraplength=400,
            )
            lbl_desc.pack(anchor=tk.W, pady=(4, 0))
            self.widgets_melhorias[chave] = (lbl_desc, btn)

    def _construir_aba_tecnologias(self) -> None:
        self.widgets_tech: dict[str, tuple[ttk.Label, ttk.Button]] = {}
        for chave, info in TECNOLOGIAS_DISPONIVEIS.items():
            card = ttk.Frame(self.tab_tech, style="Card.TFrame", padding=8)
            card.pack(fill=tk.X, pady=5)

            topo = ttk.Frame(card, style="Card.TFrame")
            topo.pack(fill=tk.X)
            ttk.Label(
                topo,
                text=info["nome"],
                background=COR_CARD,
                foreground=COR_DOURADO,
                font=("Segoe UI", 10, "bold"),
            ).pack(side=tk.LEFT)

            btn = ttk.Button(
                topo,
                text="Investigar",
                style="Acao.TButton",
                command=lambda c=chave: self._acao_investigar(c),
            )
            btn.pack(side=tk.RIGHT)

            lbl_desc = ttk.Label(
                card,
                text="",
                background=COR_CARD,
                foreground=COR_TEXTO,
                font=("Segoe UI", 9),
                wraplength=400,
            )
            lbl_desc.pack(anchor=tk.W, pady=(4, 0))
            self.widgets_tech[chave] = (lbl_desc, btn)

    def _construir_aba_registo(self) -> None:
        self.txt_registo = tk.Text(
            self.tab_registo,
            bg="#151920",
            fg=COR_TEXTO,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=8,
            pady=8,
        )
        scroll = ttk.Scrollbar(self.tab_registo, command=self.txt_registo.yview)
        self.txt_registo.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_registo.pack(fill=tk.BOTH, expand=True)

    def _desenhar_mapa(self) -> None:
        self.canvas_mapa.delete("all")
        self.celulas_canvas.clear()

        largura = max(300, self.canvas_mapa.winfo_width())
        altura = max(300, self.canvas_mapa.winfo_height())
        margem = 14
        espaco = 6
        larg_cel = (largura - 2 * margem - (COLUNAS_MAPA - 1) * espaco) / COLUNAS_MAPA
        alt_cel = (altura - 2 * margem - (LINHAS_MAPA - 1) * espaco) / LINHAS_MAPA

        for t in self.estado["territorios"]:
            x0 = margem + t["coluna"] * (larg_cel + espaco)
            y0 = margem + t["linha"] * (alt_cel + espaco)
            x1 = x0 + larg_cel
            y1 = y0 + alt_cel

            info_fac = FACCOES[t["dono"]]
            selecionado = t["id"] == self.territorio_selecionado_id
            cor_borda = COR_DOURADO if selecionado else info_fac["cor_borda"]
            espessura = 4 if selecionado else 2

            ret = self.canvas_mapa.create_rectangle(
                x0, y0, x1, y1,
                fill=info_fac["cor"],
                outline=cor_borda,
                width=espessura,
                tags=(f"ter_{t['id']}",),
            )
            self.celulas_canvas[ret] = t["id"]

            simbolo = TIPOS_TERRITORIO[t["tipo"]]["simbolo"]
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            self.canvas_mapa.create_text(
                cx, y0 + 16,
                text=t["nome"],
                fill="#FFFFFF",
                font=("Segoe UI", 8, "bold"),
            )
            self.canvas_mapa.create_text(
                cx, cy + 2,
                text=f"{simbolo} {t['guarnicao']} tropas",
                fill="#FFFFFF",
                font=("Segoe UI", 10, "bold"),
            )
            self.canvas_mapa.create_text(
                cx, y1 - 12,
                text=t["tipo"],
                fill="#E8EEF2",
                font=("Segoe UI", 8),
            )

    def _ao_clicar_mapa(self, evento: tk.Event) -> None:
        largura = max(300, self.canvas_mapa.winfo_width())
        altura = max(300, self.canvas_mapa.winfo_height())
        margem = 14
        espaco = 6
        larg_cel = (largura - 2 * margem - (COLUNAS_MAPA - 1) * espaco) / COLUNAS_MAPA
        alt_cel = (altura - 2 * margem - (LINHAS_MAPA - 1) * espaco) / LINHAS_MAPA

        col = int((evento.x - margem) // (larg_cel + espaco))
        lin = int((evento.y - margem) // (alt_cel + espaco))
        if 0 <= lin < LINHAS_MAPA and 0 <= col < COLUNAS_MAPA:
            self.territorio_selecionado_id = lin * COLUNAS_MAPA + col
            self.atualizar_tudo()

    def atualizar_tudo(self) -> None:
        """Atualiza todos os painéis visuais a partir do estado atual."""
        rec = self.estado["recursos"]
        prod = calcular_producao_turno(self.estado)
        manut = calcular_manutencao_turno(self.estado)

        self.lbl_turno.config(text=f"Turno {self.estado['turno']}")
        self.lbl_recursos.config(
            text=(
                f"Ouro: {rec['ouro']} (+{prod['ouro']}/-{manut['ouro']})  |  "
                f"Madeira: {rec['madeira']} (+{prod['madeira']})  |  "
                f"Ferro: {rec['ferro']} (+{prod['ferro']})  |  "
                f"Alimentos: {rec['alimentos']} (+{prod['alimentos']}/-{manut['alimentos']})"
            )
        )

        contagem = contar_territorios_por_dono(self.estado)
        tropas_jog = calcular_total_tropas(self.estado, "jogador")
        self.lbl_exercito.config(
            text=(
                f"Exército Total: {tropas_jog} soldados  |  "
                f"Territórios: {contagem['jogador']}/{TOTAL_TERRITORIOS}  |  "
                f"Valória: {contagem['inimigo_1']}  |  Kael: {contagem['inimigo_2']}"
            )
        )
        self.lbl_legenda.config(
            text="Cores: Azul = Tu | Vermelho = Reino de Valória | Roxo = Império de Kael | Cinza = Neutro"
        )
        self.lbl_objetivo.config(
            text=f"Objetivo: ≥{OBJETIVO_TERRITORIOS_VITORIA} territórios e derrotar rivais ({contagem['jogador']}/{TOTAL_TERRITORIOS})"
        )
        self.barra_dominio["value"] = contagem["jogador"]

        self._desenhar_mapa()
        self._atualizar_painel_territorio()
        self._atualizar_painel_melhorias()
        self._atualizar_painel_tecnologias()
        self._atualizar_registo()

    def _atualizar_painel_territorio(self) -> None:
        t = obter_territorio(self.estado, self.territorio_selecionado_id or 0)
        if t is None:
            return

        dono_nome = FACCOES[t["dono"]]["nome"]
        prod = t["producao"]
        self.lbl_ter_nome.config(text=f"{t['nome']} ({t['tipo']})")
        self.lbl_ter_detalhes.config(
            text=(
                f"Proprietário: {dono_nome}\n"
                f"Guarnição: {t['guarnicao']} soldados  |  Defesa terreno: x{t['defesa_base']:.2f}\n"
                f"Produção base: +{prod['ouro']} ouro, +{prod['madeira']} madeira, "
                f"+{prod['ferro']} ferro, +{prod['alimentos']} alimentos"
            )
        )

        eh_meu = t["dono"] == "jogador"
        em_curso = self.estado["estado_jogo"] == "em_curso"
        self.btn_recrutar.config(state=tk.NORMAL if (eh_meu and em_curso) else tk.DISABLED)

        vizinhos = obter_vizinhos_aliados(self.estado, t["id"], "jogador")
        opcoes = [f"{v['id']} - {v['nome']} ({v['guarnicao']} tropas)" for v in vizinhos]
        self.combo_origem["values"] = opcoes
        if opcoes:
            if self.var_origem.get() not in opcoes:
                self.var_origem.set(opcoes[0])
        else:
            self.var_origem.set("")

        tem_vizinho_capaz = any(v["guarnicao"] > 1 for v in vizinhos)
        self.btn_atacar.config(
            state=tk.NORMAL if (not eh_meu and tem_vizinho_capaz and em_curso) else tk.DISABLED
        )
        self.btn_mover.config(
            state=tk.NORMAL if (eh_meu and tem_vizinho_capaz and em_curso) else tk.DISABLED
        )

    def _atualizar_painel_melhorias(self) -> None:
        for chave, info in MELHORIAS_DISPONIVEIS.items():
            nivel = self.estado["melhorias"].get(chave, 0)
            fator_custo = 1.0 + 0.5 * nivel
            custo = {k: int(round(v * fator_custo)) for k, v in info["custo"].items()}
            lbl, btn = self.widgets_melhorias[chave]
            if nivel >= info["nivel_max"]:
                texto = f"Nível {nivel}/{info['nivel_max']} (MÁXIMO) — {info['descricao']}"
                btn.config(state=tk.DISABLED, text="Máximo")
            else:
                texto = (
                    f"Nível {nivel}/{info['nivel_max']} — {info['descricao']}\n"
                    f"Próximo custo: {custo['ouro']} ouro, {custo['madeira']} madeira, {custo['ferro']} ferro"
                )
                estado_btn = tk.NORMAL if self.estado["estado_jogo"] == "em_curso" else tk.DISABLED
                btn.config(state=estado_btn, text="Melhorar")
            lbl.config(text=texto)

    def _atualizar_painel_tecnologias(self) -> None:
        for chave, info in TECNOLOGIAS_DISPONIVEIS.items():
            lbl, btn = self.widgets_tech[chave]
            custo = info["custo"]
            req = info["requisito"]
            req_txt = f" | Requer: {TECNOLOGIAS_DISPONIVEIS[req]['nome']}" if req else ""
            if chave in self.estado["tecnologias"]:
                lbl.config(text=f"[INVESTIGADA] {info['descricao']}")
                btn.config(state=tk.DISABLED, text="Concluída")
            else:
                lbl.config(
                    text=(
                        f"{info['descricao']}\n"
                        f"Custo: {custo['ouro']} ouro, {custo['madeira']} madeira, {custo['ferro']} ferro{req_txt}"
                    )
                )
                estado_btn = tk.NORMAL if self.estado["estado_jogo"] == "em_curso" else tk.DISABLED
                btn.config(state=estado_btn, text="Investigar")

    def _atualizar_registo(self) -> None:
        self.txt_registo.config(state=tk.NORMAL)
        self.txt_registo.delete("1.0", tk.END)
        for linha in reversed(self.estado["registo"]):
            self.txt_registo.insert(tk.END, f"• {linha}\n")
        self.txt_registo.config(state=tk.DISABLED)

    def _obter_origem_selecionada(self) -> int | None:
        texto = self.var_origem.get().strip()
        if not texto or " - " not in texto:
            return None
        try:
            return int(texto.split(" - ", 1)[0])
        except ValueError:
            return None

    def _acao_recrutar(self) -> None:
        if self.territorio_selecionado_id is None:
            return
        try:
            qtd = int(self.var_qtd_recrutar.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Valor inválido", "Introduz uma quantidade inteira positiva.")
            return
        ok, msg = recrutar_soldados(self.estado, self.territorio_selecionado_id, qtd)
        if not ok:
            messagebox.showwarning("Recrutamento", msg)
        self.atualizar_tudo()

    def _acao_atacar(self) -> None:
        origem_id = self._obter_origem_selecionada()
        if origem_id is None or self.territorio_selecionado_id is None:
            messagebox.showwarning("Ataque", "Seleciona um território aliado adjacente como origem.")
            return
        try:
            qtd = int(self.var_tropas_op.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Valor inválido", "Quantidade de tropas inválida.")
            return
        venceu, msg = atacar_territorio(self.estado, origem_id, self.territorio_selecionado_id, qtd)
        if venceu:
            messagebox.showinfo("Combate", msg)
        else:
            messagebox.showwarning("Combate", msg)
        self.atualizar_tudo()
        self._verificar_alerta_fim()

    def _acao_mover(self) -> None:
        origem_id = self._obter_origem_selecionada()
        if origem_id is None or self.territorio_selecionado_id is None:
            return
        try:
            qtd = int(self.var_tropas_op.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Valor inválido", "Quantidade de tropas inválida.")
            return
        ok, msg = mover_tropas(self.estado, origem_id, self.territorio_selecionado_id, qtd)
        if not ok:
            messagebox.showwarning("Movimentação", msg)
        self.atualizar_tudo()

    def _acao_melhorar(self, chave: str) -> None:
        ok, msg = construir_melhoria(self.estado, chave)
        if not ok:
            messagebox.showwarning("Melhoria", msg)
        else:
            messagebox.showinfo("Melhoria", msg)
        self.atualizar_tudo()

    def _acao_investigar(self, chave: str) -> None:
        ok, msg = investigar_tecnologia(self.estado, chave)
        if not ok:
            messagebox.showwarning("Investigação", msg)
        else:
            messagebox.showinfo("Investigação", msg)
        self.atualizar_tudo()

    def _acao_terminar_turno(self) -> None:
        terminar_turno(self.estado)
        self.atualizar_tudo()
        self._verificar_alerta_fim()

    def _verificar_alerta_fim(self) -> None:
        if self.estado["estado_jogo"] == "vitoria":
            messagebox.showinfo("Vitória!", self.estado["motivo_fim"])
        elif self.estado["estado_jogo"] == "derrota":
            messagebox.showerror("Derrota", self.estado["motivo_fim"])

    def _acao_novo_jogo(self) -> None:
        if messagebox.askyesno("Novo Jogo", "Tens a certeza que queres iniciar uma nova campanha?"):
            self.estado = criar_novo_jogo()
            self.territorio_selecionado_id = 20
            self.atualizar_tudo()

    def _acao_guardar(self) -> None:
        ok, msg = guardar_partida(self.estado)
        if ok:
            messagebox.showinfo("Guardar", msg)
        else:
            messagebox.showerror("Guardar", msg)

    def _acao_carregar(self) -> None:
        dados, msg = carregar_partida()
        if dados is None:
            messagebox.showwarning("Carregar", msg)
            return
        self.estado = dados
        self.territorio_selecionado_id = 20
        self.atualizar_tudo()
        messagebox.showinfo("Carregar", msg)


def iniciar_interface() -> None:
    """Inicia a janela principal do jogo Empire."""
    raiz = tk.Tk()
    AplicacaoEmpire(raiz)
    raiz.mainloop()
