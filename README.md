# Fazenda do Frances

**Guest House Regenerativa** - Cachoeiras de Macacu, RJ, Brasil
*"RE CONECTE-SE"*

---

## Sobre o Projeto

Repositorio de gestao e desenvolvimento da Fazenda do Frances, propriedade familiar com mais de 40 anos de historia onde a tradicao francesa encontra a Mata Atlantica. Este repositorio centraliza documentacao, analises de propriedade, planos de negocio e pesquisa juridica.

---

## Estrutura do Repositorio

```
fazenda-do-frances/
├── README.md                          <- Este arquivo
├── docs/
│   ├── ANALYSIS/                      <- Analise completa do negocio (13 arquivos)
│   │   ├── 00-resumo-executivo.md     <- Visao geral do negocio
│   │   ├── 01-propriedade.md          <- Dados da propriedade, historia, localizacao
│   │   ├── 02-acomodacoes.md          <- 7 suites (parcial)
│   │   ├── 03-atividades.md           <- Atividades e experiencias
│   │   ├── 04-gastronomia.md          <- Culinaria francesa, cardapio
│   │   ├── 05-eventos.md              <- Casamentos, corporativos (parcial)
│   │   ├── 06-investimento.md         <- Projecoes financeiras, payback
│   │   ├── 07-presenca-digital.md     <- Redes sociais, website
│   │   ├── 08-proximos-passos.md      <- Status da analise e pendencias
│   │   ├── 09-retiros.md              <- Retiros wellness e terapeuticos
│   │   ├── 10-programas-educacionais.md <- Day Use Escolar
│   │   ├── 11-parcerias.md            <- Modelo de permuta, influenciadores
│   │   ├── 12-receitas-detalhadas.md  <- 6 receitas francesas da familia
│   │   ├── 13-plano-desenvolvimento.md <- 24 ideias de receita, ONG, WWOOF, permacultura
│   │   └── 14-planta-topografica.md   <- Planta topografica oficial (SIRGAS 2000)
│   ├── PLANTA .pdf                    <- Planta oficial da propriedade (pre-venda, 44 ha)
│   ├── Fazenda do Frances (informacoes).pdf
│   ├── Atividades Fazenda e Regiao.pdf
│   ├── Permuta Parceria.pdf
│   ├── Receitas.pdf
│   ├── Retiro Sucesso integrativo.pdf
│   ├── Retiros BYB 2022.pdf
│   ├── Day Use Escola.pdf
│   ├── Casamentos.pdf
│   ├── Suites - Workshop Cacau.pdf
│   ├── Papiers-partage-fazenda.pdf
│   └── DOM guest 25.xlsx / .csv       <- Dados de hospedes 2025
│
├── land-ownership/                    <- Pesquisa juridica de propriedade
│   ├── README.md                      <- Guia do modulo juridico
│   ├── OWNERSHIP_STATUS.md            <- Status atual e acoes pendentes
│   ├── family-tree/                   <- Arvore genealogica e heranca
│   ├── documents/                     <- Documentos originais e transcricoes
│   ├── legal-issues/                  <- Conflitos e estrategias juridicas
│   ├── timeline/                      <- Cronologia de eventos
│   ├── agreements/                    <- Acordos (rascunhos e assinados)
│   └── ownership-shares/             <- Cotas de propriedade
│
├── PROPERTY_ANALYSIS_SUMMARY.md       <- Analise de limites (parcela DESMEMBRADO)
├── README_ANALYSIS.md                 <- Guia rapido da analise de limites
├── property_coordinates.json          <- Coordenadas do perimetro (DESMEMBRADO)
├── property_points.csv                <- Pontos de limite em CSV
├── property_plot_data.txt             <- Dados para plotagem
├── Fazenda_Santa_Fe_DESMEMBRADO_*     <- Arquivos GIS (CSV, WKT, JSON)
├── property_*.html                    <- Visualizacoes interativas (mapas)
├── analyze_property.py                <- Script de analise v1
├── analyze_property_v2.py             <- Script de analise v2 (final)
│
├── src/                               <- Codigo fonte (futuro)
├── tests/                             <- Testes (futuro)
└── config/                            <- Configuracoes (futuro)
```

---

## A Propriedade

