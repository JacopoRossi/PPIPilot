# Funzionalità: Selezione Attività

## 🎯 Obiettivo
Permettere all'utente di scegliere se analizzare **tutte le attività** del log o solo **alcune specifiche**.

## ✅ Implementazione

### 1. Comportamento di Default
- ✅ **Checkbox "Analyze all activities" attivata** per default
- ✅ Analizza automaticamente **tutte le attività** del log
- ✅ Mostra il numero totale di attività che verranno analizzate

### 2. Selezione Manuale
- ⬜ **Deseleziona** il checkbox "Analyze all activities"
- 📋 Appare un **multiselect** con tutte le attività disponibili
- ✅ Seleziona **una o più attività** specifiche
- 🚫 Il pulsante "Start Batch Execution" è **disabilitato** se nessuna attività è selezionata

## 📊 Interfaccia Utente

### Modalità: Tutte le Attività (Default)
```
🎯 Activity Selection
☑️ Analyze all activities

ℹ️ Will analyze all 25 activities

🚀 Ready to execute 10 runs for each of the 25 selected activities
[▶️ Start Batch Execution]
```

### Modalità: Selezione Specifica
```
🎯 Activity Selection
☐ Analyze all activities

Select specific activities to analyze:
[▼ Declaration SUBMITTED by EMPLOYEE        ]
[▼ Declaration APPROVED by ADMINISTRATION   ]
[▼ Declaration FINAL_APPROVED by SUPERVISOR ]

ℹ️ Will analyze 3 selected activities

🚀 Ready to execute 10 runs for each of the 3 selected activities
[▶️ Start Batch Execution]
```

### Modalità: Nessuna Selezione
```
🎯 Activity Selection
☐ Analyze all activities

Select specific activities to analyze:
[                                           ]

⚠️ Please select at least one activity

🚀 Ready to execute 10 runs for each of the 0 selected activities
[▶️ Start Batch Execution] (DISABILITATO)
```

## 🔧 Codice Implementato

```python
# Activity selection
st.markdown("---")
st.markdown("### 🎯 Activity Selection")

use_all_activities = st.checkbox("✅ Analyze all activities", value=True)

if use_all_activities:
    selected_activities = st.session_state.activities
    st.info(f"📊 Will analyze **all {len(selected_activities)} activities**")
else:
    selected_activities = st.multiselect(
        "Select specific activities to analyze:",
        options=st.session_state.activities,
        default=st.session_state.activities[:1] if len(st.session_state.activities) > 0 else []
    )
    if len(selected_activities) > 0:
        st.info(f"📊 Will analyze **{len(selected_activities)} selected activities**")
    else:
        st.warning("⚠️ Please select at least one activity")

st.markdown("---")
st.markdown(f"### 🚀 Ready to execute {NUM_RUNS_PER_ACTIVITY} runs for each of the {len(selected_activities)} selected activities")

boton = st.button("▶️ Start Batch Execution", type="primary", disabled=(len(selected_activities) == 0))
```

## 📈 Casi d'Uso

### Caso 1: Analisi Completa (Default)
**Scenario**: Vuoi analizzare tutte le attività del log
**Azione**: Lascia il checkbox "Analyze all activities" attivato
**Risultato**: Vengono analizzate tutte le 25 attività (esempio)

### Caso 2: Test su Poche Attività
**Scenario**: Vuoi testare il sistema su 2-3 attività prima di lanciare l'analisi completa
**Azione**: 
1. Deseleziona "Analyze all activities"
2. Seleziona 2-3 attività dal dropdown
3. Avvia l'esecuzione
**Risultato**: Vengono analizzate solo le attività selezionate

### Caso 3: Focus su Attività Specifiche
**Scenario**: Sei interessato solo ad alcune attività critiche del processo
**Azione**:
1. Deseleziona "Analyze all activities"
2. Seleziona le attività di interesse (es. "Declaration APPROVED by ADMINISTRATION", "Payment Handled")
3. Avvia l'esecuzione
**Risultato**: Vengono analizzate solo le attività critiche

### Caso 4: Ri-esecuzione di Attività Problematiche
**Scenario**: Alcune attività hanno dato errori e vuoi ri-eseguirle
**Azione**:
1. Deseleziona "Analyze all activities"
2. Seleziona solo le attività che hanno dato problemi
3. Avvia l'esecuzione
**Risultato**: Vengono ri-analizzate solo le attività problematiche

## 🎯 Vantaggi

### 1. **Flessibilità**
- Analisi completa o parziale a scelta
- Adattabile a diverse esigenze

### 2. **Risparmio Tempo**
- Test rapidi su poche attività
- Evita di aspettare analisi complete per test

### 3. **Focus**
- Concentrazione su attività specifiche
- Analisi mirate su processi critici

### 4. **Debugging**
- Ri-esecuzione selettiva di attività problematiche
- Isolamento di problemi specifici

### 5. **Risorse**
- Risparmio di chiamate API OpenAI
- Riduzione tempo di esecuzione per test

## 📊 Esempio Pratico

### Scenario: Log con 25 Attività

#### Opzione 1: Analisi Completa
```
✅ Analyze all activities
📊 Will analyze all 25 activities
🚀 Ready to execute 10 runs for each of the 25 selected activities
Total: 250 esecuzioni (25 attività × 10 run)
Tempo stimato: ~2-3 ore
```

#### Opzione 2: Test su 3 Attività
```
☐ Analyze all activities
Selected:
  - Declaration SUBMITTED by EMPLOYEE
  - Declaration APPROVED by ADMINISTRATION
  - Payment Handled
📊 Will analyze 3 selected activities
🚀 Ready to execute 10 runs for each of the 3 selected activities
Total: 30 esecuzioni (3 attività × 10 run)
Tempo stimato: ~15-20 minuti
```

## 🔄 Workflow Consigliato

### 1. Prima Esecuzione (Test)
```
1. Carica il file XES
2. Deseleziona "Analyze all activities"
3. Seleziona 2-3 attività rappresentative
4. Esegui l'analisi
5. Verifica i risultati
```

### 2. Esecuzione Completa
```
1. Usa lo stesso file XES
2. Lascia "Analyze all activities" attivato
3. Esegui l'analisi completa
4. Raccogli tutti i risultati
```

### 3. Ri-esecuzione Selettiva
```
1. Identifica attività con problemi
2. Deseleziona "Analyze all activities"
3. Seleziona solo le attività problematiche
4. Ri-esegui l'analisi
5. Confronta con risultati precedenti
```

## 📁 Struttura Output

### Tutte le Attività
```
results_run_20241110_140000/
├── Activity_1/
│   ├── run_01_iteration_01.csv
│   └── ...
├── Activity_2/
│   └── ...
├── Activity_3/
│   └── ...
...
└── Activity_25/
    └── ...
```

### Attività Selezionate (3)
```
results_run_20241110_140000/
├── Declaration_SUBMITTED_by_EMPLOYEE/
│   ├── run_01_iteration_01.csv
│   └── ...
├── Declaration_APPROVED_by_ADMINISTRATION/
│   └── ...
└── Payment_Handled/
    └── ...
```

## 🎉 Conclusione

La funzionalità di selezione attività offre:
- ✅ **Default intelligente**: Analizza tutto
- ✅ **Flessibilità**: Selezione manuale quando serve
- ✅ **Validazione**: Impedisce esecuzioni vuote
- ✅ **Feedback**: Mostra sempre quante attività verranno analizzate
- ✅ **Efficienza**: Risparmio tempo e risorse per test

**Perfetto per test rapidi e analisi mirate!** 🚀
