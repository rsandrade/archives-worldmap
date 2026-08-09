# AWM · proposta de nova interface

> Arquivo visual: `index.html`  
> Base factual: repositório local `/home/hermes/websites/archives-worldmap`, logo atual, API pública `/api/pins` consultada em 2026-05-10.  
> Dados usados como âncora: 849 instituições, 95 países, 6 idiomas ativos.

## 1. Tese da proposta

A interface nova deve reposicionar o **Archives World Map** como uma superfície de decisão institucional: o usuário não apenas vê pins, mas entende a qualidade do registro, a disponibilidade de dados, a origem institucional e o próximo passo.

A separação conceitual fica explícita:

- **AWM:** onde estão os arquivos — camada institucional, compatível com lógica ISDIAH.
- **ArchivAI:** o que os acervos descrevem — exploração de metadados, busca assistida e RAG.

## 2. Problema atual percebido

A home atual cumpre a função básica — mapa + busca + submissão — mas ainda parece uma aplicação Bootstrap/Leaflet inicial. O mapa domina a tela, porém não orienta decisões:

- busca e filtros aparecem como função secundária;
- popup do pin é pouco informativo;
- não há distinção visual entre instituição verificada, registro problemático, lacunas e integração com acervos;
- a ponte AWM → ArchivAI ainda não aparece como narrativa de produto;
- a colaboração existe, mas não está incorporada ao fluxo de consulta.

## 3. Direção visual

**Nome interno:** cartografia arquivística contemporânea.

Características:

- fundo quente, tipo papel cartográfico, para evitar aparência genérica de dashboard;
- azul atual do logotipo como cor estrutural;
- ferrugem, verde e ouro apenas como estados funcionais do mapa;
- serif display para autoridade patrimonial;
- sans neutra para operação e leitura rápida;
- interfaces em painéis translúcidos, mas sem “neon tech” nem gradiente SaaS genérico.

## 4. Nova arquitetura da tela principal

### Topbar

- Logo do AWM.
- Navegação curta: Mapa, Instituições, Estatísticas, Sobre, Contato.
- Idiomas compactados.
- CTA principal: “Adicionar instituição”.
- Login discreto para admin/moderação.

### Painel esquerdo

Função: comandar a consulta.

Componentes:

- busca global por arquivo, cidade, país ou identificador;
- filtros persistentes por país/região, tipo, qualidade, disponibilidade de acervos e atualização;
- camada especial “Instituições com descrições arquivísticas coletadas”; 
- mini-distribuição por país, usando dados reais.

### Mapa central

Função: superfície geográfica e interpretativa.

Camadas propostas:

- instituições verificadas;
- clusters/concentração regional;
- lacunas de cobertura;
- registros que precisam revisão;
- instituições com acervos exploráveis no ArchivAI.

### Painel direito

Função: ficha institucional resumida.

Componentes:

- status de verificação;
- resumo ISDIAH simplificado;
- qualidade/completude do registro;
- ações de colaboração;
- bloco “Disponibilidade de acervos”;
- botão “Explorar acervos no ArchivAI”, quando aplicável.

### Mobile

- mapa continua como tela principal;
- ficha vira bottom sheet;
- busca global vira comando superior;
- ações críticas ficam no rodapé do sheet.

## 5. Integração AWM → ArchivAI

Regra de produto proposta:

- se a instituição possui metadados/acervos coletados, o painel mostra:
  - quantidade aproximada de descrições;
  - fontes;
  - última coleta;
  - botão “Explorar acervos no ArchivAI”.
- se não possui, o painel mostra uma chamada editorial:
  - “Ainda não há acervos coletados para esta instituição”.
  - “Sugerir fonte / informar catálogo”.

Isso mantém o AWM leve e institucional, sem tentar virar o ambiente completo de exploração.

## 6. Implementação sugerida em etapas

### Etapa 1 — Redesign da home pública

Escopo:

- novo `home.html`;
- novo CSS modular;
- manter Leaflet e endpoint `/api/pins`;
- adicionar painel esquerdo e painel de ficha;
- não alterar admin/moderação.

### Etapa 2 — Ficha institucional aprimorada

Escopo:

- revisar `info.html`;
- expor campos em grupos ISDIAH simplificados;
- adicionar índice de completude;
- separar correção, denúncia e atualização.

### Etapa 3 — Camadas de dados

Escopo:

- criar metadados de qualidade para pins;
- diferenciar verificados, pendentes, revisáveis e duplicados;
- preparar atributo de disponibilidade ArchivAI.

### Etapa 4 — Ponte com ArchivAI

Escopo:

- campo por instituição para URL/slug no ArchivAI;
- bloco “acervos disponíveis” no painel;
- rota externa filtrada por instituição.

## 7. Cuidados

- Não transformar o AWM em repositório de acervos: isso é ArchivAI.
- Não inflar o banco agora; primeiro desenhar campos mínimos e estados visuais.
- Não quebrar i18n: qualquer texto novo precisa entrar nos 6 JSONs.
- Não alterar admin/moderação no primeiro ciclo, exceto se necessário para suportar o painel público.

## 8. Entregável atual

Foi preparado um mockup estático em HTML com a proposta visual e funcional:

- `index.html` — design board/protótipo visual;
- `proposta.md` — esta especificação resumida;
- screenshot gerado para revisão visual.
