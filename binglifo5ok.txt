import pandas as pd

# Carica i dati delle posizioni e delle transazioni
posizioni = posizioni = pd.read_csv('posizioni.csv', sep=';')
transazioni = pd.read_csv('transazioni.csv', sep= ';')

# Definisco una funzione che accetta come parametri il dizionario capital_gain_loss e il DataFrame posizioni
def stampa_risultato(capital_gain_loss, posizioni):
    # Apro un file in modalità scrittura
    with open('risultato.txt', 'w') as f:
        # Itero attraverso ogni conto nel dizionario
        for account_id, total_gain_loss in capital_gain_loss.items():
            # Scrivo il conto e il capital gain/loss totale nel file
            f.write(f'Account ID: {account_id}\n')
            f.write(f'Capital Gain/Loss Totale: {total_gain_loss}\n')

            # Filtro le posizioni per questo conto
            posizioni_conto = posizioni[posizioni['ClientAccountID'] == account_id]

            # Raggruppo le posizioni per simbolo e calcolo il capital gain/loss per ogni simbolo
            posizioni_simbolo = posizioni_conto.groupby('Symbol').apply(lambda x: (x['TradePrice'] - x['CostBasisPrice']) * x['Quantity'] - x['IBCommission']).reset_index(name='Capital Gain/Loss')

            # Itero attraverso ogni simbolo e il relativo capital gain/loss
            for index, row in posizioni_simbolo.iterrows():
                # Scrivo il simbolo e il capital gain/loss nel file
                f.write(f'Simbolo: {row["Symbol"]}\n')
                f.write(f'Capital Gain/Loss: {row["Capital Gain/Loss"]}\n')

            # Scrivo una riga vuota per separare i conti
            f.write('\n')


# Ordina le transazioni per data di regolamento
transazioni = transazioni.sort_values(by='SettleDateTarget')

# Crea un dizionario per tenere traccia del capital gain/loss per ogni conto
capital_gain_loss = {}

# Itera attraverso ogni transazione
for index, row in transazioni.iterrows():
    # Ottieni le informazioni sulla transazione
    account_id = row['ClientAccountID']
    symbol = row['Symbol']
    quantity = row['Quantity']
    trade_price = row['TradePrice']
    commission = row['IBCommission']
    side = row['Buy/Sell']

    # Inizializza il capital gain/loss per questo conto se non è già presente nel dizionario
    if account_id not in capital_gain_loss:
        capital_gain_loss[account_id] = 0

    # Calcola il costo totale della transazione (prezzo di acquisto/vendita + commissioni)
    total_cost = trade_price * quantity + commission

    # Se la transazione è un acquisto
    if side == 'BUY':
        # Aggiungi una nuova posizione
        new_position = pd.DataFrame({
            'ClientAccountID': [account_id],
            'Symbol': [symbol],
            'Quantity': [quantity],
            'OpenPrice': [trade_price],
            'CostBasisPrice': [total_cost / quantity],
            'Side': ['LONG'],
            'OpenDateTime': [row['SettleDateTarget']],
            'HoldingPeriodDateTime': [None]
        })
        posizioni = pd.concat([posizioni, new_position], ignore_index=True)

    # Se la transazione è una vendita
    elif side == 'SELL':
        # Trova le posizioni aperte per questo simbolo e conto
        open_positions = posizioni[(posizioni['ClientAccountID'] == account_id) & (posizioni['Symbol'] == symbol) & (posizioni['Side'] == 'LONG')]

        # Ordina le posizioni aperte per data di apertura (LIFO)
        open_positions = open_positions.sort_values(by='OpenDateTime', ascending=False)

        # Itera attraverso le posizioni aperte
        for index, position in open_positions.iterrows():
            # Se la quantità della posizione è maggiore o uguale alla quantità della transazione
            if position['Quantity'] >= quantity:
                # Calcola il capital gain/loss per questa posizione
                gain_loss = (trade_price - position['CostBasisPrice']) * quantity - commission

                # Aggiorna il capital gain/loss totale per questo conto
                capital_gain_loss[account_id] += gain_loss

                # Aggiorna la quantità della posizione
                posizioni.at[index, 'Quantity'] -= quantity

                # Imposta la data di chiusura della posizione se la quantità è ora 0
                if posizioni.at[index, 'Quantity'] == 0:
                    posizioni.at[index, 'HoldingPeriodDateTime'] = row['SettleDateTarget']

                # Esci dal ciclo delle posizioni aperte
                break

            # Se la quantità della posizione è minore della quantità della transazione
            else:
                # Calcola il capital gain/loss per questa posizione
                gain_loss = (trade_price - position['CostBasisPrice']) * position['Quantity'] - commission

                # Aggiorna il capital gain/loss totale per questo conto
                capital_gain_loss[account_id] += gain_loss

                # Aggiorna la quantità della transazione
                quantity -= position['Quantity']

                # Imposta la data di chiusura della posizione
                posizioni.at[index, 'HoldingPeriodDateTime'] = row['SettleDateTarget']

# Chiamo la funzione con i parametri capital_gain_loss e posizioni

print('TradePrice' in posizioni.keys())
print(posizioni.columns)
print(posizioni.dtypes)
stampa_risultato(capital_gain_loss, posizioni)
