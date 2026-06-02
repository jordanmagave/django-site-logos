# Baseline Lighthouse — Centro Educacional Logos

**Data:** 2026-06-02
**URL:** `https://www.celogos.com.br`
**Versão Lighthouse:** 13.3.0
**Branch:** `feat/performance-and-segment-fix`

---

## Sumário executivo

| Métrica | Mobile (média) | Desktop (média) |
|---|---|---|
| **Performance** | 🟡 **52** | 🟡 **59** |
| Acessibilidade | 🟡 77 | 🟡 76 |
| Best Practices | 🟢 95 | 🟢 96 |
| SEO | 🟢 100 | 🟢 100 |

### Métricas Core Web Vitals (média mobile)

| Métrica | Valor atual | Meta Google | Status |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | **~33,4 s** | < 2,5 s | 🔴 Crítico |
| FCP (First Contentful Paint) | ~8,7 s | < 1,8 s | 🔴 Crítico |
| Speed Index | ~19,3 s | < 3,4 s | 🔴 Crítico |
| TBT (Total Blocking Time) | ~195 ms | < 200 ms | 🟢 Bom |
| CLS (Cumulative Layout Shift) | 0,019 | < 0,1 | 🟢 Bom |
| TTI (Time to Interactive) | ~47,8 s | < 3,8 s | 🔴 Crítico |

### Volume transferido (mobile)

| Rota | Total Bytes |
|---|---|
| home | 16,6 MiB |
| about | 7,0 MiB |
| contato | 4,0 MiB |
| infantil | 10,4 MiB |
| fundamental1 | 18,4 MiB |
| medio | 21,1 MiB |

Para referência: meta saudável < 1.6 MiB total por página.

---

## Diagnóstico raiz

A análise dos audits do Lighthouse revela **3 causas dominantes** do score baixo, todas em mobile:

### 1. Imagens não otimizadas (não aparece nas savings porque a maioria nunca carrega no LCP)
- 12 PNGs com >5 MiB cada em `static/images/gallery/`
- Imagens não responsivas (sem `srcset`)
- Formato PNG em vez de WebP/AVIF
- Sem `loading="lazy"` em imagens fora da viewport
- **Impacto estimado:** redução de 80–95% do total de bytes; LCP de 30s+ → 2-3s

### 2. CSS não utilizado (~1,15 MiB por página)
- Bundle Bootstrap completo + Swiper + Magnific Popup + Metismenu + Fontawesome carregados em **todas** as rotas, mesmo onde não há slider/popup/menu hamburguer
- `unused-css-rules` aponta savings de **6 a 7 segundos** em mobile
- **Impacto estimado:** redução de 80% do CSS bloqueante; FCP de 8,7s → ~2s

### 3. JavaScript não utilizado (~1,1 MiB por página)
- jQuery, GSAP, ScrollTrigger, Swiper, Magnific Popup, jQuery UI, Theia Sticky Sidebar, Counter-Up, etc. carregados em todas as rotas
- `unused-javascript` aponta savings de **2,4 a 3,3 segundos** em mobile
- **Impacto estimado:** TTI de 47s → ~5s

### 4. Causas secundárias
- CSS não minificado (savings ~140 KiB)
- Dois CDPs simultâneos no front-end (Segment + RudderStack)
- Whitenoise compressed manifest ativo mas sem brotli explícito
- Preloader controlado por JS (paint extra)
- Fontes não usam `font-display: swap`

---

## Tabela completa de scores

Consulte `reports/baseline_summary.md` para a tabela detalhada por rota × form-factor.

## Tabela completa de oportunidades

Consulte `reports/baseline_opportunities.md` para todas as `Opportunities` ordenadas por impacto.

---

## Alvos pós-otimização (estimativa)

Após Bloco A + B do plano:

| Métrica | Baseline mobile | Alvo mobile |
|---|---|---|
| Performance score | 52 | ≥ 85 |
| LCP | 33,4 s | < 2,5 s |
| FCP | 8,7 s | < 1,8 s |
| Total bytes (home) | 16,6 MiB | < 1,5 MiB |

## Próximos passos (cronograma)

| Fase | Status | Risco visual | Ganho esperado |
|------|--------|--------------|----------------|
| 0 - QA setup | ✅ Completa | Zero | — |
| 1 - Baseline | ✅ Completa | Zero | — |
| 2 - Refactor hexagonal | 🔵 Próxima | Zero | Qualidade |
| 3 - RudderStack out, Segment LGPD | Pendente | Zero | ~3-5 pts |
| 4 - SEO sitemap/schema | Pendente | Zero | SEO ≥99 |
| 5 - Cache + brotli | Pendente | Zero | ~5-10 pts |
| **Checkpoint 1** | — | — | **+15-25 pts** |
| 6 - Imagens (aprovação por lote) | Pendente | Médio | **+25-40 pts** |
| 7 - Critical CSS | Pendente | Baixo-Médio | +5-15 pts |
| 8 - JS audit | Pendente | Médio | +10-20 pts |
| 9 - Subset fonts | Pendente | Baixo | +3-8 pts |

