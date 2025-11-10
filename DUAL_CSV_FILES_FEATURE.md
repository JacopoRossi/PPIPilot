# Funzionalità: Doppio Salvataggio CSV

## 🎯 Obiettivo
Salvare **due versioni** del CSV per ogni iterazione:
1. **`_withoutErrors.csv`** - Solo PPI validi (senza errori)
2. **`_withErrors.csv`** - Tutti i PPI, inclusi quelli con errori

## ✅ Implementazione

### Nuova Struttura File

**Prima**: Un file per iterazione
```
Declaration_SUBMITTED_by_EMPLOYEE/
├── run_01_iteration_01.csv
├── run_02_iteration_01.csv
└── run_03_iteration_01.csv
```

**Dopo**: Due file per iterazione
```
Declaration_SUBMITTED_by_EMPLOYEE/
├── run_01_iteration_01_withoutErrors.csv
├── run_01_iteration_01_withErrors.csv
├── run_02_iteration_01_withoutErrors.csv
├── run_02_iteration_01_withErrors.csv
├── run_03_iteration_01_withoutErrors.csv
├── run_03_iteration_01_withErrors.csv
├── run_03_iteration_02_withoutErrors.csv
└── run_03_iteration_02_withErrors.csv
```

## 📊 Differenza tra i File

### File `_withoutErrors.csv`
**Contenuto**: Solo PPI che sono stati eseguiti **con successo**
**Uso**: Analisi dei risultati validi, metriche affidabili

**Esempio**:
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
Minimum time from D to E;Description...;00:00:01;;A
```
**Risultato**: 3 PPI validi

### File `_withErrors.csv`
**Contenuto**: **Tutti** i PPI generati, inclusi quelli che hanno dato errore
**Uso**: Debug, analisi completa, identificazione problemi

**Esempio**:
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from A to B;Description...;2 days, 14:16:11;;A
Total time for C;Description...;76387 days, 9:04:32;;A
Minimum time from D to E;Description...;00:00:01;;A
Average time from X to Y;Description...;ERROR;;A
Maximum time for Z;Description...;ERROR;;A
```
**Risultato**: 5 PPI totali (3 validi + 2 con errori)

## 🔍 Casi d'Uso

### Caso 1: Analisi Risultati Validi
**Obiettivo**: Calcolare metriche sui PPI che funzionano
**File da usare**: `_withoutErrors.csv`
**Motivo**: Contiene solo dati affidabili

```python
import pandas as pd

# Leggi solo i PPI validi
df = pd.read_csv('run_01_iteration_01_withoutErrors.csv', sep=';')
print(f"PPI validi: {len(df) - 2}")  # -2 per header e error line
```

### Caso 2: Debug e Identificazione Problemi
**Obiettivo**: Capire quali PPI danno errore
**File da usare**: `_withErrors.csv`
**Motivo**: Mostra anche i PPI problematici

```python
import pandas as pd

# Leggi tutti i PPI
df_all = pd.read_csv('run_01_iteration_01_withErrors.csv', sep=';')
df_valid = pd.read_csv('run_01_iteration_01_withoutErrors.csv', sep=';')

total_ppis = len(df_all) - 2
valid_ppis = len(df_valid) - 2
error_ppis = total_ppis - valid_ppis

print(f"Totale PPI: {total_ppis}")
print(f"PPI validi: {valid_ppis}")
print(f"PPI con errori: {error_ppis}")
print(f"Success rate: {valid_ppis/total_ppis*100:.1f}%")
```

### Caso 3: Confronto Pre/Post Correzione
**Obiettivo**: Vedere come le correzioni migliorano i risultati
**File da usare**: Entrambi, per diverse iterazioni

```python
# Iterazione 1 (prima correzione)
df_iter1_errors = pd.read_csv('run_03_iteration_01_withErrors.csv', sep=';')
df_iter1_valid = pd.read_csv('run_03_iteration_01_withoutErrors.csv', sep=';')

# Iterazione 2 (dopo correzione)
df_iter2_errors = pd.read_csv('run_03_iteration_02_withErrors.csv', sep=';')
df_iter2_valid = pd.read_csv('run_03_iteration_02_withoutErrors.csv', sep=';')

print("Iterazione 1:")
print(f"  Validi: {len(df_iter1_valid) - 2}")
print(f"  Totali: {len(df_iter1_errors) - 2}")

print("Iterazione 2:")
print(f"  Validi: {len(df_iter2_valid) - 2}")
print(f"  Totali: {len(df_iter2_errors) - 2}")
print(f"  Miglioramento: +{len(df_iter2_valid) - len(df_iter1_valid)} PPI corretti")
```

### Caso 4: Identificazione PPI Problematici
**Obiettivo**: Trovare quali PPI specifici danno sempre errore
**File da usare**: `_withErrors.csv` di tutti i run

```python
import pandas as pd
from collections import Counter

problematic_ppis = []

# Analizza tutti i run
for run in range(1, 11):
    df_errors = pd.read_csv(f'run_{run:02d}_iteration_01_withErrors.csv', sep=';')
    df_valid = pd.read_csv(f'run_{run:02d}_iteration_01_withoutErrors.csv', sep=';')
    
    # Trova PPI che sono in withErrors ma non in withoutErrors
    all_names = set(df_errors['Name'].dropna())
    valid_names = set(df_valid['Name'].dropna())
    error_names = all_names - valid_names
    
    problematic_ppis.extend(error_names)

# Conta frequenza errori
error_freq = Counter(problematic_ppis)
print("PPI più problematici:")
for ppi, count in error_freq.most_common(5):
    print(f"  {ppi}: {count}/10 run con errori")
```

