"""Interface de consola organizada para o Planeamento Alimentar Semanal."""

from __future__ import annotations

from app.armazenamento import carregar_plano, guardar_plano
from app.dados import ALIMENTOS_PREDEFINIDOS, DIAS_SEMANA, NOTA_NUTRICIONAL, REFEICOES
from app.logica import (
    adicionar_alimento_refeicao,
    alterar_quantidade_alimento,
    calcular_nutrientes_porcao,
    calcular_totais_dia,
    calcular_totais_refeicao,
    calcular_totais_semana,
    criar_plano_vazio,
    identificar_refeicoes_nao_planeadas,
    obter_alimento_por_id,
    pesquisar_alimentos,
    remover_alimento_refeicao,
    substituir_refeicao,
)

LARGURA_LINHA = 78


def _separador(caractere: str = "=") -> None:
    print(caractere * LARGURA_LINHA)


def _cabecalho(titulo: str) -> None:
    print()
    _separador("=")
    print(f"  {titulo}")
    _separador("=")


def _ler_inteiro(mensagem: str, minimo: int, maximo: int) -> int | None:
    while True:
        bruto = input(mensagem).strip()
        if bruto.lower() in ("c", "cancelar"):
            return None
        try:
            valor = int(bruto)
            if minimo <= valor <= maximo:
                return valor
            print(f"  [Erro] Escolhe um número entre {minimo} e {maximo}.")
        except ValueError:
            print("  [Erro] Introduz um número inteiro válido (ou 'c' para cancelar).")


def _ler_gramas(mensagem: str) -> float | None:
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        if bruto.lower() in ("c", "cancelar"):
            return None
        try:
            valor = float(bruto)
            if 0 < valor <= 5000:
                return valor
            print("  [Erro] A quantidade deve ser positiva (até 5000g).")
        except ValueError:
            print("  [Erro] Introduz um número válido em gramas (ou 'c' para cancelar).")


def _escolher_dia() -> str | None:
    print("\n  Dias da semana:")
    for idx, dia in enumerate(DIAS_SEMANA, start=1):
        print(f"    {idx}. {dia}")
    op = _ler_inteiro("  Escolhe o dia (1-7, ou 'c' para voltar): ", 1, len(DIAS_SEMANA))
    return DIAS_SEMANA[op - 1] if op is not None else None


def _escolher_refeicao() -> str | None:
    print("\n  Refeições:")
    for idx, ref in enumerate(REFEICOES, start=1):
        print(f"    {idx}. {ref}")
    op = _ler_inteiro("  Escolhe a refeição (1-5, ou 'c' para voltar): ", 1, len(REFEICOES))
    return REFEICOES[op - 1] if op is not None else None


def _mostrar_tabela_alimentos(lista: list[dict]) -> None:
    print(f"\n  {'ID':<4} {'Alimento':<30} {'Kcal':>7} {'Prot(g)':>8} {'Hidr(g)':>8} {'Gord(g)':>8}")
    print("  " + "-" * 70)
    for a in lista:
        print(
            f"  {a['id']:<4} {a['nome']:<30} {a['calorias']:>7.1f} "
            f"{a['proteinas']:>8.1f} {a['hidratos']:>8.1f} {a['gorduras']:>8.1f}"
        )
    print(f"\n  {NOTA_NUTRICIONAL}")


def _barra_prato_nutricional(prot: float, hidr: float, gord: float) -> str:
    total = prot + hidr + gord
    if total <= 0:
        return "[Prato vazio]"
    p_pct = round((prot / total) * 100)
    h_pct = round((hidr / total) * 100)
    g_pct = max(0, 100 - p_pct - h_pct)
    return f"Distribuição do Prato -> Prot: {p_pct}% | Hidratos: {h_pct}% | Gorduras: {g_pct}%"


def _consultar_alimentos() -> None:
    _cabecalho("BASE DE DADOS DE ALIMENTOS (por 100g)")
    termo = input("  Pesquisar por nome (Enter para listar todos): ")
    encontrados = pesquisar_alimentos(termo)
    if not encontrados:
        print("  Nenhum alimento encontrado com esse filtro.")
    else:
        _mostrar_tabela_alimentos(encontrados)


def _adicionar_alimento(plano: dict) -> None:
    _cabecalho("ADICIONAR ALIMENTO A UMA REFEIÇÃO")
    dia = _escolher_dia()
    if dia is None:
        return
    ref = _escolher_refeicao()
    if ref is None:
        return

    _mostrar_tabela_alimentos(ALIMENTOS_PREDEFINIDOS)
    alimento_id = _ler_inteiro("\n  ID do alimento (ou 'c' para cancelar): ", 1, len(ALIMENTOS_PREDEFINIDOS))
    if alimento_id is None:
        return
    gramas = _ler_gramas("  Quantidade em gramas (ex.: 150): ")
    if gramas is None:
        return

    ok, msg = adicionar_alimento_refeicao(plano, dia, ref, alimento_id, gramas)
    print(f"\n  {msg}")


