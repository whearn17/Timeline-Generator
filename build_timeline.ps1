# Read the data
$data = Get-Content 'C:\Users\whearn\OneDrive - surefirecyber.com\Documents\Programs\Python\TimelineGenerator\test.txt'

# Start Word and create a new document
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $true
$document = $wordApp.Documents.Add()

# Add a table
$table = $document.Tables.Add($document.Range(), $data.Count, 3)  # 3 columns: time, event, description
$table.Style = 'Table Grid'

# Populate the table
for ($i = 0; $i -lt $data.Count; $i++) {
    $columns = $data[$i] -split '\t'  # assuming a tab-separated format
    for ($j = 0; $j -lt 3; $j++) {
        $table.Cell($i + 1, $j + 1).Range.Text = $columns[$j]
    }
}

# Save and close the document (optional)
$document.SaveAs('C:\Users\whearn\OneDrive - surefirecyber.com\Documents\Programs\Python\TimelineGenerator\test.docx')
$document.Close()
