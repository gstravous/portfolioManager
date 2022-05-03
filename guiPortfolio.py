from newPortfolio import new_portfolio
import PySimpleGUI as sg
import pandas as pd

# GUI Window Layout
layout = [sg.Text('Portfolio Name'), sg.InputText()], \
         [sg.Text('Date Opened'), sg.InputText()], \
         [sg.Text('Starting Balance'), sg.InputText()], \
         [sg.Button('Enter'), sg.Button('Cancel')]

window = sg.Window('Input Transaction', layout)  # Create the Window

# GUI
while True:
    event, portfolio = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break

    portfolio = list(pd.json_normalize(portfolio).loc[0])  # converts to list

    portfolio = [x.upper().replace(' ', '') for x in portfolio]

    new_portfolio(*portfolio)

window.close()