def _gerir_refeicao_existente(plano: dict) -> None:
    _cabecalho("REMOVER, ALTERAR QUANTIDADE OU SUBSTITUIR REFEIÇÃO")
    dia = _escolher_dia()
    if dia is None:
        return
    ref = _escolher_refeicao()
    if ref is None:
        return

    itens = plano["dias"][dia][ref]
    print(f"\n  Conteúdo atual de {dia} — {ref}:")
    if not itens:
        print("    (Refeição vazia)")
    else:
        for idx, item in enumerate(itens, start=1):
            print(f"    {idx}. {item['nome']} — {item['gramas']}g")

    print("\n  1. Alterar quantidade de um alimento")
    print("  2. Remover um alimento")
    print("  3. Substituir toda a refeição")
    print("  0. Voltar")
    op = _ler_inteiro("  Opção: ", 0, 3)
    if op in (None, 0):
        return

    if op == 1:
        if not itens:
            print("  Não existem alimentos para alterar.")
            return
        idx = _ler_inteiro(f"  Número do alimento (1-{len(itens)}): ", 1, len(itens))
        if idx is None:
            return
        gramas = _ler_gramas("  Nova quantidade em gramas: ")
        if gramas is None:
            return
        _, msg = alterar_quantidade_alimento(plano, dia, ref, idx - 1, gramas)
        print(f"  {msg}")
    elif op == 2:
        if not itens:
            print("  Não existem alimentos para remover.")
            return
        idx = _ler_inteiro(f"  Número do alimento a remover (1-{len(itens)}): ", 1, len(itens))
        if idx is None:
            return
        _, msg = remover_alimento_refeicao(plano, dia, ref, idx - 1)
        print(f"  {msg}")
    elif op == 3:
        _mostrar_tabela_alimentos(ALIMENTOS_PREDEFINIDOS)
        novos: list[tuple[int, float]] = []
        print("\n  Introduz os novos alimentos para substituir a refeição (Enter vazio no ID para concluir):")
        while True:
            bruto_id = input("  ID do alimento (Enter para terminar): ").strip()
            if not bruto_id:
                break
            try:
                aid = int(bruto_id)
            except ValueError:
                print("  [Erro] ID inválido.")
                continue
            if obter_alimento_por_id(aid) is None:
                print("  [Erro] Alimento inexistente.")
                continue
            gramas = _ler_gramas("  Quantidade em gramas: ")
            if gramas is None:
                break
            novos.append((aid, gramas))
        _, msg = substituir_refeicao(plano, dia, ref, novos)
        print(f"  {msg}")


def _consultar_plano_dia(plano: dict) -> None:
    _cabecalho("CONSULTAR PLANO DE UM DIA")
    dia = _escolher_dia()
    if dia is None:
        return

    _cabecalho(f"PLANO DE {dia.upper()}")
    for ref in REFEICOES:
        itens = plano["dias"][dia][ref]
        tot_ref = calcular_totais_refeicao(plano, dia, ref)
        print(f"\n  [{ref}]  —  {tot_ref['calorias']:.1f} kcal | P: {tot_ref['proteinas']:.1f}g | H: {tot_ref['hidratos']:.1f}g | G: {tot_ref['gorduras']:.1f}g")
        if not itens:
            print("    • (Não planeada)")
        else:
            for item in itens:
                alim = obter_alimento_por_id(item["alimento_id"])
                if alim:
                    nut = calcular_nutrientes_porcao(alim, item["gramas"])
                    print(
                        f"    • {item['nome']} ({item['gramas']:.0f}g) -> "
                        f"{nut['calorias']:.1f} kcal | P:{nut['proteinas']:.1f}g H:{nut['hidratos']:.1f}g G:{nut['gorduras']:.1f}g"
                    )

    tot_dia = calcular_totais_dia(plano, dia)
    print()
    _separador("-")
    print(
        f"  TOTAIS DO DIA: {tot_dia['calorias']:.1f} kcal | "
        f"Proteínas: {tot_dia['proteinas']:.1f}g | Hidratos: {tot_dia['hidratos']:.1f}g | Gorduras: {tot_dia['gorduras']:.1f}g"
    )
    print("  " + _barra_prato_nutricional(tot_dia["proteinas"], tot_dia["hidratos"], tot_dia["gorduras"]))
    print(f"  {NOTA_NUTRICIONAL}")


