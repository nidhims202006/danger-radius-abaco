# Reference spot-check (item 5), 2026-10-01

Scope: the 20 references in the current list that predate v23 (the 14 you named plus Ajeil 2020, Montiel 2015, Phillips & Likhachev 2011, Xiong 2021, Yang L. 2022, Li T. 2026), plus the two open flags from CHANGES_v24_to_v25 (Li Y. 2020 initials, Ntakolia 2023 "Part B").

Method: web search against publisher or index records (ScienceDirect, ACM DL, MDPI, AIMS Press, SAGE, PubMed, IEEE Xplore, CMU RI, Frontiers/PMC, DOAJ, EconPapers, Semantic Scholar) and citing papers. I did not open DOI resolvers or the reference manager, so "record" below means an index/publisher page, not a DOI redirect.

## Result: no reference looks wrong. Two need a decision, three are optional tidy-ups.

### Needs a decision
| Reference | Issue |
|---|---|
| Joshy & Supriya (2016) | Reference says pp. 1-6. The Amrita record gives ICICT 2016, Vol. 3, pp. 163-168 (DOI 10.1109/INVENTIVE.2016.7823281). Both can be right (per-paper vs proceedings pagination), but I could not tell which one the IEEE Xplore page shows. Check Xplore, or drop the page range and add the DOI. |
| Abdulghani & Abdulghani (2024) | Title, authors, 3(4), 214-224 and DOI 10.56578/ataiml030403 (Acadlore) all agree, but the journal name varies. Citing papers use "Acadlore Transactions on Machine Learning"; the DOI code "ataiml" suggests the full title is "Acadlore Transactions on AI and Machine Learning". I did not see the publisher page, so check the journal title there. |

### Optional tidy-ups
- Dorigo et al. (1996): no DOI in the reference. IEEE Xplore record gives 10.1109/3477.484436 (vol. 26, no. 1, pp. 29-41, matches).
- Jasna et al. (2016): no pages in the reference. Only a citing paper was found (ICCIC, IEEE, pp. 1-5). Title, authors, venue match. No DOI found.
- Shi et al. (2023): authors, vol. 20 no. 9 and DOI confirmed (DOAJ); pages 15568-15602 not seen on any record.

### The two open flags
| Flag | Result |
|---|---|
| Li Y. 2020 (PQ-RRT*) initials | Semantic Scholar record lists Yanjie Li, Wu Wei, Yong Gao, Dongliang Wang, Zhun Fan, so initials Y., W., Y., D., Z. match the reference. Volume 152, article 113425 also confirmed (same record; about eight citing papers agree). Source is an index plus citing papers, not the Elsevier page. |
| Ntakolia 2023 "Part B" | ScienceDirect page reads "Volume 213, Part B, 1 March 2023, 119049". Confirmed. |

### Confirmed (title, authors, venue, volume/pages as listed)
| Reference | Source seen |
|---|---|
| Wu 2023 (ESWA 215, 119410) | ACM DL and ScienceDirect (title, DOI); authors and vol./article number from Springer and ScienceDirect citing reference lists |
| Gong 2022 (MBE 19(12), 12405-12426) | AIMS Press |
| Deng 2021 (ESWA 183, 115445) | ScienceDirect (author Gui confirmed) |
| Guo 2025 (ESWA 266, 126123) | ACM DL (title, vol. 266, DOI); authors from several citing papers |
| Dian 2022 (ESWA 208, 118256) | ScienceDirect |
| Si & Bao 2024 (MBE 21(2), 2568-2586) | AIMS Press, PubMed |
| Liu 2023 (ESWA 227, 120254) | ScienceDirect |
| Khatib 1986 (IJRR 5(1), 90-98) | CiNii / SAGE DOI record |
| Fiorini & Shiller 1998 (IJRR 17(7), 760-772) | SAGE, TRID |
| Ajeil 2020 (Sensors 20(7), 1880) | MDPI |
| Montiel 2015 (ESWA 42(12), 5177-5191) | Elsevier-hosted record (title, authors, pages) and DOI listing; issue number not seen directly |
| Phillips & Likhachev 2011 (ICRA, 5628-5635) | CMU Robotics Institute |
| Xiong 2021 (Front. Neurorobot. 15, 642733) | Frontiers / PMC |
| Yang L. 2022 (Machines 10(1), 50) | MDPI |
| Li T. 2026 (PLOS ONE, e0340336) | EconPapers / PMC (authors Tengyan Li, Shuaishuai Cui, Xiaming Cui, Yaqi Wang, Guozhu Song; published 2026-07-27) |

Not re-checked this round: the 9 references added in v23 (already verified in CHANGES_v24_to_v25).
