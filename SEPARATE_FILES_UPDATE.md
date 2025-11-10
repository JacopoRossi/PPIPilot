# Aggiornamento: File Separati per Run e Iterazioni

## 🎯 Obiettivo
Modificare `interface_batch.py` per creare **file CSV separati** per:
1. Ogni run (1-10)
2. Ogni iterazione di correzione errori

## ✅ Modifiche Implementate

### 1. Nuova Struttura Cartelle

**Prima**: Un singolo file per attività
```
quantitative_assessment/batch_results/time/results_run_20241110_121132/
├── Declaration_SUBMITTED_by_EMPLOYEE.csv
├── Declaration_APPROVED_by_ADMINISTRATION.csv
└── ...
```

**Dopo**: Cartella per attività con file per run/iterazione
```
quantitative_assessment/batch_results/time/results_run_20241110_121132/
├── Declaration_SUBMITTED_by_EMPLOYEE/
│   ├── run_01_iteration_01.csv
│   ├── run_02_iteration_01.csv
│   ├── run_03_iteration_01.csv
│   ├── run_03_iteration_02.csv  (correzione errori)
│   ├── run_04_iteration_01.csv
│   ├── run_05_iteration_01.csv
│   ├── run_05_iteration_02.csv
│   ├── run_05_iteration_03.csv  (correzione Level 2)
│   ├── run_06_iteration_01.csv
│   ├── run_07_iteration_01.csv
│   ├── run_08_iteration_01.csv
│   ├── run_09_iteration_01.csv
│   └── run_10_iteration_01.csv
├── Declaration_APPROVED_by_ADMINISTRATION/
│   ├── run_01_iteration_01.csv
│   ├── run_02_iteration_01.csv
│   └── ...
└── ...
```

### 2. Nomenclatura File

**Formato**: `run_{XX}_iteration_{YY}.csv`
- `XX`: Numero run (01-10)
- `YY`: Numero iterazione (01-99)

**Esempi**:
- `run_01_iteration_01.csv` - Primo run, prima esecuzione
- `run_03_iteration_02.csv` - Terzo run, dopo una correzione
- `run_05_iteration_03.csv` - Quinto run, dopo due correzioni

### 3. Funzione `save_results_to_csv()` Aggiornata

```python
def save_results_to_csv(df, activity_name, run_number, category, output_folder, 
                        num_errors=0, iteration=1):
    # Crea cartella per attività
    clean_activity = activity_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    activity_folder = os.path.join(output_folder, clean_activity)
    os.makedirs(activity_folder, exist_ok=True)
    
    # Nome file con run e iterazione
    filename = f"run_{run_number:02d}_iteration_{iteration:02d}.csv"
    filepath = os.path.join(activity_folder, filename)
    
    # Ogni file ha il proprio header
    rows_to_write = []
    rows_to_write.append("Name;Metric;Value;Agrupation;Colonna77")
    rows_to_write.append(";ERROR: computing metric {};;;")
    
    # ... salva dati ...
```

### 4. Nuova Funzione `execute_and_save_iterations()`

Wrapper che:
1. Esegue la prima iterazione
2. Salva il risultato iniziale
3. Se ci sono errori, esegue correzioni
4. Salva ogni iterazione di correzione

```python
def execute_and_save_iterations(xes_file, file_path, ppis, activities, attributes, client,
                                activity_name, run_num, output_folder,
                                max_level1_iterations=2, max_level2_iterations=2):
    # Esecuzione iniziale
    batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_time(...)
    
    # Salva iterazione 1
    csv_path = save_results_to_csv(df_sin_error, activity_name, run_num, ppis, 
                                    output_folder, num_errors, iteration=1)
    
    # Se ci sono errori, esegue correzioni
    if num_errors > 0:
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, total_iterations = \
            auto_correct_errors_with_retry(...)
        
        # Salva risultato finale dopo correzioni
        csv_path = save_results_to_csv(df_sin_error, activity_name, run_num, ppis,
                                        output_folder, num_errors, iteration=total_iterations)
    
    return batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, total_iterations, all_saved_files
```

## 📊 Esempio Pratico

### Scenario: Activity con 3 Run

#### Run 1: Successo al primo tentativo
```
Declaration_SUBMITTED_by_EMPLOYEE/
└── run_01_iteration_01.csv  (16 PPIs, 0 errori)
```

#### Run 2: Errori corretti in Level 1
```
Declaration_SUBMITTED_by_EMPLOYEE/
├── run_01_iteration_01.csv
├── run_02_iteration_01.csv  (12 PPIs, 4 errori)
└── run_02_iteration_02.csv  (15 PPIs, 1 errore) ← Dopo correzione Level 1
```

#### Run 3: Errori corretti in Level 2
```
Declaration_SUBMITTED_by_EMPLOYEE/
├── run_01_iteration_01.csv
├── run_02_iteration_01.csv
├── run_02_iteration_02.csv
├── run_03_iteration_01.csv  (10 PPIs, 6 errori)
├── run_03_iteration_02.csv  (13 PPIs, 3 errori) ← Dopo correzione Level 1
└── run_03_iteration_03.csv  (14 PPIs, 2 errori) ← Dopo correzione Level 2
```

## 📝 Contenuto File CSV

