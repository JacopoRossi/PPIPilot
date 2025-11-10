# Riepilogo Completo: Batch Mode PPIPilot

## 🎯 Funzionalità Implementate

### 1. ✅ Esecuzione Batch Automatica
- **10 run per attività** (configurabile)
- **Tutte le attività del log** (o selezione manuale)
- **Correzione errori automatica** (Level 1 e Level 2)
- **Progress tracking** in tempo reale

### 2. ✅ File Separati per Run e Iterazioni
- **Cartella per attività**: Ogni attività ha la sua cartella
- **File per run**: Ogni run ha i suoi file (01-10)
- **File per iterazione**: Ogni correzione crea nuovi file
- **Nomenclatura chiara**: `run_XX_iteration_YY_[tipo].csv`

### 3. ✅ Doppio Salvataggio CSV
- **`_withoutErrors.csv`**: Solo PPI validi
- **`_withErrors.csv`**: Tutti i PPI (inclusi errori)
- **Tracciabilità completa**: Nessuna perdita di informazioni
- **Flessibilità analisi**: Scegli quale file usare

### 4. ✅ Selezione Attività
- **Default**: Analizza tutte le attività
- **Manuale**: Seleziona attività specifiche
- **Test rapidi**: Esegui su poche attività
- **Validazione**: Impedisce esecuzioni vuote

## 📁 Struttura Output Completa

```
quantitative_assessment/batch_results/time/results_run_20241110_140000/
│
├── Declaration_SUBMITTED_by_EMPLOYEE/
│   ├── run_01_iteration_01_withoutErrors.csv    (16 PPI validi)
│   ├── run_01_iteration_01_withErrors.csv       (16 PPI totali)
│   │
│   ├── run_02_iteration_01_withoutErrors.csv    (14 PPI validi)
│   ├── run_02_iteration_01_withErrors.csv       (16 PPI totali)
│   │
│   ├── run_03_iteration_01_withoutErrors.csv    (12 PPI validi, 4 errori)
│   ├── run_03_iteration_01_withErrors.csv       (16 PPI totali)
│   ├── run_03_iteration_02_withoutErrors.csv    (15 PPI validi, 1 errore - dopo Level 1)
│   ├── run_03_iteration_02_withErrors.csv       (16 PPI totali)
│   ├── run_03_iteration_03_withoutErrors.csv    (16 PPI validi - dopo Level 2)
│   ├── run_03_iteration_03_withErrors.csv       (16 PPI totali)
│   │
│   ├── run_04_iteration_01_withoutErrors.csv
│   ├── run_04_iteration_01_withErrors.csv
│   │
│   ├── run_05_iteration_01_withoutErrors.csv
│   ├── run_05_iteration_01_withErrors.csv
│   ├── run_05_iteration_02_withoutErrors.csv
│   ├── run_05_iteration_02_withErrors.csv
│   │
│   ├── run_06_iteration_01_withoutErrors.csv
│   ├── run_06_iteration_01_withErrors.csv
│   │
│   ├── run_07_iteration_01_withoutErrors.csv
│   ├── run_07_iteration_01_withErrors.csv
│   │
│   ├── run_08_iteration_01_withoutErrors.csv
│   ├── run_08_iteration_01_withErrors.csv
│   │
│   ├── run_09_iteration_01_withoutErrors.csv
│   ├── run_09_iteration_01_withErrors.csv
│   │
│   └── run_10_iteration_01_withoutErrors.csv
│       run_10_iteration_01_withErrors.csv
│
├── Declaration_APPROVED_by_ADMINISTRATION/
│   ├── run_01_iteration_01_withoutErrors.csv
│   ├── run_01_iteration_01_withErrors.csv
│   └── ...
│
├── Declaration_FINAL_APPROVED_by_SUPERVISOR/
│   ├── run_01_iteration_01_withoutErrors.csv
│   ├── run_01_iteration_01_withErrors.csv
│   └── ...
│
└── [... altre attività ...]
```

## 🚀 Come Usare

### 1. Avvio
```bash
cd c:\Users\jacop\Desktop\PPIPilot_OTTOBRE\PPIPilot
streamlit run interface_batch.py
```

