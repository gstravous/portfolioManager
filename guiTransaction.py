from addTransaction import add_transaction
import PySimpleGUI as sg
import pandas as pd

# GUI Window Layout
layout = [sg.Text('Portfolio Name'), sg.InputText()], \
         [sg.Text('Position ID'), sg.InputText()], \
         [sg.Text('Stock'), sg.InputText()], \
         [sg.Text('Expiration Month'), sg.InputText()], \
         [sg.Text('Expiration Day'), sg.InputText()], \
         [sg.Text('Expiration Year'), sg.InputText()], \
         [sg.Text('Put Call'), sg.InputText()], \
         [sg.Text('Strike'), sg.InputText()], \
         [sg.Text('Change in Shares'), sg.InputText()], \
         [sg.Text('Price per Share'), sg.InputText()], \
         [sg.Text('Trade Date'), sg.InputText()], \
         [sg.Button('Enter'), sg.Button('Cancel')]

window = sg.Window('Input Transaction', layout)  # Create the Window

# GUI
while True:
    event, transaction = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break

    transaction = list(pd.json_normalize(transaction).loc[0])  # converts to list

    transaction = [x.upper().replace(' ', '') for x in transaction]

    add_transaction(*transaction)

window.close()


