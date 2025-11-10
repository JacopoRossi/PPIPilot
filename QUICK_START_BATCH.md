# Quick Start - Batch Mode con File Separati

## 🚀 Avvio Rapido

```bash
streamlit run interface_batch.py
```

## 📁 Struttura Output

```
quantitative_assessment/batch_results/time/results_run_YYYYMMDD_HHMMSS/
├── Activity_1/
│   ├── run_01_iteration_01.csv
│   ├── run_02_iteration_01.csv
│   ├── run_03_iteration_01.csv
│   ├── run_03_iteration_02.csv  ← Dopo correzione errori
│   ├── run_04_iteration_01.csv
│   └── ...
├── Activity_2/
│   ├── run_01_iteration_01.csv
│   └── ...
└── ...
```

## 🎯 Caratteristiche

- ✅ **10 run per attività**
- ✅ **File separato per ogni run**
- ✅ **File separato per ogni iterazione di correzione**
- ✅ **Cartella per attività**
- ✅ **Tracciamento completo**

## 📊 Formato File

Ogni file CSV contiene:
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
PPI 1;Description...;Value 1;;A
PPI 2;Description...;Value 2;;A
...
```

## 🔍 Esempio

### Run senza errori
```
Activity_X/
└── run_01_iteration_01.csv  (16 PPIs)
```

### Run con correzioni
```
Activity_Y/
├── run_03_iteration_01.csv  (12 PPIs, 4 errori)
├── run_03_iteration_02.csv  (15 PPIs, 1 errore)  ← Level 1
└── run_03_iteration_03.csv  (16 PPIs, 0 errori)  ← Level 2
```

## 📈 Analisi Rapida

```python
import glob

# Conta iterazioni per run
activity_folder = "path/to/Activity_Name/"
for run in range(1, 11):
    files = glob.glob(f"{activity_folder}/run_{run:02d}_*.csv")
    print(f"Run {run}: {len(files)} iterazioni")
```

## 📚 Documentazione Completa

- `BATCH_MODE_README.md` - Guida completa
- `SEPARATE_FILES_UPDATE.md` - Dettagli struttura file
- `BATCH_MODE_SUMMARY.md` - Riepilogo funzionalità
