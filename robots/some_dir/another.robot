*** Settings ***
Library    OperatingSystem
Library    RPA.Robocorp.WorkItems

*** Tasks ***
Another Demo Task
    ${PAYLOAD}=     Get work item variable    test
    
    ${variables}=    Create Dictionary
    ...    foo=${PAYLOAD}

    Create Output Work Item    variables=${variables}    save=True