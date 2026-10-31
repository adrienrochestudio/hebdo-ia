# EN lexicon of AI markers

Format read by `scripts/audit.py`: `- term | replacement`. Prefix `re:` = regex. Headings tagged `[rouge]` (red) or `[orange]`.
Source for eras: Wikipedia "Signs of AI writing" (WikiProject AI Cleanup). Literal sense stays fine (an underscore character, a key on a keyboard).

## 2023 to mid-2024 (GPT-4) [rouge]
- delve | look at, examine
- tapestry | mix, or nothing
- testament | proof, or cut
- intricate | complex, detailed
- intricacies | details
- meticulous | careful
- meticulously | carefully
- boasts | has
- bolstered | strengthened
- garner | get, win
- enduring | lasting, or cut
- interplay | relation
- vibrant | lively, or describe
- valuable | useful, or cut
- re:\bunderscor(?:e|es|ed|ing)\b | show, stress
- re:\bkey\b | main, or cut
- re:\bcrucial\b | cut, or "decisive" if true
- re:\bpivotal\b | cut, describe the change
- re:\blandscape\b | field, market
- re:\badditionally\b | also, or cut

## Mid-2024 to mid-2025 (GPT-4o) [rouge]
- re:\balign(?:s|ed)? with\b | match, fit
- re:\bfoster(?:s|ed|ing)?\b | build, help
- re:\benhanc(?:e|es|ed|ing)\b | improve, or say how
- re:\bhighlight(?:s|ed|ing)?\b | show, point out
- re:\bshowcas(?:e|es|ed|ing)\b | show
- re:\bemphasi[sz](?:e|es|ed|ing)\b | stress, say

## Claude-specific [rouge]
- re:\breliabl(?:e|y)\b | say what was tested, or the figure
- re:\bwhy (?:this|it|that) matters\b | cut, give the consequence
- re:\b(?:this|that|it) matters\b | cut
- re:\bgenuinely\b | cut
- re:\bhonestly\b | cut
- re:\bhere's the thing\b | cut
- re:\bthe real (?:question|issue|problem)\b | cut
- re:\bit's worth noting\b | cut

## Openers and closers [rouge]
- it is important to note | cut
- it's important to note | cut
- in conclusion | cut
- in summary | cut
- in today's fast-paced world | cut
- in the ever-evolving | cut
- navigate the complexities | handle
- a rich history | give one fact
- plays a vital role | say what it does
- plays a crucial role | say what it does
- stands as | is
- serves as | is
- marking a pivotal moment | cut
- a broader movement | cut, or name it
- I hope this email finds you well | Hi
- re:\bnot (?:just|only)\b.{0,60}\bbut\b | state the second part directly

## Staging and chatbot residue [rouge]
- at its core | state the specific claim
- what really matters | state the specific claim
- contrary to popular belief | cut
- re:\bthis isn't (?:mainly|just|only) about\b | state the claim directly
- re:\bgreat question\b | cut
- re:\bi hope this helps\b | cut
- re:\blet me know if\b | cut
- re:\bas of my (?:last|latest) (?:update|knowledge)\b | cut, or cite the source
- re:\bdetails are limited\b | state what the source shows
- re:\bthe table below (?:compares|shows|summarizes)\b | describe the subject
- re:\bin this section,? we(?:'ll| will)\b | describe the subject
- re:\blet's dive\b | cut

## Hedging [orange]
- re:\bcould potentially\b | could
- re:\bit appears that\b | state it, or cite the source
- re:\bit could be argued\b | name who argues it, or cut

## Transitions and fillers [orange]
- moreover | cut
- furthermore | cut
- notably | cut
- re:\bseamless(?:ly)?\b | cut
- re:\brobust\b | solid, or cut
- re:\bleverag(?:e|es|ed|ing)\b | use
- re:\bcomprehensive\b | full, or cut
- re:\bholistic\b | cut
- re:\butiliz(?:e|es|ed|ing)\b | use
- re:\bfacilitat(?:e|es|ed|ing)\b | help, allow
- re:\bvarious\b | name them
- re:\bnumerous\b | give the number

## Mistranslations from the Ecoprod lexicon (see traduction.md) [rouge]
- re:\beco-?friendly\b | sustainable, environmentally responsible
- re:\beco-?responsible\b | sustainable, environmentally responsible
- re:\beco-?productions?\b | green production
- re:\beco-?gestures?\b | green practice
- carbon balance | carbon footprint (result), carbon assessment (exercise)
- carbon report | carbon footprint, carbon assessment
- environmental print | environmental footprint
- re:\blabell?(?:ed|i[sz]ed)\b | certified
- electrogenic group | diesel generator
- re:\breferentials?\b | framework, set of criteria, standard
- re:\bcriterium\b | criterion
- re:\bsensiti[sz]ation\b | awareness-raising
- thermic vehicle | internal combustion vehicle
- re:\bpetrol cars?\b | internal combustion vehicles
- sector chain | industry, sector
- re:\bdecarbonation\b | decarbonisation
- natural settings | practical locations

## Translation traps from the Ecoprod lexicon (check the sense) [orange]
- re:\bshooting\b | shoot, filming, on set
- re:\baudiovisual\b | film and TV (audiovisual only in an EU context)
- re:\beventually\b | possibly, if needed (if it means "éventuellement")
- re:\bactually\b | currently (if it means "actuellement")
- re:\bsupply chain\b | industry (if it means "filière")
- re:\bglobal standard\b | benchmark (never "global" for a national label)
