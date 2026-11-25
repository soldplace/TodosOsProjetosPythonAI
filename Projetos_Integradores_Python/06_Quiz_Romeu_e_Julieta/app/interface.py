"""Interface gráfica roxa e colorida (estilo Kahoot/Duolingo) do Quiz Romeu e Julieta."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.armazenamento import carregar_classificacoes, guardar_resultado_sessao
from app.dados import TOTAL_PERGUNTAS_SESSAO
from app.logica import (
    criar_nova_sessao,
    responder_pergunta,
    selecionar_proxima_pergunta,
)

COR_FUNDO = "#2B1055"
COR_PAINEL = "#3C1874"
COR_CARTAO = "#FFFFFF"
COR_TEXTO_CLARO = "#FFFFFF"
COR_TEXTO_ESCURO = "#1F1235"
COR_DOURADO = "#FFD166"

CORES_OPCOES = [
    ("#E21B3C", "#FF4B6B", "▲"),
    ("#1368CE", "#3A8DFF", "◆"),
    ("#D89E00", "#F0B922", "●"),
    ("#26890C", "#39B518", "■"),
]


class AplicacaoQuizRomeuJulieta:
    """Controlador das telas do Quiz Adaptativo: Romeu e Julieta."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Quiz Adaptativo — Romeu e Julieta")
        self.raiz.geometry("1040x720")
        self.raiz.minsize(920, 640)
        self.raiz.configure(bg=COR_FUNDO)

        self.estado: dict | None = None
        self.botoes_opcoes: list[tk.Button] = []

        self._configurar_estilos()
        self.container = tk.Frame(self.raiz, bg=COR_FUNDO)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.mostrar_ecra_inicial()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure(
            "Quiz.Horizontal.TProgressbar",
            troughcolor="#1D0A3B",
            background=COR_DOURADO,
            thickness=14,
        )
        estilo.configure(
            "Treeview",
            background="#220D44",
            foreground="#FFFFFF",
            fieldbackground="#220D44",
            rowheight=26,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Treeview.Heading",
            background=COR_PAINEL,
            foreground=COR_DOURADO,
            font=("Segoe UI", 10, "bold"),
        )

    def _limpar_container(self) -> None:
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_ecra_inicial(self) -> None:
        """Mostra o ecrã de boas-vindas e entrada do nome do jogador."""
        self._limpar_container()

        cartao = tk.Frame(self.container, bg=COR_PAINEL, bd=0, padx=36, pady=32)
        cartao.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.72)

        tk.Label(
            cartao,
            text="🎭 Quiz Adaptativo: Romeu e Julieta",
            bg=COR_PAINEL,
            fg=COR_DOURADO,
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(0, 8))

        tk.Label(
            cartao,
            text="Obra de William Shakespeare • 10 Perguntas por Ronda",
            bg=COR_PAINEL,
            fg=COR_TEXTO_CLARO,
            font=("Segoe UI", 12),
        ).pack(pady=(0, 18))

        tk.Label(
            cartao,
            text=(
                "Como funciona o sistema adaptativo:\n"
                "• Começas no nível Médio. Acertar consecutivamente aumenta a dificuldade e os pontos!\n"
                "• Se errares duas seguidas, a dificuldade ajusta-se para te ajudar a consolidar."
            ),
            bg="#4A218A",
            fg="#F2E9FF",
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            padx=16,
            pady=12,
        ).pack(fill=tk.X, pady=(0, 22))

        tk.Label(
            cartao,
            text="Introduz o teu nome de jogador:",
            bg=COR_PAINEL,
            fg=COR_TEXTO_CLARO,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor=tk.W)

        self.var_nome = tk.StringVar()
        entrada = tk.Entry(
            cartao,
            textvariable=self.var_nome,
            font=("Segoe UI", 13),
            bg="#FFFFFF",
            fg=COR_TEXTO_ESCURO,
            relief=tk.FLAT,
        )
        entrada.pack(fill=tk.X, ipady=6, pady=(6, 18))
        entrada.focus_set()
        entrada.bind("<Return>", lambda _e: self._iniciar_quiz())

        frame_btns = tk.Frame(cartao, bg=COR_PAINEL)
        frame_btns.pack(fill=tk.X)

        tk.Button(
            frame_btns,
            text="▶ Começar Quiz",
            bg="#26890C",
            fg="#FFFFFF",
            activebackground="#39B518",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._iniciar_quiz,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))

        tk.Button(
            frame_btns,
            text="🏆 Ver Classificações",
            bg="#1368CE",
            fg="#FFFFFF",
            activebackground="#3A8DFF",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.mostrar_ecra_resultados_ou_ranking,
        ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(8, 0))

    def _iniciar_quiz(self) -> None:
        nome = self.var_nome.get().strip()
        if not nome:
            messagebox.showwarning("Nome obrigatório", "Por favor, escreve o teu nome antes de começar.")
            return
        self.estado = criar_nova_sessao(nome, TOTAL_PERGUNTAS_SESSAO)
        selecionar_proxima_pergunta(self.estado)
        self.mostrar_ecra_pergunta()

    def mostrar_ecra_pergunta(self) -> None:
        """Constrói e exibe a pergunta atual com os 4 botões coloridos."""
        if self.estado is None or self.estado["terminado"] or self.estado["pergunta_atual"] is None:
            self._finalizar_quiz()
            return

        self._limpar_container()
        pergunta = self.estado["pergunta_atual"]
        num_atual = self.estado["perguntas_respondidas"] + 1
        total = self.estado["total_perguntas"]

        # Barra de estado superior
        barra_sup = tk.Frame(self.container, bg=COR_PAINEL, padx=16, pady=12)
        barra_sup.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            barra_sup,
            text=f"Jogador: {self.estado['jogador']}",
            bg=COR_PAINEL,
            fg=COR_TEXTO_CLARO,
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            barra_sup,
            text=f"Pergunta {num_atual}/{total}",
            bg=COR_PAINEL,
            fg=COR_DOURADO,
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT, padx=24)

        cores_dif = {"Fácil": "#2ECC71", "Média": "#F39C12", "Difícil": "#E74C3C"}
        dif_atual = self.estado["dificuldade_atual"]
        tk.Label(
            barra_sup,
            text=f"Nível: {dif_atual}",
            bg=cores_dif.get(dif_atual, "#9B59B6"),
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=3,
        ).pack(side=tk.LEFT, padx=8)

        tk.Label(
            barra_sup,
            text=f"🔥 Sequência: {self.estado['sequencia_acertos']}  |  ⭐ Pontos: {self.estado['pontuacao']}",
            bg=COR_PAINEL,
            fg=COR_DOURADO,
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.RIGHT)

        progresso = ttk.Progressbar(
            self.container,
            style="Quiz.Horizontal.TProgressbar",
            maximum=total,
            value=self.estado["perguntas_respondidas"],
        )
        progresso.pack(fill=tk.X, pady=(0, 14))

        # Cartão branco da pergunta
        cartao_perg = tk.Frame(self.container, bg=COR_CARTAO, padx=28, pady=24)
        cartao_perg.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            cartao_perg,
            text=f"Categoria: {pergunta['categoria']}  •  Dificuldade da Pergunta: {pergunta['dificuldade']}",
            bg=COR_CARTAO,
            fg="#6B4C9A",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 8))

        tk.Label(
            cartao_perg,
            text=pergunta["pergunta"],
            bg=COR_CARTAO,
            fg=COR_TEXTO_ESCURO,
            font=("Segoe UI", 16, "bold"),
            wraplength=900,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        # Grelha 2x2 de botões coloridos
        frame_opcoes = tk.Frame(self.container, bg=COR_FUNDO)
        frame_opcoes.pack(fill=tk.BOTH, expand=True)
        frame_opcoes.columnconfigure(0, weight=1)
        frame_opcoes.columnconfigure(1, weight=1)
        frame_opcoes.rowconfigure(0, weight=1)
        frame_opcoes.rowconfigure(1, weight=1)

        self.botoes_opcoes = []
        for idx, texto_op in enumerate(pergunta["opcoes"]):
            cor, cor_hover, simbolo = CORES_OPCOES[idx]
            btn = tk.Button(
                frame_opcoes,
                text=f"{simbolo}  {texto_op}",
                bg=cor,
                fg="#FFFFFF",
                activebackground=cor_hover,
                activeforeground="#FFFFFF",
                font=("Segoe UI", 12, "bold"),
                wraplength=410,
                justify=tk.LEFT,
                relief=tk.FLAT,
                padx=18,
                pady=14,
                cursor="hand2",
                command=lambda i=idx: self._ao_responder(i),
            )
            btn.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=8, pady=8)
            self.botoes_opcoes.append(btn)

        # Painel de feedback (inicialmente oculto/vazio até responder)
        self.frame_feedback = tk.Frame(self.container, bg=COR_PAINEL, padx=18, pady=12)
        self.lbl_feedback_tit = tk.Label(
            self.frame_feedback, text="", bg=COR_PAINEL, fg=COR_DOURADO, font=("Segoe UI", 12, "bold")
        )
        self.lbl_feedback_tit.pack(anchor=tk.W)
        self.lbl_feedback_exp = tk.Label(
            self.frame_feedback,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO_CLARO,
            font=("Segoe UI", 10),
            wraplength=760,
            justify=tk.LEFT,
        )
        self.lbl_feedback_exp.pack(side=tk.LEFT, anchor=tk.W, pady=(4, 0))
        self.btn_proxima = tk.Button(
            self.frame_feedback,
            text="Próxima ▶",
            bg=COR_DOURADO,
            fg="#1F1235",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._avancar_pergunta,
        )
        self.btn_proxima.pack(side=tk.RIGHT, padx=(12, 0))

    def _ao_responder(self, indice: int) -> None:
        if self.estado is None:
            return
        for btn in self.botoes_opcoes:
            btn.config(state=tk.DISABLED)

        ok, res = responder_pergunta(self.estado, indice)
        if not ok:
            messagebox.showerror("Erro", res.get("erro", "Erro ao responder."))
            return

        if res["correta"]:
            self.lbl_feedback_tit.config(
                text=f"✔ Resposta Correta! +{res['pontos_ganhos']} pontos  |  {res['aviso_adaptacao']}",
                fg="#52E07A",
            )
        else:
            self.lbl_feedback_tit.config(
                text=f"✘ Incorreta! Resposta certa: {res['resposta_correta']}  |  {res['aviso_adaptacao']}",
                fg="#FF6B81",
            )

        self.lbl_feedback_exp.config(text=res["explicacao"])
        if self.estado["terminado"]:
            self.btn_proxima.config(text="Ver Resultados ▶")
        self.frame_feedback.pack(fill=tk.X, pady=(8, 0))

    def _avancar_pergunta(self) -> None:
        if self.estado is None:
            return
        if self.estado["terminado"]:
            self._finalizar_quiz()
            return
        selecionar_proxima_pergunta(self.estado)
        self.mostrar_ecra_pergunta()

    def _finalizar_quiz(self) -> None:
        if self.estado is not None:
            _, ranking, _ = guardar_resultado_sessao(self.estado)
        else:
            ranking = carregar_classificacoes()
        self.mostrar_ecra_resultados_ou_ranking(ranking=ranking, com_resumo=True)

    def mostrar_ecra_resultados_ou_ranking(
        self, ranking: list[dict] | None = None, com_resumo: bool = False
    ) -> None:
        """Exibe o resumo da ronda (se aplicável) e a tabela de classificações."""
        self._limpar_container()
        lista = ranking if ranking is not None else carregar_classificacoes()

        topo = tk.Frame(self.container, bg=COR_PAINEL, padx=22, pady=18)
        topo.pack(fill=tk.X, pady=(0, 14))

        if com_resumo and self.estado is not None:
            pct = round((self.estado["acertos"] / max(1, self.estado["total_perguntas"])) * 100)
            tk.Label(
                topo,
                text=f"🎉 Ronda Concluída, {self.estado['jogador']}!",
                bg=COR_PAINEL,
                fg=COR_DOURADO,
                font=("Segoe UI", 18, "bold"),
            ).pack(anchor=tk.W)
            tk.Label(
                topo,
                text=(
                    f"Pontuação Final: {self.estado['pontuacao']} pts  |  "
                    f"Acertos: {self.estado['acertos']}/{self.estado['total_perguntas']} ({pct}%)  |  "
                    f"Melhor Sequência: {self.estado['melhor_sequencia']}  |  "
                    f"Nível Final: {self.estado['dificuldade_atual']}"
                ),
                bg=COR_PAINEL,
                fg=COR_TEXTO_CLARO,
                font=("Segoe UI", 11),
            ).pack(anchor=tk.W, pady=(6, 0))
        else:
            tk.Label(
                topo,
                text="🏆 Quadro de Classificações — Romeu e Julieta",
                bg=COR_PAINEL,
                fg=COR_DOURADO,
                font=("Segoe UI", 18, "bold"),
            ).pack(anchor=tk.W)

        frame_tab = tk.Frame(self.container, bg=COR_PAINEL, padx=14, pady=14)
        frame_tab.pack(fill=tk.BOTH, expand=True)

        cols = ("pos", "jogador", "pontos", "acertos", "seq", "dif", "data")
        tabela = ttk.Treeview(frame_tab, columns=cols, show="headings", height=12)
        for c, tit, larg in [
            ("pos", "#", 45),
            ("jogador", "Jogador", 200),
            ("pontos", "Pontuação", 100),
            ("acertos", "Acertos", 90),
            ("seq", "Melhor Seq.", 95),
            ("dif", "Nível Final", 100),
            ("data", "Data/Hora", 145),
        ]:
            tabela.heading(c, text=tit)
            tabela.column(c, width=larg, anchor=tk.CENTER)

        for idx, reg in enumerate(lista[:20], start=1):
            tabela.insert(
                "",
                tk.END,
                values=(
                    idx,
                    reg.get("jogador", ""),
                    reg.get("pontuacao", 0),
                    f"{reg.get('acertos', 0)}/{reg.get('total_perguntas', 10)}",
                    reg.get("melhor_sequencia", 0),
                    reg.get("dificuldade_final", "-"),
                    reg.get("data", "-"),
                ),
            )
        tabela.pack(fill=tk.BOTH, expand=True)

        rodape = tk.Frame(self.container, bg=COR_FUNDO)
        rodape.pack(fill=tk.X, pady=(14, 0))
        tk.Button(
            rodape,
            text="↺ Voltar ao Início / Novo Jogo",
            bg="#26890C",
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=18,
            pady=10,
            cursor="hand2",
            command=self.mostrar_ecra_inicial,
        ).pack(side=tk.RIGHT)


def iniciar_interface() -> None:
    """Inicia a janela principal do Quiz Romeu e Julieta."""
    raiz = tk.Tk()
    AplicacaoQuizRomeuJulieta(raiz)
    raiz.mainloop()
