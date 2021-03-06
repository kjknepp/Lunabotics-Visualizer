﻿Imports Microsoft.Xna
Imports Microsoft.Xna.Framework
Imports Microsoft.Xna.Framework.Input
Imports Microsoft.Xna.Framework.GamerServices
Imports Microsoft.Xna.Framework.Content
Imports System.Net
Imports System.Timers
Imports System.IO

Class MainWindow
    Inherits Elysium.Controls.Window

    Private MASK = 128
    Private MASK16 = 32768
    Private BYTEMAX = 255
    Private BIT15MAX = 32767
    Private BYTE2MAX = 65535
    Private EXCAV_MAXRPM As Double = 100
    Private EXCAV_MAXCURRENT As Double = 40
    Private LEFT_MAXRPM As Double = 100
    Private LEFT_MAXCURRENT As Double = 40
    Private RIGHT_MAXRPM As Double = 100
    Private RIGHT_MAXCURRENT As Double = 40
    Private SYS_MAXVOLT As Double = 30
    Private SYS_MAXCURRENT As Double = 40
    Private SYS_MAXPOWER As Double = 1000
    Private SYS_MAXCUMPOW As Double = 500

    Private Xon As Byte = 0
    Private Yon As Byte = 0
    Private Aon As Byte = 0
    Private Bon As Byte = 0
    Private LBon As Byte = 0
    Private RBon As Byte = 0
    Private DPDOWNon As Byte = 0
    Private DPUPon As Byte = 0
    Private DPRIGHTon As Byte = 0
    Private DPLEFTon As Byte = 0
    Private STARTon As Byte = 0
    Private BACKon As Byte = 0
    Private RightStickY As Byte = 0
    Private LeftStickY As Byte = 0
    Private RightTrigger As Byte = 0
    Private LeftTrigger As Byte = 0

    Private currentState As GamePadState
    Private DesiredValueTrue As Boolean = True
    Private DesiredValueFalse As Boolean = False
    Private DesiredContentPressed As String = "Pressed"
    Private DesiredContentLB As String = "LB"
    Private DesiredContentRB As String = "RB"

    Private theNegs As Byte

    Private isAuto As Integer = 1
    Private isRunning As Integer = 0
    Private dontTry As Integer = 0

    Private notSent As Integer = 0
    Private notRecieved As Integer = 0
    Private controllerError As Integer = 0

    Private undisplayedLog As String = ""

    Private Sub Window_Loaded(sender As Object, e As RoutedEventArgs)

    End Sub

    Friend WithEvents Timer1 As Timer





    Delegate Sub outLogs(ByVal a As Byte())
    Friend Sub setComLog(ByVal a As Byte())
        If Len(ComLog.Text) > 1000 Then
            Dim b As String() = Split(ComLog.Text, vbNewLine)

            ComLog.Text = String.Join(vbNewLine, b, 1, b.Length - 1)
        End If

        ComLog.Text += TimeValue(Now) + ","
        ComLog.Text += CStr(a(0)) + ","
        ComLog.Text += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(1)) << 8) + Convert.ToInt32(a(2))) / BYTE2MAX * SYS_MAXCURRENT * 100)) / 100) + ","
        ComLog.Text += CStr(a(3)) + ","
        ComLog.Text += CStr(a(4)) + ","
        ComLog.Text += CStr(a(5)) + ","
        ComLog.Text += CStr(a(6)) + ","
        ComLog.Text += CStr(a(7)) + ","
        ComLog.Text += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(8)) << 8) + Convert.ToInt32(a(9))) / BYTE2MAX * SYS_MAXCUMPOW * 100)) / 100) + ","
        ComLog.Text += CStr(a(10)) + ","
        ComLog.Text += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(11)) << 8) + Convert.ToInt32(a(12))) / BYTE2MAX * SYS_MAXVOLT * 100)) / 100) + ","
        ComLog.Text += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(13)) << 8) + Convert.ToInt32(a(14))) / BYTE2MAX * EXCAV_MAXCURRENT * 100)) / 100) + ","
        ComLog.Text += CStr(a(15)) + "
