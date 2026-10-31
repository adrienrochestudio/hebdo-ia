# Lexique pt-BR des marqueurs IA

Format lu par `scripts/audit.py` : `- terme | remplacement` (barre entourée d'espaces). Préfixe `re:` = expression régulière. Les titres `[rouge]` ou `[orange]` donnent la gravité.
Un mot seul ne prouve rien : c'est la densité qui trahit. Les sens propres restent permis (mergulhar no mar, a chave da porta, navegar na internet, ensino fundamental, jornada de trabalho).
Cible : la prose d'un bon journaliste brésilien (Folha, Piauí, Nexo). Phrase directe, sujet et verbe tôt, fait daté et sourcé.

## Ouvertures et clôtures pompeuses [rouge]
- re:\bé (?:importante|fundamental|essencial|crucial|interessante) (?:notar|destacar|ressaltar|lembrar|observar|sublinhar|mencionar)\b | cortar, dar o fato
- re:\bvale (?:a pena )?(?:ressaltar|destacar|lembrar|notar|mencionar|sublinhar)\b | cortar
- re:\bcabe (?:ressaltar|destacar|lembrar|notar|mencionar|sublinhar)\b | cortar
- re:\bé (?:crucial|essencial|fundamental|imprescindível) que\b | é preciso que
- re:\bdestaca-se\b | cortar, dizer o fato
- re:\bdestacam-se\b | cortar, dizer o fato
- em suma | cortar
- em resumo | cortar
- em síntese | cortar
- em conclusão | cortar
- por fim, mas não menos importante | por fim
- re:\b(?:em|num) mundo (?:onde|em que|cada vez mais)\b | cortar
- nos dias de hoje | hoje, ou a data
- re:\bna era d[aoe]\b | cortar
- re:\bcomo (?:vimos|pudemos ver)\b | cortar
- re:\bnão hesite em\b | dizer a ação
- re:\bespero que (?:esta mensagem|este e-mail) (?:o|a|te) encontre\b | Olá
- re:\bpor que (?:isso|isto) importa\b | dizer a consequência concreta

## Vocabulaire surutilisé [rouge]
- re:\bmergulh(?:ar|a|am|amos|ando|ou|o|e)\b | tratar de, examinar, ou cortar
- crucial | decisivo, ou nada
- cruciais | decisivos, ou nada
- re:(?<!ensino )(?<!direitos )(?<!direito )\bfundamenta(?:l|is)\b | necessário, básico, ou nada
- re:\bessencia(?:l|is)\b | necessário, ou nada
- re:\bimprescindíve(?:l|is)\b | necessário, ou nada
- re:\b(?:ponto|peça|fator|papel|questão|elemento|momento|ator|tema|figura|palavra)s?-chaves?\b | principal, ou nada
- re:\b(?:a|uma) chave (?:para|do|da|de)\b | o que explica, ou dizer o fato
- re:\b(?:neste|nesse|diante d[eo]ste|diante desse|no atual) cenário\b | agora, hoje, ou cortar
- re:\bcenário (?:atual|econômico|político|global|internacional|nacional|digital|audiovisual|cultural|geopolítico|mundial)\b | situação, setor, ou dizer qual
- re:\bpanorama\b | situação, ou cortar
- re:\brobust[oa]s?\b | sólido, ou o número que prova
- re:\bpotencializ(?:ar|a|am|ando|ou)\b | aumentar, ampliar
- re:\balavanc(?:ar|a|am|ando|ou)\b | aumentar, usar
- re:\bfoment(?:ar|a|am|ando|ou)\b | estimular, apoiar
- re:\bmeticulos[oa]s?\b | cuidadoso, ou descrever o cuidado
- re:\bmeticulosamente\b | com cuidado
- re:\bvibrantes?\b | animado, ou descrever
- re:\btapeçaria\b | mistura, ou nada
- re:\bjornadas?\b(?! de trabalho) | percurso, trajetória, ou cortar
- re:\bnaveg(?:ar|a|am|ando) (?:por|pel[oa]s?|n[oa]s?|em) (?:\w+ )?(?:complexidades?|desafios?|incertezas?|mudanças?|cenários?|águas)\b | lidar com, enfrentar
- re:\b(?:é )?(?:um )?testemunho d[eoa]s?\b | mostra, prova de
- re:\bdesempenh(?:a|am|ar|ou|aram|ando) (?:um )?papel\b | dizer o que faz
- re:\bexerc(?:e|em|er|eu) (?:um )?papel\b | dizer o que faz
- re:\becossistemas?\b | setor, rede
- re:\bsinergias?\b | nada
- re:\bholístic[oa]s?\b | global, ou nada
- re:\bpilar(?:es)?\b | base, ou nada
- re:\bdivisor de águas\b | dizer o que muda
- re:\bmarco (?:histórico|importante|fundamental)\b | dizer o que muda
- re:\bpaisagem (?:audiovisual|digital|atual|midiática|econômica|cultural|política)\b | setor, situação
- re:\bsublinh(?:a|am|ar|ando|ou)\b | dizer, mostrar

## Formules spécifiques aux modèles [rouge]
- honestamente | cortar
- sinceramente | cortar
- re:\ba (?:verdadeira|grande) questão\b | cortar
- re:\bo que realmente importa\b | dizer a coisa precisa
- re:\ba resposta é simples\b | cortar
- re:\bao contrário do que se (?:pode|poderia) (?:pensar|imaginar)\b | cortar
- re:\bespero que (?:isso|isto) (?:ajude|tenha ajudado)\b | cortar
- re:\b(?:nesta|nessa) seção,? (?:vamos|veremos)\b | falar do assunto
- re:\ba tabela abaixo (?:compara|mostra|resume)\b | falar do assunto
- re:\bcom base nas informações disponíveis\b | dizer o que a fonte mostra

## Transitions mécaniques [orange]
- além disso | cortar, ou "e", "também"
- ademais | cortar
- outrossim | cortar
- nesse sentido | cortar
- neste sentido | cortar
- diante disso | cortar, ou "por isso"
- dessa forma | assim, ou cortar
- desse modo | assim, ou cortar
- no entanto | mas
- contudo | mas
- todavia | mas
- re:\bsem dúvida(?:s)?\b | cortar
- re:\binegave(?:l|lmente)\b | cortar

## Verbes et tournures de bureau [orange]
- re:\bdestac(?:ar|a|am|ando|ou|aram)\b(?!-se) | dizer, afirmar, mostrar
- re:\bressalt(?:ar|a|am|ando|ou|aram)\b | dizer, afirmar
- re:\bimpulsion(?:ar|a|am|ando|ou)\b | aumentar, puxar
- re:\bpromov(?:er|e|em|endo|eu)\b | fazer, organizar, apoiar (dizer o quê)
- re:\bu(?:m|ma) verdadeir[oa]\b | cortar o adjetivo
- re:\bno âmbito d[eoa]s?\b | em, dentro de
- re:\bno contexto d[eoa]s?\b | em, durante
- re:\bpermit(?:e|em)\b | verbo direto
- re:\bse (?:configura|posiciona|consolida|apresenta|firma)m? como\b | é
- re:\bserv(?:e|em) (?:como|de)\b | é
- re:\bconstitu(?:i|em)\b | é
- re:\botimiz(?:ar|a|am|ando)\b | melhorar, reduzir (dizer o quê)
- re:\bcontribu(?:ir|i|em) para\b | dizer o efeito
- re:\bdivers[oa]s\b | nomear os itens
- re:\binúmer[oa]s\b | dar o número
- re:\bsignificativ(?:o|a|os|as|amente)\b | forte, claro, ou o número
- re:\bvalor agregado\b | dizer o ganho
- re:\bcontinua(?:m)? (?:a evoluir|evoluindo)\b | cortar
- re:\btransformador(?:a|es|as)?\b | dizer o que muda
- re:\brevolucion(?:ar|a|ou|ário|ária)\b | mudar, ou dizer o que muda

## Calques du français [orange]
- re:\b(?:a|ao) nível d[eoa]s?\b | em, no, na
- re:\bde fato\b | cortar (é quase sempre um "en effet" traduzido)
- re:\bo fato de que\b | que, ou reescrever
- re:\bcom efeito\b | cortar
- re:\bem termos de\b | em, quanto a
- re:\bem matéria de\b | em, sobre
- re:\bno seio d[eoa]s?\b | em, dentro de
- re:\bo conjunto d[oa]s\b | todos os, todas as
- re:\b(?:colocar|pôr|coloca|põe|colocou|pôs) em (?:prática|obra|lugar)\b | criar, adotar, implantar
- re:\bfaz(?:er|endo)? face a\b | enfrentar
- re:\bfaz(?:er|endo)? prova de\b | mostrar
- re:\bt(?:er|eve|em|êm) lugar\b | acontecer, ocorrer
- re:(?<!quando )(?<!que )(?<!se )\bse trata de\b | trata de (sujeito explícito), ou "trata-se de" (impessoal)
- re:\bem (?:França|Itália|Alemanha|Espanha|Inglaterra|Bélgica|Suíça|Holanda|China|Índia|Argentina|Europa)\b | na França, na Itália... (artigo no Brasil)
- re:\bde (?:França|Itália|Alemanha|Espanha|Inglaterra|Bélgica|Suíça|China|Índia|Argentina|Europa)\b | da França, da Itália...
- re:\brealizador(?:a|es|as)?\b | diretor, cineasta
- re:\brodagem\b | filmagem

## Português europeu ou grafia anterior ao Acordo [rouge]
- re:\bfact(?:o|os)\b | fato
- re:\becrã\b | tela
- re:\btelemóve(?:l|is)\b | celular
- re:\butilizador(?:es)?\b | usuário
- re:\bficheiros?\b | arquivo
- re:\bequipas?\b | equipe
- re:\bbiliões\b | bilhões
- re:\bbilião\b | bilhão
- re:\bmil milhões\b | bilhão
- re:\b(?:está|estão|estou|estava|estavam|estamos) a \w{2,}(?:ar|er|ir)\b | gerúndio: está fazendo
- re:\b(?:idéias?|assembléias?|européi[ao]s?|platéias?|estréias?|jibóias?|heróic[oa]s?|paranóic[oa]s?|vôos?|enjôos?|crêem|lêem|vêem|dêem)\b | grafia do Acordo de 1990 (ideia, voo, leem)
- re:\b\w*[qg]ü\w* | sem trema (consequência, frequente, linguística)

## Gallicismes de traduction (repérage en relecture)
L'audit en détecte une partie (section ci-dessus et contrôles de `audit.py`). Le reste se lit phrase par phrase.
- « É que » en cascade : le « c'est... que » français recopié. « É em Paris que o acordo foi assinado » devient « O acordo foi assinado em Paris ». Deux occurrences dans un texte court suffisent à signer la traduction.
- « De fato » partout : traduit « en effet » ou « de fait ». Le supprimer presque toujours.
- « O fato de que » : traduit « le fait que ». Réécrire avec « que » ou un verbe.
- Articles calqués : le pt-BR met l'article devant la plupart des pays (na França, da Alemanha) et devant le possessif seulement si le rythme le demande (seu livro, o seu livro). « Em França » est portugais d'Europe.
- Prépositions calquées : « ao nível de » (au niveau de), « em matéria de », « no seio de », « fazer face a » (enfrentar).
- Passif excessif : le français administratif passe au passif, le journalisme brésilien écrit à l'actif. « Foi decidido pelo governo » devient « O governo decidiu ».
- « Se trata de » mal placé : la tournure est impersonnelle. « O filme se trata de » est fautif ; écrire « O filme trata de » ou « Trata-se de um filme ».
- Ordre des mots calqué : adjectif avant le nom par imitation (« uma importante decisão »), compléments empilés avant le verbe, incises entre virgules en début de phrase. En pt-BR, sujet, verbe et complément viennent tôt ; l'incise passe en fin de phrase ou dans une autre phrase.
- Vocabulaire de cinéma : réalisateur se dit « diretor » ou « cineasta », tournage se dit « filmagem » ; « realizador » et « rodagem » sonnent portugais d'Europe.

## Marques du pt-BR à respecter
- « Você » pour s'adresser à la lectrice, jamais « tu » conjugué à la deuxième personne ni « vós ».
- Orthographe de l'Accord de 1990 : ideia, voo, leem, heroico, linguística, frequente (sans tréma).
- Variante brésilienne : fato (pas facto), tela, celular, usuário, arquivo, equipe ; gérondif « está fazendo » (pas « está a fazer »).
- Nombres : virgule décimale (3,5), point pour les milliers (12.500), « 15% » collé.
- Monnaies : « R$ 1,5 bilhão », « US$ 300 milhões », « 2 bilhões de euros ». Espace après R$ et US$.
- Milhão, bilhão (10^9), trilhão (10^12). Singulier jusqu'à 1,99 : « 1,5 bilhão », pluriel dès 2 : « 2 bilhões ». Jamais « mil milhões » ni « bilião ».
- Dates : « 26 de outubro de 2026 », « na segunda-feira (26) » à la manière de la Folha. Jours et mois en minuscule.
- Guillemets “ ” (aspas curvas) ; ‘ ’ pour une citation dans une citation. Pas de « » français.
- Pas de tiret cadratin : la presse brésilienne en use beaucoup, mais la règle du skill est absolue. Virgule, deux-points, parenthèses ou point à la place.