### 2. Configurazione
1. **OpenAI API Key**: Inserisci la chiave
2. **Upload XES File**: Carica il file evento
3. **Description**: Descrizione del processo
4. **Goal**: Obiettivo organizzativo
5. **Category**: Scegli "time" o "occurrency"
6. **Click**: "✅ Load Configuration"

### 3. Selezione Attività
- **Tutte**: Lascia ☑️ "Analyze all activities"
- **Specifiche**: Deseleziona e scegli dal menu

### 4. Esecuzione
- **Click**: "▶️ Start Batch Execution"
- **Attendi**: Progress bar mostra avanzamento
- **Risultati**: File salvati automaticamente

## 📊 Formato File CSV

### File `_withoutErrors.csv`
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
Minimum time from D to E;Description...;00:00:01;;A
```

### File `_withErrors.csv`
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
Minimum time from D to E;Description...;00:00:01;;A
Average time from X to Y;Description...;ERROR;;A
Maximum time for Z;Description...;ERROR;;A
```

## 📈 Analisi Risultati

### Analisi Base (Solo PPI Validi)
```python
import pandas as pd

# Leggi un run specifico
df = pd.read_csv('Declaration_SUBMITTED_by_EMPLOYEE/run_01_iteration_01_withoutErrors.csv', sep=';')
print(f"PPI validi: {len(df) - 2}")
```

### Analisi Completa (Con Errori)
```python
import pandas as pd

# Confronta versioni
df_valid = pd.read_csv('activity/run_01_iteration_01_withoutErrors.csv', sep=';')
df_all = pd.read_csv('activity/run_01_iteration_01_withErrors.csv', sep=';')

valid_ppis = len(df_valid) - 2
total_ppis = len(df_all) - 2
error_ppis = total_ppis - valid_ppis

print(f"Totale: {total_ppis}")
print(f"Validi: {valid_ppis}")
print(f"Errori: {error_ppis}")
print(f"Success rate: {valid_ppis/total_ppis*100:.1f}%")
```

### Analisi Aggregata (Tutti i Run)
```python
import pandas as pd
import glob

activity_folder = "Declaration_SUBMITTED_by_EMPLOYEE"

summary = []
for run in range(1, 11):
    # Trova tutte le iterazioni per questo run
    files = sorted(glob.glob(f"{activity_folder}/run_{run:02d}_*_withoutErrors.csv"))
    
    if files:
        # Prendi l'ultima iterazione (finale)
        df_final = pd.read_csv(files[-1], sep=';')
        valid_ppis = len(df_final) - 2
        
        summary.append({
            'run': run,
            'iterations': len(files),
            'final_valid_ppis': valid_ppis
        })

summary_df = pd.DataFrame(summary)
print(summary_df)
print(f"\nMedia PPI per run: {summary_df['final_valid_ppis'].mean():.1f}")
print(f"Run con correzioni: {len(summary_df[summary_df['iterations'] > 1])}/10")
```

### Confronto Iterazioni (Efficacia Correzioni)
```python
import pandas as pd

run_num = 3  # Run con correzioni

# Iterazione 1 (iniziale)
df_iter1 = pd.read_csv(f'activity/run_{run_num:02d}_iteration_01_withoutErrors.csv', sep=';')
ppis_iter1 = len(df_iter1) - 2

# Iterazione finale
import glob
files = sorted(glob.glob(f'activity/run_{run_num:02d}_*_withoutErrors.csv'))
df_final = pd.read_csv(files[-1], sep=';')
ppis_final = len(df_final) - 2

print(f"Run {run_num}:")
print(f"  Iterazione 1: {ppis_iter1} PPI")
print(f"  Iterazione finale: {ppis_final} PPI")
print(f"  Miglioramento: +{ppis_final - ppis_iter1} PPI corretti")
print(f"  Totale iterazioni: {len(files)}")
```

## 🎯 Casi d'Uso

### Caso 1: Test Rapido
**Obiettivo**: Testare il sistema su poche attività
```
1. Deseleziona "Analyze all activities"
2. Seleziona 2-3 attività
3. Esegui batch
4. Verifica risultati in ~15 minuti
```

