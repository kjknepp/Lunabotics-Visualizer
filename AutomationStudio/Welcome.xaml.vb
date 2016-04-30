Imports System.Threading
Imports Microsoft.Xna
Imports Microsoft.Xna.Framework
Imports Microsoft.Xna.Framework.Input
Imports Microsoft.Xna.Framework.GamerServices
Imports Microsoft.Xna.Framework.Content
Imports System.Net
Imports System.Timers

Public Class Welcome

    Private Async Sub Window_Loaded(sender As Object, e As RoutedEventArgs)
        Await Task.Delay(1500)
        Dim IDE As MainWindow = New MainWindow
        IDE.Show()
        IDE.Timer1 = New System.Timers.Timer()
        IDE.Timer1.Start()
        Me.Close()
    End Sub
    Private IsAliveTimer As Timers.Timer


End Class
