*** Settings ***
Library    OperatingSystem
Library    RPA.Robocorp.WorkItems

*** Tasks ***
Demo Task
    ${PAYLOAD}=     Get work item variable    test
    
    ${variables}=    Create Dictionary
    ...    Test=${PAYLOAD}

    Create Output Work Item    variables=${variables}    save=True