import csv

# Carica le posizioni dal file posizioni.csv
posizioni = {}
with open('posizioni.csv', 'r', newline='') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        symbol = row['Symbol']
        quantity = int(row['Quantity'])
        trade_price = float(row['TradePrice'].replace(',', '.'))
        cost_basis_price = float(row['CostBasisPrice'].replace(',', '.'))
        side = row['Side']
        if symbol not in posizioni:
            posizioni[symbol] = {'quantity': 0, 'cost_basis': 0, 'side': side}
        if side == 'BOT':
            posizioni[symbol]['quantity'] += quantity
            posizioni[symbol]['cost_basis'] += quantity * cost_basis_price
        else:
            posizioni[symbol]['quantity'] -= quantity
            posizioni[symbol]['cost_basis'] -= quantity * cost_basis_price

# Carica le transazioni dal file TRANSAZIONI.csv
transazioni = []
with open('TRANSAZIONI.csv', 'r', newline='') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        symbol = row['Symbol']
        quantity = int(row['Quantity'])
        trade_price = float(row['TradePrice'].replace(',', '.'))
        cost_basis = float(row['CostBasis'].replace(',', '.'))
        pnl_realized = float(row['FifoPnlRealized'].replace(',', '.'))
        commission = float(row['IBCommission'].replace(',', '.'))
        side = row['Buy/Sell']
        if side == 'BOT':
            transazioni.append({'symbol': symbol, 'quantity': quantity, 'trade_price': trade_price, 'cost_basis': cost_basis, 'pnl_realized': pnl_realized, 'commission': commission})
        else:
            transazioni.append({'symbol': symbol, 'quantity': -quantity, 'trade_price': trade_price, 'cost_basis': cost_basis, 'pnl_realized': -pnl_realized, 'commission': commission})

# Calcola il capital gain o loss per ogni posizione
risultati = []
for symbol in posizioni:
    quantity = posizioni[symbol]['quantity']
    cost_basis = posizioni[symbol]['cost_basis']
    side = posizioni[symbol]['side']
    pnl_realized_totale = 0
    commission_totale = 0
    for t in transazioni:
        if t['symbol'] == symbol and t['quantity'] != 0:
            if side == 'BOT':
                if quantity >= t['quantity']:
                    pnl_realized = (t['trade_price'] - cost_basis) * t['quantity'] - t['pnl_realized'] - t['commission']
                    quantity -= t['quantity']
                    cost_basis += t['quantity'] * t['trade_price']
                    pnl_realized_totale += pnl_realized
                    commission_totale += t['commission']
                else:
                    pnl_realized = (t['trade_price'] - cost_basis) * quantity - t['pnl_realized'] - t['commission']
                    t['quantity'] -= quantity
                    quantity = 0
                    cost_basis += quantity * t['trade_price']
                    pnl_realized_totale += pnl_realized
                    commission_totale += t['commission']
                    break
            else:
                if quantity <= -t['quantity']:
                    pnl_realized = (cost_basis - t['trade_price']) * t['quantity'] - t['pnl_realized'] - t['commission']
                    quantity += t['quantity']
                    cost_basis -= t['quantity'] * t['trade_price']
                    pnl_realized_totale += pnl_realized
                    commission_totale += t['commission']
                else:
                    pnl_realized = (cost_basis - t['trade_price']) * -quantity - t['pnl_realized'] - t['commission']
                    t['quantity'] += quantity
                    quantity = 0
                    cost_basis -= quantity * t['trade_price']
                    pnl_realized_totale += pnl_realized
                    commission_totale += t['commission']
                    break
    risultati.append({'symbol': symbol, 'quantity': posizioni[symbol]['quantity'], 'cost_basis': posizioni[symbol]['cost_basis'], 'pnl_realized_totale': pnl_realized_totale, 'commission_totale': commission_totale})

# Calcola il capital gain o loss totale e la commissione totale
capital_gain_totale = sum(r['pnl_realized_totale'] for r in risultati)
#commission_totale = sum(r['commission_totale'] for r in risultati)

# Scrive i risultati nel file risultati.csv
with open('risultati.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Symbol', 'Quantity', 'Cost Basis', 'Realized P&L', 'Commission'])
    for r in risultati:
        writer.writerow([r['symbol'], r['quantity'], r['cost_basis'], r['pnl_realized_totale'], r['commission_totale']])
    writer.writerow(['Total', '', '', capital_gain_totale, commission_totale])
