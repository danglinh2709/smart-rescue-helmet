using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;
using SmartRescueHelmet.Unity.Presentation;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Networking
{
    /// <summary>
    /// Best-effort desktop client for the backend realtime endpoint. It is only
    /// a presentation bridge: MQTT remains the device-to-backend transport.
    /// </summary>
    public sealed class BackendWebSocketClient : MonoBehaviour
    {
        [SerializeField] private string endpoint = "ws://localhost:8000/ws";
        [SerializeField] private float reconnectDelaySeconds = 3f;

        private readonly ConcurrentQueue<RealtimeEnvelope> _received = new();
        private CancellationTokenSource _cancellation;
        private ClientWebSocket _socket;

        public bool IsConnected { get; private set; }
        public string LastMessageType { get; private set; } = "NONE";
        public string LastDeviceId { get; private set; } = string.Empty;
        public CommandCenterState State { get; } = new CommandCenterState();
        public event Action<RealtimeEnvelope> EnvelopeReceived;

        private void Start()
        {
            _cancellation = new CancellationTokenSource();
            _ = RunConnectionLoopAsync(_cancellation.Token);
        }

        private void Update()
        {
            while (_received.TryDequeue(out var envelope))
            {
                LastMessageType = envelope.MessageType;
                LastDeviceId = envelope.DeviceId;
                State.Apply(envelope);
                EnvelopeReceived?.Invoke(envelope);
            }
        }

        private async Task RunConnectionLoopAsync(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    _socket = new ClientWebSocket();
                    _socket.Options.KeepAliveInterval = TimeSpan.FromSeconds(15);
                    await _socket.ConnectAsync(new Uri(endpoint), cancellationToken);
                    IsConnected = true;
                    await ReceiveLoopAsync(_socket, cancellationToken);
                }
                catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
                {
                    break;
                }
                catch (Exception exception)
                {
                    Debug.LogWarning("[SRH] Backend WebSocket unavailable: " + exception.Message);
                }
                finally
                {
                    IsConnected = false;
                    _socket?.Dispose();
                    _socket = null;
                }

                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(reconnectDelaySeconds), cancellationToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
            }
        }

        private async Task ReceiveLoopAsync(ClientWebSocket socket, CancellationToken cancellationToken)
        {
            var buffer = new byte[4096];
            using var messageBuffer = new MemoryStream();

            while (socket.State == WebSocketState.Open && !cancellationToken.IsCancellationRequested)
            {
                var result = await socket.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken);
                if (result.MessageType == WebSocketMessageType.Close) return;
                if (result.MessageType != WebSocketMessageType.Text) continue;

                messageBuffer.Write(buffer, 0, result.Count);
                if (!result.EndOfMessage) continue;

                var payload = System.Text.Encoding.UTF8.GetString(messageBuffer.ToArray());
                messageBuffer.SetLength(0);
                if (RealtimeEnvelopeParser.TryParse(payload, out var envelope))
                    _received.Enqueue(envelope);
                else
                    Debug.LogWarning("[SRH] Ignored invalid backend WebSocket envelope.");
            }
        }

        private void OnDestroy()
        {
            _cancellation?.Cancel();
            _socket?.Abort();
            _socket?.Dispose();
            _cancellation?.Dispose();
        }
    }
}
