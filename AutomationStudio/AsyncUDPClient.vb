﻿
Imports System.Net
Imports System.Net.Sockets
Imports System.Threading

Public Class AsyncUDPClient


    ' If you intend to receive multicasted datagrams, do not call the Connect method prior to calling the Receive method.
    ' The UdpClient you use to receive datagrams must be created using the multicast port number.

    Private _LocalEP As IPEndPoint 'Usually [LocalIP("192.168.1.5"), 3671]
    Private _RemoteEP As IPEndPoint 'Usually [IPInterface("192.168.1.239"),3671]
    Private _AnyEP As IPEndPoint = New IPEndPoint(IPAddress.Any, 0) 'All interfaces and Any Port
    Private _MultiCastEP As IPEndPoint = New IPEndPoint(IPAddress.Parse("224.0.23.12"), 3671) 'Usually [Multicast IP("224.0.23.12"), 3671]

    Private _Client As UdpClient

    Private _Listner As Task
    Private _ListnerCTS As CancellationTokenSource
    Public Shared BbbIP As IPEndPoint = New IPEndPoint(IPAddress.Parse("192.168.1.31"), 9909)
    Public Shared MyIP As IPEndPoint = New IPEndPoint(IPAddress.Parse("192.168.1.23"), 9910)
    'Public Shared BbbIP As IPEndPoint = New IPEndPoint(IPAddress.Parse("172.20.20.20"), 9909)
    'Public Shared MyIP As IPEndPoint = New IPEndPoint(IPAddress.Parse("172.20.20.20"), 9910)
    Public Shared client As New AsyncUDPClient()
    'Public Shared doConnect As Boolean = 0


    'Public Sub New()

    '    'Save the Local Endpoint to Use
    '    _LocalEP = LocalEndPoint

    '    ' Bind the UDP Client to Local EndPoint
    '    _Client = New UdpClient()

    '    'Set UDP Client Object Porperties
    '    _Client.DontFragment = True
    '    _Client.EnableBroadcast = True
    '    _Client.Client.SendBufferSize = 0

    'End Sub

    Public Sub New()

        'Save the Local Endpoint to Use
        _LocalEP = MyIP

        ' Bind the UDP Client to Local EndPoint
        _Client = New UdpClient(_LocalEP)

        'Set UDP Client Object Porperties
        _Client.DontFragment = True
        _Client.EnableBroadcast = True
        _Client.Client.SendBufferSize = 0

    End Sub

    Public Property LocalEndPoint As IPEndPoint
        Get
            Return _LocalEP
        End Get
        Set(value As IPEndPoint)
            _LocalEP = value
        End Set
    End Property
    Public Property MulticastEndPoint As IPEndPoint
        Get
            Return _MultiCastEP
        End Get
        Set(value As IPEndPoint)
            _MultiCastEP = value
        End Set

    End Property


    ' Async Send Recieve Functions with Time Out
    Public Async Function SendAsync(ByVal Datagram() As Byte, ByVal TimeOut As Integer, ByVal DestEndPoint As EndPoint) As Task(Of Integer)
        If Datagram Is Nothing Then
            Throw New Exception("The Datagram() passed as argument is null.")
            Return -1
        End If

        Dim CTS = New CancellationTokenSource

        Try
            If _Client IsNot Nothing Then
                CTS.CancelAfter(TimeOut)
                Await _Client.SendAsync(Datagram, Datagram.Length, DestEndPoint)
                Return Datagram.Length
            Else
                Throw New Exception("Error Sending Datagram to host.")
            End If

        Catch TaskCancelledEx As TaskCanceledException
            Throw New Exception("Send Operation Timed Out", TaskCancelledEx)
        Catch ex As Exception
            Throw New Exception("An error occured while sending data to host network. Check inner exception for details.", ex)
        Finally
            CTS = Nothing
        End Try

        Return 0

    End Function
    Public Async Function ReceiveAsync(ByVal TimeOut As Integer) As Task(Of Byte())

        Dim CTS = New CancellationTokenSource
        Dim ReceiveResult As UdpReceiveResult

        Try

            If _Client IsNot Nothing Then
                CTS.CancelAfter(TimeOut)
                ReceiveResult = Await _Client.ReceiveAsync()
            Else
                Throw New Exception("Receive operation can not be performed without a healthy connection to host.")
            End If

        Catch TaskCancelledEx As TaskCanceledException
            Throw New Exception("Receive Operation Timed Out", TaskCancelledEx)
        Catch ex As Exception
            Throw New Exception("An error occured while receiving data from host network. Check inner exception for details.", ex)
        Finally
            CTS = Nothing
        End Try

        If ReceiveResult.Buffer.Length <> 0 Then
            Return ReceiveResult.Buffer
        Else
            Dim EmpatyBuffer() As Byte = New Byte(45) {}
            Return EmpatyBuffer
        End If

    End Function

    Public Shared _Datagrams As List(Of Byte()) = New List(Of Byte())


    Public Async Function ListenFor(ByVal TimeOut As Integer) As Task(Of List(Of Byte()))

        Dim CTS = New CancellationTokenSource
        Dim ReceiveResult As UdpReceiveResult

        _Datagrams.Clear()

        Try

            If _Client IsNot Nothing Then
                CTS.CancelAfter(TimeOut)
                SyncLock (_Datagrams)
                    Task.Run(New Action(Async Function()
                                            While True
                                                ReceiveResult = Await _Client.ReceiveAsync()
                                                Dim ReceivedDatagram() As Byte = ReceiveResult.Buffer
                                                _Datagrams.Add(ReceivedDatagram)
                                            End While
                                        End Function), CTS.Token)
                End SyncLock

            Else
                Throw New Exception("Cannon listen on an uninitialized Client.The UDP Cleint is not Initialized.")
            End If

        Catch TaskCancelledEx As TaskCanceledException
            'Throw New Exception("Receive Operation Timed Out", TaskCancelledEx)
        Catch ex As Exception
            Throw New Exception("An error occured while receiving data from host network. Check inner exception for details.", ex)
        Finally
            CTS = Nothing
        End Try

        Return _Datagrams

    End Function


    Public Sub Listen()
        If _Client IsNot Nothing Then
            _ListnerCTS = New CancellationTokenSource
            _Listner = Task.Run(New Action(AddressOf Listener), _ListnerCTS.Token)
        End If
    End Sub


    Public Delegate Sub DatagramReceivedDelegate(ByVal Datagramas() As Byte)
    Public DataReceived As DatagramReceivedDelegate


    Private Async Function Listener() As Task
        Try
            While True
                Dim ReceiveResult As UdpReceiveResult = Await _Client.ReceiveAsync()
                Dim ReceivedDatagram() As Byte = ReceiveResult.Buffer
                DataReceived(ReceivedDatagram)
            End While
        Catch Ex As Exception

        End Try

    End Function

    Private Sub ListenerStopped()

    End Sub

    Public Sub Close()
        _ListnerCTS.Cancel()
        _Client.Close()
    End Sub

    Sub StopListening()
        _ListnerCTS.Cancel()
    End Sub

End Class
