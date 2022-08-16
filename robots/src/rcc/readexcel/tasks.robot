*** Settings ***
Library     Collections
Library     RPA.Excel.Files
Library     RPA.Robocorp.WorkItems


*** Tasks ***
Read Excel
    Open Workbook    data/sample.xlsx
    ${table}=    Read Worksheet As Table    header=True
    ${variables}=    Create Dictionary

    FOR    ${row}    IN    @{table}
        Set To Dictionary   ${variables}    ${row}[Col 1]=${row}[Col 2]
    END
    
    Create Output Work Item
    Set work item variables    variables=${variables}
    Save Work Item