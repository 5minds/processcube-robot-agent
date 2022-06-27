*** Settings ***
Library    OperatingSystem
Library    RPA.Robocorp.WorkItems

*** Tasks ***
Demo Task
    ${payload} =    Get work item payload   
    Log    ${payload}
    Create File   test.test    ${payload}