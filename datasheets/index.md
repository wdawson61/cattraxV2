# Datasheets

PDFs live in the subfolders on each machine but are **not committed** (vendor copyright; see
`.gitignore`). This index is the record: add a row when you add a PDF, and note the revision the
design was checked against.

| Subsystem | Part | Document | Local file | Status |
|---|---|---|---|---|
| power | Nordic nPM1300 | Product specification | | **needed** |
| power | Grepow GRP751538 (440 mAh curved) | Cell spec, Rev A | `power/GRP751538-3.85V-440mAh.pdf` | have |
| power | Grepow GRP402425 (225 mAh curved) | Cell spec, Rev A (2019-07-31) | `power/GRP402425-3.8V-225mAh.pdf` | have |
| power | Cell protector IC (TBD) | Datasheet | | part not chosen |
| mcu | Nordic nRF54L10 | nRF54L15/L10/L05 product specification | | **needed** |
| radio | Semtech SX1262 | SX1261/2 datasheet | | **needed** |
| radio | Semtech | 915 MHz reference design | | **needed** |
| radio | pSemi PE4259 (915 MHz SPDT, proposed) | Product specification | `radio/pe4259ds.pdf` | **needed** |
| radio | Skyworks SKY13351-378LF (alternative) | Datasheet | | reference only |
| gnss | u-blox MIA-M10Q | Integration manual | | **needed** |
| gnss | u-blox M10 | SPG 5.10 interface description (UBX-21035062) | `gnss/u-blox-M10-SPG-5.10_InterfaceDescription_UBX-21035062.pdf` | have |
| gnss | u-blox MAX-M10S | Integration manual (UBX-20053088) — reference only, not the V2 module | `gnss/MAX-M10S_IntegrationManual_UBX-20053088.pdf` | have |
| sensors | ST LIS2DW12 | Datasheet | | **needed** |
| sensors | TI TMAG3001 | Datasheet SLYS053C | `sensors/tmag3001.pdf` | have |
| misc | TI TMUX1101 | Datasheet | | **needed** |
| misc | TI TPD1E10B06 | Datasheet | | **needed** |
| dock | WCH CH343 (CH343P) | Datasheet CH343DS1, rev 1E English (rev 1F Chinese is latest) | `dock/CH343DS1.pdf` | **needed** |
| dock | Silicon Labs CP2102N (fallback, QFN28) | Datasheet | | reference only |
| dock | 1.8 V LDO with enable | Datasheet | | part not chosen |
| dock | 5 V current-limit switch / eFuse | Datasheet | | part not chosen |
| dock | Spring pogo pins | Datasheet | | part not chosen |
| mech | K&J Magnetics B842-N52 | Product page / spec | | **needed** |
| mech | Smooth-On Dragon Skin 20 (or 10 NV) | Technical bulletin | | **needed** |
| mech | Mill-Max dock targets | Datasheet (part TBD) | | part not chosen |