### Caso 2: Analisi Completa
**Obiettivo**: Analizzare tutto il log
```
1. Lascia "Analyze all activities" attivo
2. Esegui batch
3. Attendi completamento (~2-3 ore per 25 attività)
4. Analizza tutti i risultati
```

### Caso 3: Focus su Attività Critiche
**Obiettivo**: Analizzare solo processi importanti
```
1. Deseleziona "Analyze all activities"
2. Seleziona attività critiche (es. "Payment Handled", "Declaration APPROVED")
3. Esegui batch
4. Analisi mirata su processi chiave
```

### Caso 4: Valutazione Affidabilità
**Obiettivo**: Capire quali PPI sono più affidabili
```
1. Esegui batch completo
2. Per ogni attività, confronta _withErrors e _withoutErrors
3. Calcola success rate per ogni PPI
4. Identifica PPI più stabili
```

## 📊 Metriche Calcolabili

### Per Run
- **PPI validi generati**
- **Numero iterazioni necessarie**
- **Errori risolti vs persistenti**
- **Success rate**

### Per Attività
- **Media PPI per run**
- **Variabilità tra run**
- **Run che richiedono correzioni**
- **PPI più problematici**

### Per Log Completo
- **Attività più affidabili**
- **Attività più problematiche**
- **Success rate globale**
- **Efficacia sistema correzione**

## 🔧 Configurazione

### Parametri Modificabili (in `interface_batch.py`)
```python
NUM_RUNS_PER_ACTIVITY = 10        # Numero run per attività
MAX_LEVEL1_ITERATIONS = 2         # Iterazioni correzione Level 1
MAX_LEVEL2_ITERATIONS = 2         # Iterazioni correzione Level 2
```

### Output Folder
```python
output_folder = "quantitative_assessment/batch_results"  # Modificabile nell'UI
```

## 📚 Documentazione

1. **BATCH_MODE_README.md** - Guida completa batch mode
2. **SEPARATE_FILES_UPDATE.md** - Struttura file separati
3. **DUAL_CSV_FILES_FEATURE.md** - Doppio salvataggio CSV
4. **ACTIVITY_SELECTION_FEATURE.md** - Selezione attività
5. **QUICK_START_BATCH.md** - Guida rapida
6. **BATCH_MODE_COMPLETE_SUMMARY.md** - Questo documento

## ⚡ Performance

### Tempo Stimato (25 attività, 10 run)
- **Totale esecuzioni**: 250 (25 × 10)
- **Tempo per run**: ~30-60 secondi
- **Tempo totale**: ~2-3 ore
- **Con correzioni**: +20-30% tempo

### Ottimizzazione
- **Test su poche attività** prima dell'analisi completa
- **Esegui durante la notte** per analisi complete
- **Monitora il terminale** per identificare problemi

## 🎉 Vantaggi Finali

### 1. **Tracciabilità Totale**
- Ogni run documentato
- Ogni iterazione salvata
- Nessuna perdita di dati

### 2. **Flessibilità Massima**
- Scegli quali attività analizzare
- Scegli quale file CSV usare
- Configurazione personalizzabile

### 3. **Analisi Approfondite**
- Confronto tra run
- Confronto tra iterazioni
- Identificazione pattern

### 4. **Debug Facilitato**
- File con errori disponibili
- Traccia completa correzioni
- Identificazione PPI problematici

### 5. **Automazione Completa**
- Nessun intervento manuale
- Correzioni automatiche
- Progress tracking

## 🚀 Conclusione

Il Batch Mode di PPIPilot offre:
- ✅ **Esecuzione automatica** di 10 run per attività
- ✅ **File separati** per run e iterazioni
- ✅ **Doppio salvataggio** (con/senza errori)
- ✅ **Selezione flessibile** delle attività
- ✅ **Tracciabilità completa** di tutti i risultati
- ✅ **Analisi approfondite** con metriche dettagliate

**Sistema completo per valutazione quantitativa di PPIPilot!** 🎯