## 📈 Vantaggi

### 1. **Separazione Dati Validi/Invalidi**
- Analisi pulita sui dati validi
- Debug completo con tutti i dati

### 2. **Tracciabilità Completa**
- Nessuna perdita di informazioni
- Visibilità su tutti i PPI generati

### 3. **Flessibilità Analisi**
- Scegli quale file usare in base all'obiettivo
- Confronto facile tra versioni

### 4. **Debug Facilitato**
- Identificazione immediata PPI problematici
- Analisi pattern di errori

### 5. **Metriche Accurate**
- Success rate preciso
- Identificazione PPI affidabili

## 📊 Esempio Completo

### Scenario: Run con Correzioni

#### Iterazione 1 (Iniziale)
```
run_03_iteration_01_withoutErrors.csv:
  - 12 PPI validi

run_03_iteration_01_withErrors.csv:
  - 16 PPI totali (12 validi + 4 con errori)
```

#### Iterazione 2 (Dopo Correzione Level 1)
```
run_03_iteration_02_withoutErrors.csv:
  - 15 PPI validi (+3 corretti)

run_03_iteration_02_withErrors.csv:
  - 16 PPI totali (15 validi + 1 con errore)
```

#### Iterazione 3 (Dopo Correzione Level 2)
```
run_03_iteration_03_withoutErrors.csv:
  - 16 PPI validi (+1 corretto)

run_03_iteration_03_withErrors.csv:
  - 16 PPI totali (16 validi + 0 errori)
```

### Analisi
```python
# Carica tutte le iterazioni
iterations = [1, 2, 3]
results = []

for iter_num in iterations:
    df_valid = pd.read_csv(f'run_03_iteration_{iter_num:02d}_withoutErrors.csv', sep=';')
    df_all = pd.read_csv(f'run_03_iteration_{iter_num:02d}_withErrors.csv', sep=';')
    
    valid = len(df_valid) - 2
    total = len(df_all) - 2
    errors = total - valid
    
    results.append({
        'iteration': iter_num,
        'valid': valid,
        'total': total,
        'errors': errors,
        'success_rate': f"{valid/total*100:.1f}%"
    })

df_results = pd.DataFrame(results)
print(df_results)
```

**Output**:
```
   iteration  valid  total  errors success_rate
0          1     12     16       4        75.0%
1          2     15     16       1        93.8%
2          3     16     16       0       100.0%
```

## 🔄 Workflow Consigliato

### 1. Durante l'Esecuzione
- Sistema salva automaticamente entrambi i file
- Nessuna azione richiesta

### 2. Analisi Rapida (Solo Risultati Validi)
```python
# Usa solo _withoutErrors.csv
df = pd.read_csv('activity/run_01_iteration_01_withoutErrors.csv', sep=';')
# Analizza solo PPI affidabili
```

### 3. Analisi Completa (Debug)
```python
# Usa _withErrors.csv per vedere tutto
df_all = pd.read_csv('activity/run_01_iteration_01_withErrors.csv', sep=';')
df_valid = pd.read_csv('activity/run_01_iteration_01_withoutErrors.csv', sep=';')
# Confronta e identifica problemi
```

### 4. Report Aggregato
```python
# Analizza tutti i run
summary = []
for run in range(1, 11):
    df_valid = pd.read_csv(f'activity/run_{run:02d}_iteration_01_withoutErrors.csv', sep=';')
    df_all = pd.read_csv(f'activity/run_{run:02d}_iteration_01_withErrors.csv', sep=';')
    
    summary.append({
        'run': run,
        'valid_ppis': len(df_valid) - 2,
        'total_ppis': len(df_all) - 2,
        'success_rate': f"{(len(df_valid)-2)/(len(df_all)-2)*100:.1f}%"
    })

summary_df = pd.DataFrame(summary)
print(summary_df)
summary_df.to_csv('activity_summary.csv', index=False)
```

## 📁 Struttura Finale

```
quantitative_assessment/batch_results/time/results_run_20241110_140000/
├── Declaration_SUBMITTED_by_EMPLOYEE/
│   ├── run_01_iteration_01_withoutErrors.csv  (16 PPI validi)
│   ├── run_01_iteration_01_withErrors.csv     (16 PPI totali)
│   ├── run_02_iteration_01_withoutErrors.csv  (14 PPI validi)
│   ├── run_02_iteration_01_withErrors.csv     (16 PPI totali)
│   ├── run_03_iteration_01_withoutErrors.csv  (12 PPI validi)
│   ├── run_03_iteration_01_withErrors.csv     (16 PPI totali)
│   ├── run_03_iteration_02_withoutErrors.csv  (15 PPI validi - dopo correzione)
│   ├── run_03_iteration_02_withErrors.csv     (16 PPI totali)
│   └── ...
├── Declaration_APPROVED_by_ADMINISTRATION/
│   └── ...
└── ...
```

## 🎉 Conclusione

Il doppio salvataggio offre:
- ✅ **Dati puliti** per analisi (_withoutErrors)
- ✅ **Dati completi** per debug (_withErrors)
- ✅ **Flessibilità** nella scelta del file
- ✅ **Tracciabilità** totale di tutti i PPI
- ✅ **Metriche** accurate su success rate

**Massima flessibilità per ogni tipo di analisi!** 🚀