| Informacao | Valor |
|------------|-------|
| **Nome** | Fazenda do Frances (Fazenda Vale do Beraka - Boa Sorte) |
| **Area atual** | 42,54 ha (425.350,15 m2) |
| **Localizacao** | Funchal, 3o distrito, Cachoeiras de Macacu, RJ |
| **Distancia do Rio** | 120km (~1h30) |
| **Proprietario registrado** | Serra Negra Agropecuaria LTDA - ME |
| **CNPJ** | 27.712.553/0001-23 |
| **Matricula** | No 71 - Averbacao 09/71 de 14.09.2004 |
| **Sistema geodesico** | SIRGAS 2000 / UTM Fuso 23S |

### Historico de Subdivisao (2004)

| Parcela | Area | Status |
|---------|------|--------|
| Fazenda Santa Fe (original) | 199,37 ha | Subdividida |
| ~~DESMEMBRADO~~ | ~~156,83 ha~~ | ~~Vendida/Separada~~ |
| **REMANESCENTE = Fazenda do Frances** | **42,54 ha** | **Propriedade atual** |

### Planta Topografica Oficial

O arquivo `docs/PLANTA .pdf` contem a planta topografica com:
- Carta imagem (satelite) com perimetro demarcado
- 21 vertices georreferenciados (SIRGAS 2000 / UTM 23S)
- Direcoes e distancias entre pontos consecutivos
- Responsavel tecnica: Lorena Abreu Aseve (CREA-RJ: 2014127679)

Ver detalhes em `docs/ANALYSIS/14-planta-topografica.md`.

---

## Negocio - Guest House Regenerativa

### Fontes de Receita

| Categoria | Descricao | Projec. Mensal |
|-----------|-----------|----------------|
| Hospedagem | 7 suites exclusivas | Variavel |
| Gastronomia | Culinaria francesa autentica | R$ 2.835-21.536 |
| Eventos | Casamentos, corporativos (ate 100 pessoas) | R$ 10.000-22.000 |
| Atividades | Cavalgada, banho floresta, bicicleta | Por demanda |
| Retiros | Wellness, terapeuticos, yoga | Por pacote |
| Day Use Escolar | Ate 30 criancas, R$ 100/crianca | Por evento |

### Plano de Desenvolvimento (24 novas ideias)

Documentado em `docs/ANALYSIS/13-plano-desenvolvimento.md`:
- Meliponicultura, cogumelos gourmet, viveiro de mudas
- Piquenique frances, aulas culinaria, astroturismo
- Jantares tematicos, mercadinho, cinema ao ar livre
- Conservas artesanais, coworking rural, birdwatching
- ONG bem-estar animal (Santuario)
- Cantinho do Cafe "Le Petit Coin"
- Permacultura e sistemas agroflorestais
- Recrutamento WWOOF / Worldpackers / Workaway

**Investimento total estimado:** R$ 6.900-19.000
**Receita potencial mensal:** R$ 12.500-37.000

---

## Situacao Juridica

**Status:** COMPLEXA - Heranca familiar em andamento

Ver `land-ownership/OWNERSHIP_STATUS.md` para detalhes completos.

Acoes prioritarias:
1. Clarificar estrutura familiar e heranca
2. Identificar compradores das 3 cotas vendidas
3. Obter matricula atualizada
4. Consultar advogado especializado em direito agrario

---

## Contatos

| Canal | Informacao |
|-------|------------|
| WhatsApp | (21) 97920-1646 |
| Instagram | @fazendadofrances |
| Email | fazendadofrances@gmail.com |
| Website | www.fazendadofrances.com.br |
| Maps | https://maps.app.goo.gl/prEDdoQVswtARX3y8 |

---

## Documentos Pendentes

- [ ] Processar `Casamentos.pdf` (27.8 MB) -> atualizar `05-eventos.md`
- [ ] Processar `Suites - Workshop Cacau.pdf` (21.4 MB) -> atualizar `02-acomodacoes.md`
- [ ] Localizar `CERTIDAO SERRA NEGRA.pdf`
- [ ] Processar `DOM guest 25.xlsx` (dados de hospedes)

---

## Git — Dois Repositorios

Este projeto e publicado em dois repositorios:

| Remote | Repositorio | Tipo |
|--------|------------|------|
| `origin` | `leodom/fazenda-do-frances` | Privado |
| `fazenda-map` | `leodom/fazenda-map` | Publico (GitHub Pages) |

Ao fazer push, **sempre use**:
```
git pushall
```
Este alias sincroniza commits do `fazenda-map` (gerados pelo botao "Salvar no GitHub" do mapa) e depois envia para ambos os remotes.

**Nunca use `git push` simples** — ele envia para apenas um remote.

---

*Ultima atualizacao: 2026-03-22*
