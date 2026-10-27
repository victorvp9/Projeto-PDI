# Números do trabalho final e a origem de cada um

Gerado por `scripts/relatorio/numeros_tf.py`, que confere cada linha. Nas origens que são os arquivos de números dos relatórios (`docs/04-relatorio-numeros.md` e `docs/04-relatorio-v2-numeros.md`, conferidos por `numeros.py` e `numeros_v2.py`), a linha é a do arquivo e a coluna diz o nº da entrada; a origem primária está nela. Nas origens em CSV, a linha conta o cabeçalho como linha 1; nas em texto, a linha é a do arquivo; nas em JSON, a coluna diz o caminho das chaves; as contas dizem a expressão. As tabelas copiadas dos relatórios são conferidas linha a linha contra a tabela de mesma legenda na origem. A completude também é conferida: todo número do corpo, fora das linhas dessas tabelas, tem uma linha aqui.

As origens em PDF (artigos da pasta do projeto) dizem a página do arquivo e o trecho conferido. Elas exigem o `pdftotext` do poppler no PATH: o script roda no Git Bash, que o traz em `/mingw64/bin`; sem ele, o script para com uma mensagem.

| nº | número no texto | o que é | seção | origem | linha | coluna | valor na origem |
|---|---|---|---|---|---|---|---|
| 1 | 49 | clipes do GSR test | Resumo | `docs/04-relatorio-v2-numeros.md` | 19 | nº 11 | 49 |
| 2 | 3 | jogos do GSR test | Resumo | `docs/04-relatorio-numeros.md` | 60 | nº 52 | (no texto da linha) |
| 3 | 0,505 | cobertura do detector, GSR test | Resumo | `docs/04-relatorio-numeros.md` | 9 | nº 1 | 0.5049593224116795 |
| 4 | 0,419 | LocSim@5 penalizado do detector | Resumo | `docs/04-relatorio-numeros.md` | 10 | nº 2 | 0.4192764091198964 |
| 5 | 0,897 | cobertura do 6c fluxo | Resumo | `docs/04-relatorio-numeros.md` | 15 | nº 7 | 0.8971358520004458 |
| 6 | 0,749 | LocSim@5 penalizado do 6c fluxo | Resumo | `docs/04-relatorio-numeros.md` | 16 | nº 8 | 0.7490157917374893 |
| 7 | 0,650 | LocSim@5 penalizado do 6c, IC inferior | Resumo | `docs/04-relatorio-numeros.md` | 17 | nº 9 | 0.6499967158730244 |
| 8 | 0,920 | LocSim@5 penalizado do 6c, IC superior | Resumo | `docs/04-relatorio-numeros.md` | 18 | nº 10 | 0.9199799820597923 |
| 9 | 40 | redução do erro residual | Resumo | `docs/04-relatorio-numeros.md` | 105 | nº 97 | 40.458 |
| 10 | 38 | redução do erro residual | Resumo | `docs/04-relatorio-numeros.md` | 108 | nº 100 | 38.2609 |
| 11 | 0,902 | LocSim@5 penalizado da propagação, v2 | Resumo | `docs/04-relatorio-v2-numeros.md` | 11 | nº 3 | 0.9021534525340882 |
| 12 | 0,929 | AuxFlow | Resumo | `docs/04-relatorio-numeros.md` | 96 | nº 88 | 0.929 |
| 13 | 0,946 | H_gt pelas linhas | Resumo | `docs/04-relatorio-numeros.md` | 421 | nº 413 | 0.9464115216354456 |
| 14 | 3 | homografia 3 × 3 | 1 | `docs/04-relatorio-numeros.md` | 307 | nº 299 | (no texto da linha) |
| 15 | 25 | zoom de até 25× da câmera de transmissão (BroadTrack) | 1 | `C:/Users/victo/Downloads/Topicos Av pdi/BroadTrack__Broadcast Camera Tracking for Soccer_compressed.pdf` | — | p. 3 | “can zoom up to 25 times” |
| 16 | 0,5 | BroadTrack reinicia com IoU < 0,5 | 2 | `docs/04-relatorio-numeros.md` | 309 | nº 301 | (no texto da linha) |
| 17 | 0,8397 | BroadTrack × AuxFlow no GSR | 2 | `docs/04-relatorio-numeros.md` | 310 | nº 302 | (no texto da linha) |
| 18 | 0,8352 | BroadTrack × AuxFlow no GSR | 2 | `docs/04-relatorio-numeros.md` | 311 | nº 303 | (no texto da linha) |
| 19 | 0,9224 | BroadTrack × AuxFlow no GSR | 2 | `docs/04-relatorio-numeros.md` | 312 | nº 304 | (no texto da linha) |
| 20 | 0,9426 | BroadTrack × AuxFlow no GSR | 2 | `docs/04-relatorio-numeros.md` | 313 | nº 305 | (no texto da linha) |
| 21 | 1,34 | BroadTrack × AuxFlow no GSR | 2 | `docs/04-relatorio-numeros.md` | 314 | nº 306 | (no texto da linha) |
| 22 | 0,84 | BroadTrack × AuxFlow no GSR | 2 | `docs/04-relatorio-numeros.md` | 315 | nº 307 | (no texto da linha) |
| 23 | 2,5 | grade de pontos auxiliares 2,5 × 2 m | 2 | `docs/04-relatorio-numeros.md` | 316 | nº 308 | (no texto da linha) |
| 24 | 2 | grade de pontos auxiliares 2,5 × 2 m | 2 | `docs/04-relatorio-numeros.md` | 317 | nº 309 | (no texto da linha) |
| 25 | 1 | erro de ida e volta <= 1 px | 2 | `docs/04-relatorio-numeros.md` | 318 | nº 310 | (no texto da linha) |
| 26 | 83,67 | AuxFlow no HSB, média | 2 | `docs/04-relatorio-numeros.md` | 131 | nº 123 | (no texto da linha) |
| 27 | 23,42 | AuxFlow sem fluxo no HSB | 2 | `docs/04-relatorio-numeros.md` | 319 | nº 311 | (no texto da linha) |
| 28 | 78,30 | AuxFlow sem pontos-chave do detector | 2 | `docs/04-relatorio-numeros.md` | 320 | nº 312 | (no texto da linha) |
| 29 | 78,71 | RAFT no lugar do Lucas–Kanade | 2 | `docs/04-relatorio-numeros.md` | 321 | nº 313 | (no texto da linha) |
| 30 | 39,68 | amostragem geométrica no AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 322 | nº 314 | (no texto da linha) |
| 31 | 83,39 | amostragem aleatória no AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 323 | nº 315 | (no texto da linha) |
| 32 | 150 | âncoras ingênuas a cada 150 frames | 2 | `docs/04-relatorio-numeros.md` | 324 | nº 316 | (no texto da linha) |
| 33 | 82,48 | âncoras ingênuas no AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 325 | nº 317 | (no texto da linha) |
| 34 | 83,48 | detector sem propagação no AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 326 | nº 318 | (no texto da linha) |
| 35 | 90,65 | âncoras por heurística no AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 327 | nº 319 | (no texto da linha) |
| 36 | 91,88 | âncora de gabarito no AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 328 | nº 320 | (no texto da linha) |
| 37 | 54,74 | AuxFlow com a H inicial perturbada | 2 | `docs/04-relatorio-numeros.md` | 329 | nº 321 | (no texto da linha) |
| 38 | 43,15 | NBJW sozinho no HSB, média | 2 | `docs/04-relatorio-numeros.md` | 129 | nº 121 | (no texto da linha) |
| 39 | 0,885 | LocSim@5 do NBJW, tabela 7 do AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 95 | nº 87 | 0.885 |
| 40 | 0,8852 | BHITK no GSR, tabela 7 do AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 359 | nº 351 | (no texto da linha) |
| 41 | 0,8851 | NBJW no GSR, tabela 7 do AuxFlow | 2 | `docs/04-relatorio-numeros.md` | 360 | nº 352 | (no texto da linha) |
| 42 | 115 | molde do PnLCalib no WC14 | 2 | `docs/04-relatorio-numeros.md` | 335 | nº 327 | (no texto da linha) |
| 43 | 74 | molde do PnLCalib no WC14 | 2 | `docs/04-relatorio-numeros.md` | 336 | nº 328 | (no texto da linha) |
| 44 | 100 | molde do KpSFR e de Maglo | 2 | `docs/04-relatorio-numeros.md` | 337 | nº 329 | (no texto da linha) |
| 45 | 60 | molde do KpSFR e de Maglo | 2 | `docs/04-relatorio-numeros.md` | 338 | nº 330 | (no texto da linha) |
| 46 | 31 | Bassek et al.: janela do Savitzky–Golay | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 4 | “window length 31 and third-degree polynomial” |
| 47 | 3 | Bassek et al.: grau do Savitzky–Golay | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 4 | “window length 31 and third-degree polynomial” |
| 48 | 25 | Bassek et al.: lacunas de até 25 frames interpoladas linearmente | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 4 | “up to 25 frames (1 second) were interpolated linearly” |
| 49 | 981 | Bassek et al.: cortes por partida | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 8 | “981 cuts per match, or 10.9 cuts per minute” |
| 50 | 10,9 | Bassek et al.: cortes por minuto | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 8 | “981 cuts per match, or 10.9 cuts per minute” |
| 51 | 1 | Bassek et al.: só 1 jogador visível no feed de scouting (%) | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 8 | “only a single player (1% of footage) or no players (3%)” |
| 52 | 3 | Bassek et al.: nenhum jogador visível no feed de scouting (%) | 2, 3, 6 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 8 | “only a single player (1% of footage) or no players (3%)” |
| 53 | 8 | Bassek et al.: página dos artefatos do pipeline do campo de visão | 2 | `C:/Users/victo/Downloads/Topicos Av pdi/Broadcast analytics.pdf` | — | p. 8 | “field of view detection and filtering pipeline introduced few artifacts” |
| 54 | 105 | modelo do campo 105 × 68 m | 3 | `docs/04-relatorio-numeros.md` | 339 | nº 331 | (no texto da linha) |
| 55 | 68 | modelo do campo 105 × 68 m | 3 | `docs/04-relatorio-numeros.md` | 340 | nº 332 | (no texto da linha) |
| 56 | 20 | faixa de matiz do gramado | 3 | `docs/04-relatorio-numeros.md` | 341 | nº 333 | (no texto da linha) |
| 57 | 0,9861 | IoU médio do gramado no WC14 train_val | 3 | `docs/04-relatorio-numeros.md` | 342 | nº 334 | (no texto da linha) |
| 58 | 15 | limiar das marcações no WC14 | 3 | `docs/04-relatorio-numeros.md` | 343 | nº 335 | (no texto da linha) |
| 59 | 30 | limiar das marcações no GSR | 3 | `docs/04-relatorio-numeros.md` | 344 | nº 336 | (no texto da linha) |
| 60 | 180 | simetria de 180° do campo | 3 | `docs/04-relatorio-numeros.md` | 345 | nº 337 | (no texto da linha) |
| 61 | 0,45 | portão: fração explicada | 3 | `docs/04-relatorio-numeros.md` | 346 | nº 338 | (no texto da linha) |
| 62 | 0,85 | portão: IoU com o gramado | 3 | `docs/04-relatorio-numeros.md` | 347 | nº 339 | (no texto da linha) |
| 63 | 5 | portões logo abaixo do percentil 5 | 3 | `docs/04-relatorio-numeros.md` | 348 | nº 340 | (no texto da linha) |
| 64 | 12 | janela das âncoras candidatas | 3 | `docs/04-relatorio-numeros.md` | 349 | nº 341 | (no texto da linha) |
| 65 | 0,668 | Fatias 4 e 5, calibração no treino/valid: Elipses: calibração no GSR train, com uma repetição. | 3.1, Tabela 2 | `docs/decisoes.md` | 103 | — | (no texto da linha) |
| 66 | 0,740 | Fatias 4 e 5, calibração no treino/valid: Elipses: calibração no GSR train, com uma repetição. | 3.1, Tabela 2 | `docs/decisoes.md` | 103 | — | (no texto da linha) |
| 67 | 643 | Fatias 4 e 5, calibração no treino/valid: Elipses: calibração no GSR train, com uma repetição. | 3.1, Tabela 2 | `docs/decisoes.md` | 103 | — | (no texto da linha) |
| 68 | 0,202 | Fatias 4 e 5, calibração no treino/valid: Elipses: calibração no GSR train, com uma repetição. | 3.1, Tabela 2 | `docs/decisoes.md` | 103 | — | (no texto da linha) |
| 69 | 1.105 | Fatias 4 e 5, calibração no treino/valid: Elipses: calibração no GSR train, com uma repetição. | 3.1, Tabela 2 | `docs/decisoes.md` | 103 | — | (no texto da linha) |
| 70 | 3 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 71 | 720 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 72 | 6 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 73 | 1 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 74 | 2 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 75 | 1.697 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 76 | 0,388 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 77 | 0,0057 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 78 | 3,05 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 79 | 0,418 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 80 | 0,0064 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 81 | 0,58 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 82 | 0,339 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 83 | 0,0060 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 84 | 0,71 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 85 | 0,398 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 86 | 1,02 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 87 | 0,030 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 88 | 0,01 | Fatias 4 e 5, calibração no treino/valid: Decisões pendentes resolvidas pelo erro da homografia: td da | 3.1, Tabela 2 | `docs/decisoes.md` | 111 | — | (no texto da linha) |
| 89 | 60 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 90 | 31 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 91 | 37 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 92 | 84 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 93 | 9 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 94 | 6 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 95 | 4 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 96 | 0,48 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 97 | 300 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 98 | 0,483 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 99 | 0,0216 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 100 | 10 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 101 | 0,467 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 102 | 0,0076 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 103 | 8 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 104 | 0,433 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 105 | 0,0062 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 106 | 24 | Fatias 4 e 5, calibração no treino/valid: Fatia 5, pipeline mínimo: diagnóstico e nova verificação | 3.1, Tabela 2 | `docs/decisoes.md` | 107 | — | (no texto da linha) |
| 107 | 33 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 108 | 10 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 109 | 7 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 110 | 0,433 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 111 | 0,0058 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 112 | 6 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 113 | 0,417 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 114 | 0,200 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 115 | 0,226 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 116 | 5 | Fatias 4 e 5, calibração no treino/valid: Elipses conferidas depois da H e ablação correspondências +  | 3.1, Tabela 2 | `docs/decisoes.md` | 113 | — | (no texto da linha) |
| 117 | 209 | imagens de treino do WC14 | 4 | `docs/04-relatorio-numeros.md` | 351 | nº 343 | (no texto da linha) |
| 118 | 186 | imagens do WC14 test | 4 | `docs/04-relatorio-numeros.md` | 145 | nº 137 | 186 |
| 119 | 1280 | resolução do WC14 | 4 | `docs/04-relatorio-numeros.md` | 352 | nº 344 | (no texto da linha) |
| 120 | 720 | resolução do WC14 | 4 | `docs/04-relatorio-numeros.md` | 353 | nº 345 | (no texto da linha) |
| 121 | 750 | frames por clipe | 4 | `docs/04-relatorio-numeros.md` | 241 | nº 233 | (no texto da linha) |
| 122 | 1080 | resolução do GSR | 4 | `docs/04-relatorio-numeros.md` | 356 | nº 348 | (no texto da linha) |
| 123 | 57 | clipes de treino do GSR | 4 | `docs/04-relatorio-numeros.md` | 357 | nº 349 | (no texto da linha) |
| 124 | 58 | clipes de validação do GSR | 4 | `docs/04-relatorio-numeros.md` | 358 | nº 350 | (no texto da linha) |
| 125 | 16 | clipes do jogo 7 | 4 | `docs/04-relatorio-numeros.md` | 64 | nº 56 | 16 |
| 126 | 19 | clipes do jogo 8 | 4 | `docs/04-relatorio-numeros.md` | 72 | nº 64 | 19 |
| 127 | 14 | clipes do jogo 11 | 4 | `docs/04-relatorio-numeros.md` | 80 | nº 72 | 14 |
| 128 | 0,05 | limiar de âncora/H errada (NPE > 0,05) | 4 | `docs/04-relatorio-numeros.md` | 197 | nº 189 | (no texto da linha) |
| 129 | 0,933 | H_gt pelas linhas como predição, train | 4 | `docs/04-relatorio-numeros.md` | 398 | nº 390 | 0.9332444747326908 |
| 130 | 0,9928 | LocSim@5 do gabarito do AuxFlow (tabela 2 deles) | 4 | `docs/04-relatorio-numeros.md` | 397 | nº 389 | (no texto da linha) |
| 131 | 0,978 | H_gt_auxflow como predição: LocSim@5 | 4 | `docs/04-relatorio-numeros.md` | 422 | nº 414 | 0.9778654624887865 |
| 132 | 3 | RANSAC a 3 px da H_gt_auxflow | 4 | `docs/04-relatorio-numeros.md` | 361 | nº 353 | (no texto da linha) |
| 133 | 10 | clipes do HSB | 4 | `docs/04-relatorio-numeros.md` | 362 | nº 354 | (no texto da linha) |
| 134 | 0 | numeração dos frames a partir de 0 | 4 | `docs/04-relatorio-numeros.md` | 363 | nº 355 | (no texto da linha) |
| 135 | 90 | intervalo "90–0" do SNGS-128 | 4 | `docs/04-relatorio-numeros.md` | 364 | nº 356 | (no texto da linha) |
| 136 | 0 | intervalo "90–0" do SNGS-128 | 4 | `docs/04-relatorio-numeros.md` | 365 | nº 357 | (no texto da linha) |
| 137 | 0,05 | LocSim: exp(ln(0,05)·d²/τ²) | 4 | `docs/04-relatorio-numeros.md` | 366 | nº 358 | (no texto da linha) |
| 138 | 5 | τ = 5 m | 4 | `docs/04-relatorio-numeros.md` | 367 | nº 359 | (no texto da linha) |
| 139 | 0 | pessoa de frame sem H vale 0 | 4 | `docs/04-relatorio-numeros.md` | 370 | nº 362 | (no texto da linha) |
| 140 | 10 | mAP-LocSim: τ = 1 a 10 m | 4 | `docs/04-relatorio-numeros.md` | 369 | nº 361 | (no texto da linha) |
| 141 | 960 | escala da acurácia contra as linhas | 4 | `docs/04-relatorio-numeros.md` | 490 | nº 482 | (no texto da linha) |
| 142 | 540 | escala da acurácia contra as linhas | 4 | `docs/04-relatorio-numeros.md` | 491 | nº 483 | (no texto da linha) |
| 143 | 20 | limiares da acurácia (5, 10, 20 px) | 4 | `docs/04-relatorio-numeros.md` | 492 | nº 484 | (no texto da linha) |
| 144 | 2.000 | reamostragens do bootstrap | 5 | `docs/04-relatorio-numeros.md` | 372 | nº 364 | (no texto da linha) |
| 145 | 10 | reamostragens distintas do bootstrap com 3 jogos | 5 | `docs/04-relatorio-numeros.md` | 61 | nº 53 | (no texto da linha) |
| 146 | 95 | intervalo de 95% | 5 | `docs/04-relatorio-numeros.md` | 371 | nº 363 | (no texto da linha) |
| 147 | 1.470 | frames da conferência de determinismo | 5 | `docs/04-relatorio-numeros.md` | 373 | nº 365 | (no texto da linha) |
| 148 | 25 | frames da conferência: 1 a cada 25 | 5 | `docs/04-relatorio-numeros.md` | 374 | nº 366 | (no texto da linha) |
| 149 | 735 | tarefas da série com a chave congelada | 5 | `docs/04-relatorio-numeros.md` | 375 | nº 367 | (no texto da linha) |
| 150 | 47 | caches da valid gravados com a chave errada | 5 | `docs/04-relatorio-numeros.md` | 376 | nº 368 | (no texto da linha) |
| 151 | 18 | clipes sem âncora da valid | 6 | `docs/04-relatorio-numeros.md` | 266 | nº 258 | (no texto da linha) |
| 152 | 21 | B5, protocolo: núcleo do borrão de 21 px | 6 | `docs/04-relatorio-numeros.md` | 462 | nº 454 | (no texto da linha) |
| 153 | 50 | passos da sensibilidade (±50%) | 6 | `docs/04-relatorio-numeros.md` | 289 | nº 281 | (no texto da linha) |
| 154 | 62 | lacunas de 4-25 com as duas bordas erradas (%) | 6 | `docs/04-relatorio-numeros.md` | 223 | nº 215 | 61.6387 |
| 155 | 65 | fração da distância detector -> AuxFlow fechada pelo 6c (%) | 6 | `docs/04-relatorio-numeros.md` | 99 | nº 91 | 64.6898 |
| 156 | 79 | imagens do WC14 test sem H | 6 | `docs/04-relatorio-numeros.md` | 158 | nº 150 | 79 |
| 157 | 85 | fração ao teto nos 19 clipes do train[::3] (%) | 6 | `docs/04-relatorio-numeros.md` | 114 | nº 106 | (no texto da linha) |
| 158 | 0,1 | frames com 0 visíveis do 6c, só cobertos (%) | 6 | `docs/04-relatorio-numeros.md` | 188 | nº 180 | 0.0008182790961163215 |
| 159 | 107 | imagens com H (protocolo KpSFR) | 6 | `docs/04-relatorio-numeros.md` | 151 | nº 143 | 107 |
| 160 | 126 | s de parede por clipe com 10 processos, 6c com as ablações | 6 | `docs/04-relatorio-numeros.md` | 229 | nº 221 | 125.59183673469387 |
| 161 | 127 | 6c fluxo, ms por frame | 6 | `docs/04-relatorio-numeros.md` | 240 | nº 232 | (no texto da linha) |
| 162 | 2,1 | jogadores invertidos do 6c, só cobertos (%) | 6 | `docs/04-relatorio-numeros.md` | 187 | nº 179 | 0.020613020580008055 |
| 163 | 2,2 | aceitas erradas, entre as com gabarito (%) = 12 / 557 | 6 | `docs/04-relatorio-numeros.md` | 194 | nº 186 | 2.1544 |
| 164 | 2,6 | AuxFlow, FPS (tabela 6) | 6 | `docs/04-relatorio-numeros.md` | 236 | nº 228 | 2.6 |
| 165 | 280 | SNGS-136, fim do intervalo do HSB | 6 | `docs/04-relatorio-numeros.md` | 141 | nº 133 | 280 |
| 166 | 292 | AuxFlow, s por clipe (tabela 6) | 6 | `docs/04-relatorio-numeros.md` | 235 | nº 227 | 292 |
| 167 | 4,4 | jogadores invertidos do Kalman na interseção (%) | 6 | `docs/04-relatorio-numeros.md` | 182 | nº 174 | 0.043892732929131484 |
| 168 | 5,0 | jogadores invertidos do detector na interseção (%) | 6 | `docs/04-relatorio-numeros.md` | 183 | nº 175 | 0.0499068324247626 |
| 169 | 5,6 | jogadores invertidos do detector, só cobertos (%) | 6 | `docs/04-relatorio-numeros.md` | 186 | nº 178 | 0.05558504435383341 |
| 170 | 558 | âncoras aceitas | 6 | `docs/04-relatorio-numeros.md` | 193 | nº 185 | 558 |
| 171 | 630 | s de parede por clipe com 15 processos, série (máquina inteira) | 6 | `docs/04-relatorio-numeros.md` | 228 | nº 220 | 630.0204081632653 |
| 172 | 958 | âncoras candidatas | 6 | `docs/04-relatorio-numeros.md` | 191 | nº 183 | 958 |
| 173 | 0,02 | ganho mínimo para virar candidato | 6 | `docs/04-relatorio-numeros.md` | 295 | nº 287 | (no texto da linha) |
| 174 | 0,03 | o 6c fica a menos disto do teto nos três jogos (máximo de teto − 6c: 0,027) | 6 | `docs/04-relatorio-numeros.md` | 87 | nº 79 | 0.03 |
| 175 | 0,13 | tremor_med (px) de Kalman + RTS na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 165 | nº 157 | 0.12705495063616054 |
| 176 | 0,35 | B5, protocolo: sombra: L* × 0,35 | 6 | `docs/04-relatorio-numeros.md` | 465 | nº 457 | (no texto da linha) |
| 177 | 0,40 | tremor_med (px) de 6c fluxo na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 169 | nº 161 | 0.39837273079606117 |
| 178 | 0,57 | tremor_p90 (px) de Kalman + RTS na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 166 | nº 158 | 0.5747011364830146 |
| 179 | 1,19 | vazão da série (frames/s) | 6 | `docs/04-relatorio-numeros.md` | 227 | nº 219 | 1.1904376275468886 |
| 180 | 1,29 | tremor_med (px) de detector na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 173 | nº 165 | 1.2880092272994736 |
| 181 | 1,38 | deslize_med (px) de 6c fluxo na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 171 | nº 163 | 1.3759090615954128 |
| 182 | 1,43 | tremor_p90 (px) de 6c fluxo na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 170 | nº 162 | 1.4311293022953095 |
| 183 | 1,90 | deslize_med (px) de 6a Bassek na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 175 | nº 167 | 1.89765570974326 |
| 184 | 11,8 | jogadores invertidos do 6c, penalizada (%) | 6 | `docs/04-relatorio-numeros.md` | 185 | nº 177 | 0.1184785773854684 |
| 185 | 17,7 | HSB (2) detector, média (%) | 6 | `docs/04-relatorio-numeros.md` | 121 | nº 113 | 0.17652374081667707 |
| 186 | 2,90 | detector, s por frame num núcleo, WC14 | 6 | `docs/04-relatorio-numeros.md` | 239 | nº 231 | (no texto da linha) |
| 187 | 20,9 | B2, HSB, 6a Bassek: pen_media | 6 | `docs/04-relatorio-numeros.md` | 451 | nº 443 | 0.20927468016171605 |
| 188 | 24,5 | B2, HSB, 6a robusto: pen_media | 6 | `docs/04-relatorio-numeros.md` | 455 | nº 447 | 0.24468732504909463 |
| 189 | 28,3 | candidatas erradas, entre as com gabarito (%) | 6 | `docs/04-relatorio-numeros.md` | 192 | nº 184 | 28.2723 |
| 190 | 4,17 | deslize p90 (px) do 6c no próprio conjunto | 6 | `docs/04-relatorio-numeros.md` | 177 | nº 169 | 4.174295627239621 |
| 191 | 4,25 | deslize mediano (px) do 6c sem fluxo | 6 | `docs/04-relatorio-numeros.md` | 180 | nº 172 | 4.250941912282512 |
| 192 | 4,33 | deslize_p90 (px) de 6c fluxo na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 172 | nº 164 | 4.32759718031505 |
| 193 | 4,76 | detector, s por frame num núcleo, GSR | 6 | `docs/04-relatorio-numeros.md` | 237 | nº 229 | (no texto da linha) |
| 194 | 4090 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `docs/04-relatorio-numeros.md` | 246 | nº 238 | (no texto da linha) |
| 195 | 44,2 | SNGS-136, detector penalizado (%) | 6 | `docs/04-relatorio-numeros.md` | 139 | nº 131 | 0.4424735973751346 |
| 196 | 5,45 | deslize_p90 (px) de Kalman + RTS na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 168 | nº 160 | 5.44652216220271 |
| 197 | 50,8 | SNGS-124, só propagação (%): a menor média do HSB | 6 | `docs/04-relatorio-numeros.md` | 133 | nº 125 | 0.508383235450467 |
| 198 | 5060 | hardware (Ryzen 7 5700X, 8 núcleos, 16 threads, RTX 5060; AuxFlow: RTX 4090) | 6 | `docs/04-relatorio-numeros.md` | 245 | nº 237 | (no texto da linha) |
| 199 | 52,9 | B2, HSB, 6a Bassek: cob_media | 6 | `docs/04-relatorio-numeros.md` | 454 | nº 446 | 0.5290917421695756 |
| 200 | 53,5 | jogadores invertidos do detector, penalizada (%) | 6 | `docs/04-relatorio-numeros.md` | 184 | nº 176 | 0.5347640828260538 |
| 201 | 61,7 | HSB (3) pipeline, média (%) | 6 | `docs/04-relatorio-numeros.md` | 125 | nº 117 | 0.617443855691164 |
| 202 | 79,7 | HSB (2) detector nos cobertos, média (%) | 6 | `docs/04-relatorio-numeros.md` | 124 | nº 116 | 0.7972039907849933 |
| 203 | 8,31 | deslize_p90 (px) de 6a Bassek na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 176 | nº 168 | 8.307192313852513 |
| 204 | 8,58 | parede da série do detector (h) | 6 | `docs/04-relatorio-numeros.md` | 225 | nº 217 | 8.575277777777778 |
| 205 | 81,4 | HSB (1) só propagação, média por frame (%) | 6 | `docs/04-relatorio-numeros.md` | 118 | nº 110 | 0.8137045363350623 |
| 206 | 85,7 | SNGS-136, pipeline (%) | 6 | `docs/04-relatorio-numeros.md` | 138 | nº 130 | 0.8570981719191836 |
| 207 | 87,2 | SNGS-136, só propagação (%) | 6 | `docs/04-relatorio-numeros.md` | 137 | nº 129 | 0.8722673151278317 |
| 208 | 92,7 | HSB (1) só propagação, mediana (%) | 6 | `docs/04-relatorio-numeros.md` | 119 | nº 111 | 0.9270635285619413 |
| 209 | 95,9 | a mesma fração, em % | 6 | `docs/04-relatorio-numeros.md` | 22 | nº 14 | 0.9590228680694096 |
| 210 | 96,5 | SNGS-138, só propagação (%) | 6 | `docs/04-relatorio-numeros.md` | 135 | nº 127 | 0.9650115435209584 |
| 211 | 97,4 | SNGS-128, só propagação (%) | 6 | `docs/04-relatorio-numeros.md` | 134 | nº 126 | 0.9739655444663796 |
| 212 | 0,004 | B5: IoU do gramado, ruído σ = 20 | 6 | `docs/04-relatorio-numeros.md` | 477 | nº 469 | 0.004165937081813937 |
| 213 | 0,017 | valor de um frame ou imagem nos subconjuntos | 6 | `docs/04-relatorio-numeros.md` | 290 | nº 282 | (no texto da linha) |
| 214 | 0,029 | valor de um frame ou imagem nos subconjuntos | 6 | `docs/04-relatorio-numeros.md` | 291 | nº 283 | (no texto da linha) |
| 215 | 0,035 | o mesmo, em módulo ("fica 0,035 abaixo") | 6 | `docs/04-relatorio-numeros.md` | 92 | nº 84 | 0.0350755 |
| 216 | 0,077 | B5: cobertura do detector, borrão de 21 px | 6 | `docs/04-relatorio-numeros.md` | 480 | nº 472 | 0.07655502392344497 |
| 217 | 0,102 | B5: aceitas erradas, limpa | 6 | `docs/04-relatorio-numeros.md` | 474 | nº 466 | 0.10185185185185185 |
| 218 | 0,131 | erro residual do detector no conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 103 | nº 95 | 0.131453 |
| 219 | 0,221 | HSB (2) detector, cobertura nos frames com pessoas | 6 | `docs/04-relatorio-numeros.md` | 123 | nº 115 | 0.22142857142857142 |
| 220 | 0,244 | B5: cobertura do detector, ruído σ = 10 | 6 | `docs/04-relatorio-numeros.md` | 476 | nº 468 | 0.24401913875598086 |
| 221 | 0,290 | ganho, IC inferior | 6 | `docs/04-relatorio-numeros.md` | 89 | nº 81 | 0.2902548453039891 |
| 222 | 0,360 | LocSim@5 penalizado do detector, jogo 8 | 6 | `docs/04-relatorio-numeros.md` | 76 | nº 68 | 0.35974187056903534 |
| 223 | 0,365 | ganho, IC superior | 6 | `docs/04-relatorio-numeros.md` | 90 | nº 82 | 0.36530951944000956 |
| 224 | 0,366 | locsim_pen de 6c sem fluxo (Tabela 1) | 6 | `docs/04-relatorio-numeros.md` | 47 | nº 39 | 0.3659943581643886 |
| 225 | 0,375 | B5: aceitas erradas, borrão de 21 px | 6 | `docs/04-relatorio-numeros.md` | 481 | nº 473 | 0.375 |
| 226 | 0,380 | RE mediano (m), WC14 test | 6 | `docs/04-relatorio-numeros.md` | 149 | nº 141 | 0.37991867462940904 |
| 227 | 0,387 | B3, acurácia a 5 px penalizada, test inteiro: detector | 6 | `docs/04-relatorio-numeros.md` | 423 | nº 415 | 0.3870120116100024 |
| 228 | 0,396 | B2, HSB, 6a Bassek: cob_fr | 6 | `docs/04-relatorio-numeros.md` | 453 | nº 445 | 0.39553571428571427 |
| 229 | 0,517 | B5: cobertura do detector, limpa | 6 | `docs/04-relatorio-numeros.md` | 473 | nº 465 | 0.5167464114832536 |
| 230 | 0,526 | B5: cobertura das marcações, sombra L* × 0,5 | 6 | `docs/04-relatorio-numeros.md` | 482 | nº 474 | 0.5262829077424046 |
| 231 | 0,543 | B5: cobertura das marcações, borrão de 11 px | 6 | `docs/04-relatorio-numeros.md` | 479 | nº 471 | 0.5432420429051623 |
| 232 | 0,551 | B3, acurácia a 5 px penalizada, test inteiro: 6c fluxo | 6 | `docs/04-relatorio-numeros.md` | 435 | nº 427 | 0.5507461043869207 |
| 233 | 0,575 | cobertura do detector no WC14 test | 6 | `docs/04-relatorio-numeros.md` | 144 | nº 136 | 0.5752688172043011 |
| 234 | 0,612 | B5: cobertura das marcações a 2 px, limpa | 6 | `docs/04-relatorio-numeros.md` | 472 | nº 464 | 0.6116499441208049 |
| 235 | 0,613 | B3, acurácia a 5 px nos cobertos, test inteiro: 6c fluxo | 6 | `docs/04-relatorio-numeros.md` | 436 | nº 428 | 0.6133308889763437 |
| 236 | 0,656 | B4, fração ao teto do sistema: 6c fluxo | 6 | `docs/04-relatorio-numeros.md` | 416 | nº 408 | 0.6558496227128815 |
| 237 | 0,676 | LocSim@5 penalizado do 6c, jogo 7 | 6 | `docs/04-relatorio-numeros.md` | 69 | nº 61 | 0.6759710080828238 |
| 238 | 0,684 | B4, fração ao teto do sistema: 6c âncora de gabarito | 6 | `docs/04-relatorio-numeros.md` | 420 | nº 412 | 0.6838727673232315 |
| 239 | 0,708 | B5: IoU do gramado, ruído σ = 10 | 6 | `docs/04-relatorio-numeros.md` | 475 | nº 467 | 0.7081201491899404 |
| 240 | 0,715 | locsim_pen de 6c sem linhas (Tabela 1) | 6 | `docs/04-relatorio-numeros.md` | 42 | nº 34 | 0.715153688402002 |
| 241 | 0,735 | B3, acurácia a 5 px penalizada, conjunto comum: 6a Bassek | 6 | `docs/04-relatorio-numeros.md` | 428 | nº 420 | 0.7345968707726277 |
| 242 | 0,763 | LocSim@5 penalizado do teto | 6 | `docs/04-relatorio-numeros.md` | 57 | nº 49 | 0.7631048970488494 |
| 243 | 0,807 | B3, acurácia a 5 px penalizada, conjunto comum: 6c fluxo | 6 | `docs/04-relatorio-numeros.md` | 437 | nº 429 | 0.8071876639570899 |
| 244 | 0,818 | LocSim@5 da âncora ingênua no conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 113 | nº 105 | 0.8184115515728485 |
| 245 | 0,838 | cobertura do 6c, jogo 8 | 6 | `docs/04-relatorio-numeros.md` | 75 | nº 67 | 0.8381332151823955 |
| 246 | 0,864 | IoU_whole médio, WC14 test | 6 | `docs/04-relatorio-numeros.md` | 147 | nº 139 | 0.8635098695256653 |
| 247 | 0,889 | B5: menor IoU do campo inteiro mediano entre os níveis com resposta (borrão de 21 px) | 6 | `docs/04-relatorio-numeros.md` | 486 | nº 478 | 0.8894947602438756 |
| 248 | 0,913 | IoU_whole mediano, WC14 test | 6 | `docs/04-relatorio-numeros.md` | 146 | nº 138 | 0.9131266960388786 |
| 249 | 0,934 | B4, teto do sistema no conjunto comum: LocSim@5 pen. | 6 | `docs/04-relatorio-numeros.md` | 411 | nº 403 | 0.9339418502696739 |
| 250 | 0,959 | fração da distância ao teto condicionado às âncoras, propagação | 6 | `docs/04-relatorio-numeros.md` | 21 | nº 13 | 0.9590228680694096 |
| 251 | 0,969 | B5: IoU do gramado, sombra L* × 0,35 | 6 | `docs/04-relatorio-numeros.md` | 483 | nº 475 | 0.9692651972516488 |
| 252 | 0,986 | fração ao teto, IC superior | 6 | `docs/04-relatorio-numeros.md` | 24 | nº 16 | 0.9860390545455364 |
| 253 | 0,987 | correlação mediana do ECC | 6 | `docs/04-relatorio-numeros.md` | 162 | nº 154 | (no texto da linha) |
| 254 | 0,995 | IoU_part mediano, WC14 test | 6 | `docs/04-relatorio-numeros.md` | 148 | nº 140 | 0.9946079029829488 |
| 255 | 1,615 | RE médio (m), WC14 test | 6 | `docs/04-relatorio-numeros.md` | 150 | nº 142 | 1.615112838440006 |
| 256 | 1.120 | frames com pessoas do HSB | 6 | `docs/04-relatorio-numeros.md` | 128 | nº 120 | (no texto da linha) |
| 257 | 15,50 | tremor_p90 (px) de detector na interseção (T4b) | 6 | `docs/04-relatorio-numeros.md` | 174 | nº 166 | 15.502834899744936 |
| 258 | 23,51 | deslize p90 (px) do Kalman no próprio conjunto | 6 | `docs/04-relatorio-numeros.md` | 178 | nº 170 | 23.513633413460205 |
| 259 | 3.570 | detector, s por clipe de 750 frames num núcleo (perfil) | 6 | `docs/04-relatorio-numeros.md` | 238 | nº 230 | (no texto da linha) |
| 260 | 72,61 | deslize p90 (px) do 6a Bassek no próprio conjunto | 6 | `docs/04-relatorio-numeros.md` | 179 | nº 171 | 72.60673345089245 |
| 261 | 96,15 | AuxFlow no HSB, mediana (tabela 4) | 6 | `docs/04-relatorio-numeros.md` | 132 | nº 124 | (no texto da linha) |
| 262 | +0,003 | IC inferior do Δ do line_thr 15 | 6 | `docs/04-relatorio-numeros.md` | 299 | nº 291 | (no texto da linha) |
| 263 | +0,034 | Δ LocSim do line_thr 15 | 6 | `docs/04-relatorio-numeros.md` | 298 | nº 290 | (no texto da linha) |
| 264 | +0,044 | ganho AuxFlow − NBJW | 6 | `docs/04-relatorio-numeros.md` | 97 | nº 89 | 0.04400000000000004 |
| 265 | +0,065 | IC superior do Δ do line_thr 15 | 6 | `docs/04-relatorio-numeros.md` | 300 | nº 292 | (no texto da linha) |
| 266 | +0,127 | Δ LocSim do line_thr 15 no jogo 4 | 6 | `docs/04-relatorio-numeros.md` | 301 | nº 293 | (no texto da linha) |
| 267 | +0,330 | ganho 6c − detector, penalizado | 6 | `docs/04-relatorio-numeros.md` | 88 | nº 80 | 0.32973938261759295 |
| 268 | 0,0056 | NPE mediano do jogo 9, limiar 30 | 6 | `docs/04-relatorio-numeros.md` | 303 | nº 295 | (no texto da linha) |
| 269 | 0,0066 | NPE mediano do 6c no conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 112 | nº 104 | 0.006647632074273963 |
| 270 | 0,0072 | NPE mediano do detector | 6 | `docs/04-relatorio-numeros.md` | 14 | nº 6 | 0.007228082696151382 |
| 271 | 0,0095 | NPE mediano, 6c fluxo, lacuna 1-3 | 6 | `docs/04-relatorio-numeros.md` | 201 | nº 193 | 0.00951444925996717 |
| 272 | 0,0130 | NPE mediano do jogo 9, limiar 15 | 6 | `docs/04-relatorio-numeros.md` | 304 | nº 296 | (no texto da linha) |
| 273 | 0,0168 | NPE mediano, 6c fluxo, lacuna 4-25 | 6 | `docs/04-relatorio-numeros.md` | 206 | nº 198 | 0.01679906796130583 |
| 274 | 0,0242 | NPE mediano do 6a Bassek com as duas bordas certas | 6 | `docs/04-relatorio-numeros.md` | 224 | nº 216 | 0.024242664392004017 |
| 275 | 0,0551 | NPE mediano, 6c fluxo, lacuna > 25 | 6 | `docs/04-relatorio-numeros.md` | 209 | nº 201 | 0.055100629444049976 |
| 276 | 0,0785 | NPE mediano, 6c sem linhas, lacuna > 25 | 6 | `docs/04-relatorio-numeros.md` | 210 | nº 202 | 0.07853632934367849 |
| 277 | 0,1248 | npe_med de 6c sem fluxo (Tabela 1) | 6 | `docs/04-relatorio-numeros.md` | 46 | nº 38 | 0.12482665639288845 |
| 278 | 0,5155 | iou_whole médio no protocolo KpSFR, 186 imagens com 0 nas sem H | 6 | `docs/04-relatorio-numeros.md` | 153 | nº 145 | 0.5155405764999672 |
| 279 | 0,8634 | iou_whole mediano no protocolo KpSFR, 186 imagens com 0 nas sem H | 6 | `docs/04-relatorio-numeros.md` | 154 | nº 146 | 0.8634408188538885 |
| 280 | 0,8962 | iou_whole médio no protocolo KpSFR, 107 imagens com H | 6 | `docs/04-relatorio-numeros.md` | 155 | nº 147 | 0.8961733385887282 |
| 281 | 0,8994 | NPE mediano, 6a Bassek, lacuna 4-25 | 6 | `docs/04-relatorio-numeros.md` | 204 | nº 196 | 0.899380036414921 |
| 282 | 0,9534 | iou_whole mediano no protocolo KpSFR, 107 imagens com H | 6 | `docs/04-relatorio-numeros.md` | 156 | nº 148 | 0.953413059768704 |
| 283 | 17.828 | frames na interseção das cinco séries | 6 | `docs/04-relatorio-numeros.md` | 163 | nº 155 | (no texto da linha) |
| 284 | 18.133 | frames do conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 100 | nº 92 | 18133 |
| 285 | 36.701 | pares de frames consecutivos do ECC | 6 | `docs/04-relatorio-numeros.md` | 161 | nº 153 | (no texto da linha) |
| 286 | 36.750 | frames do GSR test | 6 | `docs/04-relatorio-numeros.md` | 164 | nº 156 | (no texto da linha) |
| 287 | −0,003 | ganho nos cobertos, IC superior | 6 | `docs/04-relatorio-numeros.md` | 94 | nº 86 | -0.00307166492950528 |
| 288 | −0,046 | Δ LocSim do line_thr 15 no jogo 9 | 6 | `docs/04-relatorio-numeros.md` | 302 | nº 294 | (no texto da linha) |
| 289 | −0,078 | ganho nos cobertos, IC inferior | 6 | `docs/04-relatorio-numeros.md` | 93 | nº 85 | -0.0780199152971085 |
| 290 | 11 | B5, protocolo: núcleo do borrão de 11 px | 6 | `docs/04-relatorio-numeros.md` | 461 | nº 453 | (no texto da linha) |
| 291 | 11 | B3: redução do erro (1 − acurácia a 5 px) | 6 | `docs/04-relatorio-numeros.md` | 450 | nº 442 | 10.5885 |
| 292 | 52 | fração do campo coberta pelo gramado no jogo 3 da valid | 6 | `docs/04-relatorio-numeros.md` | 305 | nº 297 | (no texto da linha) |
| 293 | 0,0 | HSB (2) detector, mediana | 6 | `docs/04-relatorio-numeros.md` | 122 | nº 114 | 0.0 |
| 294 | 0,8 | jogadores invertidos do 6c na interseção | 6 | `docs/04-relatorio-numeros.md` | 181 | nº 173 | 0.008411584582703042 |
| 295 | 0,8 | aceita errada: IoU do campo inteiro < 0,8 | 6 | `docs/04-relatorio-numeros.md` | 469 | nº 461 | (no texto da linha) |
| 296 | 1,71 | deslize_med (px) de Kalman + RTS na interseção | 6 | `docs/04-relatorio-numeros.md` | 167 | nº 159 | 1.7122490859544373 |
| 297 | 1,71 | parede do 6c (h) | 6 | `docs/04-relatorio-numeros.md` | 233 | nº 225 | 1.7094444444444445 |
| 298 | 0,078 | erro residual da propagação no conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 104 | nº 96 | 0.0781691 |
| 299 | 0,341 | LocSim@5 penalizado do detector, jogo 7 | 6 | `docs/04-relatorio-numeros.md` | 68 | nº 60 | 0.3410869352412535 |
| 300 | 0,478 | B5: cobertura do detector, oclusão de 20% | 6 | `docs/04-relatorio-numeros.md` | 485 | nº 477 | 0.4784688995215311 |
| 301 | 0,533 | B3, acurácia a 5 px nos cobertos, test inteiro: H_gt_auxflow | 6 | `docs/04-relatorio-numeros.md` | 448 | nº 440 | 0.5329837781433937 |
| 302 | 0,533 | B5: cobertura das marcações, oclusão de 20% | 6 | `docs/04-relatorio-numeros.md` | 484 | nº 476 | 0.5333991581010133 |
| 303 | 0,555 | LocSim@5 penalizado do detector, jogo 11 | 6 | `docs/04-relatorio-numeros.md` | 84 | nº 76 | 0.5546704626197827 |
| 304 | 0,571 | locsim_pen de 6c âncora ingênua /150 | 6 | `docs/04-relatorio-numeros.md` | 52 | nº 44 | 0.5713680143832477 |
| 305 | 0,784 | B3, acurácia a 5 px nos cobertos, test inteiro: detector | 6 | `docs/04-relatorio-numeros.md` | 424 | nº 416 | 0.7843540190077531 |
| 306 | 0,784 | B3, acurácia a 5 px penalizada, conjunto comum: detector | 6 | `docs/04-relatorio-numeros.md` | 425 | nº 417 | 0.7843540190077531 |
| 307 | 0,869 | LocSim@5 do detector nos cobertos | 6 | `docs/04-relatorio-numeros.md` | 13 | nº 5 | 0.8685472817991973 |
| 308 | 0,869 | LocSim@5 penalizado do detector no conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 102 | nº 94 | 0.8685472817991973 |
| 309 | 0,869 | B3, acurácia a 5 px nos cobertos, test inteiro: H_gt pelas linhas | 6 | `docs/04-relatorio-numeros.md` | 445 | nº 437 | 0.8694627714311767 |
| 310 | 0,899 | B4, teto do sistema: LocSim@5 pen., mín. entre os jogos | 6 | `docs/04-relatorio-numeros.md` | 404 | nº 396 | 0.8989835004477721 |
| 311 | 0,922 | LocSim@5 penalizado do 6c no conjunto comum | 6 | `docs/04-relatorio-numeros.md` | 101 | nº 93 | 0.9218309048117984 |
| 312 | 0,922 | B4, teto do sistema: LocSim@5 penalizado | 6 | `docs/04-relatorio-numeros.md` | 402 | nº 394 | 0.92204315807928 |
| 313 | 0,925 | fração ao teto, IC inferior | 6 | `docs/04-relatorio-numeros.md` | 23 | nº 15 | 0.9254527945921875 |
| 314 | 0,930 | LocSim@5 da propagação no conjunto comum, nos frames que ela cobre | 6 | `docs/04-relatorio-numeros.md` | 399 | nº 391 | 0.9302394650733893 |
| 315 | 0,930 | B5: maior IoU do campo inteiro mediano | 6 | `docs/04-relatorio-numeros.md` | 487 | nº 479 | 0.9302916877530989 |
| 316 | 0,949 | B4, teto do sistema: LocSim@5 pen., máx. entre os jogos | 6 | `docs/04-relatorio-numeros.md` | 405 | nº 397 | 0.9486980128017087 |
| 317 | 1,000 | cobertura do 6c, jogo 11 | 6 | `docs/04-relatorio-numeros.md` | 83 | nº 75 | 1.0 |
| 318 | 1,000 | B4, teto do sistema: cobertura | 6 | `docs/04-relatorio-numeros.md` | 400 | nº 392 | 1.0 |
| 319 | 13 | clipes sem âncora da valid no jogo 3 | 7 | `docs/04-relatorio-numeros.md` | 265 | nº 257 | (no texto da linha) |
| 320 | 26 | lacuna da Figura 7 (2-26) | 7 | `docs/04-relatorio-numeros.md` | 287 | nº 279 | (no texto da linha) |
| 321 | 99 | lacunas de 4-25 com as duas bordas certas | 7 | `docs/04-relatorio-numeros.md` | 218 | nº 210 | 99 |
| 322 | 106 | lacunas de 4-25 com uma borda errada | 7 | `docs/04-relatorio-numeros.md` | 219 | nº 211 | 106 |
| 323 | 250 | faixa de distância à âncora (> 250 frames) | 7 | `docs/04-relatorio-numeros.md` | 284 | nº 276 | (no texto da linha) |
| 324 | 331 | lacunas de 4-25 com as duas bordas erradas | 7 | `docs/04-relatorio-numeros.md` | 220 | nº 212 | 331 |
| 325 | 537 | lacunas de 4-25 frames no test | 7 | `docs/04-relatorio-numeros.md` | 222 | nº 214 | 537 |
| 326 | 7,1 | NPE do 6a Bassek no meio da lacuna da Figura 7 (SNGS-121, f14) | 7 | `docs/04-relatorio-numeros.md` | 285 | nº 277 | 7.107828310199786 |
| 327 | 0,79 | cobertura das marcações a 2 px, referência da Fatia 3 (GSR train) | 7 | `docs/04-relatorio-numeros.md` | 274 | nº 266 | (no texto da linha) |
| 328 | 0,81 | cobertura das marcações a 2 px, SNGS-127 | 7 | `docs/04-relatorio-numeros.md` | 270 | nº 262 | 0.8090467516697024 |
| 329 | 0,98 | cobertura das marcações a 2 px, SNGS-138 | 7 | `docs/04-relatorio-numeros.md` | 272 | nº 264 | 0.9770642201834863 |
| 330 | 15,9 | maior cobertura do detector nos sem âncora (SNGS-147, %) | 7 | `docs/04-relatorio-numeros.md` | 280 | nº 272 | 0.15930388219544847 |
| 331 | 71,1 | HSB (3) pipeline, mediana (%) | 7 | `docs/04-relatorio-numeros.md` | 126 | nº 118 | 0.7110783802185268 |
| 332 | 0,060 | menor NPE das âncoras de encaixe parcial (SNGS-122 f657) | 7 | `docs/04-relatorio-numeros.md` | 261 | nº 253 | 0.0596927737995924 |
| 333 | 0,063 | NPE da âncora SNGS-132 f721 | 7 | `docs/04-relatorio-numeros.md` | 263 | nº 255 | 0.0633359702238581 |
| 334 | 0,208 | NPE mediano do 6c nas pontas a > 250 frames da âncora | 7 | `docs/04-relatorio-numeros.md` | 283 | nº 275 | 0.207852393306958 |
| 335 | 0,235 | maior NPE das âncoras de encaixe parcial (SNGS-190 f525) | 7 | `docs/04-relatorio-numeros.md` | 262 | nº 254 | 0.23549481829491842 |
| 336 | 0,506 | LocSim@5 penalizado do 6c, SNGS-144 | 7 | `docs/04-relatorio-numeros.md` | 251 | nº 243 | 0.5055174044700732 |
| 337 | 0,635 | LocSim@5 penalizado do 6c, SNGS-126 | 7 | `docs/04-relatorio-numeros.md` | 254 | nº 246 | 0.634512353785477 |
| 338 | 0,954 | LocSim@5 penalizado do teto, SNGS-126 | 7 | `docs/04-relatorio-numeros.md` | 255 | nº 247 | 0.9541771572553578 |
| 339 | 0,988 | menor fração do campo como grama nos sem âncora (SNGS-138) | 7 | `docs/04-relatorio-numeros.md` | 269 | nº 261 | 0.9881636617093701 |
| 340 | 1,355 | NPE da âncora SNGS-126 f588 | 7 | `docs/04-relatorio-numeros.md` | 260 | nº 252 | 1.3550949476054246 |
| 341 | 0,0059 | NPE mediano do 6c a <= 25 frames da âncora, frames com H do detector | 7 | `docs/04-relatorio-numeros.md` | 281 | nº 273 | 0.005897785590997996 |
| 342 | 0,0101 | NPE mediano do 6c a <= 25 frames da âncora, pontas | 7 | `docs/04-relatorio-numeros.md` | 282 | nº 274 | 0.010138998451541235 |
| 343 | 0,7 | menor cobertura do detector nos sem âncora | 7 | `docs/04-relatorio-numeros.md` | 279 | nº 271 | 0.007194244604316547 |
| 344 | 0,495 | LocSim@5 penalizado do 6c, SNGS-143 | 7 | `docs/04-relatorio-numeros.md` | 249 | nº 241 | 0.4952325656550445 |
| 345 | 0,495 | LocSim@5 penalizado do teto, SNGS-143 | 7 | `docs/04-relatorio-numeros.md` | 250 | nº 242 | 0.49477118746227106 |
| 346 | 0,508 | LocSim@5 penalizado do teto, SNGS-144 | 7 | `docs/04-relatorio-numeros.md` | 252 | nº 244 | 0.5077625470280754 |
| 347 | 36 | clipes que melhoram | 8 | `docs/04-relatorio-v2-numeros.md` | 114 | nº 106 | 36 |
| 348 | 59 | A': clipes da metade fixa | 8 | `docs/04-relatorio-v2-numeros.md` | 28 | nº 20 | (no texto da linha) |
| 349 | 1,4 | aceitas erradas entre as com gabarito, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 107 | nº 99 | 1.44928 |
| 350 | 290 | H novas no v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 61 | nº 53 | 290 |
| 351 | 448 | A': H centrais da checagem barata | 8 | `docs/04-relatorio-v2-numeros.md` | 32 | nº 24 | (no texto da linha) |
| 352 | 722 | H do v1 idênticas bit a bit | 8 | `docs/04-relatorio-v2-numeros.md` | 60 | nº 52 | 722 |
| 353 | 765 | âncoras aceitas (n), v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 101 | nº 93 | 765 |
| 354 | 0,06 | os dois do HSB pioram cerca disto | 8 | `docs/04-relatorio-v2-numeros.md` | 118 | nº 110 | 0.06 |
| 355 | 74,5 | HSB, (3) pipeline pen média, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 77 | nº 69 | 0.7447292972410947 |
| 356 | 81,9 | HSB, (3) pipeline pen mediana, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 79 | nº 71 | 0.8191605056318045 |
| 357 | 0,006 | SNGS-136, f189: menor NPE das recusadas pelo B1 | 8 | `docs/04-relatorio-v2-numeros.md` | 142 | nº 134 | 0.0057681588338117625 |
| 358 | 0,008 | os três que pioram menos pioram menos que isto | 8 | `docs/04-relatorio-v2-numeros.md` | 117 | nº 109 | 0.008 |
| 359 | 0,020 | SNGS-136, f39: menor NPE das aceitas até a f110 | 8 | `docs/04-relatorio-v2-numeros.md` | 140 | nº 132 | 0.01977759733537401 |
| 360 | 0,020 | SNGS-136, f9: maior NPE das recusadas pelo B1 | 8 | `docs/04-relatorio-v2-numeros.md` | 143 | nº 135 | 0.02036185695399478 |
| 361 | 0,027 | AuxFlow − propagação do v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 95 | nº 87 | 0.0268465 |
| 362 | 0,032 | SNGS-136, f110: maior NPE das aceitas até a f110 | 8 | `docs/04-relatorio-v2-numeros.md` | 141 | nº 133 | 0.03173352631317232 |
| 363 | 0,624 | locsim_pen de detector, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 49 | nº 41 | 0.624146109585618 |
| 364 | 0,914 | locsim_pen de 6c âncora de gabarito, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 57 | nº 49 | 0.9140772351342509 |
| 365 | 0,914 | LocSim@5 pen. da propagação, jogo 7, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 63 | nº 55 | 0.9135220326519915 |
| 366 | 0,956 | LocSim@5 pen. da propagação, jogo 11, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 67 | nº 59 | 0.9564874784910701 |
| 367 | 0,954 | LocSim@5 pen. do teto condicionado, jogo 11, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 70 | nº 62 | 0.954306161772318 |
| 368 | 0,902 | LocSim@5 penalizado da propagação, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 11 | nº 3 | 0.9021534525340882 |
| 369 | 0,017 | propagação do v2 − NBJW | 8 | `docs/04-relatorio-v2-numeros.md` | 96 | nº 88 | 0.0171535 |
| 370 | 85 | fração da distância entre a propagação do v1 e o AuxFlow | 8 | `docs/04-relatorio-v2-numeros.md` | 97 | nº 89 | 85.0839 |
| 371 | 0,839 | LocSim@5 pen. da propagação, jogo 8, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 65 | nº 57 | 0.838581896876749 |
| 372 | 0,702 | cobertura de detector, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 51 | nº 43 | 0.7023849325755043 |
| 373 | 0,763 | locsim_pen de 6c âncora de gabarito, v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 56 | nº 48 | 0.7631048970488494 |
| 374 | 0,959 | fracao_teto de 6c fluxo, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 55 | nº 47 | 0.9588737408665611 |
| 375 | 5 | A': jogos com Δ > 0 (critério antigo) | 8 | `docs/04-relatorio-v2-numeros.md` | 15 | nº 7 | 5 |
| 376 | 6 | A': jogos com Δ >= 0 (critério novo) | 8 | `docs/04-relatorio-v2-numeros.md` | 16 | nº 8 | 6 |
| 377 | −0,03 | critério do plano: nenhum jogo abaixo de −0,03 | 8 | `docs/04-relatorio-v2-numeros.md` | 14 | nº 6 | (no texto da linha) |
| 378 | +0,178 | A': média dos Δ por jogo | 8 | `docs/04-relatorio-v2-numeros.md` | 17 | nº 9 | 0.17811624575279686 |
| 379 | 4 | critério do plano: ganho em >= 4 de 6 jogos | 8 | `docs/04-relatorio-v2-numeros.md` | 12 | nº 4 | (no texto da linha) |
| 380 | 6 | critério do plano: 6 jogos de dev | 8 | `docs/04-relatorio-v2-numeros.md` | 13 | nº 5 | (no texto da linha) |
| 381 | 5 | C: jogos em que piorou | 8 | `docs/04-relatorio-v2-numeros.md` | 24 | nº 16 | 5 |
| 382 | 3 | B2: jogos com Δ = 0 | 8 | `docs/04-relatorio-v2-numeros.md` | 25 | nº 17 | (no texto da linha) |
| 383 | 3 | A: H novas no jogo 3, todas erradas | 8 | `docs/04-relatorio-v2-numeros.md` | 26 | nº 18 | (no texto da linha) |
| 384 | 20 | A': contagem mínima de H novas | 8 | `docs/04-relatorio-v2-numeros.md` | 27 | nº 19 | (no texto da linha) |
| 385 | 4 | A': H centrais recusadas pelo filtro | 8 | `docs/04-relatorio-v2-numeros.md` | 31 | nº 23 | (no texto da linha) |
| 386 | 4 | B1b: clipes que a regra mexe | 8 | `docs/04-relatorio-v2-numeros.md` | 29 | nº 21 | (no texto da linha) |
| 387 | 2 | B1b: jogos que a regra mexe | 8 | `docs/04-relatorio-v2-numeros.md` | 30 | nº 22 | (no texto da linha) |
| 388 | 5 | B1: jogos com Δ > 0 na leitura leave-one-game-out | 8 | `docs/04-relatorio-v2-numeros.md` | 22 | nº 14 | 5 |
| 389 | 1,000 | cobertura da propagação, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 20 | nº 12 | 1.0 |
| 390 | 558 | âncoras aceitas (n), v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 100 | nº 92 | 558 |
| 391 | 12 | âncoras aceitas (erradas), v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 102 | nº 94 | 12 |
| 392 | 11 | âncoras aceitas (erradas), v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 103 | nº 95 | 11 |
| 393 | 2,2 | aceitas erradas entre as com gabarito, v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 106 | nº 98 | 2.1544 |
| 394 | 5 | clipes do test sem âncora aceita, v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 9 | nº 1 | 5 |
| 395 | 0 | clipes do test sem âncora aceita, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 10 | nº 2 | 0 |
| 396 | 61,7 | HSB, (3) pipeline pen média, v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 76 | nº 68 | 0.617443855691164 |
| 397 | 71,1 | HSB, (3) pipeline pen mediana, v1 | 8 | `docs/04-relatorio-v2-numeros.md` | 78 | nº 70 | 0.7110783802185268 |
| 398 | 83,67 | AuxFlow no HSB, média | 8 | `docs/04-relatorio-v2-numeros.md` | 83 | nº 75 | (no texto da linha) |
| 399 | 96,15 | AuxFlow no HSB, mediana | 8 | `docs/04-relatorio-v2-numeros.md` | 84 | nº 76 | (no texto da linha) |
| 400 | 81,4 | HSB, (1) só propagação pen média, v2 | 8 | `docs/04-relatorio-v2-numeros.md` | 82 | nº 74 | 0.8137045363350623 |
| 401 | 0,929 | LocSim@5 do AuxFlow | 8 | `docs/04-relatorio-v2-numeros.md` | 93 | nº 85 | 0.929 |
| 402 | 0,885 | LocSim@5 do NBJW | 8 | `docs/04-relatorio-v2-numeros.md` | 94 | nº 86 | 0.885 |
| 403 | 1 | conferência contra o v1 a 1 frame em 25 | 8 | `docs/04-relatorio-v2-numeros.md` | 58 | nº 50 | (no texto da linha) |
| 404 | 25 | conferência contra o v1 a 1 frame em 25 | 8 | `docs/04-relatorio-v2-numeros.md` | 59 | nº 51 | (no texto da linha) |
| 405 | 49 | clipes do GSR test | 8 | `docs/04-relatorio-v2-numeros.md` | 19 | nº 11 | 49 |
| 406 | −0,0123 | Δ por jogo de dev, linha 4 / 0,5155 / 0,5032 / −0,0123 | 8.3, Tabela 11 | `docs/decisoes.md` | 1059 | — | (no texto da linha) |
| 407 | +0,0034 | Δ por jogo de dev, linha 6 / 0,8805 / 0,8839 / +0,0034 | 8.3, Tabela 11 | `docs/decisoes.md` | 1060 | — | (no texto da linha) |
| 408 | −0,0029 | Δ por jogo de dev, linha 9 / 0,8282 / 0,8252 / −0,0029 | 8.3, Tabela 11 | `docs/decisoes.md` | 1061 | — | (no texto da linha) |
| 409 | −0,0059 | Δ por jogo de dev, linha 2 / 0,6427 / 0,6368 / −0,0059 | 8.3, Tabela 11 | `docs/decisoes.md` | 1062 | — | (no texto da linha) |
| 410 | −0,0078 | Δ por jogo de dev, linha 3 / 0,1410 / 0,1332 / −0,0078 | 8.3, Tabela 11 | `docs/decisoes.md` | 1063 | — | (no texto da linha) |
| 411 | −0,0050 | Δ por jogo de dev, linha 5 / 0,6273 / 0,6223 / −0,0050 | 8.3, Tabela 11 | `docs/decisoes.md` | 1064 | — | (no texto da linha) |
| 412 | +0,0175 | Δ por jogo de dev, linha 4 / 0,5155 / 0,5331 / +0,0175 / = / +0,0175 | 8.3, Tabela 11 | `docs/decisoes.md` | 1095 | — | (no texto da linha) |
| 413 | 0,0000 | Δ por jogo de dev, linha 6 / 0,8805 / 0,8805 / 0,0000 / = / 0,0000 | 8.3, Tabela 11 | `docs/decisoes.md` | 1096 | — | (no texto da linha) |
| 414 | 0,0000 | Δ por jogo de dev, linha 9 / 0,8282 / 0,8282 / 0,0000 / 0,8282 (11,25 m) / 0,0000 | 8.3, Tabela 11 | `docs/decisoes.md` | 1097 | — | (no texto da linha) |
| 415 | −0,0083 | Δ por jogo de dev, linha 2 / 0,6427 / 0,6130 / −0,0297 / 0,6344 (8,48 m) / −0,0083 | 8.3, Tabela 11 | `docs/decisoes.md` | 1098 | — | (no texto da linha) |
| 416 | +0,0042 | Δ por jogo de dev, linha 3 / 0,1410 / 0,1452 / +0,0042 / = / +0,0042 | 8.3, Tabela 11 | `docs/decisoes.md` | 1099 | — | (no texto da linha) |
| 417 | 0,0000 | Δ por jogo de dev, linha 5 / 0,6273 / 0,6273 / 0,0000 / = / 0,0000 | 8.3, Tabela 11 | `docs/decisoes.md` | 1100 | — | (no texto da linha) |
| 418 | 0 | Δ por jogo de dev, linha 4 / 0,5155 / 0,5155 / 0 | 8.3, Tabela 11 | `docs/decisoes.md` | 1130 | — | (no texto da linha) |
| 419 | 0 | Δ por jogo de dev, linha 6 / 0,8805 / 0,8805 / 0 | 8.3, Tabela 11 | `docs/decisoes.md` | 1131 | — | (no texto da linha) |
| 420 | 0 | Δ por jogo de dev, linha 9 / 0,8282 / 0,8282 / 0 | 8.3, Tabela 11 | `docs/decisoes.md` | 1132 | — | (no texto da linha) |
| 421 | +0,0223 | Δ por jogo de dev, linha 2 / 0,6427 / 0,6651 / +0,0223 | 8.3, Tabela 11 | `docs/decisoes.md` | 1133 | — | (no texto da linha) |
| 422 | +0,0007 | Δ por jogo de dev, linha 3 / 0,1410 / 0,1417 / +0,0007 | 8.3, Tabela 11 | `docs/decisoes.md` | 1134 | — | (no texto da linha) |
| 423 | 0 | Δ por jogo de dev, linha 5 / 0,6273 / 0,6273 / 0 | 8.3, Tabela 11 | `docs/decisoes.md` | 1135 | — | (no texto da linha) |
| 424 | +0,3936 | Δ por jogo de dev, linha 4 / 9 / 0,4219 / 0,8155 / +0,3936 | 8.3, Tabela 11 | `docs/decisoes.md` | 1169 | — | (no texto da linha) |
| 425 | +0,0322 | Δ por jogo de dev, linha 6 / 10 / 0,8898 / 0,9220 / +0,0322 | 8.3, Tabela 11 | `docs/decisoes.md` | 1170 | — | (no texto da linha) |
| 426 | +0,1203 | Δ por jogo de dev, linha 9 / 10 / 0,7665 / 0,8868 / +0,1203 | 8.3, Tabela 11 | `docs/decisoes.md` | 1171 | — | (no texto da linha) |
| 427 | +0,2978 | Δ por jogo de dev, linha 2 / 9 / 0,5499 / 0,8478 / +0,2978 | 8.3, Tabela 11 | `docs/decisoes.md` | 1172 | — | (no texto da linha) |
| 428 | 0 | Δ por jogo de dev, linha 3 / 11 / 0,2471 / 0,2471 / 0 | 8.3, Tabela 11 | `docs/decisoes.md` | 1173 | — | (no texto da linha) |
| 429 | +0,2247 | Δ por jogo de dev, linha 5 / 10 / 0,6256 / 0,8504 / +0,2247 | 8.3, Tabela 11 | `docs/decisoes.md` | 1174 | — | (no texto da linha) |
| 430 | +0,0245 | A: piora da fração de aceitas erradas no jogo 3 (checagem barata) | 8.3 | `docs/decisoes.md` | 1119 | — | (no texto da linha) |
| 431 | 0,02 | checagem barata: limite de piora da fração de aceitas erradas | 8.2, 8.3 | `docs/05-melhorias-plano.md` | 155 | — | (no texto da linha) |
| 432 | 14 | calibração do GSR (material suplementar) | 9.1 | `C:/Users/victo/Downloads/Topicos Av pdi/SoccerNet Game State Reconstruction__End-to-End Athlete Tracking and Identification on a Minimap_compressed.pdf` | — | p. 14 | “pinhole camera model augmented with one radial distortion coefficient” |
| 433 | 14 | calibração do GSR (material suplementar) | 9.1 | `C:/Users/victo/Downloads/Topicos Av pdi/SoccerNet Game State Reconstruction__End-to-End Athlete Tracking and Identification on a Minimap_compressed.pdf` | — | p. 14 | “only the camera position can be considered fixed” |
| 434 | 14 | calibração do GSR (material suplementar) | 9.1 | `C:/Users/victo/Downloads/Topicos Av pdi/SoccerNet Game State Reconstruction__End-to-End Athlete Tracking and Identification on a Minimap_compressed.pdf` | — | p. 14 | “It is estimated as the median 3D position” |
| 435 | 14 | calibração do GSR (material suplementar) | 9.1 | `C:/Users/victo/Downloads/Topicos Av pdi/SoccerNet Game State Reconstruction__End-to-End Athlete Tracking and Identification on a Minimap_compressed.pdf` | — | p. 14 | “A similar version of the Two-Point PTZ algorithm” |
| 436 | 14 | calibração do GSR (material suplementar) | 9.1 | `C:/Users/victo/Downloads/Topicos Av pdi/SoccerNet Game State Reconstruction__End-to-End Athlete Tracking and Identification on a Minimap_compressed.pdf` | — | p. 14 | “an industrial tool is used” |
| 437 | 0,9319 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 438 | 0,9330 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 439 | 0,9333 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 440 | 3.362 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 441 | 1 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 442 | 25 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 443 | 0,029 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 444 | +0,001 | D1, lente (calibração no treino/valid) | 9.1 | `docs/decisoes.md` | 1071 | — | (no texto da linha) |
| 445 | 0,4 | D2, centro da câmera por clipe e por frame (calibração no treino/valid) | 9.1, 9.5 | `docs/decisoes.md` | 1072 | — | (no texto da linha) |
| 446 | 1,3 | D2, centro da câmera por clipe e por frame (calibração no treino/valid) | 9.1, 9.5 | `docs/decisoes.md` | 1072 | — | (no texto da linha) |
| 447 | 1,2 | D2, centro da câmera por clipe e por frame (calibração no treino/valid) | 9.1, 9.5 | `docs/decisoes.md` | 1072 | — | (no texto da linha) |
| 448 | 2,4 | D2, centro da câmera por clipe e por frame (calibração no treino/valid) | 9.1, 9.5 | `docs/decisoes.md` | 1072 | — | (no texto da linha) |
| 449 | 0,855 | D3, AUC da nota e do centro da câmera (calibração no treino/valid) | 9.2 | `docs/decisoes.md` | 1074 | — | (no texto da linha) |
| 450 | 0,918 | D3, AUC da nota e do centro da câmera (calibração no treino/valid) | 9.2 | `docs/decisoes.md` | 1074 | — | (no texto da linha) |
| 451 | 0,984 | D3, AUC da nota e do centro da câmera (calibração no treino/valid) | 9.2 | `docs/decisoes.md` | 1074 | — | (no texto da linha) |
| 452 | 0,966 | D3, AUC da nota e do centro da câmera (calibração no treino/valid) | 9.2 | `docs/decisoes.md` | 1074 | — | (no texto da linha) |
| 453 | 5 | B1: critério na leitura leave-one-game-out | 9.2 | `docs/decisoes.md` | 1031 | — | (no texto da linha) |
| 454 | 6 | B1: critério na leitura leave-one-game-out | 9.2 | `docs/decisoes.md` | 1031 | — | (no texto da linha) |
| 455 | +0,0179 | B1: critério na leitura leave-one-game-out | 9.2 | `docs/decisoes.md` | 1031 | — | (no texto da linha) |
| 456 | −0,0223 | B1: critério na leitura leave-one-game-out | 9.2 | `docs/decisoes.md` | 1031 | — | (no texto da linha) |
| 457 | 0 | B1: no jogo 2, a nota recusa 0 das 4 aceitas erradas | 9.2 | `docs/decisoes.md` | 990 | — | (no texto da linha) |
| 458 | 4 | B1: no jogo 2, a nota recusa 0 das 4 aceitas erradas | 9.2 | `docs/decisoes.md` | 990 | — | (no texto da linha) |
| 459 | 0,5 | T5: reinicialização de 2 pontos contra o erro no centro da câmera | 9.5 | `docs/decisoes.md` | 1073 | — | (no texto da linha) |
| 460 | 1 | T5: reinicialização de 2 pontos contra o erro no centro da câmera | 9.5 | `docs/decisoes.md` | 1073 | — | (no texto da linha) |
| 461 | 12 | T5: reinicialização de 2 pontos contra o erro no centro da câmera | 9.5 | `docs/decisoes.md` | 1073 | — | (no texto da linha) |
| 462 | +0,037 | ganho da propagação v1 -> v2, jogo 11 | 9.4 | `docs/04-relatorio-v2-numeros.md` | 68 | nº 60 | 0.0365075 |
| 463 | +0,238 | ganho da propagação v1 -> v2, jogo 7 | 9.4 | `docs/04-relatorio-v2-numeros.md` | 69 | nº 61 | 0.237551 |
| 464 | 16 | jogo 3 do dev, base B1 + A': clipes sem âncora | 9.4 | `docs/04-relatorio-v2-numeros.md` | 42 | nº 34 | 16 |
| 465 | 21 | jogo 3 do dev: clipes | 9.4 | `docs/04-relatorio-v2-numeros.md` | 43 | nº 35 | 21 |
| 466 | 735 | revisão de 2026-10-14: chaves da série conferidas na rodada do test | 5 | `docs/decisoes.md` | 929 | — | (no texto da linha) |
| 467 | 49 | revisão de 2026-10-14: chaves do 6c conferidas na rodada do test | 5 | `docs/decisoes.md` | 930 | — | (no texto da linha) |