"
        undisplayedLog += TimeValue(Now) + ","
        undisplayedLog += CStr(a(0)) + ","
        undisplayedLog += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(1)) << 8) + Convert.ToInt32(a(2))) / BYTE2MAX * SYS_MAXCURRENT * 100)) / 100) + ","
        undisplayedLog += CStr(a(3)) + ","
        undisplayedLog += CStr(a(4)) + ","
        undisplayedLog += CStr(a(5)) + ","
        undisplayedLog += CStr(a(6)) + ","
        undisplayedLog += CStr(a(7)) + ","
        undisplayedLog += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(8)) << 8) + Convert.ToInt32(a(9))) / BYTE2MAX * SYS_MAXCUMPOW * 100)) / 100) + ","
        undisplayedLog += CStr(a(10)) + ","
        undisplayedLog += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(11)) << 8) + Convert.ToInt32(a(12))) / BYTE2MAX * SYS_MAXVOLT * 100)) / 100) + ","
        undisplayedLog += CStr(Convert.ToDouble(Convert.ToInt16(Convert.ToDouble((Convert.ToInt32(a(13)) << 8) + Convert.ToInt32(a(14))) / BYTE2MAX * EXCAV_MAXCURRENT * 100)) / 100) + ","
        undisplayedLog += CStr(a(15)) + "
"

    End Sub

    Delegate Sub easyLog(ByVal value As Integer)
    Friend Sub systemLog(ByVal value As Integer)
        outSystemLog.Text = ""
        If controllerError Then
            outSystemLog.Text += "Controller not connected
"
        End If
        If notRecieved Then
            outSystemLog.Text += "Message not recieved
"
        End If
        If notSent Then
            outSystemLog.Text += "Message not sent
