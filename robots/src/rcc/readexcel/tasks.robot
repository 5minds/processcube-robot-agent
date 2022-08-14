*** Settings ***
Library     RPA.Excel.Files
Library     RPA.Robocorp.WorkItems


*** Tasks ***
Read Excel
    Open Workbook    data/sample.xlsx
    ${table}=    Read Worksheet As Table    header=True

    FOR    ${row}    IN    @{table}
        Create Output Work Item    variables=${row}    save=True
    END
