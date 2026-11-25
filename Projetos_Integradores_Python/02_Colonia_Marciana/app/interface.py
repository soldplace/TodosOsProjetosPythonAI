"""Interface gráfica espacial da Colónia Marciana em Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.armazenamento import carregar_colonia, guardar_colonia
from app.dados import DIAS_OBJETIVO, INFRAESTRUTURAS, LIMITES_RECURSOS
from app.logica import (
    acolher_colonos,
    avancar_dia,
    calcular_balanco_previsto,
    calcular_capacidade_habitacional,
    construir_estrutura,
    criar_nova_colonia,
    melhorar_estrutura,
)

COR_FUNDO = "#1C1012"
COR_PAINEL = "#2B181C"
COR_CARD = "#3A2026"
COR_LARANJA = "#E06D3B"
COR_TEXTO = "#F5EBE6"
COR_TEXTO_SEC = "#CFAEA6"


class AplicacaoColoniaMarciana:
    """Controlador da interface do simulador Colónia Marciana."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Colónia Marciana — Simulador Ares-1")
        self.raiz.geometry("1160x750")
        self.raiz.minsize(1020, 660)
        self.raiz.configure(bg=COR_FUNDO)

        self.estado = criar_nova_colonia()
        self.barras_recursos: dict[str, tuple[ttk.Progressbar, ttk.Label]] = {}
        self.cards_estruturas: dict[str, tuple[ttk.Label, ttk.Button, ttk.Button]] = {}

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
            foreground=COR_TEXTO_SEC,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Marte.TButton",
            background=COR_LARANJA,
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Marte.TButton", background=[("active", "#F08354")])
        estilo.configure(
            "Sec.TButton",
            background="#4C2B32",
            foreground=COR_TEXTO,
            font=("Segoe UI", 9, "bold"),
            padding=5,
        )
        estilo.map("Sec.TButton", background=[("active", "#633842")])

        cores_barras = {
            "energia": "#F0A202",
            "agua": "#3A86FF",
            "oxigenio": "#4CC9F0",
            "alimentos": "#52B788",
            "materiais": "#E07A5F",
        }
        for chave, cor in cores_barras.items():
            estilo.configure(
                f"{chave}.Horizontal.TProgressbar",
                troughcolor="#160C0E",
                background=cor,
                thickness=14,
            )

    def _construir_interface(self) -> None:
        topo = ttk.Frame(self.raiz, style="Painel.TFrame", padding=(14, 10))
        topo.pack(fill=tk.X, padx=10, pady=(10, 6))

        self.lbl_dia = ttk.Label(topo, text="Sol 1 / 30", style="Titulo.TLabel")
        self.lbl_dia.pack(side=tk.LEFT)

        self.lbl_estado_colonia = ttk.Label(topo, text="", style="Txt.TLabel")
        self.lbl_estado_colonia.pack(side=tk.LEFT, padx=20)

        btns_topo = ttk.Frame(topo, style="Painel.TFrame")
        btns_topo.pack(side=tk.RIGHT)
        ttk.Button(btns_topo, text="Nova Colónia", style="Sec.TButton", command=self._acao_nova).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns_topo, text="Guardar", style="Sec.TButton", command=self._acao_guardar).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns_topo, text="Carregar", style="Sec.TButton", command=self._acao_carregar).pack(
            side=tk.LEFT, padx=4
        )
        self.btn_proximo_dia = ttk.Button(
            btns_topo,
            text="Avançar Sol ▶",
            style="Marte.TButton",
            command=self._acao_avancar_dia,
        )
        self.btn_proximo_dia.pack(side=tk.LEFT, padx=(10, 0))

        corpo = ttk.Frame(self.raiz)
        corpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Coluna esquerda: Recursos + Vista visual da colónia + Relatório
        col_esq = ttk.Frame(corpo, style="Painel.TFrame", padding=12)
        col_esq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ttk.Label(col_esq, text="Painel de Suporte de Vida e Recursos", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(0, 6)
        )

        frame_barras = ttk.Frame(col_esq, style="Painel.TFrame")
        frame_barras.pack(fill=tk.X, pady=(0, 8))

        nomes_rec = [
            ("energia", "Energia"),
            ("agua", "Água"),
            ("oxigenio", "Oxigénio"),
            ("alimentos", "Alimentos"),
            ("materiais", "Materiais"),
        ]
        for idx, (chave, nome) in enumerate(nomes_rec):
            ttk.Label(frame_barras, text=nome, style="Txt.TLabel", width=11).grid(
                row=idx, column=0, sticky=tk.W, pady=3
            )
            barra = ttk.Progressbar(
                frame_barras,
                style=f"{chave}.Horizontal.TProgressbar",
                maximum=LIMITES_RECURSOS[chave],
            )
            barra.grid(row=idx, column=1, sticky=tk.EW, padx=8, pady=3)
            lbl_val = ttk.Label(frame_barras, text="", style="Sec.TLabel", width=28)
            lbl_val.grid(row=idx, column=2, sticky=tk.W)
            self.barras_recursos[chave] = (barra, lbl_val)
        frame_barras.columnconfigure(1, weight=1)

        ttk.Label(col_esq, text="Vista da Base Marciana Ares-1", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(6, 4)
        )
        self.canvas_base = tk.Canvas(
            col_esq, height=250, bg="#361915", highlightthickness=1, highlightbackground=COR_LARANJA
        )
        self.canvas_base.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.canvas_base.bind("<Configure>", lambda _e: self._desenhar_colonia())

        ttk.Label(col_esq, text="Relatório Diário e Eventos", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(2, 4)
        )
        self.txt_relatorio = tk.Text(
            col_esq,
            height=8,
            bg="#150B0D",
            fg=COR_TEXTO,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=8,
            pady=6,
        )
        self.txt_relatorio.pack(fill=tk.X)

        # Coluna direita: Gestão de Construções e População
        col_dir = ttk.Frame(corpo, style="Painel.TFrame", padding=12, width=460)
        col_dir.pack(side=tk.RIGHT, fill=tk.BOTH)
        col_dir.pack_propagate(False)

        frame_pop = ttk.Frame(col_dir, style="Card.TFrame", padding=10)
        frame_pop.pack(fill=tk.X, pady=(0, 10))
        self.lbl_pop_info = ttk.Label(
            frame_pop,
            text="",
            background=COR_CARD,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        )
        self.lbl_pop_info.pack(side=tk.LEFT)
        self.btn_acolher = ttk.Button(
            frame_pop,
            text="+2 Colonos (16 alim, 12 água)",
            style="Sec.TButton",
            command=self._acao_acolher,
        )
        self.btn_acolher.pack(side=tk.RIGHT)

        ttk.Label(col_dir, text="Menu de Construções e Melhorias", style="Sub.TLabel").pack(
            anchor=tk.W, pady=(0, 6)
        )

        for chave, espec in INFRAESTRUTURAS.items():
            card = ttk.Frame(col_dir, style="Card.TFrame", padding=8)
            card.pack(fill=tk.X, pady=4)

            cab = ttk.Frame(card, style="Card.TFrame")
            cab.pack(fill=tk.X)
            ttk.Label(
                cab,
                text=espec["nome"],
                background=COR_CARD,
                foreground=espec["cor"],
                font=("Segoe UI", 10, "bold"),
            ).pack(side=tk.LEFT)

            btn_mel = ttk.Button(
                cab,
                text="Melhorar",
                style="Sec.TButton",
                command=lambda c=chave: self._acao_melhorar(c),
            )
            btn_mel.pack(side=tk.RIGHT, padx=(4, 0))
            btn_const = ttk.Button(
                cab,
                text="Construir",
                style="Marte.TButton",
                command=lambda c=chave: self._acao_construir(c),
            )
            btn_const.pack(side=tk.RIGHT)

            lbl_det = ttk.Label(
                card,
                text="",
                background=COR_CARD,
                foreground=COR_TEXTO,
                font=("Segoe UI", 8),
                wraplength=415,
            )
            lbl_det.pack(anchor=tk.W, pady=(4, 0))
            self.cards_estruturas[chave] = (lbl_det, btn_const, btn_mel)

    def _desenhar_colonia(self) -> None:
        self.canvas_base.delete("all")
        largura = max(400, self.canvas_base.winfo_width())
        altura = max(200, self.canvas_base.winfo_height())

        # Céu marciano e solo
        cor_ceu = "#5A2A1E" if self.estado["dias_tempestade"] > 0 else "#2D1418"
        self.canvas_base.create_rectangle(0, 0, largura, altura * 0.42, fill=cor_ceu, outline="")
        self.canvas_base.create_rectangle(
            0, altura * 0.42, largura, altura, fill="#6F2D1F", outline=""
        )

        # Crateras decorativas no fundo
        self.canvas_base.create_oval(30, altura * 0.65, 110, altura * 0.80, outline="#542015", width=2)
        self.canvas_base.create_oval(
            largura - 140, altura * 0.55, largura - 40, altura * 0.72, outline="#542015", width=2
        )

        if self.estado["dias_tempestade"] > 0:
            self.canvas_base.create_text(
                largura / 2,
                22,
                text="⚠ TEMPESTADE DE POEIRA ATIVA (Eficiência Solar -40%)",
                fill="#FFD166",
                font=("Segoe UI", 10, "bold"),
            )

        chaves = list(INFRAESTRUTURAS.keys())
        colunas = 3
        larg_bloco = (largura - 60) / colunas
        alt_bloco = (altura - 70) / 2

        for idx, chave in enumerate(chaves):
            col = idx % colunas
            lin = idx // colunas
            cx = 30 + col * larg_bloco + larg_bloco / 2
            cy = 50 + lin * alt_bloco + alt_bloco / 2

            espec = INFRAESTRUTURAS[chave]
            dados_est = self.estado["estruturas"][chave]

            if chave == "cupula":
                self.canvas_base.create_arc(
                    cx - 42, cy - 28, cx + 42, cy + 36,
                    start=0, extent=180,
                    fill=espec["cor"], outline="#FFFFFF", width=2,
                )
            elif chave == "painel_solar":
                self.canvas_base.create_polygon(
                    cx - 36, cy + 12, cx - 20, cy - 16, cx + 36, cy - 16, cx + 20, cy + 12,
                    fill=espec["cor"], outline="#FFFFFF", width=2,
                )
            else:
                self.canvas_base.create_rectangle(
                    cx - 32, cy - 18, cx + 32, cy + 18,
                    fill=espec["cor"], outline="#FFFFFF", width=2,
                )

            self.canvas_base.create_text(
                cx, cy + 28,
                text=f"{espec['nome']} ({dados_est['quantidade']}x | Nv.{dados_est['nivel']})",
                fill="#FFFFFF",
                font=("Segoe UI", 8, "bold"),
            )

    def atualizar_interface(self) -> None:
        """Sincroniza todos os widgets com o estado da simulação."""
        self.lbl_dia.config(text=f"Sol {self.estado['dia']} / {DIAS_OBJETIVO}")
        tempestade_txt = (
            f"  |  Tempestade: {self.estado['dias_tempestade']} sol(s)"
            if self.estado["dias_tempestade"] > 0
            else "  |  Clima: Estável"
        )
        self.lbl_estado_colonia.config(
            text=f"Moral: {self.estado['moral']}%{tempestade_txt}"
        )

        balanco = calcular_balanco_previsto(self.estado)
        prod = balanco["producao"]
        cons = balanco["consumo"]

        for chave, (barra, lbl) in self.barras_recursos.items():
            atual = self.estado["recursos"][chave]
            limite = LIMITES_RECURSOS[chave]
            saldo = prod[chave] - cons[chave]
            sinal = "+" if saldo >= 0 else ""
            barra["value"] = atual
            lbl.config(text=f"{atual}/{limite} ({sinal}{saldo}/sol)")

        cap = calcular_capacidade_habitacional(self.estado)
        self.lbl_pop_info.config(text=f"População: {self.estado['populacao']} / {cap} colonos")

        em_curso = self.estado["estado_simulacao"] == "em_curso"
        self.btn_proximo_dia.config(state=tk.NORMAL if em_curso else tk.DISABLED)
        self.btn_acolher.config(state=tk.NORMAL if em_curso else tk.DISABLED)

        for chave, (lbl_det, btn_const, btn_mel) in self.cards_estruturas.items():
            espec = INFRAESTRUTURAS[chave]
            est = self.estado["estruturas"][chave]
            c_const = espec["custo_construir"]["materiais"]
            fator_m = 1.0 + 0.4 * (est["nivel"] - 1)
            c_mel = int(round(espec["custo_melhorar"]["materiais"] * fator_m))
            lbl_det.config(
                text=(
                    f"Qtd: {est['quantidade']} | Nível: {est['nivel']}/5 — {espec['descricao']}\n"
                    f"Construir: {c_const} mat. | Melhorar: {c_mel} mat."
                )
            )
            btn_const.config(state=tk.NORMAL if em_curso else tk.DISABLED)
            btn_mel.config(state=tk.NORMAL if (em_curso and est["nivel"] < 5) else tk.DISABLED)

        self.txt_relatorio.config(state=tk.NORMAL)
        self.txt_relatorio.delete("1.0", tk.END)
        for linha in reversed(self.estado["historico"][-25:]):
            self.txt_relatorio.insert(tk.END, f"• {linha}\n")
        self.txt_relatorio.config(state=tk.DISABLED)

        self._desenhar_colonia()

    def _acao_construir(self, chave: str) -> None:
        ok, msg = construir_estrutura(self.estado, chave)
        if not ok:
            messagebox.showwarning("Construção", msg)
        self.atualizar_interface()

    def _acao_melhorar(self, chave: str) -> None:
        ok, msg = melhorar_estrutura(self.estado, chave)
        if not ok:
            messagebox.showwarning("Melhoria", msg)
        self.atualizar_interface()

    def _acao_acolher(self) -> None:
        ok, msg = acolher_colonos(self.estado, 2)
        if not ok:
            messagebox.showwarning("Novos Colonos", msg)
        self.atualizar_interface()

    def _acao_avancar_dia(self) -> None:
        relatorio = avancar_dia(self.estado)
        self.atualizar_interface()

        if self.estado["estado_simulacao"] != "em_curso":
            est = self.estado["estatisticas"]
            resumo_final = (
                f"{self.estado['motivo_fim']}\n\n"
                f"Estatísticas Finais:\n"
                f"- Dias sobrevividos: {self.estado['dia']}\n"
                f"- População final: {self.estado['populacao']}\n"
                f"- Construções feitas: {est['construcoes_feitas']}\n"
                f"- Melhorias aplicadas: {est['melhorias_feitas']}\n"
                f"- Eventos enfrentados: {est['eventos_enfrentados']}"
            )
            if self.estado["estado_simulacao"] == "vitoria":
                messagebox.showinfo("Vitória da Missão!", resumo_final)
            else:
                messagebox.showerror("Colónia Perdida", resumo_final)
        elif any("CRISE" in r or "Evento:" in r for r in relatorio):
            destaques = [r for r in relatorio if "CRISE" in r or "Evento:" in r or "ALERTA" in r]
            if destaques:
                messagebox.showinfo(f"Relatório do Sol {self.estado['dia'] - 1}", "\n".join(destaques))

    def _acao_nova(self) -> None:
        if messagebox.askyesno("Nova Colónia", "Desejas reiniciar a missão marciana?"):
            self.estado = criar_nova_colonia()
            self.atualizar_interface()

    def _acao_guardar(self) -> None:
        ok, msg = guardar_colonia(self.estado)
        if ok:
            messagebox.showinfo("Guardar", msg)
        else:
            messagebox.showerror("Guardar", msg)

    def _acao_carregar(self) -> None:
        dados, msg = carregar_colonia()
        if dados is None:
            messagebox.showwarning("Carregar", msg)
            return
        self.estado = dados
        self.atualizar_interface()
        messagebox.showinfo("Carregar", msg)


def iniciar_interface() -> None:
    """Inicia a janela principal do simulador Colónia Marciana."""
    raiz = tk.Tk()
    AplicacaoColoniaMarciana(raiz)
    raiz.mainloop()
