Imports System.IO
Imports System.Threading


Public Class FmgEdit
    Shared bigendian = False
    Shared fs As FileStream

    Private Sub btnOpen_Click(sender As Object, e As EventArgs) Handles btnOpen.Click
        fs = File.Open(txtFMGfile.Text, FileMode.Open)

        bigendian = (RInt8(9) = -1)

        Dim numEntries As Integer
        Dim startOffset As Integer


        numEntries = RInt32(&HC)
        startOffset = RInt32(&H14)


        For i = 0 To numEntries - 1
            Dim startIndex As Integer
            Dim startID As Integer
            Dim endID As Integer
            Dim txtOffset As Integer
            Dim txt As String

            startIndex = RInt32(&H1C + i * &HC)
            startID = RInt32(&H1C + i * &HC + 4)
            endID = RInt32(&H1C + i * &HC + 8)

            For j = 0 To (endID - startID)
                txtOffset = RInt32(startOffset + ((startIndex + j) * 4))

                txt = ""
                If txtOffset > 0 Then
                    txt = RUniString(txtOffset)
                    txt = txt.Replace(Chr(10), "/n/")
                End If

                dgvTextEntries.Rows.Add({j + startID, txt})
            Next
        Next

        fs.Close()
    End Sub

    Private Function RInt8(ByVal loc As Integer) As SByte
        Dim tmpInt8 As SByte
        Dim byt(0) As Byte

        fs.Position = loc
        fs.Read(byt, 0, 1)

        tmpInt8 = CSByte(byt(0))

        Return tmpInt8
    End Function

    Private Function RInt32(ByVal loc As Integer) As Int32
        Dim tmpInt32 As Integer = 0
        Dim byt = New Byte() {0, 0, 0, 0}

        fs.Position = loc
        fs.Read(byt, 0, 4)

        If bigendian Then
            Array.Reverse(byt)
        End If

        tmpInt32 = BitConverter.ToInt32(byt, 0)

        Return tmpInt32
    End Function

    Private Function RUInt32(ByVal loc As Integer) As UInt32
        Dim tmpUInt32 As UInt32 = 0
        Dim byt = New Byte() {0, 0, 0, 0}

        fs.Position = loc
        fs.Read(byt, 0, 4)

        If bigendian Then
            Array.Reverse(byt)
        End If

        tmpUInt32 = BitConverter.ToUInt32(byt, 0)

        Return tmpUInt32
    End Function

    Private Function RUniString(ByVal loc As Integer) As String
        fs.Position = loc

        Dim tmpStr As String = ""
        Dim endstr As Boolean = False
        Dim byt(1) As Byte
        Dim chara As Char

        While Not endstr
            fs.Read(byt, 0, 2)

            If bigendian Then
                Array.Reverse(byt)
            End If

            chara = System.Text.Encoding.Unicode.GetString(byt)(0)
            If chara = Chr(0) Then
                endstr = True

            Else
                tmpStr = tmpStr & chara
            End If


        End While

        Return tmpStr
    End Function

    Private Sub WInt8(ByVal loc As Integer, ByVal val As SByte)
        fs.Position = loc
        fs.Write({CByte(val)}, 0, 1)
    End Sub

    Private Sub WInt16(ByVal loc As Integer, ByVal val As Int16)
        fs.Position = loc
        Dim byt(1) As Byte
        byt = BitConverter.GetBytes(val)

        If bigendian Then
            Array.Reverse(byt)
        End If

        fs.Write(byt, 0, 2)
    End Sub

    Private Sub WInt32(ByVal loc As Integer, ByVal val As Int32)
        fs.Position = loc
        Dim byt(3) As Byte

        byt = BitConverter.GetBytes(val)

        If bigendian Then
            Array.Reverse(byt)
        End If

        fs.Write(byt, 0, 4)
    End Sub

    Private Sub WUniString(ByVal loc As Integer, ByRef str As String)
        fs.Position = loc

        Dim byt(1) As Byte
        Dim chara As Char

        For i = 0 To str.Length - 1
            chara = str(i)
            byt = BitConverter.GetBytes(chara)

            If bigendian Then
                Array.Reverse(byt)
            End If

            fs.Write(byt, 0, 2)
        Next
    End Sub

    Private Sub WBytes(ByVal loc As Integer, ByVal byt() As Byte)
        fs.Position = loc
        fs.Write(byt, 0, byt.Length)
    End Sub
End Class