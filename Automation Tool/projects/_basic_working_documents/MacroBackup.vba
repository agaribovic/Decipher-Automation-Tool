Sub ConvertListToNumber()
'
' bbhelpFunctions.ConvertListToNumber Macro
'
'

ActiveDocument.ConvertNumbersToText

n = ActiveDocument.Hyperlinks.Count

For i = n To 1 Step -1

    ActiveDocument.Hyperlinks(i).Delete

Next i

ActiveDocument.Range.Find.ClearFormatting
ActiveDocument.Range.Find.Replacement.ClearFormatting
With ActiveDocument.Range.Find
    .Text = "^l"
    .Replacement.Text = "^p"
    .Forward = True
    .Wrap = wdFindContinue
    .Format = False
    .MatchCase = False
    .MatchWholeWord = False
    .MatchWildcards = False
    .MatchSoundsLike = False
    .MatchAllWordForms = False
End With
ActiveDocument.Range.Find.Execute Replace:=wdReplaceAll


End Sub