"
        End If
    End Sub




    Delegate Sub SetVectors(ByVal x As Integer, ByVal y As Integer)
    Friend Sub setPosition(ByVal x As Integer, ByVal y As Integer) 'SET POSITION HERE
    End Sub
    Friend Sub setDirection(ByVal x As Integer, ByVal y As Integer) 'SET DIRECTION HERE
    End Sub





    Delegate Sub SetTextBoxes(ByVal value As Integer)
    Friend Sub checkAutoToggle(ByVal value As Integer)
        If AutoToggle.IsChecked = "True" Then
            isAuto = 1
        Else
            isAuto = 0
        End If
    End Sub
    Friend Sub setSwitches(ByVal value As Integer)
        If (value And (1 << 7)) Then
            excavStowed_control.Text = "True"
        Else
            excavStowed_control.Text = "False"
        End If
        If (value And (1 << 6)) Then
            excavExtended_control.Text = "True"
        Else
            excavExtended_control.Text = "False"
        End If
        If (value And (1 << 5)) Then
            binExtended_control.Text = "True"
        Else
            binExtended_control.Text = "False"
        End If
        If (value And (1 << 4)) Then
            binStowed_control.Text = "True"
        Else
            binStowed_control.Text = "False"
        End If
        If (value And (1 << 3)) Then
            leftBumper_control.Text = "True"
        Else
            leftBumper_control.Text = "False"
        End If
        If (value And (1 << 2)) Then
            rightBumper_control.Text = "True"
        Else
            rightBumper_control.Text = "False"
        End If
    End Sub
    Friend Sub setCurrent(ByVal value As Integer)
        Dim out As Double = Convert.ToDouble(value) / BYTE2MAX * SYS_MAXCURRENT
        out = Convert.ToDouble(Convert.ToInt16(out * 100)) / 100 'Two Decimal Places
        p_outCurrent_overview.Text = out
        p_outCurrent.Text = out
        'Dim thing As New Sparrow.Chart.DoublePoint()
        'thing.Data = nextPointCurrent
        'nextPointCurrent += 1
        'thing.Value = value

    End Sub
    Friend Sub setERR(ByVal value As Integer) 'FIX ERR CODES HERE
    End Sub
    Friend Sub setTotalPower(ByVal value As Integer)
        Dim out As Double = Convert.ToDouble(value) / BYTE2MAX * SYS_MAXCUMPOW
        out = Convert.ToDouble(Convert.ToInt16(out * 100)) / 100 'Two Decimal Places
        p_outPowerConsumed_overview.Text = out
        p_outPowerConsumed.Text = out
    End Sub
    Friend Sub setExcPos(ByVal value As Integer)
        outExcAngle_control.Text = value
    End Sub
    Friend Sub setExcCurrent(ByVal value As Integer)
        Dim isNeg As UShort = (theNegs And (1 << 7)) >> 7
        Dim out As Double = Convert.ToDouble(value) / BYTE2MAX * EXCAV_MAXCURRENT
        If isNeg = 1 Then
            out = out * -1
        End If
        out = Convert.ToDouble(Convert.ToInt16(out * 100)) / 100 'Two Decimal Places
        outExcCurrent_control.Text = out
    End Sub
    Friend Sub setVoltage(ByVal value As Integer)
        Dim out As Double = Convert.ToDouble(value) / BYTE2MAX * SYS_MAXVOLT
        out = Convert.ToDouble(Convert.ToInt16(out * 100)) / 100 'Two Decimal Places
        p_outVoltage_overview.Text = out
        p_outVoltage.Text = out
    End Sub




    Delegate Sub SetCheckBoxCallback(ByVal value As Boolean)
    Friend Sub setOnline(ByVal value As Boolean)
        If value = True Then
            label_Connection.Content = "Online"
        Else
            label_Connection.Content = "Offline"
        End If
    End Sub
    Friend Sub SetXCheckBox(ByVal value As Boolean)
        XButton.IsChecked = value
    End Sub
    Friend Sub SetYCheckBox(ByVal value As Boolean)
        YButton.IsChecked = value
    End Sub
    Friend Sub SetACheckBox(ByVal value As Boolean)
        AButton.IsChecked = value
    End Sub
    Friend Sub SetBCheckBox(ByVal value As Boolean)
        BButton.IsChecked = value
    End Sub
    Friend Sub SetUpCheckBox(ByVal value As Boolean)
        UpButton.IsChecked = value
    End Sub
    Friend Sub SetDownCheckBox(ByVal value As Boolean)
        DownButton.IsChecked = value
    End Sub
    Friend Sub SetLeftCheckBox(ByVal value As Boolean)
        LeftButton.IsChecked = value
    End Sub
    Friend Sub SetRightCheckBox(ByVal value As Boolean)
        RightButton.IsChecked = value
    End Sub
    Friend Sub SetStartCheckBox(ByVal value As Boolean)
        StartButton.IsChecked = value
    End Sub
    Friend Sub SetBackCheckBox(ByVal value As Boolean)
        BackButton.IsChecked = value
    End Sub




    Delegate Sub SetButtonCallback(ByVal value As String)
    Friend Sub SetLBButton(ByVal value As String)
        LB.Content = value
    End Sub
    Friend Sub SetRBButton(ByVal value As String)
        RB.Content = value
    End Sub




    Delegate Sub SetProgressBarCallback(ByVal value As Single)
    Friend Sub SetLProgressBar(ByVal value As Single)
        LProgress.Value = Convert.ToDouble(value) * 100
    End Sub
    Friend Sub SetRProgressBar(ByVal value As Single)
        RProgress.Value = Convert.ToDouble(value) * 100
    End Sub
    Friend Sub SetUpProgressBar(ByVal value As Single)
        If value > 0 Then
            UpProgress.Value = Convert.ToDouble(value) * 100
        Else
            UpProgress.Value = 0
        End If
    End Sub
    Friend Sub SetDownProgressBar(ByVal value As Single)
        If value < 0 Then
            DownProgress.Value = Convert.ToDouble(value) * -100
        Else
            DownProgress.Value = 0
        End If

    End Sub
    Friend Sub SetLeftProgressBar(ByVal value As Single)
        If value < 0 Then
            LeftProgress.Value = Convert.ToDouble(value) * -100
        Else
            LeftProgress.Value = 0
        End If

    End Sub
    Friend Sub SetRightProgressBar(ByVal value As Single)
        If value > 0 Then
            RightProgress.Value = Convert.ToDouble(value) * 100
        Else
            RightProgress.Value = 0
        End If
    End Sub
    Friend Sub SetUp1ProgressBar(ByVal value As Single)
        If value > 0 Then
            Up1Progress.Value = Convert.ToDouble(value) * 100
        Else
            Up1Progress.Value = 0
        End If
    End Sub
    Friend Sub SetDown1ProgressBar(ByVal value As Single)
        If value < 0 Then
            Down1Progress.Value = Convert.ToDouble(value) * -100
        Else
            Down1Progress.Value = 0
        End If

    End Sub
    Friend Sub SetLeft1ProgressBar(ByVal value As Single)
        If value < 0 Then
            Left1Progress.Value = Convert.ToDouble(value) * -100
        Else
            Left1Progress.Value = 0
        End If

    End Sub
    Friend Sub SetRight1ProgressBar(ByVal value As Single)
        If value > 0 Then
            Right1Progress.Value = Convert.ToDouble(value) * 100
        Else
            Right1Progress.Value = 0
        End If
    End Sub





    Private Function setXBoxButtons()
        If currentState.IsConnected Then
            'Right side control buttons
            If currentState.Buttons.X = ButtonState.Pressed Then
                Xon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetXCheckBox), New Object() {DesiredValueTrue})
            Else
                Xon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetXCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.Buttons.Y = ButtonState.Pressed Then
                Yon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetYCheckBox), New Object() {DesiredValueTrue})
            Else
                Yon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetYCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.Buttons.A = ButtonState.Pressed Then
                Aon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetACheckBox), New Object() {DesiredValueTrue})
            Else
                Aon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetACheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.Buttons.B = ButtonState.Pressed Then
                Bon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetBCheckBox), New Object() {DesiredValueTrue})
            Else
                Bon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetBCheckBox), New Object() {DesiredValueFalse})
            End If
            'Left and right shoulders
            If currentState.Buttons.LeftShoulder = ButtonState.Pressed Then
                LBon = 1
                Me.Dispatcher.Invoke(New SetButtonCallback(AddressOf SetLBButton), New Object() {DesiredContentPressed})
            Else
                LBon = 0
                Me.Dispatcher.Invoke(New SetButtonCallback(AddressOf SetLBButton), New Object() {DesiredContentLB})
            End If
            If currentState.Buttons.RightShoulder = ButtonState.Pressed Then
                RBon = 1
                Me.Dispatcher.Invoke(New SetButtonCallback(AddressOf SetRBButton), New Object() {DesiredContentPressed})
            Else
                RBon = 0
                Me.Dispatcher.Invoke(New SetButtonCallback(AddressOf SetRBButton), New Object() {DesiredContentRB})
            End If
            'D Pad
            If currentState.DPad.Up = ButtonState.Pressed Then
                DPUPon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetUpCheckBox), New Object() {DesiredValueTrue})
            Else
                DPUPon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetUpCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.DPad.Down = ButtonState.Pressed Then
                DPDOWNon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetDownCheckBox), New Object() {DesiredValueTrue})
            Else
                DPDOWNon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetDownCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.DPad.Right = ButtonState.Pressed Then
                DPRIGHTon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetRightCheckBox), New Object() {DesiredValueTrue})
            Else
                DPRIGHTon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetRightCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.DPad.Left = ButtonState.Pressed Then
                DPLEFTon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetLeftCheckBox), New Object() {DesiredValueTrue})
            Else
                DPLEFTon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetLeftCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.Buttons.Start = ButtonState.Pressed Then
                STARTon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetStartCheckBox), New Object() {DesiredValueTrue})
            Else
                STARTon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetStartCheckBox), New Object() {DesiredValueFalse})
            End If
            If currentState.Buttons.Back = ButtonState.Pressed Then
                BACKon = 1
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetBackCheckBox), New Object() {DesiredValueTrue})
            Else
                BACKon = 0
                Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf SetBackCheckBox), New Object() {DesiredValueFalse})
            End If
            'Triggers
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetLProgressBar), New Object() {currentState.Triggers.Left})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetRProgressBar), New Object() {currentState.Triggers.Right})

            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetUpProgressBar), New Object() {currentState.ThumbSticks.Left.Y})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetDownProgressBar), New Object() {currentState.ThumbSticks.Left.Y})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetLeftProgressBar), New Object() {currentState.ThumbSticks.Left.X})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetRightProgressBar), New Object() {currentState.ThumbSticks.Left.X})

            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetUp1ProgressBar), New Object() {currentState.ThumbSticks.Right.Y})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetDown1ProgressBar), New Object() {currentState.ThumbSticks.Right.Y})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetLeft1ProgressBar), New Object() {currentState.ThumbSticks.Right.X})
            Me.Dispatcher.Invoke(New SetProgressBarCallback(AddressOf SetRight1ProgressBar), New Object() {currentState.ThumbSticks.Right.X})
            Return 0
        End If
        Return 1
    End Function






    Private Sub AutoToggle_Unchecked(sender As Object, e As RoutedEventArgs) Handles AutoToggle.Unchecked
        'Are You sure?
        If dontTry = 0 Then
            Dim result As Integer = MessageBox.Show("This will terminate Autonomy mode and may NOT be turned back on", "Are You sure?", MessageBoxButton.YesNo)
            If result = 6 Then
                AutoToggle.IsEnabled = False
                isAuto = 0
            ElseIf result = 7 Then
                AutoToggle.IsChecked = True
            End If
        End If
    End Sub

    Private Sub saveButton_Click(sender As Object, e As RoutedEventArgs) Handles saveButton.Click
        Dim L As Boolean = 1
        Dim LogFile As String = "LogFile.csv"
        Dim i As Integer = 0
        While ([L])
            If My.Computer.FileSystem.FileExists(LogFile) Then
                LogFile = "LogFile" + CStr(i) + ".csv"
                i += 1
            Else
                Dim file As System.IO.StreamWriter
                file = My.Computer.FileSystem.OpenTextFileWriter(LogFile, True)
                file.Write("Time,Switches,Current,Err,Position X,Position Y,Direction X,Direction Y,Total Power,Exc Position,System Voltage,Exc Current,The Negatives
")
                file.Write(undisplayedLog)
                file.Close()
                L = 0
            End If
        End While
    End Sub











    Private Async Sub MessageOutTimer_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Elapsed
        Dim outMessage(7) As Byte
        Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf checkAutoToggle), New Object() {1})
        Try
            If isAuto = 0 Then 'CHANGE FOR AUTONOMY CHANGE 0 to 1
                outMessage(0) = 1 'Auto ON
                Dim r As Integer = Await AsyncUDPClient.client.SendAsync(outMessage, 10, AsyncUDPClient.BbbIP)
            Else
                outMessage(0) = 0 'Auto OFF
                Dim out As Byte = (Aon << 7) + (Bon << 6) + (BACKon << 5) + (LBon << 4) + (RBon << 3) + (DPDOWNon << 2) + (DPLEFTon << 1) + (DPRIGHTon)
                outMessage(1) = out
                out = (DPUPon << 7) + (STARTon << 6) + (Xon << 5) + (Yon << 4) 'ROOM FOR 2 MORE BOOLS WITHOUT INCREASE OF DATA
                outMessage(2) = out
                If currentState.ThumbSticks.Left.Y >= 0 Then
                    outMessage(3) = Conversion.Int(currentState.ThumbSticks.Left.Y * 255)
                Else
                    outMessage(2) += 1 << 3 'outMessage(2) index 4
                    outMessage(3) = Conversion.Int(currentState.ThumbSticks.Left.Y * -255)
                End If
                If currentState.ThumbSticks.Right.Y >= 0 Then
                    outMessage(4) = Conversion.Int(currentState.ThumbSticks.Right.Y * 255)
                Else
                    outMessage(2) += 1 << 2 'outMessage(2) index 5
                    outMessage(4) = Conversion.Int(currentState.ThumbSticks.Right.Y * -255)
                End If
                outMessage(5) = Conversion.Int(currentState.Triggers.Left * 255)
                outMessage(6) = Conversion.Int(currentState.Triggers.Right * 255)

                Dim r As Integer = Await AsyncUDPClient.client.SendAsync(outMessage, 1, AsyncUDPClient.BbbIP)
            End If
            notSent = 0
        Catch
            notSent = 1
        End Try
    End Sub



    Private Async Sub MessageInTimer_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Elapsed
        Dim a As Byte()
        Try
            a = Await AsyncUDPClient.client.ReceiveAsync(1)
            theNegs = a(15)
            Me.Dispatcher.Invoke(New outLogs(AddressOf setComLog), New Object() {a})
            Me.Dispatcher.Invoke(New SetCheckBoxCallback(AddressOf setOnline), New Object() {True})
            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setSwitches), New Object() {a(0)})

            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setCurrent), New Object() {(Convert.ToInt32(a(1)) << 8) + Convert.ToInt32(a(2))})
            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setERR), New Object() {a(3)})

            'SetPosition
            Me.Dispatcher.Invoke(New SetVectors(AddressOf setPosition), New Object() {a(4), a(5)})

            'SetDirection
            Me.Dispatcher.Invoke(New SetVectors(AddressOf setDirection), New Object() {a(6), a(7)})

            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setTotalPower), New Object() {(Convert.ToInt32(a(8)) << 8) + Convert.ToInt32(a(9))})
            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setExcPos), New Object() {a(10)})

            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setVoltage), New Object() {(Convert.ToInt32(a(11)) << 8) + Convert.ToInt32(a(12))})

            Me.Dispatcher.Invoke(New SetTextBoxes(AddressOf setExcCurrent), New Object() {(Convert.ToInt32(a(13)) << 8) + Convert.ToInt32(a(14))})
            notRecieved = 0
        Catch
            notRecieved = 1
        End Try
    End Sub



    Private Async Sub Timer1_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Elapsed
        Await Task.Delay(0)
        Me.Dispatcher.Invoke(New easyLog(AddressOf systemLog), New Object() {1})
        isRunning = 1
        currentState = GamePad.GetState(PlayerIndex.One)
        If setXBoxButtons() Then
            controllerError = 1
        Else
            controllerError = 0
        End If
    End Sub
End Class