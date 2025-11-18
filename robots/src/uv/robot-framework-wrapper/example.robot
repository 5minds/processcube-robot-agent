*** Settings ***
Documentation     Example Robot Framework file for UV wrapper testing
Library           Collections
Library           String

*** Variables ***
${DEFAULT_TIMEOUT}    5s
${EXAMPLE_VAR}    default_value

*** Test Cases ***
Example Test 1: Simple Variable Processing
    [Documentation]    Demonstrates variable passing and string operations
    Log    Testing with variable: ${EXAMPLE_VAR}
    Should Be Equal As Strings    ${EXAMPLE_VAR}    default_value
    Log    Variable test passed

Example Test 2: Dictionary Operations
    [Documentation]    Demonstrates working with collections
    &{data}=    Create Dictionary    key1=value1    key2=value2
    Log Dictionary    ${data}
    Should Be Equal    ${data}[key1]    value1
    Log    Dictionary operations test passed

Example Test 3: String Manipulation
    [Documentation]    Demonstrates string operations
    ${text}=    Set Variable    Hello Robot Framework
    ${uppercase}=    Convert To Uppercase    ${text}
    Log    Original: ${text}
    Log    Uppercase: ${uppercase}
    Should Contain    ${uppercase}    ROBOT
    Log    String manipulation test passed

*** Keywords ***
Log Dictionary
    [Arguments]    ${dict}
    Log    Dictionary content: ${dict}