def _consultar_semana_e_relatorios(plano: dict) -> None:
    _cabecalho("PLANO SEMANAL E RELATÓRIO NUTRICIONAL")

    # Grelha resumida da semana
    print(f"  {'Dia':<15} | " + " | ".join(f"{r[:9]:<9}" for r in REFEICOES))
    print("  " + "-" * 74)
    for dia in DIAS_SEMANA:
        celulas = []
        for ref in REFEICOES:
            qtd = len(plano["dias"][dia][ref])
            celulas.append(f"{qtd} item(s)" if qtd > 0 else "Vazio    ")
        print(f"  {dia:<15} | " + " | ".join(f"{c:<9}" for c in celulas))

    resumo = calcular_totais_semana(plano)
    print("\n  COMPARAÇÃO DIÁRIA DE CALORIAS E MACRONUTRIENTES:")
    print(f"  {'Dia':<15} {'Kcal':>8} {'Prot(g)':>8} {'Hidr(g)':>8} {'Gord(g)':>8}  Gráfico")
    print("  " + "-" * 74)
    max_kcal = max([d["calorias"] for d in resumo["por_dia"].values()] + [1.0])
    for dia in DIAS_SEMANA:
        d = resumo["por_dia"][dia]
        barras = "#" * int(round((d["calorias"] / max_kcal) * 18))
        print(
            f"  {dia:<15} {d['calorias']:>8.1f} {d['proteinas']:>8.1f} "
            f"{d['hidratos']:>8.1f} {d['gorduras']:>8.1f}  {barras}"
        )

    t = resumo["totais"]
    m = resumo["medias_diarias"]
    print()
    _separador("-")
    print(
        f"  TOTAIS SEMANAIS: {t['calorias']:.1f} kcal | "
        f"P: {t['proteinas']:.1f}g | H: {t['hidratos']:.1f}g | G: {t['gorduras']:.1f}g"
    )
    print(
        f"  MÉDIA DIÁRIA:    {m['calorias']:.1f} kcal | "
        f"P: {m['proteinas']:.1f}g | H: {m['hidratos']:.1f}g | G: {m['gorduras']:.1f}g"
    )
    print("  " + _barra_prato_nutricional(t["proteinas"], t["hidratos"], t["gorduras"]))

    vazias = identificar_refeicoes_nao_planeadas(plano)
    print(f"\n  Refeições ainda não planeadas: {len(vazias)} de {len(DIAS_SEMANA) * len(REFEICOES)}")
    if vazias:
        amostra = ", ".join(f"{d[:3]}({r})" for d, r in vazias[:8])
        extra = f" ... (+{len(vazias) - 8})" if len(vazias) > 8 else ""
        print(f"  Exemplos: {amostra}{extra}")
    print(f"\n  {NOTA_NUTRICIONAL}")


def executar_consola() -> None:
    """Ciclo principal do menu de consola do Planeamento Alimentar."""
    plano = criar_plano_vazio()
    print("\n  Bem-vindo ao Planeamento Alimentar Semanal (Aplicação de Consola)!")
    print(f"  {NOTA_NUTRICIONAL}")

    try:
        while True:
            _cabecalho("MENU PRINCIPAL — PLANEAMENTO ALIMENTAR SEMANAL")
            print("  1. Consultar base de dados de alimentos")
            print("  2. Adicionar alimento a uma refeição")
            print("  3. Alterar, remover ou substituir refeição")
            print("  4. Consultar plano de um dia e totais")
            print("  5. Consultar semana completa, comparação e relatórios")
            print("  6. Guardar plano semanal (JSON)")
            print("  7. Carregar plano semanal (JSON)")
            print("  8. Limpar / Iniciar novo plano semanal")
            print("  0. Sair")

            opcao = _ler_inteiro("\n  Escolhe uma opção (0-8): ", 0, 8)
            if opcao is None:
                continue

            if opcao == 0:
                print("\n  Até breve! Mantém uma alimentação equilibrada.\n")
                break
            elif opcao == 1:
                _consultar_alimentos()
            elif opcao == 2:
                _adicionar_alimento(plano)
            elif opcao == 3:
                _gerir_refeicao_existente(plano)
            elif opcao == 4:
                _consultar_plano_dia(plano)
            elif opcao == 5:
                _consultar_semana_e_relatorios(plano)
            elif opcao == 6:
                _, msg = guardar_plano(plano)
                print(f"\n  {msg}")
            elif opcao == 7:
                carregado, msg = carregar_plano()
                if carregado is not None:
                    plano = carregado
                print(f"\n  {msg}")
            elif opcao == 8:
                conf = input("  Tens a certeza que queres limpar o plano atual? (s/N): ").strip().lower()
                if conf == "s":
                    plano = criar_plano_vazio()
                    print("  Novo plano semanal criado.")
    except (EOFError, KeyboardInterrupt):
        print("\n\n  Aplicação terminada pelo utilizador.")
