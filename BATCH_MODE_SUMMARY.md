# Riepilogo Modifiche - Modalità Batch PPIPilot

## 📋 Obiettivo
Creare una nuova interfaccia per eseguire automaticamente 10 analisi PPI per ogni attività del log, salvando i risultati in formato CSV senza visualizzazione a schermo.

## 🆕 File Creati

### 1. `interface_batch.py`
**Nuova interfaccia Streamlit per esecuzione batch**

Caratteristiche principali:
- ✅ Nessun display dei risultati a schermo
- ✅ Esecuzione automatica per tutte le attività
- ✅ 10 run per ogni attività (configurabile)
- ✅ Salvataggio automatico in CSV
- ✅ Barra di progresso e statistiche in tempo reale
- ✅ Gestione automatica degli errori (Level 1 e Level 2)

### 2. `BATCH_MODE_README.md`
**Documentazione completa della modalità batch**

Include:
- Panoramica delle funzionalità
- Istruzioni d'uso dettagliate
- Formato CSV di output
- Organizzazione dei file
- Parametri di configurazione
- Risoluzione problemi
- Esempi pratici

### 3. `run_batch_mode.bat`
**Script Windows Batch per avvio rapido**

Utilizzo:
```bash
run_batch_mode.bat
```

### 4. `run_batch_mode.ps1`
**Script PowerShell per avvio rapido**

Utilizzo:
```powershell
.\run_batch_mode.ps1
```

### 5. `test_batch_csv_format.py`
**Script di test per verificare il formato CSV**

Utilizzo:
```bash
python test_batch_csv_format.py
```

### 6. `BATCH_MODE_SUMMARY.md`
**Questo documento - riepilogo delle modifiche**

## 📊 Formato CSV Output

### Struttura
```
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
[dati PPI...]
```

### Colonne
1. **Name**: Nome del PPI
2. **Metric**: Descrizione del PPI
3. **Value**: Valore calcolato
4. **Agrupation**: Dati aggregati (JSON)
5. **Colonna77**: Classificazione (A, B, C, D)

### Esempio Reale
```csv
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from Declaration SUBMITTED by EMPLOYEE to Declaration APPROVED by ADMINISTRATION;The average of the duration between activity 'Declaration SUBMITTED by EMPLOYEE' and activity 'Declaration APPROVED by ADMINISTRATION';2 days, 14:16:11.181887;;A
Total time for Declaration APPROVED by ADMINISTRATION across all cases;The sum of the duration between activity Declaration APPROVED by ADMINISTRATION and the end of the case;76387 days, 9:04:32;;A
;RUN 3: No valid PPIs generated (2 errors);;;
Average time for Declaration APPROVED by ADMINISTRATION grouped by org:role;The average of the duration between activity 'Declaration APPROVED by ADMINISTRATION' and the end of case grouped by the last value of org:role;ADMINISTRATION:NaT;{"ADMINISTRATION":null,"EMPLOYEE":1212853258,"MISSING":null,"SUPERVISOR":517170500,"UNDEFINED":824069599};A
;RUN 5: No valid PPIs generated (1 errors);;;
```

**Nota Importante**: I CSV vengono salvati per **tutti i run**, anche quando non ci sono PPI validi. I run falliti sono tracciati con righe di commento che mostrano il numero del run e il conteggio degli errori.

## 📁 Organizzazione File Output

```
quantitative_assessment/
└── batch_results/
    └── [time|occurrency]/
        └── results_run_YYYYMMDD_HHMMSS/
            ├── Activity_1.csv
            ├── Activity_2.csv
            ├── Activity_3.csv
            └── ...
```

### Esempio Concreto
```
quantitative_assessment/
└── batch_results/
    └── time/
        └── results_run_20241110_115430/
            ├── Declaration_SUBMITTED_by_EMPLOYEE.csv
            ├── Declaration_APPROVED_by_ADMINISTRATION.csv
            ├── Declaration_FINAL_APPROVED_by_SUPERVISOR.csv
            ├── Declaration_REJECTED_by_PRE_APPROVER.csv
            └── Payment_Handled.csv
```

## 🔧 Parametri Configurabili

In `interface_batch.py`:

```python
NUM_RUNS_PER_ACTIVITY = 10  # Numero di esecuzioni per attività
MAX_LEVEL1_ITERATIONS = 2   # Iterazioni Level 1 (Re-translation)
MAX_LEVEL2_ITERATIONS = 2   # Iterazioni Level 2 (Error correction)
```

## 🚀 Come Utilizzare

### Metodo 1: Script Batch (Windows)
```bash
run_batch_mode.bat
```

### Metodo 2: Script PowerShell
```powershell
.\run_batch_mode.ps1
```

### Metodo 3: Comando Diretto
```bash
streamlit run interface_batch.py
```

### Configurazione nell'Interfaccia
1. **OpenAI API Key**: Inserire la chiave API
2. **Upload XES**: Caricare il file di log
3. **Description**: Descrizione del processo
4. **Organizational Goal**: Obiettivo organizzativo
5. **Category**: Scegliere "time" o "occurrency"
6. **Output Folder**: Cartella di destinazione (default: `quantitative_assessment/batch_results`)
7. **Click**: "▶️ Start Batch Execution"

## 📈 Statistiche Visualizzate

Durante l'esecuzione, per ogni attività vengono mostrate:
- **Total PPIs**: Numero totale di PPI generati
- **Total Errors**: Numero totale di errori
- **Success Rate**: Percentuale di successo
- **Avg PPIs/Run**: Media PPI per esecuzione

