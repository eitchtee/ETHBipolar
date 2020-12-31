import locale
import os
import pickle
import signal
import time
import traceback
from datetime import datetime
from random import randint

from money.currency import Currency
from money.money import Money

from twitter import twittar
from api import get_price

locale.setlocale(locale.LC_ALL, '')


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def checar_diferenca(ultimo_valor, valor_atual):
    valor_minimo = 30
    diferenca = round(abs(valor_atual - ultimo_valor), 2)

    aumento = valor_atual - ultimo_valor
    aumento_porcentagem = aumento / ultimo_valor

    if aumento_porcentagem >= 0:
        porcentagem_status = "📈"
    else:
        porcentagem_status = "📉"

    aumento_porcentagem = "{:+.2%}".format(aumento_porcentagem).replace('.', ',')

    return diferenca > valor_minimo, diferenca, valor_atual > ultimo_valor, aumento_porcentagem, porcentagem_status


def price_check():
    # Carrega o último valor verificado de uma db ou cria a database e
    # aguarda a próxima execução
    try:
        with open(valor_db_path, 'rb') as db:
            ultimo_valor = pickle.load(db)
    except FileNotFoundError:
        print('Rodando pela primeira vez.')
        try:
            valor_atual_brl = get_price()[0]
            with open(valor_db_path, 'wb') as db:
                pickle.dump(valor_atual_brl, db,
                            protocol=pickle.HIGHEST_PROTOCOL)
        except:
            traceback.print_exc()
            return
    else:
        try:
            valor_atual_brl, brl_24hr, valor_atual_usd, usd_24hr = get_price()

            dif_check, dif_valor, subiu, porcentagem, porcentagem_status = checar_diferenca(ultimo_valor,
                                                                        valor_atual_brl)

            if dif_check:
                valor_reais = Money(str(valor_atual_brl), Currency.BRL). \
                    format('pt_BR')
                valor_dolar = Money(str(valor_atual_usd), Currency.USD). \
                    format('pt_BR')
                hora = datetime.now().strftime('%H:%M')
                dia = datetime.now().strftime('%d/%m/%Y')

                if subiu:
                    msg = f"🟢 Ethereum subiu :)\n\n" \
                          f"🇧🇷 {valor_reais} ({porcentagem})\n" \
                          f"🇺🇸 {valor_dolar}\n\n" \
                          f"{porcentagem_status} 24h: {brl_24hr}\n\n" \
                          f"🗓️ Em {dia} às {hora}."
                    try:
                        twittar(msg)
                        print(f"🟢 Ethereum subiu. "
                              f'Último valor: {ultimo_valor} | '
                              f'Valor atual: {valor_atual_brl} | '
                              f'Diferença: {dif_valor}')
                    except:
                        traceback.print_exc()
                        return
                else:
                    msg = f"🔴 Ethereum caiu :(\n\n" \
                          f"🇧🇷 {valor_reais} ({porcentagem})\n" \
                          f"🇺🇸 {valor_dolar}\n\n" \
                          f"{porcentagem_status} 24h: {brl_24hr}\n\n" \
                          f"🗓️ Em {dia} às {hora}."
                    try:
                        twittar(msg)
                        print(f"🔴 Ethereum caiu. "
                              f'Último valor: {ultimo_valor} | '
                              f'Valor atual: {valor_atual_brl} | '
                              f'Diferença: {dif_valor}')
                    except:
                        traceback.print_exc()
                        return
                with open(valor_db_path, 'wb') as db:
                    pickle.dump(valor_atual_brl, db,
                                protocol=pickle.HIGHEST_PROTOCOL)
            else:
                print(f'Diferença insignificante para ser postada. Último '
                      f'valor: {ultimo_valor} | Valor a'
                      f'tual: {valor_atual_brl} | Diferença: {dif_valor}')
        except:
            traceback.print_exc()
            return


if __name__ == '__main__':
    work_dir = os.path.dirname(os.path.realpath(__file__))
    valor_db_path = os.path.normpath(f'{work_dir}/ultimo_valor.db')

    killer = GracefulKiller()
    while not killer.kill_now:
        price_check()
        print("---")  # Separa os logs de cada execução.
        time.sleep(randint(180, 1800))

    print("Parando execução.")