### Esempio: `run_01_iteration_01.csv`
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
Minimum time from D to E;Description...;00:00:01;;A
```

### Esempio: `run_03_iteration_01.csv` (con errori)
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
```

### Esempio: `run_03_iteration_02.csv` (dopo correzione)
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
Minimum time from D to E;Description...;00:00:01;;A  ← PPI corretto aggiunto
```

## 🎯 Vantaggi

### 1. **Tracciabilità Completa**
- Ogni tentativo è documentato
- Visibilità del processo di correzione
- Facile confronto tra iterazioni

### 2. **Analisi Dettagliata**
- Confronto pre/post correzione
- Identificazione PPI problematici
- Valutazione efficacia correzioni

### 3. **Debugging Facilitato**
- Ispezione di ogni fase
- Identificazione quando gli errori vengono corretti
- Comprensione del processo di correzione

### 4. **Flessibilità**
- Ogni file è indipendente
- Facile selezione di specifici run/iterazioni
- Possibilità di analisi granulare

## 📈 Metriche Calcolabili

### Per Run
- **Numero iterazioni necessarie**: Quante correzioni servono
- **Tasso di miglioramento**: PPI aggiunti per iterazione
- **Errori persistenti**: Errori che non vengono corretti

### Per Attività
- **Media iterazioni per run**: Complessità media
- **Success rate per iterazione**: Efficacia correzioni
- **Run più problematici**: Identificazione outlier

### Per Log Completo
- **Distribuzione iterazioni**: Quanti run richiedono correzioni
- **Attività più complesse**: Più iterazioni necessarie
- **Efficacia sistema correzione**: % errori risolti

## 🔍 Analisi Esempio

### Struttura Generata
```
Declaration_SUBMITTED_by_EMPLOYEE/
├── run_01_iteration_01.csv  (16 PPIs)
├── run_02_iteration_01.csv  (14 PPIs)
├── run_03_iteration_01.csv  (12 PPIs, 4 errori)
├── run_03_iteration_02.csv  (15 PPIs, 1 errore)
├── run_04_iteration_01.csv  (16 PPIs)
├── run_05_iteration_01.csv  (10 PPIs, 6 errori)
├── run_05_iteration_02.csv  (13 PPIs, 3 errori)
├── run_05_iteration_03.csv  (14 PPIs, 2 errori)
├── run_06_iteration_01.csv  (16 PPIs)
├── run_07_iteration_01.csv  (15 PPIs)
├── run_08_iteration_01.csv  (16 PPIs)
├── run_09_iteration_01.csv  (16 PPIs)
└── run_10_iteration_01.csv  (16 PPIs)
```

### Analisi
- **Run con 1 iterazione**: 8/10 (80%)
- **Run con 2 iterazioni**: 1/10 (10%)
- **Run con 3+ iterazioni**: 1/10 (10%)
- **Media PPI finali**: 15.1
- **Correzioni efficaci**: Run 3 e 5 migliorati

## 🔄 Workflow di Analisi

### 1. Identificare Run Problematici
```python
import os
import glob

activity_folder = "quantitative_assessment/batch_results/time/results_run_20241110_121132/Declaration_SUBMITTED_by_EMPLOYEE/"

# Conta iterazioni per run
for run_num in range(1, 11):
    files = glob.glob(f"{activity_folder}/run_{run_num:02d}_*.csv")
    print(f"Run {run_num}: {len(files)} iterazioni")
```

### 2. Confrontare Iterazioni
```python
import pandas as pd

# Leggi prima e ultima iterazione di un run
run3_iter1 = pd.read_csv(f"{activity_folder}/run_03_iteration_01.csv", sep=';')
run3_iter2 = pd.read_csv(f"{activity_folder}/run_03_iteration_02.csv", sep=';')

print(f"Iterazione 1: {len(run3_iter1)} PPIs")
print(f"Iterazione 2: {len(run3_iter2)} PPIs")
print(f"Miglioramento: +{len(run3_iter2) - len(run3_iter1)} PPIs")
```

### 3. Analisi Aggregata
```python
# Analizza tutti i run di un'attività
results = []
for run_num in range(1, 11):
    files = sorted(glob.glob(f"{activity_folder}/run_{run_num:02d}_*.csv"))
    
    # Prima iterazione
    df_first = pd.read_csv(files[0], sep=';')
    ppis_first = len(df_first) - 2  # Escludi header e error line
    
    # Ultima iterazione
    df_last = pd.read_csv(files[-1], sep=';')
    ppis_last = len(df_last) - 2
    
    results.append({
        'run': run_num,
        'iterations': len(files),
        'initial_ppis': ppis_first,
        'final_ppis': ppis_last,
        'improvement': ppis_last - ppis_first
    })

results_df = pd.DataFrame(results)
print(results_df)
```

## 📚 File Modificati

1. ✅ `interface_batch.py` - Nuova struttura file e cartelle
2. ✅ `SEPARATE_FILES_UPDATE.md` - Questa documentazione

## 🎉 Conclusione

Ora ogni run e ogni iterazione di correzione ha il **proprio file CSV indipendente**, permettendo:

- ✅ **Tracciabilità completa** del processo
- ✅ **Analisi granulare** di ogni fase
- ✅ **Confronto** tra iterazioni
- ✅ **Debugging** facilitato
- ✅ **Flessibilità** nell'analisi

**Struttura perfetta per analisi approfondite!** 🚀