Al termine, viene mostrata una tabella riassuntiva con tutte le attività.

## ⚙️ Differenze con Interface Standard

| Caratteristica | Interface Standard | Interface Batch |
|----------------|-------------------|-----------------|
| **Display** | Tabelle interattive | Nessun display |
| **Esecuzione** | Singola attività | Tutte le attività |
| **Run** | 1 per esecuzione | 10 per attività |
| **Output** | UI Streamlit | File CSV |
| **Progresso** | Spinner | Barra + metriche |
| **Selezione** | Manuale | Automatica |

## 🎯 Vantaggi della Modalità Batch

1. **Automazione Completa**: Nessun intervento manuale richiesto
2. **Analisi Statistica**: 10 run permettono calcolo di media, deviazione standard, outlier
3. **Riproducibilità**: Risultati salvati permanentemente
4. **Scalabilità**: Gestione di log con molte attività
5. **Efficienza**: Esecuzione notturna o in background
6. **Formato Standard**: CSV facilmente importabile in Excel, Python, R

## 📊 Analisi dei Risultati

Con 10 run per attività è possibile:
- Calcolare **media** e **deviazione standard** dei valori PPI
- Identificare **outlier** e **anomalie**
- Valutare **consistenza** della generazione PPI
- Confrontare **affidabilità** di diversi tipi di PPI
- Analizzare **variabilità** dovuta a OpenAI

## ⏱️ Tempi di Esecuzione Stimati

- **Per attività**: ~2-5 minuti (dipende da dimensione log)
- **Per run**: ~15-30 secondi
- **Totale**: `num_attività × 10 × tempo_medio`

### Esempio
- Log con 20 attività
- 10 run per attività
- 3 minuti per run
- **Totale**: ~10 ore

**Raccomandazione**: Eseguire durante la notte o in orari non lavorativi

## 🔍 Gestione Errori

### Correzione Automatica
- **Level 1**: Re-traduzione JSON (max 2 iterazioni)
- **Level 2**: Correzione errori specifici (max 2 iterazioni)

### Tracking Errori
- Conteggio errori per run
- Status per ogni run (✅, ⚠️, ❌)
- Success rate per attività
- Log dettagliati in console

## 🧪 Testing

### Test Formato CSV
```bash
python test_batch_csv_format.py
```

Output atteso:
```
✅ Test CSV created: test_output.csv
📊 Number of data rows: 3
📄 Total lines in CSV: 5
📝 First 5 lines of CSV:
  1: Name;Metric;Value;Agrupation;Colonna77
  2: ;ERROR: computing metric {};;;
  3: [dati PPI...]
  ...
🧹 Test file removed
```

## 📝 Note Importanti

1. **Non Modificare `interface_2.py`**: L'interfaccia standard rimane invariata
2. **Compatibilità**: Utilizza le stesse funzioni di `fromLogtoPPI_prompt_pipeline_goal.py` e `ppinatjson.py`
3. **Formato CSV**: Compatibile con il formato esistente nei risultati quantitativi
4. **OpenAI API**: Richiede connessione internet stabile e quota API sufficiente
5. **Spazio Disco**: Verificare spazio disponibile per i file CSV

## 🔄 Workflow Consigliato

1. **Test Iniziale**: Eseguire con 1-2 attività per verificare configurazione
2. **Modifica Parametri**: Eventualmente ridurre `NUM_RUNS_PER_ACTIVITY` per test
3. **Esecuzione Completa**: Lanciare batch completo durante la notte
4. **Analisi Risultati**: Importare CSV in strumento di analisi (Excel, Python, R)
5. **Validazione**: Confrontare risultati tra diversi run
6. **Report**: Generare statistiche aggregate

## 🛠️ Troubleshooting

### Problema: Nessun PPI Generato
**Soluzione**: Verificare chiave OpenAI, nomi attività, descrizione/goal

### Problema: Tasso di Errore Alto
**Soluzione**: Semplificare goal, verificare attributi log, aumentare iterazioni

### Problema: Esecuzione Lenta
**Soluzione**: Ridurre `NUM_RUNS_PER_ACTIVITY`, usare log più piccolo per test

### Problema: File CSV Non Creati
**Soluzione**: Verificare permessi cartella output, spazio disco disponibile

## 📞 Supporto

Per problemi o domande:
1. Controllare log console per errori dettagliati
2. Consultare `BATCH_MODE_README.md`
3. Verificare `TESTING_GUIDE.md` per debug
4. Controllare stato API OpenAI

## ✅ Checklist Pre-Esecuzione

- [ ] OpenAI API key valida e con quota sufficiente
- [ ] File XES caricato correttamente
- [ ] Description e Goal compilati
- [ ] Categoria selezionata (time/occurrency)
- [ ] Output folder specificata
- [ ] Spazio disco sufficiente
- [ ] Connessione internet stabile
- [ ] Tempo disponibile per esecuzione completa

## 🎉 Conclusione

La modalità batch di PPIPilot permette di:
- ✅ Automatizzare completamente l'analisi PPI
- ✅ Generare dati per analisi statistica robusta
- ✅ Salvare risultati in formato standard CSV
- ✅ Gestire log con molte attività in modo efficiente
- ✅ Eseguire valutazioni quantitative riproducibili

**Pronto per l'uso!** 🚀
