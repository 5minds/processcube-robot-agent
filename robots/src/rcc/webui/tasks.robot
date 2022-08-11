*** Settings ***
Library     RPA.Browser.Selenium


*** Tasks ***
Open Web UI
    Open Available Browser    https://www.5minds.de    browser_selection=chrome
    Click Element When Visible    css=._brlbs-btn-accept-all
    Capture Element Screenshot    alias:Div
